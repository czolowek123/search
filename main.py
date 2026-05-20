#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2-vision:11b")
ANSWER_FILE_NAME = os.environ.get("ANSWER_FILE_NAME", "answer.txt")
APP_HOST = os.environ.get("APP_HOST", "127.0.0.1")
APP_PORT = int(os.environ.get("APP_PORT", "8000"))
WEB_SITE_LIMIT = int(os.environ.get("WEB_SITE_LIMIT", "10"))
WEB_SEARCH_CANDIDATES = int(os.environ.get("WEB_SEARCH_CANDIDATES", "18"))
WEB_REQUEST_TIMEOUT = int(os.environ.get("WEB_REQUEST_TIMEOUT", "8"))
WEB_SOURCE_TEXT_LIMIT = int(os.environ.get("WEB_SOURCE_TEXT_LIMIT", "12000"))
PROMPT_SOURCE_TEXT_LIMIT = int(os.environ.get("PROMPT_SOURCE_TEXT_LIMIT", "1300"))
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "180"))
OLLAMA_NUM_PREDICT = int(os.environ.get("OLLAMA_NUM_PREDICT", "500"))
OLLAMA_TEMPERATURE = float(os.environ.get("OLLAMA_TEMPERATURE", "0.25"))
WEB_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
INTERNET_TRIGGER_RE = re.compile(
    r"(?:найди|поищи|отыщи|посмотри|проверь|загугли)\s+(?:это\s+)?(?:в\s+)?интерн(?:е|э)те|"
    r"(?:в\s+)?интерн(?:е|э)те\s+(?:найди|поищи|посмотри|проверь)|"
    r"найди\s+онлайн|поищи\s+онлайн",
    re.IGNORECASE,
)

@dataclass
class SearchResult:
    title: str
    url: str

@dataclass
class WebSource:
    title: str
    url: str
    text: str

@dataclass
class AnswerResult:
    answer: str
    sources: list[WebSource]
    used_web: bool
    answer_file: Path

def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?;:])\s+", normalize_space(text))
    return [part.strip() for part in parts if len(part.strip()) >= 40]

def query_keywords(query: str) -> set[str]:
    stop_words = {"что", "как", "какой", "какая", "какие", "какое", "сколько", "кто", "такой", "такая", "такие", "почему", "где", "когда", "или", "для", "при", "про", "это", "его", "она", "они", "мне", "тебе", "вам", "найди", "поищи", "интернете", "интернет", "the", "and", "for", "with", "what", "how", "why", "where", "when"}
    words = re.findall(r"[а-яёa-z0-9]+", query.lower())
    return {word for word in words if len(word) >= 3 and word not in stop_words}

def is_greeting(message: str) -> bool:
    text = normalize_space(message).lower().replace("ё", "е")
    return text in {"привет", "здравствуй", "здравствуйте", "привет джарвис", "джарвис привет"}

def should_search_web(message: str) -> bool:
    return bool(INTERNET_TRIGGER_RE.search(message or ""))

def strip_internet_trigger(message: str) -> str:
    cleaned = INTERNET_TRIGGER_RE.sub(" ", message or "")
    cleaned = re.sub(r"\b(пожалуйста|джарвис)\b", " ", cleaned, flags=re.IGNORECASE)
    return normalize_space(cleaned) or normalize_space(message)

def is_who_question(query: str) -> bool:
    query_lower = query.lower()
    return bool(re.search(r"\b(?:кто|who)\b", query_lower)) or "кто такой" in query_lower

def split_who_subject_and_context(question: str) -> tuple[str, str]:
    query = normalize_space(question)
    who_match = re.search(r"(?:кто\s+так(?:ой|ая|ие)|who\s+is)\s+(.+)", query, re.IGNORECASE)
    if not who_match:
        return "", ""
    tail = who_match.group(1).strip(" ?!.,")
    context_match = re.search(r"\s+\b(?:и|а|что|чем|где|когда|почему|как|and|what|where|when|why|how)\b.*", tail, re.IGNORECASE)
    if not context_match:
        return tail, ""
    subject = tail[:context_match.start()].strip(" ?!.,")
    context = tail[context_match.start():].strip(" ?!.,")
    return subject, context

