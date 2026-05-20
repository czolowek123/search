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
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2-vision:11b")
ANSWER_FILE_NAME = os.environ.get("ANSWER_FILE_NAME", "answer.txt")

WEB_SITE_LIMIT = int(os.environ.get("WEB_SITE_LIMIT", "10"))
WEB_SEARCH_CANDIDATES = int(os.environ.get("WEB_SEARCH_CANDIDATES", "25"))
WEB_REQUEST_TIMEOUT = int(os.environ.get("WEB_REQUEST_TIMEOUT", "12"))
WEB_SOURCE_TEXT_LIMIT = int(os.environ.get("WEB_SOURCE_TEXT_LIMIT", "12000"))
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "240"))

WEB_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
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


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


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

        if tag in (
            "p",
            "br",
            "div",
            "section",
            "article",
            "header",
            "footer",
            "li",
            "h1",
            "h2",
            "h3",
            "td",
            "th",
        ):
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
    search_url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    page_html = request_url_text(search_url)
    parser = DuckDuckGoResultParser()
    parser.feed(page_html)

    unique_results: list[SearchResult] = []
    seen_urls: set[str] = set()

    for result in parser.results:
        if result.url in seen_urls:
            continue

        seen_urls.add(result.url)
        unique_results.append(result)

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

    return WebSource(
        title=parser.title or result.title or result.url,
        url=result.url,
        text=text,
    )


def collect_sources(question: str) -> list[WebSource]:
    print(f"Ищу сайты по теме: {question}")
    search_results = search_web(question)
    sources: list[WebSource] = []

    for index, result in enumerate(search_results, start=1):
        if len(sources) >= WEB_SITE_LIMIT:
            break

        print(f"[{index}] Читаю: {result.url}")
        try:
            source = read_web_page(result)
        except Exception as exc:
            print(f"    пропуск: {exc}")
            continue

        if not source:
            print("    пропуск: нет читаемого текста")
            continue

        sources.append(source)
        print(f"    готово: {len(source.text)} символов текста")

    return sources


def build_ollama_prompt(question: str, sources: list[WebSource]) -> str:
    source_blocks: list[str] = []

    for index, source in enumerate(sources, start=1):
        source_blocks.append(
            f"Источник {index}: {source.title}\n"
            f"URL: {source.url}\n"
            f"Текст:\n{source.text}"
        )

    joined_sources = "\n\n---\n\n".join(source_blocks)

    return (
        "Ты анализируешь информацию из интернета и отвечаешь кратко по-русски.\n"
        "Используй только данные из источников ниже. Если данных мало, честно скажи об этом.\n"
        "Ответ должен быть коротким: 5-10 предложений максимум.\n"
        "Если вопрос про сравнение, дай понятный вывод: что лучше и почему.\n\n"
        f"Вопрос пользователя:\n{question}\n\n"
        f"Источники ({len(sources)} сайтов):\n{joined_sources}\n\n"
        "Сделай краткий итоговый ответ."
    )


def stream_ollama_answer(prompt: str):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True,
    }

    request = urllib.request.Request(
        OLLAMA_BASE_URL + "/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            data = json.loads(line)
            chunk = data.get("response", "")

            if chunk:
                yield chunk

            if data.get("done"):
                break


def get_answer_file_path() -> Path:
    current_dir = Path(__file__).resolve().parent
    answer_file = Path(ANSWER_FILE_NAME)

    if answer_file.is_absolute():
        return answer_file

    return current_dir / answer_file


def write_answer_header(question: str, sources: list[WebSource]) -> Path:
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
    )

    answer_file_path.write_text(text, encoding="utf-8")
    return answer_file_path


def append_answer_footer(answer_file_path: Path, sources: list[WebSource]) -> None:
    source_lines = "\n".join(
        f"{index}. {source.title}\n   {source.url}"
        for index, source in enumerate(sources, start=1)
    )
    text = (
        "\n\n"
        "SOURCES:\n"
        f"{source_lines}\n"
    )

    with answer_file_path.open("a", encoding="utf-8") as answer_file:
        answer_file.write(text)


def write_streaming_answer(question: str, prompt: str, sources: list[WebSource]) -> tuple[Path, str]:
    answer_file_path = write_answer_header(question, sources)
    answer_parts: list[str] = []

    with answer_file_path.open("a", encoding="utf-8") as answer_file:
        for chunk in stream_ollama_answer(prompt):
            print(chunk, end="", flush=True)
            answer_file.write(chunk)
            answer_file.flush()
            answer_parts.append(chunk)

    append_answer_footer(answer_file_path, sources)
    return answer_file_path, "".join(answer_parts).strip()


def get_question_from_user() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    return input("Напиши вопрос: ").strip()


def main() -> int:
    question = get_question_from_user()

    if not question:
        print("Вопрос пустой. Напиши вопрос и запусти ещё раз.")
        return 1

    try:
        sources = collect_sources(question)
    except urllib.error.URLError as exc:
        print(f"Не получилось выполнить веб-поиск: {exc}")
        return 1
    except Exception as exc:
        print(f"Ошибка веб-поиска: {exc}")
        return 1

    if not sources:
        print("Не получилось собрать текст с сайтов.")
        return 1

    print(f"Собрано сайтов: {len(sources)}. Отправляю текст в Ollama {OLLAMA_MODEL}...")
    prompt = build_ollama_prompt(question, sources)

    try:
        print("\nКраткий ответ:")
        answer_file_path, answer = write_streaming_answer(question, prompt, sources)
    except urllib.error.URLError as exc:
        print("Не получилось подключиться к Ollama.")
        print("Проверь, что Ollama запущена: ollama serve")
        print(f"Ошибка: {exc}")
        return 1
    except Exception as exc:
        print(f"Ошибка при запросе к Ollama: {exc}")
        return 1

    if not answer:
        answer = "Ollama вернула пустой ответ."

    print("\nОтвет записан в файл:")
    print(answer_file_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())