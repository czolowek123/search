#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import os
import queue
import re
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2-vision:11b")
ANSWER_FILE_NAME = os.environ.get("ANSWER_FILE_NAME", "answer.txt")
MEMORY_FILE_NAME = os.environ.get("MEMORY_FILE_NAME", "memory.json")

WEB_SITE_LIMIT = int(os.environ.get("WEB_SITE_LIMIT", "10"))
WEB_SEARCH_CANDIDATES = int(os.environ.get("WEB_SEARCH_CANDIDATES", "18"))
WEB_REQUEST_TIMEOUT = int(os.environ.get("WEB_REQUEST_TIMEOUT", "8"))
WEB_SOURCE_TEXT_LIMIT = int(os.environ.get("WEB_SOURCE_TEXT_LIMIT", "12000"))
PROMPT_SOURCE_TEXT_LIMIT = int(os.environ.get("PROMPT_SOURCE_TEXT_LIMIT", "1300"))
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "180"))
OLLAMA_NUM_PREDICT = int(os.environ.get("OLLAMA_NUM_PREDICT", "700"))
OLLAMA_TEMPERATURE = float(os.environ.get("OLLAMA_TEMPERATURE", "0.25"))

WEB_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

INTERNET_TRIGGER_WORDS = {
    "найди",
    "наиди",
    "найдм",
    "поищи",
    "паищи",
    "посмотри",
    "проверь",
    "загугли",
    "ищи",
}

INTERNET_WORDS = {
    "интернет",
    "интернете",
    "интеренет",
    "интеренете",
    "интеренете",
    "интернте",
    "инете",
    "онлайн",
    "гугле",
    "сети",
}


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


def words_of(text: str) -> list[str]:
    return re.findall(r"[а-яёa-z0-9]+", (text or "").lower())


def edit_distance_is_close(a: str, b: str, max_distance: int = 2) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > max_distance:
        return False
    previous = list(range(len(b) + 1))
    for index_a, char_a in enumerate(a, start=1):
        current = [index_a]
        for index_b, char_b in enumerate(b, start=1):
            current.append(
                min(
                    current[index_b - 1] + 1,
                    previous[index_b] + 1,
                    previous[index_b - 1] + (char_a != char_b),
                )
            )
        previous = current
    return previous[-1] <= max_distance


def contains_fuzzy_word(tokens: list[str], variants: set[str], max_distance: int = 2) -> bool:
    return any(
        edit_distance_is_close(token, variant, max_distance=max_distance)
        for token in tokens
        for variant in variants
    )


def is_greeting(message: str) -> bool:
    text = normalize_space(message).lower().replace("ё", "е")
    return text in {"привет", "здравствуй", "здравствуйте", "привет джарвис", "джарвис привет"}


def should_search_web(message: str) -> bool:
    tokens = words_of(message)
    has_search_word = contains_fuzzy_word(tokens, INTERNET_TRIGGER_WORDS)
    has_internet_word = contains_fuzzy_word(tokens, INTERNET_WORDS)
    return has_search_word and has_internet_word


def strip_internet_trigger(message: str) -> str:
    tokens = words_of(message)
    remove_words = INTERNET_TRIGGER_WORDS | INTERNET_WORDS | {"джарвис", "пожалуйста", "это"}
    kept_tokens = [
        token
        for token in tokens
        if not any(edit_distance_is_close(token, remove_word) for remove_word in remove_words)
    ]
    cleaned = " ".join(kept_tokens)
    return normalize_space(cleaned) or normalize_space(message)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?;:])\s+", normalize_space(text))
    return [part.strip() for part in parts if len(part.strip()) >= 40]


def query_keywords(query: str) -> set[str]:
    stop_words = {
        "что", "как", "какой", "какая", "какие", "какое", "сколько", "кто",
        "такой", "такая", "такие", "почему", "где", "когда", "или", "для",
        "при", "про", "это", "его", "она", "они", "мне", "тебе", "вам",
        "найди", "поищи", "интернете", "интернет", "the", "and", "for",
        "with", "what", "how", "why", "where", "when",
    }
    words = words_of(query)
    return {word for word in words if len(word) >= 3 and word not in stop_words}


