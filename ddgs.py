"""Small local DDGS-compatible search adapter.

The project imports ``DDGS`` from the third-party ``ddgs`` package, but the
repository does not declare that dependency.  This module provides the subset
of the API used by the app so imports resolve and web search keeps working with
the standard library only.
"""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional, Set, Tuple


DEFAULT_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _extract_duckduckgo_target_url(href: str) -> str:
    if href.startswith("//"):
        href = "https:" + href

    parsed_href = urllib.parse.urlparse(href)
    query = urllib.parse.parse_qs(parsed_href.query)

    if query.get("uddg"):
        return urllib.parse.unquote(query["uddg"][0])

    if href.startswith(("http://", "https://")):
        return href

    return ""


class _DuckDuckGoHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: List[Dict[str, str]] = []
        self._current_href = ""
        self._current_title_parts: List[str] = []
        self._current_snippet_parts: List[str] = []
        self._snippet_depth = 0

    def handle_starttag(self, tag: str, attrs: Iterable[Tuple[str, Optional[str]]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}
        class_name = attrs_dict.get("class", "")
        href = attrs_dict.get("href", "")

        if tag == "a" and href and ("result__a" in class_name or "uddg=" in href):
            self._current_href = href
            self._current_title_parts = []

        if tag in {"a", "div", "span"} and "result__snippet" in class_name:
            self._snippet_depth += 1
            self._current_snippet_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._current_title_parts.append(data)

        if self._snippet_depth:
            self._current_snippet_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current_href:
            url = _extract_duckduckgo_target_url(self._current_href)
            title = _normalize_space(" ".join(self._current_title_parts))

            if url and title:
                self.results.append(
                    {
                        "href": url,
                        "title": title,
                        "body": "",
                    }
                )

            self._current_href = ""
            self._current_title_parts = []

        if tag in {"a", "div", "span"} and self._snippet_depth:
            self._snippet_depth -= 1
            if not self._snippet_depth and self.results:
                snippet = _normalize_space(" ".join(self._current_snippet_parts))
                if snippet:
                    self.results[-1]["body"] = snippet
                self._current_snippet_parts = []


class DDGS:
    """Subset of the external ddgs.DDGS interface used by this project."""

    def __init__(self, timeout: int = DEFAULT_TIMEOUT, **_: object) -> None:
        self.timeout = timeout

    def __enter__(self) -> "DDGS":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def text(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: Optional[str] = None,
        safesearch: Optional[str] = None,
        **_: object,
    ) -> List[Dict[str, str]]:
        params = {"q": query}
        if region:
            params["kl"] = region
        if safesearch:
            params["kp"] = "-2" if safesearch == "off" else "1"

        search_url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                html = response.read().decode(charset, errors="ignore")
        except Exception:
            return []

        parser = _DuckDuckGoHtmlParser()
        parser.feed(html)

        unique_results: List[Dict[str, str]] = []
        seen_urls: Set[str] = set()
        limit = max_results or 10

        for result in parser.results:
            href = result.get("href", "")
            if not href or href in seen_urls:
                continue
            seen_urls.add(href)
            unique_results.append(result)
            if len(unique_results) >= limit:
                break

        return unique_results

    def news(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: Optional[str] = None,
        safesearch: Optional[str] = None,
        **_: object,
    ) -> List[Dict[str, str]]:
        results = self.text(query, max_results=max_results, region=region, safesearch=safesearch)
        return [
            {
                "url": result.get("href", ""),
                "title": result.get("title", ""),
                "body": result.get("body", ""),
                "date": "",
            }
            for result in results
        ]

    def images(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: Optional[str] = None,
        safesearch: Optional[str] = None,
        **_: object,
    ) -> List[Dict[str, str]]:
        results = self.text(query, max_results=max_results, region=region, safesearch=safesearch)
        return [
            {
                "url": result.get("href", ""),
                "title": result.get("title", ""),
                "image": result.get("href", ""),
                "thumbnail": "",
            }
            for result in results
        ]


__all__ = ["DDGS"]