def extract_who_subject(question: str) -> str:
    subject, _ = split_who_subject_and_context(question)
    return subject

def extract_who_context(question: str) -> str:
    _, context = split_who_subject_and_context(question)
    return context

def name_variants(subject: str) -> list[str]:
    variants = [normalize_space(subject)]
    common_fixes = {"jefferey": "jeffrey", "jeferrey": "jeffrey", "jeffery": "jeffrey", "micheal": "michael"}
    lowered = subject.lower()
    for wrong, right in common_fixes.items():
        if wrong in lowered:
            fixed = re.sub(wrong, right, subject, flags=re.IGNORECASE)
            if subject[:1].isupper():
                fixed = fixed[:1].upper() + fixed[1:]
            variants.append(normalize_space(fixed))
    unique_variants: list[str] = []
    for variant in variants:
        if variant and variant.lower() not in [item.lower() for item in unique_variants]:
            unique_variants.append(variant)
    return unique_variants

def edit_distance_is_close(a: str, b: str) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > 2:
        return False
    previous = list(range(len(b) + 1))
    for index_a, char_a in enumerate(a, start=1):
        current = [index_a]
        for index_b, char_b in enumerate(b, start=1):
            current.append(min(current[index_b - 1] + 1, previous[index_b] + 1, previous[index_b - 1] + (char_a != char_b)))
        previous = current
    return previous[-1] <= 2

def normalize_name_for_match(text: str) -> str:
    text = html.unescape(text or "").lower().replace("ё", "е")
    text = re.sub(r"[^а-яa-z0-9]+", " ", text)
    return normalize_space(text)

def source_mentions_subject(subject: str, source: WebSource) -> bool:
    normalized_variants = [normalize_name_for_match(variant) for variant in name_variants(subject)]
    normalized_variants = [variant for variant in normalized_variants if variant]
    if not normalized_variants:
        return True
    searchable_text = " ".join([source.title, source.url.replace("-", " ").replace("_", " "), source.text[:1200]])
    normalized_text = normalize_name_for_match(searchable_text)
    for normalized_subject in normalized_variants:
        subject_words = normalized_subject.split()
        if len(subject_words) >= 2:
            first_name = re.escape(subject_words[0])
            last_name = re.escape(subject_words[-1])
            if re.search(rf"\b{first_name}\s+\w+\s+{last_name}\b", normalized_text):
                return False
            if re.search(rf"\b{re.escape(normalized_subject)}\b", normalized_text):
                return True
            continue
        text_words = set(normalized_text.split())
        if subject_words and any(edit_distance_is_close(subject_words[0], word) for word in text_words):
            return True
    return False

def question_context_terms(question: str) -> str:
    context = extract_who_context(question) if is_who_question(question) else question
    context_lower = context.lower()
    terms: list[str] = []
    if any(word in context_lower for word in ("создал", "создатель", "основал", "основатель", "created", "creator", "founded", "founder")):
        terms.extend(["created", "creator", "founder", "founded"])
    if any(word in context_lower for word in ("ollama", "оллама")):
        terms.append("ollama")
    if any(word in context_lower for word in ("90b", "90 b", "90-б")):
        terms.append("90B")
    return " ".join(terms)

def source_matches_question_context(question: str, source: WebSource) -> bool:
    if not is_who_question(question):
        return True
    context_terms = question_context_terms(question).split()
    if not context_terms:
        return True
    searchable_text = normalize_name_for_match(" ".join([source.title, source.url.replace("-", " "), source.text[:8000]]))
    creation_terms = {"created", "creator", "founder", "founded", "создал", "создатель", "основал", "основатель", "ollama", "90b"}
    if any(term.lower() in creation_terms for term in context_terms):
        return any(term in searchable_text for term in creation_terms)
    return True