def is_who_question(query: str) -> bool:
    query_lower = query.lower()
    return bool(re.search(r"\b(?:кто|who)\b", query_lower)) or "кто такой" in query_lower


def split_who_subject_and_context(question: str) -> tuple[str, str]:
    query = normalize_space(question)
    who_match = re.search(r"(?:кто\s+так(?:ой|ая|ие)|who\s+is)\s+(.+)", query, re.IGNORECASE)
    if not who_match:
        return "", ""
    tail = who_match.group(1).strip(" ?!.,")
    context_match = re.search(
        r"\s+\b(?:и|а|что|чем|где|когда|почему|как|and|what|where|when|why|how)\b.*",
        tail,
        re.IGNORECASE,
    )
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
    common_fixes = {
        "jefferey": "jeffrey",
        "jeferrey": "jeffrey",
        "jeffery": "jeffrey",
        "micheal": "michael",
    }
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


def normalize_name_for_match(text: str) -> str:
    text = html.unescape(text or "").lower().replace("ё", "е")
    text = re.sub(r"[^а-яa-z0-9]+", " ", text)
    return normalize_space(text)


def source_mentions_subject(subject: str, source: WebSource) -> bool:
    normalized_variants = [normalize_name_for_match(variant) for variant in name_variants(subject)]
    normalized_variants = [variant for variant in normalized_variants if variant]
    if not normalized_variants:
        return True
    searchable_text = " ".join(
        [source.title, source.url.replace("-", " ").replace("_", " "), source.text[:1200]]
    )
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
    searchable_text = normalize_name_for_match(
        " ".join([source.title, source.url.replace("-", " "), source.text[:8000]])
    )
    creation_terms = {
        "created", "creator", "founder", "founded", "создал", "создатель",
        "основал", "основатель", "ollama", "90b",
    }
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
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": WEB_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        },
    )
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


