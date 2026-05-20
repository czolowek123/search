import os
import re
import json
import urllib.request
import urllib.parse
from datetime import datetime
from html.parser import HTMLParser
from django.urls import path, re_path
from django.shortcuts import render
from django.conf import settings
from django.views.static import serve
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST, require_GET


OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2-vision:11b')
WEB_SEARCH_RESULT_LIMIT = int(os.environ.get('WEB_SEARCH_RESULT_LIMIT', '3'))
WEB_SOURCE_TEXT_LIMIT = int(os.environ.get('WEB_SOURCE_TEXT_LIMIT', '4000'))
WEB_REQUEST_TIMEOUT = int(os.environ.get('WEB_REQUEST_TIMEOUT', '10'))
OLLAMA_ANSWER_FILE = os.environ.get('OLLAMA_ANSWER_FILE', 'main.txt')
WEB_USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/124.0 Safari/537.36'
)


def _normalize_space(text):
    return re.sub(r'\s+', ' ', text or '').strip()


def _is_fetchable_web_url(url):
    parsed_url = urllib.parse.urlparse(url)
    hostname = (parsed_url.hostname or '').lower()

    if parsed_url.scheme not in ('http', 'https'):
        return False

    if not parsed_url.netloc:
        return False

    if hostname in ('localhost', '127.0.0.1', '0.0.0.0', '::1'):
        return False

    return True


class _ReadableTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._title_depth = 0
        self._title_parts = []
        self._text_parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript', 'svg', 'canvas'):
            self._skip_depth += 1

        if tag == 'title':
            self._title_depth += 1

        if tag in ('p', 'br', 'div', 'section', 'article', 'header', 'footer', 'li', 'h1', 'h2', 'h3'):
            self._text_parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'svg', 'canvas') and self._skip_depth:
            self._skip_depth -= 1

        if tag == 'title' and self._title_depth:
            self._title_depth -= 1

        if tag in ('p', 'div', 'section', 'article', 'li', 'h1', 'h2', 'h3'):
            self._text_parts.append(' ')

    def handle_data(self, data):
        if self._title_depth:
            self._title_parts.append(data)

        if not self._skip_depth:
            self._text_parts.append(data)

    @property
    def title(self):
        return _normalize_space(' '.join(self._title_parts))

    @property
    def text(self):
        return _normalize_space(' '.join(self._text_parts))


class _DuckDuckGoResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._current_href = ''
        self._current_text_parts = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        href = attrs_dict.get('href', '')
        class_name = attrs_dict.get('class', '')

        if tag == 'a' and href and ('result__a' in class_name or 'uddg=' in href):
            self._current_href = href
            self._current_text_parts = []

    def handle_data(self, data):
        if self._current_href:
            self._current_text_parts.append(data)

    def handle_endtag(self, tag):
        if tag != 'a' or not self._current_href:
            return

        url = _extract_duckduckgo_target_url(self._current_href)
        title = _normalize_space(' '.join(self._current_text_parts))

        if url and title and _is_fetchable_web_url(url):
            self.results.append({
                'title': title,
                'url': url,
            })

        self._current_href = ''
        self._current_text_parts = []


def _extract_duckduckgo_target_url(href):
    if href.startswith('//'):
        href = 'https:' + href

    parsed_href = urllib.parse.urlparse(href)
    query = urllib.parse.parse_qs(parsed_href.query)

    if 'uddg' in query and query['uddg']:
        return urllib.parse.unquote(query['uddg'][0])

    if href.startswith('http://') or href.startswith('https://'):
        return href

    return ''


def _request_url_text(url):
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': WEB_USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5',
        },
    )

    with urllib.request.urlopen(request, timeout=WEB_REQUEST_TIMEOUT) as response:
        content_type = response.headers.get('Content-Type', '')

        if 'text/html' not in content_type and 'text/plain' not in content_type and 'application/xhtml+xml' not in content_type:
            return ''

        charset = response.headers.get_content_charset() or 'utf-8'
        return response.read().decode(charset, errors='ignore')


def _search_web(query):
    search_url = 'https://duckduckgo.com/html/?' + urllib.parse.urlencode({'q': query})
    html = _request_url_text(search_url)
    parser = _DuckDuckGoResultParser()
    parser.feed(html)

    unique_results = []
    seen_urls = set()

    for result in parser.results:
        if result['url'] in seen_urls:
            continue

        seen_urls.add(result['url'])
        unique_results.append(result)

        if len(unique_results) >= WEB_SEARCH_RESULT_LIMIT:
            break

    return unique_results