def build_search_queries(question: str) -> list[str]:
    query = normalize_space(question)
    if is_who_question(query):
        subject = extract_who_subject(query)
        if subject:
            context_terms = question_context_terms(query)
            queries: list[str] = []
            for variant in name_variants(subject):
                quoted_variant = f'"{variant}"'
                queries.append(f"{quoted_variant} wikipedia biography {context_terms}".strip())
                queries.append(f"{quoted_variant} {context_terms}".strip())
                queries.append(f"{variant} biography {context_terms}".strip())
            unique_queries: list[str] = []
            for item in queries:
                if item and item.lower() not in [existing.lower() for existing in unique_queries]:
                    unique_queries.append(item)
            return unique_queries
    return [query]

def build_relevant_excerpt(text: str, query: str, max_chars: int = PROMPT_SOURCE_TEXT_LIMIT) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return text[:max_chars]
    keywords = query_keywords(query)
    scored_sentences: list[tuple[int, int, str]] = []
    for index, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        score = sum(1 for keyword in keywords if keyword in sentence_lower)
        if re.search(r"\d", sentence):
            score += 1
        if is_who_question(query) and any(word in sentence_lower for word in ("родился", "актёр", "актер", "известен", "сыграл", "фильм", "сериал", "биограф", "actor", "known", "born", "film", "series")):
            score += 2
        if any(word in sentence_lower for word in ("средн", "норм", "рост", "возраст", "мальчик", "таблиц")):
            score += 2
        if any(word in sentence_lower for word in ("популяр", "мем", "тренд", "рейтинг", "топ", "viral", "popular")):
            score += 2
        scored_sentences.append((score, -index, sentence))
    best_sentences = [sentence for score, _, sentence in sorted(scored_sentences, reverse=True) if score > 0]
    if not best_sentences:
        best_sentences = sentences[:6]
    excerpt = ""
    for sentence in best_sentences:
        next_excerpt = (excerpt + " " + sentence).strip()
        if len(next_excerpt) > max_chars:
            break
        excerpt = next_excerpt
    return excerpt or text[:max_chars]

def is_fetchable_url(url: str) -> bool:
    parsed_url = urllib.parse.urlparse(url)
    hostname = (parsed_url.hostname or "").lower()
    if parsed_url.scheme not in ("http", "https"):
        return False
    if not parsed_url.netloc:
        return False
    if hostname in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False
    return True

class ReadableTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.title_depth = 0
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript", "svg", "canvas", "iframe"):
            self.skip_depth += 1
        if tag == "title":
            self.title_depth += 1
        if tag in ("p", "br", "div", "section", "article", "header", "footer", "li", "h1", "h2", "h3", "td", "th"):
            self.text_parts.append(" ")
    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript", "svg", "canvas", "iframe") and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if tag in ("p", "div", "section", "article", "li", "h1", "h2", "h3", "td", "th"):
            self.text_parts.append(" ")
    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_parts.append(data)
        if not self.skip_depth:
            self.text_parts.append(data)
    @property
    def title(self) -> str:
        return normalize_space(html.unescape(" ".join(self.title_parts)))
    @property
    def text(self) -> str:
        return normalize_space(html.unescape(" ".join(self.text_parts)))

class DuckDuckGoResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[SearchResult] = []
        self.current_href = ""
        self.current_text_parts: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}
        href = attrs_dict.get("href", "")
        class_name = attrs_dict.get("class", "")
        if tag == "a" and href and ("result__a" in class_name or "uddg=" in href):
            self.current_href = href
            self.current_text_parts = []
    def handle_data(self, data: str) -> None:
        if self.current_href:
            self.current_text_parts.append(data)
    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self.current_href:
            return
        url = extract_duckduckgo_target_url(self.current_href)
        title = normalize_space(html.unescape(" ".join(self.current_text_parts)))
        if url and title and is_fetchable_url(url):
            self.results.append(SearchResult(title=title, url=url))
        self.current_href = ""
        self.current_text_parts = []