def build_web_prompt(question: str, sources: list[WebSource], memory: dict[str, Any]) -> str:
    source_blocks: list[str] = []
    for index, source in enumerate(sources, start=1):
        excerpt = build_relevant_excerpt(source.text, question)
        source_blocks.append(f"Источник {index}: {source.title}\nURL: {source.url}\nВажные фрагменты текста:\n{excerpt}")
    joined_sources = "\n\n---\n\n".join(source_blocks)
    answer_rules = build_answer_rules(question)
    return (
        "Ты Джарвис — точный русскоязычный помощник-аналитик.\n"
        "Пользователь попросил найти информацию в интернете. Используй только факты из источников ниже.\n"
        "Учитывай память и недавний контекст, но факты из интернета важнее.\n"
        f"{format_memory_for_prompt(memory)}\n\n"
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


def build_chat_prompt(message: str, memory: dict[str, Any]) -> str:
    return (
        "Ты Джарвис — спокойный, умный русскоязычный ИИ-помощник.\n"
        "Общайся естественно, как ChatGPT. Понимай сообщения с опечатками и отвечай по смыслу.\n"
        "Не начинай каждый ответ с 'Приветствую вас'. Используй эту фразу только если пользователь реально поздоровался.\n"
        "Не ищи в интернете и не утверждай свежие факты, если пользователь не попросил явно найти в интернете.\n"
        "У тебя есть долговременная память ниже. Используй её, чтобы не говорить с пользователем как в первый раз.\n"
        f"{format_memory_for_prompt(memory)}\n\n"
        f"Сообщение пользователя:\n{message}\n\n"
        "Ответ:"
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
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": OLLAMA_NUM_PREDICT,
            "top_p": 0.9,
        },
    }
    request = urllib.request.Request(
        OLLAMA_BASE_URL + "/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
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
    retry_prompt = (
        f"{prompt}\n\n"
        f"Предыдущий ответ получился слишком коротким:\n{answer}\n\n"
        "Напиши заново нормальный полезный ответ."
    )
    improved_answer = ask_ollama(retry_prompt)
    return improved_answer or answer


def project_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / filename


def get_answer_file_path() -> Path:
    answer_file = Path(ANSWER_FILE_NAME)
    if answer_file.is_absolute():
        return answer_file
    return project_path(ANSWER_FILE_NAME)


def get_memory_file_path() -> Path:
    memory_file = Path(MEMORY_FILE_NAME)
    if memory_file.is_absolute():
        return memory_file
    return project_path(MEMORY_FILE_NAME)


def default_memory() -> dict[str, Any]:
    return {"facts": [], "history": []}


def load_memory() -> dict[str, Any]:
    path = get_memory_file_path()
    if not path.exists():
        return default_memory()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default_memory()
    if not isinstance(data, dict):
        return default_memory()
    data.setdefault("facts", [])
    data.setdefault("history", [])
    return data


def save_memory(memory: dict[str, Any]) -> None:
    path = get_memory_file_path()
    path.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")


def remember_from_message(memory: dict[str, Any], message: str) -> None:
    text = normalize_space(message)
    match = re.search(r"(?:запомни(?:\s+что)?|remember that)\s+(.+)", text, re.IGNORECASE)
    if not match:
        return
    fact = match.group(1).strip(" .,!?:;")
    if not fact:
        return
    facts = memory.setdefault("facts", [])
    if fact not in facts:
        facts.append(fact)
        del facts[:-40]


def add_history(memory: dict[str, Any], role: str, text: str) -> None:
    history = memory.setdefault("history", [])
    history.append({"role": role, "text": text, "time": dt.datetime.now().isoformat(timespec="seconds")})
    del history[:-30]


def format_memory_for_prompt(memory: dict[str, Any]) -> str:
    facts = memory.get("facts", [])[-12:]
    history = memory.get("history", [])[-10:]
    lines = ["Память Джарвиса:"]
    if facts:
        lines.append("Факты:")
        lines.extend(f"- {fact}" for fact in facts)
    if history:
        lines.append("Недавний диалог:")
        for item in history:
            role = "Пользователь" if item.get("role") == "user" else "Джарвис"
            lines.append(f"{role}: {item.get('text', '')}")
    if len(lines) == 1:
        lines.append("Пока нет сохранённой памяти.")
    return "\n".join(lines)


def write_answer_to_file(question: str, answer: str, sources: list[WebSource]) -> Path:
    answer_file_path = get_answer_file_path()
    source_lines = "\n".join(
        f"{index}. {source.title}\n   {source.url}"
        for index, source in enumerate(sources, start=1)
    )
    text = (
        "AI WEB ANSWER\n"
        f"Created: {dt.datetime.now().isoformat(timespec='seconds')}\n"
        f"Model: {OLLAMA_MODEL}\n"
        f"Sites used: {len(sources)}\n\n"
        "QUESTION:\n"
        f"{question}\n\n"
        "ANSWER:\n"
        f"{answer}\n\n"
        "SOURCES:\n"
        f"{source_lines}\n"
    )
    answer_file_path.write_text(text, encoding="utf-8")
    return answer_file_path


def answer_without_web(message: str, memory: dict[str, Any]) -> AnswerResult:
    if is_greeting(message):
        answer = "Приветствую вас."
    else:
        answer = ask_ollama(build_chat_prompt(message, memory))
        if not answer:
            answer = "Я не получил ответ от модели. Проверьте Ollama и попробуйте ещё раз."
    answer_file_path = write_answer_to_file(message, answer, [])
    return AnswerResult(answer=answer, sources=[], used_web=False, answer_file=answer_file_path)


def answer_with_web(message: str, memory: dict[str, Any]) -> AnswerResult:
    question = strip_internet_trigger(message)
    sources = collect_sources(question)
    if not sources:
        subject = extract_who_subject(question) if is_who_question(question) else ""
        if subject:
            answer = (
                f"Я не нашёл надёжных источников именно по точному имени «{subject}». "
                "Чтобы не заменить человека на более популярного однофамильца, я не буду отвечать про другого человека. "
                "Попробуй уточнить имя, профессию, страну или добавить ссылку/контекст."
            )
        else:
            answer = "Не получилось собрать текст с сайтов по этому запросу. Попробуй уточнить запрос."
        answer_file_path = write_answer_to_file(question, answer, [])
        return AnswerResult(answer=answer, sources=[], used_web=True, answer_file=answer_file_path)
    prompt = build_web_prompt(question, sources, memory)
    answer = ask_ollama(prompt)
    answer = improve_too_short_answer(question, prompt, answer)
    if not answer:
        answer = "Ollama вернула пустой ответ."
    answer_file_path = write_answer_to_file(question, answer, sources)
    return AnswerResult(answer=answer, sources=sources, used_web=True, answer_file=answer_file_path)


def answer_message(message: str, memory: dict[str, Any] | None = None) -> AnswerResult:
    memory = memory if memory is not None else load_memory()
    remember_from_message(memory, message)
    add_history(memory, "user", message)
    if should_search_web(message):
        result = answer_with_web(message, memory)
    else:
        result = answer_without_web(message, memory)
    add_history(memory, "assistant", result.answer)
    save_memory(memory)
    return result


class VoiceEngine:
    def __init__(self) -> None:
        self.engine: Any | None = None
        self.error = ""
        try:
            import pyttsx3  # type: ignore
            engine = pyttsx3.init()
            self.engine = engine
            voices = engine.getProperty("voices")
            for voice in voices:
                name = f"{getattr(voice, 'name', '')} {getattr(voice, 'id', '')}".lower()
                if any(word in name for word in ("male", "david", "pavel", "dmitry", "daniel", "муж")):
                    engine.setProperty("voice", voice.id)
                    break
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 0.95)
        except Exception as exc:
            self.error = str(exc)

    def speak(self, text: str) -> None:
        engine = self.engine
        if not engine:
            return
        def run() -> None:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=run, daemon=True).start()