def _read_web_page(url, fallback_title=''):
    if not _is_fetchable_web_url(url):
        return None

    try:
        html = _request_url_text(url)
    except Exception as exc:
        return {
            'url': url,
            'title': fallback_title or url,
            'text': '',
            'error': str(exc),
        }

    parser = _ReadableTextParser()
    parser.feed(html)

    readable_text = parser.text[:WEB_SOURCE_TEXT_LIMIT]

    if not readable_text:
        return {
            'url': url,
            'title': fallback_title or url,
            'text': '',
            'error': 'No readable text found on page.',
        }

    return {
        'url': url,
        'title': parser.title or fallback_title or url,
        'text': readable_text,
        'error': '',
    }


def _collect_web_sources(question, provided_urls, use_search):
    sources_to_read = []

    for url in provided_urls:
        if isinstance(url, str) and _is_fetchable_web_url(url):
            sources_to_read.append({
                'title': url,
                'url': url,
            })

    if use_search:
        try:
            for result in _search_web(question):
                if result['url'] not in [source['url'] for source in sources_to_read]:
                    sources_to_read.append(result)
        except Exception:
            pass

    sources = []

    for source in sources_to_read[:WEB_SEARCH_RESULT_LIMIT]:
        page = _read_web_page(source['url'], source.get('title', ''))

        if page and page.get('text'):
            sources.append(page)

    return sources


def _build_ollama_prompt(question, sources):
    source_blocks = []

    for index, source in enumerate(sources, start=1):
        source_blocks.append(
            f"[{index}] {source['title']}\n"
            f"URL: {source['url']}\n"
            f"TEXT:\n{source['text']}"
        )

    return (
        "Ты локальный помощник, который отвечает по-русски на основе текста из интернета.\n"
        "Используй только полезную информацию из источников ниже.\n"
        "Если в источниках нет ответа, честно скажи, что данных не хватило.\n"
        "В конце кратко перечисли источники, которыми пользовался.\n\n"
        f"ВОПРОС ПОЛЬЗОВАТЕЛЯ:\n{question}\n\n"
        "ИСТОЧНИКИ:\n"
        + "\n\n".join(source_blocks)
    )


def _ask_ollama(question, sources, model_name):
    payload = {
        'model': model_name or OLLAMA_MODEL,
        'prompt': _build_ollama_prompt(question, sources),
        'stream': False,
    }

    request = urllib.request.Request(
        OLLAMA_BASE_URL + '/api/generate',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode('utf-8'))

    return data.get('response', '').strip()