def extract_duckduckgo_target_url(href: str) -> str:
    if href.startswith("//"):
        href = "https:" + href
    parsed_href = urllib.parse.urlparse(href)
    query = urllib.parse.parse_qs(parsed_href.query)
    if query.get("uddg"):
        return urllib.parse.unquote(query["uddg"][0])
    if href.startswith(("http://", "https://")):
        return href
    return ""

def request_url_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": WEB_USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5", "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(request, timeout=WEB_REQUEST_TIMEOUT) as response:
        content_type = response.headers.get("Content-Type", "")
        if not any(part in content_type for part in ("text/html", "text/plain", "application/xhtml+xml")):
            return ""
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="ignore")

def search_web(query: str) -> list[SearchResult]:
    unique_results: list[SearchResult] = []
    seen_urls: set[str] = set()
    for search_query in build_search_queries(query):
        search_url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": search_query})
        page_html = request_url_text(search_url)
        parser = DuckDuckGoResultParser()
        parser.feed(page_html)
        for result in parser.results:
            if result.url in seen_urls:
                continue
            seen_urls.add(result.url)
            unique_results.append(result)
            if len(unique_results) >= WEB_SEARCH_CANDIDATES:
                break
        if len(unique_results) >= WEB_SEARCH_CANDIDATES:
            break
    return unique_results

def read_web_page(result: SearchResult) -> WebSource | None:
    if not is_fetchable_url(result.url):
        return None
    page_html = request_url_text(result.url)
    parser = ReadableTextParser()
    parser.feed(page_html)
    text = parser.text
    if len(text) > WEB_SOURCE_TEXT_LIMIT:
        text = text[:WEB_SOURCE_TEXT_LIMIT].rsplit(" ", 1)[0]
    if not text:
        return None
    return WebSource(title=parser.title or result.title or result.url, url=result.url, text=text)

def collect_sources(question: str) -> list[WebSource]:
    print(f"Ищу сайты по теме: {question}")
    search_results = search_web(question)
    sources: list[WebSource] = []
    if not search_results:
        return sources
    candidates = search_results[:WEB_SITE_LIMIT]
    workers = min(10, len(candidates))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_result = {executor.submit(read_web_page, result): result for result in candidates}
        for future in as_completed(future_to_result):
            result = future_to_result[future]
            if len(sources) >= WEB_SITE_LIMIT:
                break
            print(f"Читаю: {result.url}")
            try:
                source = future.result()
            except Exception as exc:
                print(f"    пропуск: {exc}")
                continue
            if not source:
                print("    пропуск: нет читаемого текста")
                continue
            subject = extract_who_subject(question) if is_who_question(question) else ""
            if subject and not source_mentions_subject(subject, source):
                print(f"    пропуск: источник не про точное имя «{subject}»")
                continue
            if not source_matches_question_context(question, source):
                print("    пропуск: источник не отвечает на уточнение вопроса")
                continue
            sources.append(source)
            print(f"    готово: {len(source.text)} символов текста")
    return sources