class SpeechInput:
    def __init__(self) -> None:
        self.error = ""
        self.recognizer: Any | None = None
        self.microphone_type: Any | None = None
        try:
            import speech_recognition as sr  # type: ignore
            self.recognizer = sr.Recognizer()
            self.microphone_type = sr.Microphone
        except Exception as exc:
            self.error = str(exc)

    def listen(self) -> str:
        if not self.recognizer or not self.microphone_type:
            raise RuntimeError("Микрофон недоступен. Установи: pip install SpeechRecognition pyttsx3 pyaudio")
        with self.microphone_type() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=18)
        return self.recognizer.recognize_google(audio, language="ru-RU")


class JarvisDesktopApp:
    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import scrolledtext

        self.tk = tk
        self.root = tk.Tk()
        self.root.title("Джарвис")
        self.root.geometry("920x680")
        self.root.minsize(720, 520)
        self.root.configure(bg="#07111f")
        self.memory = load_memory()
        self.voice = VoiceEngine()
        self.speech = SpeechInput()
        self.queue: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.last_input_was_voice = False

        header = tk.Frame(self.root, bg="#0d1c30")
        header.pack(fill="x")
        tk.Label(header, text="Джарвис", fg="#e8f1ff", bg="#0d1c30", font=("Segoe UI", 20, "bold")).pack(side="left", padx=16, pady=12)
        self.status = tk.Label(header, text="Готов", fg="#5eead4", bg="#0d1c30", font=("Segoe UI", 11))
        self.status.pack(side="right", padx=16)

        self.chat = scrolledtext.ScrolledText(
            self.root,
            wrap="word",
            bg="#07111f",
            fg="#e8f1ff",
            insertbackground="#e8f1ff",
            font=("Segoe UI", 12),
            relief="flat",
            padx=12,
            pady=12,
        )
        self.chat.pack(fill="both", expand=True, padx=12, pady=12)
        self.chat.configure(state="disabled")

        bottom = tk.Frame(self.root, bg="#07111f")
        bottom.pack(fill="x", padx=12, pady=(0, 12))
        self.entry = tk.Text(bottom, height=3, wrap="word", bg="#0d1c30", fg="#e8f1ff", insertbackground="#e8f1ff", font=("Segoe UI", 12), relief="flat", padx=10, pady=8)
        self.entry.pack(side="left", fill="both", expand=True)
        self.entry.bind("<Control-Return>", lambda _event: self.send_text())

        buttons = tk.Frame(bottom, bg="#07111f")
        buttons.pack(side="right", padx=(10, 0))
        self.send_button = tk.Button(buttons, text="Отправить", command=self.send_text, bg="#5eead4", fg="#03131f", relief="flat", font=("Segoe UI", 11, "bold"), width=12)
        self.send_button.pack(fill="x", pady=(0, 8))
        self.mic_button = tk.Button(buttons, text="🎙 Голос", command=self.listen_voice, bg="#1f6feb", fg="white", relief="flat", font=("Segoe UI", 11, "bold"), width=12)
        self.mic_button.pack(fill="x")

        self.add_message("Джарвис", "Приветствую вас. Я буду отвечать текстом. Если нажмёте микрофон — отвечу голосом. Для поиска скажите или напишите: «найди в интернете ...».")
        if self.voice.error:
            self.add_message("Система", "Озвучка недоступна. Для голоса установи: pip install pyttsx3")
        if self.speech.error:
            self.add_message("Система", "Микрофон недоступен. Для распознавания установи: pip install SpeechRecognition pyaudio")

        self.root.after(100, self.process_queue)

    def add_message(self, sender: str, text: str) -> None:
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{sender}: {text}\n\n")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def set_busy(self, busy: bool, status: str) -> None:
        state = "disabled" if busy else "normal"
        self.send_button.configure(state=state)
        self.mic_button.configure(state=state)
        self.status.configure(text=status)

    def send_text(self) -> None:
        message = self.entry.get("1.0", "end").strip()
        if not message:
            return
        self.entry.delete("1.0", "end")
        self.last_input_was_voice = False
        self.start_answer(message, speak_answer=False)

    def listen_voice(self) -> None:
        self.set_busy(True, "Слушаю...")
        self.add_message("Система", "Слушаю микрофон...")
        threading.Thread(target=self._listen_voice_worker, daemon=True).start()

    def _listen_voice_worker(self) -> None:
        try:
            text = self.speech.listen()
            self.queue.put(("voice_text", text))
        except Exception as exc:
            self.queue.put(("error", f"Микрофон: {exc}"))

    def start_answer(self, message: str, speak_answer: bool) -> None:
        self.add_message("Вы", message)
        if should_search_web(message):
            self.add_message("Джарвис", "Ищу в интернете...")
            if speak_answer:
                self.voice.speak("Ищу в интернете.")
        self.set_busy(True, "Думаю...")
        threading.Thread(target=self._answer_worker, args=(message, speak_answer), daemon=True).start()

    def _answer_worker(self, message: str, speak_answer: bool) -> None:
        try:
            result = answer_message(message, self.memory)
            self.queue.put(("answer", (result, speak_answer)))
        except Exception as exc:
            self.queue.put(("error", str(exc)))

    def process_queue(self) -> None:
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == "voice_text":
                    self.start_answer(str(payload), speak_answer=True)
                elif kind == "answer":
                    result, speak_answer = payload
                    self.add_message("Джарвис", result.answer)
                    if speak_answer:
                        self.voice.speak(result.answer)
                    self.set_busy(False, "Готов")
                elif kind == "error":
                    self.add_message("Ошибка", str(payload))
                    self.set_busy(False, "Готов")
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def run(self) -> None:
        self.root.mainloop()


def get_question_from_user() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return input("Напиши вопрос: ").strip()


def run_cli() -> int:
    message = get_question_from_user()
    if not message:
        print("Вопрос пустой. Напиши вопрос и запусти ещё раз.")
        return 1
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
    print(result.answer)
    print(f"\nОтвет записан в файл: {result.answer_file}")
    return 0


def run_app() -> int:
    try:
        app = JarvisDesktopApp()
    except ModuleNotFoundError as exc:
        print("Не удалось открыть desktop-приложение.")
        print("В этой установке Python нет tkinter.")
        print("На Ubuntu обычно помогает: sudo apt install python3-tk")
        print(f"Ошибка: {exc}")
        return 1
    app.run()
    return 0


def main() -> int:
    if len(sys.argv) > 1:
        return run_cli()
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