def _get_ollama_answer_file_path():
    answer_file = OLLAMA_ANSWER_FILE.strip() or 'main.txt'

    if os.path.isabs(answer_file):
        return answer_file

    base_dir = str(getattr(settings, 'BASE_DIR', os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, answer_file)


def _write_ollama_answer_file(question, answer, model_name, sources):
    output_file_path = _get_ollama_answer_file_path()
    output_dir = os.path.dirname(output_file_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    source_lines = []

    for index, source in enumerate(sources, start=1):
        source_lines.append(f"{index}. {source['title']} - {source['url']}")

    file_text = (
        "OLLAMA WEB ANSWER\n"
        "=================\n\n"
        f"Saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Model: {model_name}\n\n"
        "QUESTION:\n"
        f"{question}\n\n"
        "ANSWER:\n"
        f"{answer}\n\n"
        "SOURCES:\n"
        + ("\n".join(source_lines) if source_lines else "No sources")
        + "\n"
    )

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(file_text)

    return output_file_path


def _ctx(request):
    return {'google_client_id': getattr(settings, 'GOOGLE_CLIENT_ID', '')}


def home(request):
    return render(request, 'index.html', _ctx(request))


def collections_view(request):
    return render(request, 'collections.html', _ctx(request))


def stones_view(request):
    return render(request, 'stones.html', _ctx(request))


def about_view(request):
    return render(request, 'about.html', _ctx(request))


def support_view(request):
    return render(request, 'support.html', _ctx(request))


def custom_view(request):
    return render(request, 'support.html', _ctx(request))


def product_detail_view(request, product_id):
    return render(request, 'product_detail.html', _ctx(request))


def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()

    if not email or not password:
        return JsonResponse({'ok': False, 'error': 'Email and password required'}, status=400)

    if len(password) < 4:
        return JsonResponse({'ok': False, 'error': 'Password too short (min 4)'}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({'ok': False, 'error': 'Account already exists'}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    login(request, user)
    return JsonResponse({
        'ok': True,
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    })


def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return JsonResponse({'ok': False, 'error': 'Email and password required'}, status=400)

    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            'ok': True,
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    else:
        return JsonResponse({'ok': False, 'error': 'Invalid email or password'}, status=401)


def api_logout(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST only'}, status=405)
    logout(request)
    return JsonResponse({'ok': True})


def api_user(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'ok': True,
            'authenticated': True,
            'user': {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        })
    return JsonResponse({'ok': True, 'authenticated': False})


def api_google_auth(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    credential = data.get('credential', '')
    if not credential:
        return JsonResponse({'ok': False, 'error': 'No credential'}, status=400)

    try:
        url = 'https://oauth2.googleapis.com/tokeninfo?id_token=' + credential
        resp = urllib.request.urlopen(url, timeout=10)
        token_data = json.loads(resp.read().decode())
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Token verification failed'}, status=400)

    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    if google_client_id and token_data.get('aud') != google_client_id:
        return JsonResponse({'ok': False, 'error': 'Invalid client ID'}, status=400)

    email = token_data.get('email', '').lower()
    first_name = token_data.get('given_name', '')
    last_name = token_data.get('family_name', '')

    if not email:
        return JsonResponse({'ok': False, 'error': 'No email in token'}, status=400)

    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    if not created:
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

    login(request, user)
    return JsonResponse({
        'ok': True,
        'user': {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    })


@require_POST
def api_ollama_web(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    question = data.get('question', '')
    provided_urls = data.get('urls', [])
    use_search = data.get('search', True)
    model_name = data.get('model', OLLAMA_MODEL)

    if not isinstance(question, str) or not question.strip():
        return JsonResponse({'ok': False, 'error': 'Question is required'}, status=400)

    if not isinstance(provided_urls, list):
        return JsonResponse({'ok': False, 'error': 'urls must be a list'}, status=400)

    if not isinstance(use_search, bool):
        return JsonResponse({'ok': False, 'error': 'search must be true or false'}, status=400)

    if not isinstance(model_name, str) or not model_name.strip():
        model_name = OLLAMA_MODEL

    question = question.strip()
    model_name = model_name.strip()
    sources = _collect_web_sources(question, provided_urls, use_search)

    if not sources:
        return JsonResponse({
            'ok': False,
            'error': 'Could not read any web sources for this question.',
            'sources': [],
        }, status=502)

    try:
        answer = _ask_ollama(question, sources, model_name)
    except Exception as exc:
        return JsonResponse({
            'ok': False,
            'error': 'Ollama request failed. Check that Ollama is running and the model is installed.',
            'details': str(exc),
            'sources': [
                {
                    'title': source['title'],
                    'url': source['url'],
                }
                for source in sources
            ],
        }, status=502)

    try:
        output_file_path = _write_ollama_answer_file(question, answer, model_name, sources)
    except Exception as exc:
        return JsonResponse({
            'ok': False,
            'error': 'Ollama answered, but saving answer to txt failed.',
            'details': str(exc),
            'answer': answer,
            'sources': [
                {
                    'title': source['title'],
                    'url': source['url'],
                }
                for source in sources
            ],
        }, status=500)

    return JsonResponse({
        'ok': True,
        'answer': answer,
        'model': model_name,
        'output_file': output_file_path,
        'sources': [
            {
                'title': source['title'],
                'url': source['url'],
            }
            for source in sources
        ],
    })


STATIC_ROOT_DIR = str(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else ''

urlpatterns = [
    path('', home, name='home'),
    path('collections/', collections_view, name='collections'),
    path('stones/', stones_view, name='stones'),
    path('custom/', custom_view, name='custom'),
    path('about/', about_view, name='about'),
    path('support/', support_view, name='support'),
    path('product/<str:product_id>/', product_detail_view, name='product_detail'),
    path('api/register/', api_register, name='api_register'),
    path('api/login/', api_login, name='api_login'),
    path('api/logout/', api_logout, name='api_logout'),
    path('api/user/', api_user, name='api_user'),
    path('api/google-auth/', api_google_auth, name='api_google_auth'),
    path('api/ollama-web/', api_ollama_web, name='api_ollama_web'),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT_DIR}),
]