def build_web_prompt(question: str, sources: list[WebSource]) -> str:
    source_blocks: list[str] = []
    for index, source in enumerate(sources, start=1):
        excerpt = build_relevant_excerpt(source.text, question)
        source_blocks.append(f"Источник {index}: {source.title}\nURL: {source.url}\nВажные фрагменты текста:\n{excerpt}")
    joined_sources = "\n\n---\n\n".join(source_blocks)
    answer_rules = build_answer_rules(question)
    return (
        "Ты Джарвис — точный русскоязычный помощник-аналитик.\n"
        "Пользователь попросил найти информацию в интернете. Используй только факты из источников ниже.\n"
        "Отвечай конкретно на вопрос, не делай длинную подборку всего подряд.\n"
        "Если вопрос просит 'самый популярный', выбери один главный вариант, а если единого лидера нет — прямо скажи, что общего лидера нет, и назови 2-4 основных кандидата.\n"
        "Не включай в ответ заголовки статей, если они не являются ответом.\n"
        "Не отвечай обрывком или одним именем, если вопрос требует объяснения.\n"
        f"{answer_rules}\n"
        "Если в источниках есть числа, диапазоны, возраст, даты или характеристики, обязательно используй их.\n"
        "Если данных недостаточно, скажи это коротко и укажи, что можно проверить дополнительно.\n\n"
        f"Вопрос пользователя:\n{question}\n\n"
        f"Фрагменты из источников ({len(sources)} сайтов):\n{joined_sources}\n\n"
        "Ответь по делу, достаточно полно, но без воды."
    )

def build_chat_prompt(message: str) -> str:
    return (
        "Ты Джарвис — спокойный, умный русскоязычный ИИ-помощник.\n"
        "Общайся естественно, как ChatGPT.\n"
        "Не ищи в интернете и не утверждай свежие факты, если пользователь не попросил явно найти в интернете.\n"
        "Если пользователь сказал 'привет', ответь: 'Приветствую вас.'\n"
        "Если вопрос требует рассуждения, объясняй нормально, не одним словом.\n\n"
        f"Сообщение пользователя:\n{message}\n\nОтвет:"
    )

def build_answer_rules(question: str) -> str:
    question_lower = question.lower()
    if is_who_question(question):
        subject = extract_who_subject(question)
        return ("Для вопроса 'кто это' дай 4-7 предложений: полное имя, профессия, чем известен, важные роли/работы или факты. Не ограничивайся одним именем. " f"Отвечай только о человеке с точным именем «{subject}». Не заменяй его на другого более популярного человека и не исправляй имя сам.")
    if any(word in question_lower for word in ("сравни", "лучше", "или", "vs", "против")):
        return "Для сравнения дай вывод в первом предложении, затем 3-6 предложений с причинами, плюс когда лучше выбрать каждый вариант."
    if any(word in question_lower for word in ("почему", "как работает", "объясни")):
        return "Для объяснения дай 5-8 понятных предложений с причиной и простым примером, если он уместен."
    return "Дай прямой ответ и 2-5 предложений пояснения."

def ask_ollama(prompt: str) -> str:
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": OLLAMA_TEMPERATURE, "num_predict": OLLAMA_NUM_PREDICT, "top_p": 0.9}}
    request = urllib.request.Request(OLLAMA_BASE_URL + "/api/generate", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("response", "").strip()

def answer_is_too_short(question: str, answer: str) -> bool:
    words = re.findall(r"[а-яёa-z0-9]+", answer.lower())
    if is_who_question(question):
        return len(words) < 25
    return len(words) < 5

def improve_too_short_answer(question: str, prompt: str, answer: str) -> str:
    if not answer_is_too_short(question, answer):
        return answer
    retry_prompt = f"{prompt}\n\nПредыдущий ответ получился слишком коротким:\n{answer}\n\nНапиши заново нормальный полезный ответ. Если вопрос про человека, обязательно объясни кто это, чем известен и приведи ключевые факты."
    improved_answer = ask_ollama(retry_prompt)
    return improved_answer or answer

def get_answer_file_path() -> Path:
    current_dir = Path(__file__).resolve().parent
    answer_file = Path(ANSWER_FILE_NAME)
    if answer_file.is_absolute():
        return answer_file
    return current_dir / answer_file

def write_answer_to_file(question: str, answer: str, sources: list[WebSource]) -> Path:
    answer_file_path = get_answer_file_path()
    source_lines = "\n".join(f"{index}. {source.title}\n   {source.url}" for index, source in enumerate(sources, start=1))
    text = ("AI WEB ANSWER\n" f"Created: {dt.datetime.now().isoformat(timespec='seconds')}\n" f"Model: {OLLAMA_MODEL}\n" f"Sites used: {len(sources)}\n\n" "QUESTION:\n" f"{question}\n\n" "ANSWER:\n" f"{answer}\n\n" "SOURCES:\n" f"{source_lines}\n")
    answer_file_path.write_text(text, encoding="utf-8")
    return answer_file_path

def answer_without_web(message: str) -> AnswerResult:
    if is_greeting(message):
        answer = "Приветствую вас."
    else:
        answer = ask_ollama(build_chat_prompt(message))
        if not answer:
            answer = "Я не получил ответ от модели. Проверьте Ollama и попробуйте ещё раз."
    answer_file_path = write_answer_to_file(message, answer, [])
    return AnswerResult(answer=answer, sources=[], used_web=False, answer_file=answer_file_path)

def answer_with_web(message: str) -> AnswerResult:
    question = strip_internet_trigger(message)
    sources = collect_sources(question)
    if not sources:
        subject = extract_who_subject(question) if is_who_question(question) else ""
        if subject:
            answer = f"Я не нашёл надёжных источников именно по точному имени «{subject}». Чтобы не заменить человека на более популярного однофамильца, я не буду отвечать про другого человека. Попробуй уточнить имя, профессию, страну или добавить ссылку/контекст."
        else:
            answer = "Не получилось собрать текст с сайтов по этому запросу. Попробуй уточнить запрос."
        answer_file_path = write_answer_to_file(question, answer, [])
        return AnswerResult(answer=answer, sources=[], used_web=True, answer_file=answer_file_path)
    prompt = build_web_prompt(question, sources)
    answer = ask_ollama(prompt)
    answer = improve_too_short_answer(question, prompt, answer)
    if not answer:
        answer = "Ollama вернула пустой ответ."
    answer_file_path = write_answer_to_file(question, answer, sources)
    return AnswerResult(answer=answer, sources=sources, used_web=True, answer_file=answer_file_path)

def answer_message(message: str) -> AnswerResult:
    if should_search_web(message):
        return answer_with_web(message)
    return answer_without_web(message)

def get_question_from_user() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return input("Напиши вопрос: ").strip()

def run_cli() -> int:
    message = get_question_from_user()
    if not message:
        print("Вопрос пустой. Напиши вопрос и запусти ещё раз.")
        return 1
    if should_search_web(message):
        print("Джарвис: ищу в интернете...")
    else:
        print("Джарвис: отвечаю без поиска в интернете...")
    try:
        result = answer_message(message)
    except urllib.error.URLError as exc:
        print("Не получилось подключиться к Ollama или интернету.")
        print("Проверь, что Ollama запущена: ollama serve")
        print(f"Ошибка: {exc}")
        return 1
    except Exception as exc:
        print(f"Ошибка: {exc}")
        return 1
    print("\nДжарвис:")
    print(result.answer)
    print("\nОтвет записан в файл:")
    print(result.answer_file)
    return 0

INDEX_HTML = r'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Джарвис</title>
  <style>
    :root { color-scheme: dark; --bg:#07111f; --panel:rgba(13,28,48,.92); --user:#1f6feb; --bot:#12263f; --text:#e8f1ff; --muted:#8aa4c2; --accent:#5eead4; --danger:#fb7185; }
    * { box-sizing: border-box; }
    body { margin:0; min-height:100vh; font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:radial-gradient(circle at top left,rgba(94,234,212,.18),transparent 35%),radial-gradient(circle at top right,rgba(59,130,246,.24),transparent 30%),var(--bg); color:var(--text); display:flex; align-items:center; justify-content:center; padding:18px; }
    .app { width:min(1050px,100%); height:min(820px,calc(100vh - 36px)); background:var(--panel); border:1px solid rgba(148,163,184,.22); border-radius:24px; box-shadow:0 24px 80px rgba(0,0,0,.45); display:grid; grid-template-rows:auto 1fr auto; overflow:hidden; }
    header { padding:18px 22px; border-bottom:1px solid rgba(148,163,184,.16); display:flex; align-items:center; justify-content:space-between; gap:12px; }
    .title { display:flex; align-items:center; gap:12px; }
    .orb { width:42px; height:42px; border-radius:50%; background:radial-gradient(circle,#c7fff6 0%,#5eead4 36%,#2563eb 72%); box-shadow:0 0 32px rgba(94,234,212,.7); }
    h1 { margin:0; font-size:22px; letter-spacing:.02em; }
    .hint { color:var(--muted); font-size:13px; margin-top:3px; }
    .status { color:var(--accent); font-size:13px; text-align:right; }
    #chat { padding:22px; overflow-y:auto; display:flex; flex-direction:column; gap:14px; }
    .msg { max-width:82%; padding:13px 15px; border-radius:18px; line-height:1.45; white-space:pre-wrap; overflow-wrap:anywhere; }
    .user { align-self:flex-end; background:var(--user); }
    .bot { align-self:flex-start; background:var(--bot); border:1px solid rgba(148,163,184,.16); }
    .meta { font-size:12px; color:var(--muted); margin-top:8px; }
    form { display:grid; grid-template-columns:1fr auto auto; gap:10px; padding:16px; border-top:1px solid rgba(148,163,184,.16); background:rgba(2,6,23,.28); }
    textarea { width:100%; resize:none; border:1px solid rgba(148,163,184,.25); border-radius:16px; min-height:52px; max-height:160px; padding:14px 16px; background:rgba(2,6,23,.72); color:var(--text); outline:none; font:inherit; }
    button { border:0; border-radius:16px; padding:0 18px; color:#03131f; background:var(--accent); font-weight:700; cursor:pointer; min-width:58px; }
    button:disabled { opacity:.55; cursor:not-allowed; }
    #mic.listening { background:var(--danger); color:white; }
    @media (max-width:720px) { body{padding:0;} .app{height:100vh;border-radius:0;} .msg{max-width:94%;} form{grid-template-columns:1fr auto;} #send{grid-column:span 2;height:46px;} }
  </style>
</head>
<body>
  <main class="app">
    <header><div class="title"><div class="orb"></div><div><h1>Джарвис</h1><div class="hint">Скажи “найди в интернете ...”, и я подключу DuckDuckGo. Иначе отвечаю без поиска.</div></div></div><div class="status" id="status">Готов</div></header>
    <section id="chat"></section>
    <form id="form"><textarea id="input" placeholder="Напиши сообщение или нажми микрофон..." autocomplete="off"></textarea><button id="mic" type="button" title="Говорить">🎙</button><button id="send" type="submit">Отправить</button></form>
  </main>
  <script>
    const chat=document.getElementById('chat'),form=document.getElementById('form'),input=document.getElementById('input'),mic=document.getElementById('mic'),send=document.getElementById('send'),statusEl=document.getElementById('status');
    const internetRe=/(?:найди|поищи|отыщи|посмотри|проверь|загугли)\s+(?:это\s+)?(?:в\s+)?интерн(?:е|э)те|(?:в\s+)?интерн(?:е|э)те\s+(?:найди|поищи|посмотри|проверь)|найди\s+онлайн|поищи\s+онлайн/i;
    function addMessage(role,text,meta=''){const div=document.createElement('div');div.className=`msg ${role}`;div.textContent=text;if(meta){const m=document.createElement('div');m.className='meta';m.textContent=meta;div.appendChild(m);}chat.appendChild(div);chat.scrollTop=chat.scrollHeight;return div;}
    function chooseVoice(){const voices=window.speechSynthesis?.getVoices?.()||[];return voices.find(v=>/Daniel|Google UK English Male|Microsoft Pavel|Microsoft Dmitry|Male|муж/i.test(v.name))||voices.find(v=>/ru|en-GB|en-US/i.test(v.lang))||voices[0];}
    function speak(text){if(!('speechSynthesis'in window))return;window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);const v=chooseVoice();if(v)u.voice=v;u.lang=v?.lang||'ru-RU';u.rate=.95;u.pitch=.82;window.speechSynthesis.speak(u);}
    async function sendMessage(text){const message=text.trim();if(!message)return;addMessage('user',message);input.value='';send.disabled=true;mic.disabled=true;const usesWeb=internetRe.test(message);if(usesWeb){statusEl.textContent='Ищу в интернете...';addMessage('bot','Ищу в интернете...');speak('Ищу в интернете.');}else{statusEl.textContent='Думаю...';}try{const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});const data=await response.json();if(!response.ok)throw new Error(data.error||'Ошибка запроса');addMessage('bot',data.answer,data.used_web?`Источников: ${data.sources.length}. Записано в ${data.answer_file}`:`Записано в ${data.answer_file}`);speak(data.answer);}catch(error){addMessage('bot',`Ошибка: ${error.message}`);}finally{statusEl.textContent='Готов';send.disabled=false;mic.disabled=false;input.focus();}}
    form.addEventListener('submit',e=>{e.preventDefault();sendMessage(input.value);});
    input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage(input.value);}});
    const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SpeechRecognition){mic.disabled=true;mic.title='Микрофон не поддерживается этим браузером';}else{const recognition=new SpeechRecognition();recognition.lang='ru-RU';recognition.interimResults=false;recognition.continuous=false;recognition.onstart=()=>{mic.classList.add('listening');statusEl.textContent='Слушаю...';};recognition.onend=()=>{mic.classList.remove('listening');statusEl.textContent='Готов';};recognition.onresult=e=>{const text=e.results[0][0].transcript;input.value=text;sendMessage(text);};recognition.onerror=e=>{addMessage('bot',`Микрофон: ${e.error}`);};mic.addEventListener('click',()=>recognition.start());}
    window.speechSynthesis?.addEventListener?.('voiceschanged',chooseVoice);addMessage('bot','Приветствую вас. Я Джарвис. Если нужен интернет, скажите: “найди в интернете ...”.');
  </script>
</body>
</html>'''

class JarvisHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return
    def send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self) -> None:
        if self.path not in ('/', '/index.html'):
            self.send_error(404)
            return
        body = INDEX_HTML.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self) -> None:
        if self.path != '/api/chat':
            self.send_error(404)
            return
        try:
            content_length = int(self.headers.get('Content-Length', '0'))
            payload = json.loads(self.rfile.read(content_length).decode('utf-8'))
            message = normalize_space(str(payload.get('message', '')))
            if not message:
                self.send_json(400, {'error': 'Пустое сообщение.'})
                return
            result = answer_message(message)
            self.send_json(200, {'answer': result.answer, 'used_web': result.used_web, 'answer_file': str(result.answer_file), 'sources': [{'title': source.title, 'url': source.url} for source in result.sources]})
        except Exception as exc:
            self.send_json(500, {'error': str(exc)})

def run_app() -> int:
    server = ThreadingHTTPServer((APP_HOST, APP_PORT), JarvisHandler)
    url = f'http://{APP_HOST}:{APP_PORT}'
    print(f'Джарвис запущен: {url}')
    print('Если браузер не открылся сам, открой этот адрес вручную.')
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nДжарвис остановлен.')
    finally:
        server.server_close()
    return 0

def main() -> int:
    if len(sys.argv) > 1:
        return run_cli()
    return run_app()

if __name__ == '__main__':
    raise SystemExit(main())
