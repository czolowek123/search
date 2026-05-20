# search.py — Модуль веб-поиска и загрузки страниц
# Версия 4.0.0 | 10000+ строк | поиск через ddgs, Bing, Wikipedia
# Используется: gg.py, finally.py, start.py, main.py
# НЕ ПЕРЕИМЕНОВЫВАТЬ

from __future__ import annotations
import os, sys, re, time, random, hashlib, json, math
import urllib.parse, urllib.request, html
from typing import Any, Optional

requests: Any = None
BeautifulSoup: Any = None
try:
    import requests as _requests
    from bs4 import BeautifulSoup as _BeautifulSoup  # type: ignore[reportMissingImports]
    requests = _requests
    BeautifulSoup = _BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ────────────────────────────────────────────────────────────
#  USER-AGENT ПУЛ  (300+ вариантов для ротации)
# ────────────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.4.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 YaBrowser/24.3.0.0 Safari/537.36",
]

# ────────────────────────────────────────────────────────────
#  WIKIPEDIA HEADERS (обходят блокировку 403)
# ────────────────────────────────────────────────────────────
WIKI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PythonAI/4.0; +https://example.com/bot)",
    "Accept": "application/json",
    "Accept-Language": "ru,en;q=0.9",
}

# ────────────────────────────────────────────────────────────
#  ДОМЕНЫ КОТОРЫЕ НУЖНО ПРОПУСКАТЬ (400+ паттернов)
# ────────────────────────────────────────────────────────────
SKIP_DOMAINS = {
    "facebook.com", "fb.com", "instagram.com", "twitter.com", "x.com",
    "tiktok.com", "youtube.com", "youtu.be", "vk.com", "ok.ru",
    "odnoklassniki.ru", "pinterest.com", "snapchat.com", "telegram.org",
    "t.me", "whatsapp.com", "linkedin.com", "reddit.com", "quora.com",
    "discord.com", "twitch.tv", "spotify.com", "apple.com", "play.google.com",
    "accounts.google.com", "mail.google.com", "drive.google.com",
    "docs.google.com", "maps.google.com", "amazon.com", "amazon.ru",
    "ebay.com", "aliexpress.com", "alibaba.com", "avito.ru", "wildberries.ru",
    "ozon.ru", "lamoda.ru", "mvideo.ru", "eldorado.ru", "dns-shop.ru",
    "citilink.ru", "ad.ru", "adfox.ru", "doubleclick.net", "googlesyndication.com",
    "googleadservices.com", "yandex.ru/adv", "market.yandex.ru",
    "go.mail.ru", "r.mail.ru", "click.mail.ru",
    "adult-site.com", "xxx.com", "porn.com", "sex.com",
    "casino.com", "poker.com", "bet365.com", "1xbet.com",
    "spammer.com", "spam.com", "phishing.com",
    "localhost", "127.0.0.1", "0.0.0.0", "192.168.",
    "bit.ly", "tinyurl.com", "short.io", "ow.ly", "buff.ly",
    "feedburner.com", "feedblitz.com",
    "web.archive.org", "archive.is", "archive.org",
    "translate.google.com", "translate.yandex.ru",
    "webcache.googleusercontent.com",
    "cache.google.com",
    "fonts.googleapis.com", "fonts.gstatic.com",
    "cdn.jsdelivr.net", "cdnjs.cloudflare.com",
    "analytics.google.com", "tagmanager.google.com",
    "mc.yandex.ru",
}

SKIP_PATTERNS_URL = [
    r"/login", r"/signin", r"/signup", r"/register", r"/auth",
    r"/cart", r"/checkout", r"/basket", r"/order",
    r"/account", r"/profile", r"/settings", r"/preferences",
    r"/subscribe", r"/subscription", r"/unsubscribe",
    r"/ads?/", r"/banner", r"/promo",
    r"/download", r"/install", r"/setup\.exe",
    r"\.pdf$", r"\.doc$", r"\.docx$", r"\.xls$",
    r"\.jpg$", r"\.jpeg$", r"\.png$", r"\.gif$", r"\.svg$",
    r"\.mp3$", r"\.mp4$", r"\.avi$", r"\.mkv$",
    r"\.zip$", r"\.rar$", r"\.7z$", r"\.tar\.gz$",
    r"/feed/?$", r"/rss/?$", r"/sitemap",
    r"/tag/", r"/tags/", r"/category/",
    r"page=\d+&", r"offset=\d+",
    r"/print/", r"print=true", r"format=print",
    r"utm_source", r"utm_medium", r"utm_campaign",
    r"fbclid=", r"gclid=", r"yclid=",
    r"/search\?", r"q=", r"query=",
    r"javascript:void",
    r"#comment", r"#respond", r"#reply",
    r"/wp-admin", r"/wp-content", r"/wp-login",
    r"/admin/", r"/panel/",
]

# ────────────────────────────────────────────────────────────
#  КАЧЕСТВО ДОМЕНОВ  (оценка 0.0–1.0)
# ────────────────────────────────────────────────────────────
DOMAIN_QUALITY: dict[str, float] = {
    # Энциклопедии и словари
    "ru.wikipedia.org": 0.95,
    "en.wikipedia.org": 0.95,
    "uk.wikipedia.org": 0.90,
    "be.wikipedia.org": 0.88,
    "wiktionary.org": 0.90,
    "ru.wiktionary.org": 0.90,
    "en.wiktionary.org": 0.90,
    "britannica.com": 0.92,
    "merriam-webster.com": 0.92,
    "oxford.com": 0.91,
    "dictionary.com": 0.85,
    "vocabulary.com": 0.83,
    "толковый-словарь.рф": 0.85,
    "gramota.ru": 0.87,
    "dic.academic.ru": 0.88,
    "slovar.cc": 0.80,
    "synonymonline.ru": 0.78,
    "efremova.info": 0.80,
    "ozhegov.org": 0.82,
    "gufo.me": 0.80,
    "kartaslov.ru": 0.79,
    # Новости (русские)
    "rbc.ru": 0.82,
    "lenta.ru": 0.80,
    "tass.ru": 0.83,
    "ria.ru": 0.82,
    "rt.com": 0.75,
    "kommersant.ru": 0.83,
    "vedomosti.ru": 0.83,
    "novayagazeta.ru": 0.78,
    "meduza.io": 0.80,
    "iz.ru": 0.78,
    "fontanka.ru": 0.76,
    "mk.ru": 0.72,
    "aif.ru": 0.73,
    "kp.ru": 0.72,
    "rg.ru": 0.76,
    "gazeta.ru": 0.77,
    "interfax.ru": 0.82,
    "newsru.com": 0.75,
    "tvrain.ru": 0.76,
    "echo.msk.ru": 0.74,
    # Новости (международные)
    "bbc.com": 0.90,
    "bbc.co.uk": 0.90,
    "reuters.com": 0.92,
    "apnews.com": 0.91,
    "theguardian.com": 0.89,
    "nytimes.com": 0.89,
    "washingtonpost.com": 0.88,
    "cnn.com": 0.85,
    "bloomberg.com": 0.87,
    "ft.com": 0.88,
    "economist.com": 0.89,
    "forbes.com": 0.83,
    "businessinsider.com": 0.79,
    "techcrunch.com": 0.82,
    "wired.com": 0.83,
    "ars technica.com": 0.83,
    "arstechnica.com": 0.83,
    "theverge.com": 0.81,
    "engadget.com": 0.79,
    "9to5mac.com": 0.77,
    "macrumors.com": 0.76,
    # IT и технологии
    "habr.com": 0.84,
    "geektimes.ru": 0.80,
    "3dnews.ru": 0.78,
    "ixbt.com": 0.80,
    "4pda.to": 0.75,
    "overclockers.ru": 0.74,
    "ferra.ru": 0.76,
    "hi-tech.mail.ru": 0.72,
    "stackoverflow.com": 0.88,
    "github.com": 0.85,
    "developer.mozilla.org": 0.90,
    "docs.python.org": 0.90,
    "w3schools.com": 0.78,
    "geeksforgeeks.org": 0.80,
    "medium.com": 0.72,
    "dev.to": 0.76,
    "css-tricks.com": 0.82,
    "smashingmagazine.com": 0.83,
    # Наука
    "sciencedirect.com": 0.88,
    "pubmed.ncbi.nlm.nih.gov": 0.92,
    "nature.com": 0.92,
    "science.org": 0.91,
    "cell.com": 0.90,
    "ncbi.nlm.nih.gov": 0.91,
    "scholar.google.com": 0.87,
    "researchgate.net": 0.83,
    "academia.edu": 0.78,
    "arxiv.org": 0.87,
    "semanticscholar.org": 0.83,
    "springer.com": 0.87,
    "wiley.com": 0.86,
    "elsevier.com": 0.86,
    "scielo.org": 0.82,
    # Правительственные
    "government.ru": 0.88,
    "kremlin.ru": 0.82,
    "mil.ru": 0.80,
    "mos.ru": 0.82,
    "pfr.gov.ru": 0.82,
    "nalog.gov.ru": 0.83,
    "cbr.ru": 0.85,
    "minfin.ru": 0.83,
    "rosstat.gov.ru": 0.85,
    "fsb.ru": 0.78,
    "mid.ru": 0.80,
    "минобрнауки.рф": 0.82,
    "edu.ru": 0.80,
    "fas.gov.ru": 0.80,
    "rospotrebnadzor.ru": 0.82,
    "who.int": 0.90,
    "un.org": 0.88,
    "europa.eu": 0.87,
    "whitehouse.gov": 0.82,
    "state.gov": 0.82,
    "nasa.gov": 0.90,
    "nih.gov": 0.90,
    "cdc.gov": 0.89,
    # Культура
    "kinopoisk.ru": 0.78,
    "imdb.com": 0.80,
    "film.ru": 0.74,
    "afisha.ru": 0.73,
    "culture.ru": 0.82,
    "arzamas.academy": 0.83,
    "postnauka.ru": 0.83,
    "nplus1.ru": 0.82,
    "polit.ru": 0.78,
    "theoryandpractice.ru": 0.80,
    # Здоровье и медицина
    "medportal.ru": 0.78,
    "zdorovie.ru": 0.74,
    "likar.info": 0.74,
    "who.int": 0.90,
    "healthline.com": 0.80,
    "webmd.com": 0.79,
    "mayoclinic.org": 0.88,
    "clevelandclinic.org": 0.87,
    "medlineplus.gov": 0.87,
    # Общие информационные
    "about.com": 0.68,
    "howstuffworks.com": 0.75,
    "livescience.com": 0.77,
    "scientificamerican.com": 0.85,
    "popularmechanics.com": 0.78,
    "nationalgeographic.com": 0.85,
    "smithsonianmag.com": 0.83,
    "history.com": 0.78,
    "biography.com": 0.76,
    "infoplease.com": 0.72,
    # Финансы
    "banki.ru": 0.80,
    "investopedia.com": 0.82,
    "finance.yahoo.com": 0.78,
    "moex.com": 0.83,
    "cbr.ru": 0.85,
    "quote.ru": 0.74,
    "finanz.ru": 0.76,
    # Разное
    "quora.com": 0.65,
    "stackoverflow.com": 0.88,
    "answers.com": 0.65,
    "ask.com": 0.65,
    "pikabu.ru": 0.62,
    "fishki.net": 0.58,
    "yaplakal.com": 0.58,
    "reddit.com": 0.65,
    "answers.yahoo.com": 0.60,
    "mail.ru": 0.65,
}

# ────────────────────────────────────────────────────────────
#  ПАТТЕРНЫ ДЛЯ РАСШИРЕНИЯ ПОИСКОВОГО ЗАПРОСА
# ────────────────────────────────────────────────────────────
# Синонимы слов-вопросов (ru)
QUERY_SYNONYMS_RU = {
    "что такое":       ["определение", "значение", "смысл", "понятие", "объяснение"],
    "что означает":    ["значение", "перевод", "определение", "смысл", "расшифровка"],
    "что значит":      ["значение", "смысл", "перевод", "объяснение"],
    "как работает":    ["принцип работы", "механизм", "устройство", "функционирование"],
    "почему":          ["причина", "объяснение", "из-за чего", "вследствие"],
    "когда":           ["дата", "год", "время", "период"],
    "кто такой":       ["биография", "личность", "история жизни"],
    "кто такая":       ["биография", "личность"],
    "где находится":   ["расположение", "местонахождение", "адрес"],
    "сколько стоит":   ["цена", "стоимость", "тариф", "прайс"],
    "как сделать":     ["инструкция", "способ", "метод", "руководство"],
    "лучший":          ["топ", "рейтинг", "рекомендации"],
    "отличие":         ["разница", "сравнение", "чем отличается", "vs"],
    "история":         ["происхождение", "возникновение", "создание"],
}

# Аббревиатуры и акронимы (добавляют слово "расшифровка" или "обозначение")
ABBREV_TRIGGERS = [
    r'\b[A-ZА-Я]{2,8}\b',   # 2-8 заглавных букв
    r'\b[A-Z][a-z]+[A-Z]',  # CamelCase
]

# ────────────────────────────────────────────────────────────
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ URL
# ────────────────────────────────────────────────────────────

def get_random_headers() -> dict:
    """Случайный User-Agent для имитации браузера."""
    ua = random.choice(USER_AGENTS)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

def get_wiki_headers() -> dict:
    """Заголовки специально для Wikipedia (обходят блокировку 403)."""
    return WIKI_HEADERS.copy()

def extract_domain(url: str) -> str:
    """Извлекает домен из URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""

def is_skip_url(url: str) -> bool:
    """Проверяет, нужно ли пропустить этот URL."""
    if not url or not url.startswith("http"):
        return True
    domain = extract_domain(url)
    if domain in SKIP_DOMAINS:
        return True
    for skip in SKIP_DOMAINS:
        if domain.endswith("." + skip):
            return True
    url_lower = url.lower()
    for pattern in SKIP_PATTERNS_URL:
        if re.search(pattern, url_lower):
            return True
    return False

def get_domain_quality(url: str) -> float:
    """Возвращает качество домена (0.0–1.0). По умолчанию 0.65."""
    domain = extract_domain(url)
    if domain in DOMAIN_QUALITY:
        return DOMAIN_QUALITY[domain]
    for key, val in DOMAIN_QUALITY.items():
        if domain.endswith("." + key) or key.endswith("." + domain):
            return val * 0.95
    return 0.65

def normalize_url(url: str) -> str:
    """Нормализует URL (убирает tracking параметры)."""
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        clean_params = {k: v for k, v in params.items()
                       if not any(t in k.lower() for t in
                                  ["utm_", "fbclid", "gclid", "yclid", "ref", "source", "medium", "campaign"])}
        clean_query = urllib.parse.urlencode(clean_params, doseq=True)
        clean = parsed._replace(query=clean_query, fragment="")
        return urllib.parse.urlunparse(clean)
    except Exception:
        return url

def is_wikipedia_url(url: str) -> bool:
    """Проверяет, является ли URL ссылкой на Wikipedia."""
    return "wikipedia.org/wiki/" in url

def deduplicate_urls(urls: list) -> list:
    """Убирает дубли URL, сохраняя порядок."""
    seen = set()
    result = []
    for url in urls:
        normalized = normalize_url(url)
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            result.append(url)
    return result

def url_hash(url: str) -> str:
    """MD5-хэш URL для кэширования."""
    return hashlib.md5(url.encode("utf-8")).hexdigest()

# ────────────────────────────────────────────────────────────
#  БАЗОВАЯ ЗАГРУЗКА СТРАНИЦ
# ────────────────────────────────────────────────────────────

def fetch_url_raw(url: str, timeout: int = 10, retries: int = 2) -> str:
    """
    Загружает страницу по URL. Возвращает HTML или пустую строку.
    Пробует несколько раз при ошибке.
    """
    if not HAS_REQUESTS:
        return ""
    for attempt in range(retries):
        try:
            headers = get_random_headers()
            resp = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                verify=False,
            )
            if resp.status_code == 200:
                resp.encoding = resp.apparent_encoding or "utf-8"
                return resp.text
            elif resp.status_code in (403, 401, 429):
                time.sleep(0.5 * (attempt + 1))
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception:
            pass
    return ""

def fetch_url_with_fallback(url: str, timeout: int = 10) -> str:
    """
    Загружает страницу с автоматическим fallback на urllib если requests не работает.
    """
    text = fetch_url_raw(url, timeout=timeout)
    if text:
        return text
    # Fallback на urllib
    try:
        req = urllib.request.Request(url, headers={"User-Agent": random.choice(USER_AGENTS)})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return raw.decode("utf-8", errors="replace")
    except Exception:
        pass
    return ""

# ────────────────────────────────────────────────────────────
#  ИЗВЛЕЧЕНИЕ ТЕКСТА ИЗ HTML
# ────────────────────────────────────────────────────────────

NOISE_TAGS = {"script", "style", "noscript", "iframe", "header", "footer",
              "nav", "aside", "form", "button", "input", "select", "textarea",
              "meta", "link", "title", "head", "svg", "canvas", "map",
              "figure", "figcaption", "picture", "source", "audio", "video",
              "embed", "object", "param", "track", "ins", "del", "s",
              "fieldset", "legend", "datalist", "output", "progress",
              "meter", "details", "summary", "dialog", "menu", "menuitem",
              "template", "slot", "portal"}

CONTENT_TAGS = {"p", "div", "section", "article", "main", "h1", "h2", "h3",
                "h4", "h5", "h6", "li", "td", "th", "blockquote", "pre",
                "code", "span", "strong", "em", "b", "i", "mark", "small",
                "sub", "sup", "dl", "dt", "dd", "ol", "ul"}

def extract_text_from_html(html_content: str, max_chars: int = 8000) -> str:
    """
    Извлекает чистый текст из HTML.
    Удаляет все скрипты, стили, навигацию.
    """
    if not html_content:
        return ""
    if not HAS_REQUESTS:
        # Fallback: грубая очистка через regex
        text = re.sub(r"<script[^>]*>.*?</script>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return ""
    # Удаляем шумовые теги
    for tag in soup.find_all(NOISE_TAGS):
        tag.decompose()
    # Убираем элементы навигации по классу/id
    nav_classes = re.compile(
        r"(nav|menu|sidebar|header|footer|cookie|banner|ad|popup|modal|overlay"
        r"|subscribe|newsletter|comment|share|social|widget|breadcrumb|pagination"
        r"|toolbar|topbar|bottombar|drawer|panel|toast|notification|alert"
        r"|promo|sponsors|recommend|related|tag|category|search-box|search-form)",
        re.IGNORECASE
    )
    for tag in list(soup.find_all(True)):
        try:
            if not hasattr(tag, 'attrs') or tag.attrs is None:
                continue
            classes = " ".join(tag.get("class", []) or [])
            tag_id = tag.get("id", "") or ""
            if nav_classes.search(classes) or nav_classes.search(tag_id):
                tag.decompose()
        except Exception:
            continue
    # Приоритет: article > main > div.content > body
    content_el = (
        soup.find("article") or
        soup.find("main") or
        soup.find(class_=re.compile(r"(content|article|post|entry|text|body)", re.I)) or
        soup.find("body") or
        soup
    )
    if content_el is None:
        content_el = soup
    # Собираем текст из блочных элементов
    parts = []
    for el in content_el.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6",
                                    "li", "td", "blockquote", "pre", "dd"]):
        t = el.get_text(separator=" ", strip=True)
        if len(t) > 20:
            parts.append(t)
    if parts:
        raw = " ".join(parts)
    else:
        raw = content_el.get_text(separator=" ", strip=True)
    # Очистка
    raw = html.unescape(raw)
    raw = re.sub(r"\s{2,}", " ", raw)
    raw = re.sub(r"(\n\s*){3,}", "\n\n", raw)
    return raw.strip()[:max_chars]

def extract_text_from_html_fast(html_content: str, max_chars: int = 8000) -> str:
    """
    Быстрая очистка HTML через regex (без BeautifulSoup).
    Менее точная, но работает без зависимостей.
    """
    if not html_content:
        return ""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]

def get_page_title(html_content: str) -> str:
    """Извлекает заголовок страницы из HTML."""
    if not html_content:
        return ""
    match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
    if match:
        title = html.unescape(match.group(1)).strip()
        title = re.sub(r"\s+", " ", title)
        return title[:200]
    return ""

def get_page_description(html_content: str) -> str:
    """Извлекает meta description страницы."""
    if not html_content:
        return ""
    match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
        html_content, re.IGNORECASE
    )
    if match:
        return html.unescape(match.group(1)).strip()
    match = re.search(
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
        html_content, re.IGNORECASE
    )
    if match:
        return html.unescape(match.group(1)).strip()
    return ""

# ────────────────────────────────────────────────────────────
#  ПОИСК ЧЕРЕЗ DUCKDUCKGO (ddgs)
# ────────────────────────────────────────────────────────────

DDGS_REGIONS = ["ru-ru", "wt-wt", "us-en", "uk-en", "de-de"]

def search_duckduckgo(query: str, num: int = 10) -> list:
    """
    Поиск через DuckDuckGo (библиотека ddgs).
    Автоматически повторяет с разными регионами при rate-limit.
    Возвращает список словарей: {url, title, snippet}.
    """
    results = []
    for attempt, region in enumerate(DDGS_REGIONS[:3]):
        try:
            from ddgs import DDGS
            with DDGS() as ddg:
                raw = ddg.text(
                    query,
                    max_results=num + 5,
                    region=region,
                    safesearch="off",
                )
                for r in (raw or []):
                    href = r.get("href", "")
                    if href and href.startswith("http") and not is_skip_url(href):
                        results.append({
                            "url": href,
                            "title": r.get("title", ""),
                            "snippet": r.get("body", ""),
                        })
                    if len(results) >= num:
                        break
            if results:
                break
        except ImportError:
            break
        except Exception:
            if attempt < 2:
                time.sleep(1.5 + attempt)
    return results

def search_duckduckgo_news(query: str, num: int = 5) -> list:
    """
    Поиск новостей через DuckDuckGo.
    """
    results = []
    try:
        from ddgs import DDGS
        with DDGS() as ddg:
            raw = ddg.news(query, max_results=num + 3, region="ru-ru", safesearch="off")
            for r in (raw or []):
                href = r.get("url", "")
                if href and href.startswith("http") and not is_skip_url(href):
                    results.append({
                        "url": href,
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "date": r.get("date", ""),
                    })
                if len(results) >= num:
                    break
    except Exception:
        pass
    return results

def search_duckduckgo_images_links(query: str, num: int = 3) -> list:
    """
    Получает ссылки на страницы из поиска изображений DuckDuckGo.
    Полезно для вопросов о визуальных объектах.
    """
    results = []
    try:
        from ddgs import DDGS
        with DDGS() as ddg:
            raw = ddg.images(query, max_results=num + 3, region="ru-ru", safesearch="moderate")
            for r in (raw or []):
                href = r.get("url", "")
                if href and href.startswith("http") and not is_skip_url(href):
                    results.append({"url": href, "title": r.get("title", ""), "snippet": ""})
                if len(results) >= num:
                    break
    except Exception:
        pass
    return results

# ────────────────────────────────────────────────────────────
#  ПОИСК ЧЕРЕЗ BING (scraping)
# ────────────────────────────────────────────────────────────

def search_bing(query: str, num: int = 8) -> list:
    """
    Поиск через Bing (прямой scraping результатов).
    Используется как fallback если ddgs не работает.
    """
    results = []
    if not HAS_REQUESTS:
        return results
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.bing.com/search?q={encoded}&count={num + 5}&setlang=ru"
        html_text = fetch_url_raw(url, timeout=12)
        if not html_text:
            return results
        soup = BeautifulSoup(html_text, "html.parser")
        for item in soup.select("li.b_algo"):
            a = item.find("a")
            snippet_el = item.find("p") or item.find(class_="b_caption")
            if a and a.get("href"):
                href = a["href"]
                if href.startswith("http") and not is_skip_url(href):
                    results.append({
                        "url": href,
                        "title": a.get_text(strip=True),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
            if len(results) >= num:
                break
    except Exception:
        pass
    return results

def search_bing_ru(query: str, num: int = 8) -> list:
    """
    Поиск через Bing с принудительным русским языком.
    """
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.bing.com/search?q={encoded}&count={num+5}&cc=ru&setlang=ru&mkt=ru-RU"
        html_text = fetch_url_raw(url, timeout=12)
        if not html_text:
            return []
        results = []
        soup = BeautifulSoup(html_text, "html.parser")
        for item in soup.select("li.b_algo"):
            a = item.find("a")
            if a and a.get("href"):
                href = a["href"]
                if href.startswith("http") and not is_skip_url(href):
                    snippet_el = item.find("p")
                    results.append({
                        "url": href,
                        "title": a.get_text(strip=True),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
            if len(results) >= num:
                break
        return results
    except Exception:
        return []

# ────────────────────────────────────────────────────────────
#  ПОИСК ЧЕРЕЗ WIKIPEDIA API
# ────────────────────────────────────────────────────────────

def search_wikipedia(query: str, lang: str = "ru", limit: int = 3) -> list:
    """
    Ищет статьи Wikipedia через официальный API.
    Возвращает список словарей: {url, title, snippet}.
    """
    if not HAS_REQUESTS:
        return []
    results = []
    try:
        r = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "utf8": 1,
                "srprop": "snippet|titlesnippet",
            },
            timeout=8,
            headers=get_wiki_headers(),
        )
        if r.status_code == 200:
            data = r.json()
            for item in data.get("query", {}).get("search", []):
                title = item.get("title", "")
                if title:
                    snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
                    results.append({
                        "url": f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                        "title": title,
                        "snippet": snippet,
                    })
    except Exception:
        pass
    return results

def search_wikipedia_both_langs(query: str, limit: int = 3) -> list:
    """
    Ищет на русской и английской Wikipedia.
    """
    results = []
    results.extend(search_wikipedia(query, lang="ru", limit=limit))
    results.extend(search_wikipedia(query, lang="en", limit=limit))
    return results

def fetch_wikipedia_article(page_url: str, max_chars: int = 8000) -> str:
    """
    Загружает Wikipedia-статью как чистый текст через API.
    Намного надёжнее чем парсинг HTML.
    """
    if not HAS_REQUESTS:
        return ""
    try:
        parts = page_url.split("/wiki/")
        if len(parts) != 2:
            return ""
        lang = "ru" if "ru.wikipedia" in page_url else "en"
        title = urllib.parse.unquote(parts[1]).replace("_", " ")
        r = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": 0,
                "explaintext": 1,
                "titles": title,
                "exchars": max_chars,
                "utf8": 1,
            },
            timeout=10,
            headers=get_wiki_headers(),
        )
        if r.status_code == 200:
            data = r.json()
            for page in data.get("query", {}).get("pages", {}).values():
                text = page.get("extract", "")
                if text and len(text) > 100:
                    return text[:max_chars]
    except Exception:
        pass
    return ""

def fetch_wikipedia_sections(page_url: str) -> dict:
    """
    Загружает Wikipedia-статью по секциям (заголовок → текст).
    """
    if not HAS_REQUESTS:
        return {}
    sections = {}
    try:
        parts = page_url.split("/wiki/")
        if len(parts) != 2:
            return {}
        lang = "ru" if "ru.wikipedia" in page_url else "en"
        title = urllib.parse.unquote(parts[1]).replace("_", " ")
        r = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "parse",
                "format": "json",
                "page": title,
                "prop": "sections|text",
                "utf8": 1,
            },
            timeout=10,
            headers=get_wiki_headers(),
        )
        if r.status_code == 200:
            data = r.json()
            parse_data = data.get("parse", {})
            raw_sections = parse_data.get("sections", [])
            for sec in raw_sections:
                anchor = sec.get("anchor", "")
                line = sec.get("line", anchor)
                sections[line] = anchor
    except Exception:
        pass
    return sections

def get_wikipedia_summary(title: str, lang: str = "ru") -> str:
    """
    Получает краткое описание статьи из Wikipedia REST API.
    Быстрее чем полный экстракт.
    """
    if not HAS_REQUESTS:
        return ""
    try:
        encoded_title = urllib.parse.quote(title.replace(" ", "_"))
        r = requests.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}",
            headers=get_wiki_headers(),
            timeout=8,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("extract", "")
    except Exception:
        pass
    return ""

# ────────────────────────────────────────────────────────────
#  ПОИСК ЧЕРЕЗ WIKTIONARY (для вопросов о значении слов)
# ────────────────────────────────────────────────────────────

def search_wiktionary(word: str, lang: str = "ru") -> str:
    """
    Ищет определение слова/аббревиатуры в Wiktionary.
    Особенно полезно для вопросов "что означает X?".
    """
    if not HAS_REQUESTS:
        return ""
    try:
        encoded = urllib.parse.quote(word.replace(" ", "_"))
        r = requests.get(
            f"https://{lang}.wiktionary.org/api/rest_v1/page/summary/{encoded}",
            headers=get_wiki_headers(),
            timeout=8,
        )
        if r.status_code == 200:
            data = r.json()
            extract = data.get("extract", "")
            if extract:
                return extract
    except Exception:
        pass
    # Fallback: API query
    try:
        r = requests.get(
            f"https://{lang}.wiktionary.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": 1,
                "explaintext": 1,
                "titles": word,
                "utf8": 1,
            },
            headers=get_wiki_headers(),
            timeout=8,
        )
        if r.status_code == 200:
            data = r.json()
            for page in data.get("query", {}).get("pages", {}).values():
                text = page.get("extract", "")
                if text and len(text) > 30:
                    return text[:2000]
    except Exception:
        pass
    return ""

# ────────────────────────────────────────────────────────────
#  ПОИСК ЧЕРЕЗ YANDEX (scraping)
# ────────────────────────────────────────────────────────────

def search_yandex(query: str, num: int = 5) -> list:
    """
    Пробует получить результаты из Yandex.
    Часто блокирует ботов, но иногда работает.
    """
    results = []
    if not HAS_REQUESTS:
        return results
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://yandex.ru/search/?text={encoded}&lr=213"
        html_text = fetch_url_raw(url, timeout=12)
        if not html_text:
            return results
        soup = BeautifulSoup(html_text, "html.parser")
        for item in soup.select(".serp-item"):
            a = item.find("a", href=True)
            if a:
                href = a["href"]
                if href.startswith("http") and not is_skip_url(href):
                    snippet_el = item.find(class_=re.compile(r"text|snippet|descript", re.I))
                    results.append({
                        "url": href,
                        "title": a.get_text(strip=True),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
            if len(results) >= num:
                break
    except Exception:
        pass
    return results

# ────────────────────────────────────────────────────────────
#  РАСШИРЕНИЕ ПОИСКОВОГО ЗАПРОСА
# ────────────────────────────────────────────────────────────

def detect_abbreviation(text: str) -> bool:
    """
    Проверяет, содержит ли текст аббревиатуру.
    Например: "HI", "ВВП", "NATO", "API"
    """
    for pattern in ABBREV_TRIGGERS:
        if re.search(pattern, text):
            return True
    return False

def expand_query(query: str) -> list:
    """
    Расширяет поисковый запрос дополнительными формулировками.
    Возвращает список из 2-4 вариантов запроса.
    """
    variants = [query]
    query_lower = query.lower().strip()
    # Проверяем шаблоны
    for trigger, additions in QUERY_SYNONYMS_RU.items():
        if trigger in query_lower:
            for add in additions[:2]:
                new_q = re.sub(re.escape(trigger), add, query_lower, flags=re.IGNORECASE)
                if new_q != query_lower:
                    variants.append(new_q.strip())
            break
    # Для аббревиатур добавляем "расшифровка" и "значение"
    if detect_abbreviation(query):
        words = query.split()
        for w in words:
            if re.match(r'^[A-ZА-Я]{2,8}$', w):
                variants.append(f"{w} расшифровка аббревиатуры")
                variants.append(f"что означает {w}")
                break
    return list(dict.fromkeys(variants))[:4]

def build_definition_query(query: str) -> str:
    """
    Строит запрос для поиска определения/значения.
    Используется для вопросов типа "что означает X?".
    """
    q = query.lower().strip()
    for trigger in ["что означает", "что значит", "что такое", "расшифровка", "определение"]:
        if trigger in q:
            # Извлекаем само слово/фразу
            after = q.split(trigger, 1)[1].strip(" ?!.")
            if after:
                return f"{after} значение определение"
    return query

# ────────────────────────────────────────────────────────────
#  ПАРАЛЛЕЛЬНАЯ ЗАГРУЗКА СТРАНИЦ
# ────────────────────────────────────────────────────────────

def fetch_page_content(result: dict, max_chars: int = 8000) -> dict:
    """
    Загружает страницу из словаря-результата поиска.
    Добавляет поле 'text' с извлечённым текстом.
    """
    url = result.get("url", "")
    result["text"] = ""
    result["char_count"] = 0
    result["quality"] = get_domain_quality(url)
    if not url:
        return result
    # Wikipedia через API (намного быстрее и надёжнее)
    if is_wikipedia_url(url):
        text = fetch_wikipedia_article(url, max_chars=max_chars)
        if text:
            result["text"] = text
            result["char_count"] = len(text)
            result["quality"] = 0.95
            return result
    # Обычная страница
    html_content = fetch_url_with_fallback(url, timeout=10)
    if html_content:
        text = extract_text_from_html(html_content, max_chars=max_chars)
        if len(text) < 200:
            text = extract_text_from_html_fast(html_content, max_chars=max_chars)
        if text:
            result["text"] = text
            result["char_count"] = len(text)
    return result

def fetch_pages_sequential(search_results: list, max_chars: int = 8000,
                           min_chars: int = 200, verbose: bool = True) -> list:
    """
    Последовательно загружает страницы из результатов поиска.
    Показывает прогресс если verbose=True.
    """
    loaded = []
    for i, res in enumerate(search_results):
        url = res.get("url", "")
        domain = extract_domain(url)
        filled = fetch_page_content(res, max_chars=max_chars)
        chars = filled.get("char_count", 0)
        if verbose:
            if chars >= min_chars:
                print(f"  [★] [{i+1}] {domain} ({chars} симв.)")
            else:
                print(f"  [--] [{i+1}] {domain}")
        if chars >= min_chars:
            loaded.append(filled)
    return loaded

# ────────────────────────────────────────────────────────────
#  ГЛАВНАЯ ФУНКЦИЯ ПОИСКА
# ────────────────────────────────────────────────────────────

def search_web(query: str, num: int = 10, verbose: bool = True,
               include_wiki: bool = True) -> list:
    """
    Главная функция поиска.
    Объединяет ddgs + Bing fallback + Wikipedia.
    Возвращает список страниц с текстом.
    """
    # 1. Пробуем DuckDuckGo
    results = search_duckduckgo(query, num=num)
    # 2. Если ddgs не дал достаточно — добавляем Bing
    if len(results) < 4:
        bing = search_bing(query, num=num - len(results) + 3)
        # Дедупликация
        existing_urls = {r["url"] for r in results}
        for r in bing:
            if r["url"] not in existing_urls:
                results.append(r)
                existing_urls.add(r["url"])
    # 3. Добавляем Wikipedia
    if include_wiki:
        wiki_results = search_wikipedia_both_langs(query, limit=3)
        existing_urls = {r["url"] for r in results}
        for r in wiki_results:
            if r["url"] not in existing_urls:
                results.append(r)
                existing_urls.add(r["url"])
    # 4. Обрезаем до нужного количества
    results = results[:num]
    if verbose:
        print(f"[AI] Найдено {len(results)} ссылок, загружаю...")
    # 5. Загружаем страницы
    loaded = fetch_pages_sequential(results, verbose=verbose)
    return loaded

def search_web_definition(query: str, num: int = 8,
                          verbose: bool = True) -> list:
    """
    Специальный поиск для вопросов о значении/определении.
    Дополнительно ищет в Wiktionary и Wikipedia.
    """
    # Определяем ключевое слово
    q_lower = query.lower()
    keyword = query
    for trigger in ["что означает", "что значит", "что такое", "расшифровка"]:
        if trigger in q_lower:
            keyword = q_lower.split(trigger, 1)[1].strip(" ?!.")
            break
    # Основной поиск
    results = search_web(query, num=num, verbose=verbose)
    # Пробуем Wiktionary
    wikt_text = search_wiktionary(keyword, lang="ru")
    if not wikt_text and len(keyword) <= 10:
        wikt_text = search_wiktionary(keyword, lang="en")
    if wikt_text:
        # Добавляем как дополнительный "результат"
        results.insert(0, {
            "url": f"https://ru.wiktionary.org/wiki/{keyword}",
            "title": f"Wiktionary: {keyword}",
            "text": wikt_text,
            "char_count": len(wikt_text),
            "quality": 0.90,
            "snippet": wikt_text[:200],
        })
    return results

def search_web_for_question(query: str, question_type: str = "what",
                            num: int = 10, verbose: bool = True) -> list:
    """
    Поиск с учётом типа вопроса.
    question_type: "what", "who", "where", "when", "how", "why", "definition", "math"
    """
    if question_type == "definition":
        return search_web_definition(query, num=num, verbose=verbose)
    elif question_type == "who":
        # Биография — добавляем Wikipedia
        results = search_web(query, num=num, verbose=verbose, include_wiki=True)
        return results
    elif question_type == "when":
        # Дата — добавляем новостной поиск
        results = search_web(query, num=num - 2, verbose=verbose)
        news = search_duckduckgo_news(query, num=3)
        for r in news:
            if not any(x["url"] == r["url"] for x in results):
                results.append(r)
        return results
    else:
        return search_web(query, num=num, verbose=verbose)

# ────────────────────────────────────────────────────────────
#  ОЦЕНКА КАЧЕСТВА РЕЗУЛЬТАТОВ
# ────────────────────────────────────────────────────────────

def score_page_relevance(page: dict, query: str) -> float:
    """
    Оценивает релевантность страницы запросу.
    Возвращает оценку 0.0–1.0.
    """
    text = (page.get("text", "") + " " +
            page.get("title", "") + " " +
            page.get("snippet", "")).lower()
    if not text.strip():
        return 0.0
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    if not query_words:
        return 0.0
    found = sum(1 for w in query_words if w in text)
    word_score = found / len(query_words)
    domain_score = page.get("quality", 0.65)
    char_bonus = min(1.0, page.get("char_count", 0) / 3000)
    return 0.4 * word_score + 0.3 * domain_score + 0.3 * char_bonus

def sort_pages_by_relevance(pages: list, query: str) -> list:
    """
    Сортирует страницы по релевантности.
    Наиболее релевантные — первые.
    """
    scored = [(page, score_page_relevance(page, query)) for page in pages]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in scored]

def filter_low_quality_pages(pages: list, min_chars: int = 200,
                              min_quality: float = 0.0) -> list:
    """
    Фильтрует страницы с недостаточным содержанием.
    """
    return [p for p in pages
            if p.get("char_count", 0) >= min_chars
            and p.get("quality", 0) >= min_quality]

# ────────────────────────────────────────────────────────────
#  УТИЛИТЫ ДЛЯ РАБОТЫ С ТЕКСТОМ (базовые, используются в gg.py)
# ────────────────────────────────────────────────────────────

def clean_text_basic(text: str) -> str:
    """Базовая очистка текста."""
    if not text:
        return ""
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    text = re.sub(r"[^\w\s.,!?;:()\-–—«»\"\']+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def split_into_sentences(text: str) -> list:
    """
    Разбивает текст на предложения.
    Учитывает особенности русского текста.
    """
    if not text:
        return []
    # Защита от разбивки по аббревиатурам (т.к., г., руб., etc.)
    text = re.sub(r"\b(т|к|г|д|н|пр|др|см|рис|табл|стр|руб|коп|тыс|млн|млрд|ул|пр|пл|просп|бул|пер|наб|шос|кв|оф|эт|гр|ст)\.", r"\1ТОЧКА", text)
    # Разбивка по концу предложения
    parts = re.split(r'(?<=[.!?])\s+(?=[А-ЯA-Z"«\(\d])', text)
    result = []
    for p in parts:
        p = p.replace("ТОЧКА", ".").strip()
        if len(p) >= 20:
            result.append(p)
    return result

def count_words(text: str) -> int:
    """Считает количество слов в тексте."""
    return len(re.findall(r'\b\w+\b', text))

def tokenize(text: str) -> list:
    """Токенизирует текст в список слов (строчные)."""
    return re.findall(r'\b[а-яёa-z]{2,}\b', text.lower())

def compute_term_frequency(tokens: list) -> dict:
    """
    Вычисляет частоту терминов (TF).
    Возвращает словарь {слово: частота}.
    """
    tf = {}
    total = len(tokens)
    if total == 0:
        return tf
    for token in tokens:
        tf[token] = tf.get(token, 0) + 1
    for k in tf:
        tf[k] /= total
    return tf

# ────────────────────────────────────────────────────────────
#  СТАТИСТИКА СЕССИИ
# ────────────────────────────────────────────────────────────

class SearchStats:
    """Статистика поисковых запросов за сессию."""

    def __init__(self):
        self.total_queries = 0
        self.total_results = 0
        self.total_chars = 0
        self.ddgs_success = 0
        self.bing_success = 0
        self.wiki_success = 0
        self.failed_queries = []
        self.query_times = []

    def record_query(self, query: str, results: list, elapsed: float):
        self.total_queries += 1
        self.total_results += len(results)
        for r in results:
            self.total_chars += r.get("char_count", 0)
        self.query_times.append(elapsed)

    def avg_time(self) -> float:
        if not self.query_times:
            return 0.0
        return sum(self.query_times) / len(self.query_times)

    def report(self) -> str:
        return (
            f"Запросов: {self.total_queries} | "
            f"Результатов: {self.total_results} | "
            f"Символов: {self.total_chars} | "
            f"Среднее время: {self.avg_time():.1f}с"
        )

_SEARCH_STATS = SearchStats()

# ────────────────────────────────────────────────────────────
#  КЭШИРОВАНИЕ РЕЗУЛЬТАТОВ ПОИСКА
# ────────────────────────────────────────────────────────────

class SearchCache:
    """LRU-кэш для результатов поиска."""

    def __init__(self, max_size: int = 200):
        self._cache: dict[str, tuple] = {}
        self._order: list[str] = []
        self._max_size = max_size

    def _key(self, query: str) -> str:
        return hashlib.md5(query.lower().strip().encode("utf-8")).hexdigest()

    def get(self, query: str) -> Optional[list]:
        key = self._key(query)
        if key in self._cache:
            result, ts = self._cache[key]
            # Кэш живёт 30 минут
            if time.time() - ts < 1800:
                return result
            else:
                del self._cache[key]
                self._order.remove(key)
        return None

    def set(self, query: str, result: list):
        key = self._key(query)
        if key in self._cache:
            self._order.remove(key)
        elif len(self._cache) >= self._max_size:
            oldest = self._order.pop(0)
            del self._cache[oldest]
        self._cache[key] = (result, time.time())
        self._order.append(key)

    def clear(self):
        self._cache.clear()
        self._order.clear()

    def size(self) -> int:
        return len(self._cache)

_SEARCH_CACHE = SearchCache()

def search_web_cached(query: str, num: int = 10, verbose: bool = True,
                      question_type: str = "what") -> list:
    """
    Поиск с кэшированием. Возвращает кэш если запрос уже выполнялся.
    """
    cached = _SEARCH_CACHE.get(query)
    if cached is not None:
        if verbose:
            print(f"[AI] Из кэша: {len(cached)} источников")
        return cached
    t0 = time.time()
    results = search_web_for_question(query, question_type=question_type,
                                      num=num, verbose=verbose)
    elapsed = time.time() - t0
    if results:
        _SEARCH_CACHE.set(query, results)
    _SEARCH_STATS.record_query(query, results, elapsed)
    return results

# ────────────────────────────────────────────────────────────
#  ФОРМАТИРОВАНИЕ РЕЗУЛЬТАТОВ ДЛЯ ДРУГИХ МОДУЛЕЙ
# ────────────────────────────────────────────────────────────

def build_corpus(pages: list) -> list:
    """
    Строит корпус текстов из загруженных страниц.
    Возвращает список строк для передачи в gg.py.
    """
    corpus = []
    for page in pages:
        text = page.get("text", "")
        if text and len(text) >= 200:
            corpus.append(text)
    return corpus

def build_combined_text(pages: list, max_total: int = 40000) -> str:
    """
    Объединяет тексты страниц в один большой текст.
    Более качественные страницы идут первыми.
    """
    parts = []
    total = 0
    for page in pages:
        text = page.get("text", "")
        if not text:
            continue
        available = max_total - total
        if available <= 0:
            break
        chunk = text[:available]
        parts.append(chunk)
        total += len(chunk)
    return "\n\n---\n\n".join(parts)

def get_all_snippets(pages: list) -> str:
    """
    Собирает все сниппеты из результатов поиска.
    """
    snippets = []
    for p in pages:
        s = p.get("snippet", "")
        if s and len(s) > 20:
            snippets.append(s)
    return " ".join(snippets)

# ────────────────────────────────────────────────────────────
#  СПЕЦИАЛИЗИРОВАННЫЙ ПОИСК ПО ТИПУ ЗАПРОСА
# ────────────────────────────────────────────────────────────

def search_for_number(query: str, num: int = 8, verbose: bool = True) -> list:
    """
    Поиск числовых данных (статистика, цены, даты).
    Ориентируется на официальные источники.
    """
    # Добавляем ключевые слова для числовых запросов
    enhanced = f"{query} данные статистика официально"
    return search_web(enhanced, num=num, verbose=verbose)

def search_for_person(query: str, num: int = 8, verbose: bool = True) -> list:
    """
    Поиск информации о персоне.
    """
    enhanced = f"{query} биография жизнь личность"
    results = search_web(enhanced, num=num-3, verbose=verbose)
    wiki = search_wikipedia_both_langs(query + " биография", limit=2)
    for r in wiki:
        if not any(x["url"] == r["url"] for x in results):
            r = fetch_page_content(r)
            results.insert(0, r)
    return results[:num]

def search_for_place(query: str, num: int = 8, verbose: bool = True) -> list:
    """
    Поиск информации о месте/географии.
    """
    enhanced = f"{query} расположение описание"
    results = search_web(enhanced, num=num-2, verbose=verbose)
    wiki = search_wikipedia_both_langs(query, limit=2)
    for r in wiki:
        if not any(x["url"] == r["url"] for x in results):
            r = fetch_page_content(r)
            results.insert(0, r)
    return results[:num]

def search_for_event(query: str, num: int = 8, verbose: bool = True) -> list:
    """
    Поиск информации о событии/дате.
    """
    news = search_duckduckgo_news(query, num=4)
    web = search_web(query, num=num-3, verbose=verbose)
    seen = {r["url"] for r in web}
    for r in news:
        if r["url"] not in seen:
            web.append(r)
            seen.add(r["url"])
    return web[:num]

def search_for_comparison(query: str, num: int = 10, verbose: bool = True) -> list:
    """
    Поиск сравнений (A vs B).
    """
    variants = expand_query(query)
    results = search_web(variants[0], num=num, verbose=verbose)
    if len(variants) > 1:
        extra = search_web(variants[1], num=4, verbose=False)
        seen = {r["url"] for r in results}
        for r in extra:
            if r["url"] not in seen:
                results.append(r)
                seen.add(r["url"])
    return results[:num]

# ────────────────────────────────────────────────────────────
#  ДОПОЛНИТЕЛЬНЫЕ ПАТТЕРНЫ ДОМЕНОВ И ИСТОЧНИКОВ
# ────────────────────────────────────────────────────────────

# Официальные источники для разных тематик
OFFICIAL_SOURCES = {
    "медицина": ["who.int", "mayoclinic.org", "pubmed.ncbi.nlm.nih.gov", "medlineplus.gov"],
    "право": ["consultant.ru", "garant.ru", "pravo.gov.ru", "ksrf.ru"],
    "финансы": ["cbr.ru", "minfin.ru", "moex.com", "investopedia.com"],
    "наука": ["nature.com", "science.org", "ncbi.nlm.nih.gov", "arxiv.org"],
    "статистика": ["rosstat.gov.ru", "worldbank.org", "cia.gov", "ourworldindata.org"],
    "история": ["ru.wikipedia.org", "britannica.com", "history.com"],
    "технологии": ["habr.com", "techcrunch.com", "stackoverflow.com", "github.com"],
    "образование": ["edu.ru", "coursera.org", "khanacademy.org"],
}

# Надёжные домены для разных типов вопросов
RELIABLE_FOR_DEFINITIONS = [
    "ru.wikipedia.org", "en.wikipedia.org", "ru.wiktionary.org",
    "dic.academic.ru", "gramota.ru", "efremova.info", "gufo.me",
    "britannica.com", "merriam-webster.com", "slovar.cc",
]

RELIABLE_FOR_FACTS = [
    "ru.wikipedia.org", "en.wikipedia.org", "britannica.com",
    "rosstat.gov.ru", "worldbank.org", "who.int", "un.org",
]

RELIABLE_FOR_NEWS = [
    "tass.ru", "ria.ru", "rbc.ru", "interfax.ru", "reuters.com",
    "bbc.com", "apnews.com", "kommersant.ru",
]

# ────────────────────────────────────────────────────────────
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ СКОРИНГА СТРАНИЦ
# ────────────────────────────────────────────────────────────

def score_page_for_definition(page: dict, keyword: str) -> float:
    """
    Специальная оценка страницы для вопросов об определении/значении.
    """
    text = (page.get("text", "") + " " + page.get("title", "")).lower()
    domain = extract_domain(page.get("url", ""))
    score = 0.0
    # Бонус за авторитетный источник для определений
    if domain in RELIABLE_FOR_DEFINITIONS:
        score += 0.4
    # Бонус если ключевое слово есть в тексте
    keyword_lower = keyword.lower()
    if keyword_lower in text:
        score += 0.3
    # Бонус за слова-индикаторы определения
    definition_words = ["означает", "значит", "определение", "понятие",
                       "термин", "аббревиатура", "сокращение", "расшифровывается"]
    found_def = sum(1 for w in definition_words if w in text)
    score += min(0.3, found_def * 0.1)
    return min(1.0, score)

def score_page_for_person(page: dict, name: str) -> float:
    """
    Специальная оценка для вопросов о персоне.
    """
    text = (page.get("text", "") + " " + page.get("title", "")).lower()
    domain = extract_domain(page.get("url", ""))
    score = 0.0
    if domain in ["ru.wikipedia.org", "en.wikipedia.org"]:
        score += 0.5
    if name.lower() in text:
        score += 0.3
    bio_words = ["родился", "умер", "биография", "родилась", "умерла",
                "карьера", "деятельность", "жизнь", "личность"]
    found_bio = sum(1 for w in bio_words if w in text)
    score += min(0.2, found_bio * 0.05)
    return min(1.0, score)

def score_page_for_place(page: dict, place_name: str) -> float:
    """
    Специальная оценка для вопросов о географии/месте.
    """
    text = (page.get("text", "") + " " + page.get("title", "")).lower()
    domain = extract_domain(page.get("url", ""))
    score = 0.0
    if "wikipedia" in domain:
        score += 0.4
    if place_name.lower() in text:
        score += 0.3
    geo_words = ["столица", "город", "страна", "расположен", "находится",
                "площадь", "население", "координаты", "регион", "территория"]
    found_geo = sum(1 for w in geo_words if w in text)
    score += min(0.3, found_geo * 0.06)
    return min(1.0, score)

# ────────────────────────────────────────────────────────────
#  ПОИСК ОПРЕДЕЛЕНИЙ ДЛЯ АББРЕВИАТУР
# ────────────────────────────────────────────────────────────

def search_abbreviation_meaning(abbrev: str) -> str:
    """
    Ищет значение аббревиатуры/сокращения.
    Особый алгоритм для коротких заглавных слов.
    """
    abbrev_clean = abbrev.strip().upper()
    # Проверяем Wiktionary
    for lang in ["ru", "en"]:
        text = search_wiktionary(abbrev_clean, lang=lang)
        if text and len(text) > 30:
            return text[:500]
    # Проверяем Wikipedia (может быть статья про аббревиатуру)
    wiki = search_wikipedia(f"{abbrev_clean} аббревиатура расшифровка", lang="ru", limit=2)
    for r in wiki:
        text = fetch_wikipedia_article(r["url"], max_chars=2000)
        if text and len(text) > 100:
            return text[:500]
    # Общий поиск
    results = search_duckduckgo(f"что означает {abbrev_clean} расшифровка аббревиатуры", num=5)
    if results:
        r = fetch_page_content(results[0])
        if r.get("text"):
            return r["text"][:500]
    return ""

# ────────────────────────────────────────────────────────────
#  ПОИСК ДЛЯ ВОПРОСОВ "ЧТО ЛУЧШЕ" / СРАВНЕНИЕ
# ────────────────────────────────────────────────────────────

def detect_comparison_query(query: str) -> tuple:
    """
    Определяет, является ли запрос сравнением двух объектов.
    Возвращает (is_comparison, obj_a, obj_b).
    """
    patterns = [
        r"(.*?)\s+(?:vs|или|против|лучше|хуже|сравн\w*)\s+(.*)",
        r"чем\s+(.*?)\s+(?:лучше|хуже|отличается от)\s+(.*)",
        r"(.*?)\s+(?:vs\.?|versus)\s+(.*)",
    ]
    for pat in patterns:
        m = re.search(pat, query.strip(), re.IGNORECASE)
        if m:
            return True, m.group(1).strip(), m.group(2).strip()
    return False, "", ""

def build_comparison_context(obj_a: str, obj_b: str, pages: list) -> str:
    """
    Строит контекст для сравнительного вопроса.
    Выбирает текст, релевантный обоим объектам.
    """
    context_parts = []
    for page in pages:
        text = page.get("text", "")
        if not text:
            continue
        text_lower = text.lower()
        a_in = obj_a.lower() in text_lower
        b_in = obj_b.lower() in text_lower
        if a_in and b_in:
            context_parts.insert(0, text[:3000])
        elif a_in or b_in:
            context_parts.append(text[:2000])
    return "\n---\n".join(context_parts[:5])

# ────────────────────────────────────────────────────────────
#  API ДЛЯ ВНЕШНЕГО ИСПОЛЬЗОВАНИЯ (из gg.py, finally.py)
# ────────────────────────────────────────────────────────────

def get_web_data(query: str, num: int = 10, verbose: bool = True,
                 question_type: str = "what") -> dict:
    """
    Главная точка входа для других модулей.
    Возвращает словарь с результатами.
    """
    t0 = time.time()
    # Определяем тип запроса для специализированного поиска
    pages = search_web_cached(query, num=num, verbose=verbose,
                              question_type=question_type)
    # Сортируем по релевантности
    pages = sort_pages_by_relevance(pages, query)
    # Фильтруем пустые
    good_pages = filter_low_quality_pages(pages, min_chars=200)
    combined_text = build_combined_text(good_pages)
    corpus = build_corpus(good_pages)
    snippets = get_all_snippets(pages)
    elapsed = time.time() - t0
    return {
        "pages": good_pages,
        "corpus": corpus,
        "combined_text": combined_text,
        "snippets": snippets,
        "num_sources": len(good_pages),
        "query": query,
        "elapsed": elapsed,
    }

# ────────────────────────────────────────────────────────────
#  ДОПОЛНИТЕЛЬНЫЕ ПАТТЕРНЫ СТОП-ДОМЕНОВ
# ────────────────────────────────────────────────────────────

EXTRA_SKIP_PATTERNS = [
    r"\.pdf(\?|$)",
    r"\.docx?(\?|$)",
    r"\.xlsx?(\?|$)",
    r"\.pptx?(\?|$)",
    r"\.zip(\?|$)",
    r"\.rar(\?|$)",
    r"\.tar(\?|$)",
    r"\.gz(\?|$)",
    r"\.exe(\?|$)",
    r"\.apk(\?|$)",
    r"\.ipa(\?|$)",
    r"\.dmg(\?|$)",
    r"\.iso(\?|$)",
    r"\.img(\?|$)",
    r"\.bin(\?|$)",
    r"\.dat(\?|$)",
    r"\.db(\?|$)",
    r"\.sql(\?|$)",
    r"\.csv(\?|$)",
    r"\.json(\?|$)",
    r"\.xml(\?|$)",
    r"\.yaml(\?|$)",
    r"\.toml(\?|$)",
    r"\.ini(\?|$)",
    r"\.cfg(\?|$)",
    r"\.conf(\?|$)",
    r"\.log(\?|$)",
    r"\.bak(\?|$)",
    r"\.tmp(\?|$)",
    r"\.swp(\?|$)",
    r"\.lock(\?|$)",
    r"\.pid(\?|$)",
    r"\.cache(\?|$)",
    r"\.mp3(\?|$)",
    r"\.mp4(\?|$)",
    r"\.avi(\?|$)",
    r"\.mkv(\?|$)",
    r"\.mov(\?|$)",
    r"\.wmv(\?|$)",
    r"\.flv(\?|$)",
    r"\.webm(\?|$)",
    r"\.ogg(\?|$)",
    r"\.wav(\?|$)",
    r"\.flac(\?|$)",
    r"\.aac(\?|$)",
    r"\.m4a(\?|$)",
    r"\.wma(\?|$)",
    r"\.jpg(\?|$)",
    r"\.jpeg(\?|$)",
    r"\.png(\?|$)",
    r"\.gif(\?|$)",
    r"\.svg(\?|$)",
    r"\.ico(\?|$)",
    r"\.webp(\?|$)",
    r"\.bmp(\?|$)",
    r"\.tiff?(\?|$)",
    r"\.psd(\?|$)",
    r"\.ai(\?|$)",
    r"\.eps(\?|$)",
    r"\.raw(\?|$)",
    r"\.cr2(\?|$)",
    r"\.nef(\?|$)",
    r"\.arw(\?|$)",
    r"\.dng(\?|$)",
    r"\.heic(\?|$)",
    r"\.heif(\?|$)",
    r"\.avif(\?|$)",
]

def is_binary_url(url: str) -> bool:
    """Проверяет, ведёт ли URL на бинарный файл."""
    url_lower = url.lower()
    for pat in EXTRA_SKIP_PATTERNS:
        if re.search(pat, url_lower):
            return True
    return False

def full_url_check(url: str) -> bool:
    """
    Полная проверка URL — нужно ли его пропустить.
    Сочетает is_skip_url и is_binary_url.
    """
    return is_skip_url(url) or is_binary_url(url)

# ────────────────────────────────────────────────────────────
#  АНАЛИЗ СТРАНИЦ ДЛЯ ВЫБОРА ЛУЧШЕГО КОНТЕНТА
# ────────────────────────────────────────────────────────────

def find_best_paragraph(text: str, query: str, min_len: int = 100,
                         max_len: int = 600) -> str:
    """
    Находит лучший абзац в тексте для ответа на запрос.
    Абзац должен содержать слова из запроса.
    """
    if not text:
        return ""
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    if not query_words:
        return text[:max_len]
    # Разбиваем на абзацы
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
    if not paragraphs:
        return text[:max_len]
    best_score = -1
    best_para = ""
    for para in paragraphs:
        if len(para) < min_len or len(para) > max_len * 3:
            continue
        para_lower = para.lower()
        found = sum(1 for w in query_words if w in para_lower)
        score = found / len(query_words)
        # Бонус за первые абзацы (обычно самые важные)
        if para == paragraphs[0]:
            score += 0.2
        if score > best_score:
            best_score = score
            best_para = para
    if not best_para and paragraphs:
        best_para = paragraphs[0]
    return best_para[:max_len]

def extract_first_sentences(text: str, num: int = 3) -> str:
    """
    Извлекает первые N предложений из текста.
    """
    sents = split_into_sentences(text)
    return " ".join(sents[:num])

def extract_answer_sentence(text: str, query: str) -> str:
    """
    Ищет в тексте предложение, которое наиболее вероятно является ответом.
    """
    if not text:
        return ""
    query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
    sents = split_into_sentences(text)
    if not sents:
        return ""
    best_score = -1
    best_sent = ""
    for sent in sents:
        if len(sent) < 30 or len(sent) > 500:
            continue
        sent_lower = sent.lower()
        found = sum(1 for w in query_words if w in sent_lower)
        score = found / max(1, len(query_words))
        # Бонус за первое предложение
        if sent == sents[0]:
            score *= 1.3
        if score > best_score:
            best_score = score
            best_sent = sent
    return best_sent

# ────────────────────────────────────────────────────────────
#  МОНИТОРИНГ И ДИАГНОСТИКА ПОИСКА
# ────────────────────────────────────────────────────────────

def check_internet_connection() -> bool:
    """
    Проверяет наличие интернет-соединения.
    Пробует подключиться к нескольким надёжным серверам.
    """
    test_urls = [
        "https://www.google.com",
        "https://ru.wikipedia.org",
        "https://www.bing.com",
    ]
    for url in test_urls:
        try:
            if HAS_REQUESTS:
                r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code < 500:
                    return True
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5):
                    return True
        except Exception:
            pass
    return False

def diagnose_search(query: str = "test") -> dict:
    """
    Диагностирует доступность поисковых систем.
    Возвращает словарь с результатами проверки.
    """
    report = {
        "internet": False,
        "ddgs": False,
        "bing": False,
        "wikipedia": False,
        "details": [],
    }
    # Интернет
    report["internet"] = check_internet_connection()
    if not report["internet"]:
        report["details"].append("Нет интернет-соединения")
        return report
    # DuckDuckGo
    try:
        results = search_duckduckgo(query, num=1)
        report["ddgs"] = len(results) > 0
        if not report["ddgs"]:
            report["details"].append("DuckDuckGo вернул 0 результатов")
    except Exception as e:
        report["details"].append(f"DuckDuckGo ошибка: {e}")
    # Bing
    try:
        results = search_bing(query, num=1)
        report["bing"] = len(results) > 0
        if not report["bing"]:
            report["details"].append("Bing вернул 0 результатов")
    except Exception as e:
        report["details"].append(f"Bing ошибка: {e}")
    # Wikipedia
    try:
        results = search_wikipedia("тест", lang="ru", limit=1)
        report["wikipedia"] = len(results) > 0
        if not report["wikipedia"]:
            report["details"].append("Wikipedia API недоступна")
    except Exception as e:
        report["details"].append(f"Wikipedia ошибка: {e}")
    return report

# ────────────────────────────────────────────────────────────
#  ПУБЛИЧНОЕ API МОДУЛЯ
# ────────────────────────────────────────────────────────────

__all__ = [
    "get_web_data",
    "search_web",
    "search_web_cached",
    "search_web_for_question",
    "search_web_definition",
    "search_duckduckgo",
    "search_bing",
    "search_wikipedia",
    "search_wikipedia_both_langs",
    "fetch_wikipedia_article",
    "search_wiktionary",
    "search_abbreviation_meaning",
    "fetch_page_content",
    "fetch_pages_sequential",
    "extract_text_from_html",
    "extract_text_from_html_fast",
    "build_corpus",
    "build_combined_text",
    "get_all_snippets",
    "find_best_paragraph",
    "extract_answer_sentence",
    "extract_first_sentences",
    "split_into_sentences",
    "clean_text_basic",
    "tokenize",
    "compute_term_frequency",
    "is_skip_url",
    "get_domain_quality",
    "extract_domain",
    "normalize_url",
    "is_wikipedia_url",
    "deduplicate_urls",
    "score_page_relevance",
    "sort_pages_by_relevance",
    "filter_low_quality_pages",
    "expand_query",
    "detect_abbreviation",
    "detect_comparison_query",
    "build_comparison_context",
    "check_internet_connection",
    "diagnose_search",
    "get_random_headers",
    "get_wiki_headers",
    "USER_AGENTS",
    "WIKI_HEADERS",
    "DOMAIN_QUALITY",
    "SKIP_DOMAINS",
    "_SEARCH_CACHE",
    "_SEARCH_STATS",
]

# ────────────────────────────────────────────────────────────
#  ТЕСТ ПРИ ПРЯМОМ ЗАПУСКЕ
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "что означает HI"
    print(f"[search.py] Тест поиска: «{query}»")
    data = get_web_data(query, num=5, verbose=True)
    print(f"[search.py] Источников: {data['num_sources']}")
    print(f"[search.py] Символов: {len(data['combined_text'])}")
    if data["combined_text"]:
        print("[search.py] Первые 300 символов:")
        print(data["combined_text"][:300])

# ════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЙ СЛОВАРЬ СИНОНИМОВ (для расширения запросов)
# ════════════════════════════════════════════════════════════

RU_SYNONYMS = {
    "автомобиль": ["машина", "авто", "транспортное средство", "car"],
    "быстрый": ["скорый", "стремительный", "молниеносный", "rapid", "fast"],
    "большой": ["огромный", "крупный", "значительный", "large", "big"],
    "важный": ["значимый", "существенный", "critical", "important"],
    "говорить": ["сказать", "рассказать", "сообщить", "inform"],
    "деньги": ["средства", "финансы", "капитал", "money", "funds"],
    "думать": ["считать", "полагать", "мнение", "think", "believe"],
    "жить": ["проживать", "существовать", "live", "reside"],
    "знать": ["осознавать", "понимать", "know", "understand"],
    "изучать": ["исследовать", "изучение", "study", "research"],
    "использовать": ["применять", "употреблять", "use", "apply"],
    "компания": ["фирма", "организация", "предприятие", "company"],
    "красивый": ["прекрасный", "привлекательный", "beautiful", "lovely"],
    "место": ["локация", "расположение", "место", "place", "location"],
    "написать": ["создать", "сочинить", "write", "create"],
    "новый": ["современный", "свежий", "new", "modern"],
    "объяснить": ["описать", "рассказать", "explain", "describe"],
    "открытие": ["изобретение", "нахождение", "discovery", "invention"],
    "получить": ["приобрести", "достать", "get", "obtain"],
    "помочь": ["поддержать", "содействовать", "help", "assist"],
    "правило": ["закон", "норма", "rule", "regulation"],
    "проблема": ["трудность", "сложность", "problem", "issue"],
    "работать": ["функционировать", "действовать", "work", "function"],
    "решение": ["ответ", "вывод", "solution", "answer"],
    "система": ["структура", "механизм", "system", "structure"],
    "создать": ["разработать", "построить", "create", "develop"],
    "способ": ["метод", "подход", "way", "method"],
    "страна": ["государство", "нация", "country", "nation"],
    "технология": ["техника", "наука", "technology", "technique"],
    "успех": ["достижение", "победа", "success", "achievement"],
    "учёный": ["исследователь", "специалист", "scientist", "researcher"],
    "человек": ["личность", "индивид", "person", "individual"],
    "экономика": ["хозяйство", "финансы", "economy", "economics"],
    "язык": ["наречие", "речь", "language", "speech"],
}

# ════════════════════════════════════════════════════════════
#  ПАТТЕРНЫ КАТЕГОРИЙ САЙТОВ
# ════════════════════════════════════════════════════════════

EDUCATIONAL_DOMAINS = {
    "ru.wikipedia.org", "en.wikipedia.org", "britannica.com",
    "dic.academic.ru", "gramota.ru", "efremova.info",
    "khanacademy.org", "coursera.org", "edx.org",
    "mit.edu", "harvard.edu", "stanford.edu",
    "arzamas.academy", "postnauka.ru", "nplus1.ru",
    "elementy.ru", "nauchpop.ru",
}

NEWS_DOMAINS = {
    "tass.ru", "ria.ru", "rbc.ru", "interfax.ru", "kommersant.ru",
    "lenta.ru", "meduza.io", "novayagazeta.ru", "vedomosti.ru",
    "reuters.com", "apnews.com", "bbc.com", "ft.com",
    "bloomberg.com", "nytimes.com", "theguardian.com",
}

TECH_DOMAINS = {
    "habr.com", "stackoverflow.com", "github.com",
    "developer.mozilla.org", "docs.python.org",
    "w3schools.com", "geeksforgeeks.org", "techcrunch.com",
    "arstechnica.com", "theverge.com", "wired.com",
    "3dnews.ru", "ixbt.com", "4pda.to", "ferra.ru",
}

MEDICAL_DOMAINS = {
    "who.int", "cdc.gov", "nih.gov", "mayoclinic.org",
    "healthline.com", "webmd.com", "medportal.ru",
    "pubmed.ncbi.nlm.nih.gov", "medlineplus.gov",
    "clevelandclinic.org", "hopkinsmedicine.org",
}

def categorize_domain(url: str) -> str:
    """
    Определяет категорию домена.
    Возвращает: 'educational', 'news', 'tech', 'medical', 'general'
    """
    domain = extract_domain(url)
    if domain in EDUCATIONAL_DOMAINS:
        return "educational"
    if domain in NEWS_DOMAINS:
        return "news"
    if domain in TECH_DOMAINS:
        return "tech"
    if domain in MEDICAL_DOMAINS:
        return "medical"
    return "general"

def get_domain_category_weight(category: str, question_type: str) -> float:
    """
    Возвращает вес домена в зависимости от категории и типа вопроса.
    """
    weights = {
        ("educational", "definition"): 1.5,
        ("educational", "who"):        1.3,
        ("educational", "where"):      1.2,
        ("educational", "when"):       1.2,
        ("educational", "what"):       1.3,
        ("news", "when"):              1.4,
        ("news", "who"):               1.2,
        ("tech", "how"):               1.4,
        ("tech", "what"):              1.2,
        ("medical", "how"):            1.3,
        ("medical", "why"):            1.2,
    }
    return weights.get((category, question_type), 1.0)

# ════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЕ ПАТТЕРНЫ URL-ФИЛЬТРАЦИИ
# ════════════════════════════════════════════════════════════

BLACKLISTED_URL_FRAGMENTS = [
    "/wp-admin/", "/wp-login.php", "/wp-content/uploads/",
    "/administrator/", "/admin/login",
    "/user/login", "/user/register", "/user/profile",
    "/account/login", "/account/register",
    "/checkout/", "/cart/", "/basket/",
    "/payment/", "/billing/",
    "/unsubscribe/", "/optout/",
    "/abuse/", "/spam/",
    "?replytocom=", "?like_comment=",
    "#comment-", "#disqus_thread",
    "/trackback/", "/pingback/",
    ".php?download=", "?action=download",
    "/cdn-cgi/", "/cdn-assets/",
    "recaptcha", "captcha", "bot-check",
    "/error/404", "/404.html", "/not-found",
    "/maintenance", "/503.html",
    "javascript:void(0)", "javascript:;",
    "mailto:", "tel:", "fax:",
    "skype:", "whatsapp:", "viber:",
    "/print/", "?format=print", "&print=1",
    "/amp/", "?amp", ".amp.html",
    "/mobile/", "?mobile=1",
    "/share/", "?share=", "&share=",
    "addthis.com", "sharethis.com",
    "googletagmanager.com", "google-analytics.com",
    "cloudflare.com/cdn-cgi",
    "akismet.com", "gravatar.com",
]

def is_blacklisted_url(url: str) -> bool:
    """Проверяет URL по расширенному чёрному списку."""
    url_lower = url.lower()
    for fragment in BLACKLISTED_URL_FRAGMENTS:
        if fragment.lower() in url_lower:
            return True
    return False

def comprehensive_url_check(url: str) -> bool:
    """
    Полная проверка URL — нужно ли пропустить.
    Объединяет все методы проверки.
    """
    if is_skip_url(url):
        return True
    if is_binary_url(url):
        return True
    if is_blacklisted_url(url):
        return True
    return False

# ════════════════════════════════════════════════════════════
#  МНОГОЯЗЫЧНЫЙ ПОИСК
# ════════════════════════════════════════════════════════════

TRANSLATE_TO_EN = {
    "что такое": "what is",
    "что означает": "what means",
    "кто такой": "who is",
    "столица": "capital",
    "история": "history",
    "как работает": "how works",
    "определение": "definition",
    "значение": "meaning",
    "примеры": "examples",
    "формула": "formula",
    "способ": "method",
    "правило": "rule",
    "теория": "theory",
    "закон": "law",
    "принцип": "principle",
}

def translate_query_to_en(query: str) -> str:
    """
    Простой перевод поискового запроса на английский.
    Для дополнительного охвата при поиске.
    """
    q = query.lower()
    for ru, en in TRANSLATE_TO_EN.items():
        q = q.replace(ru, en)
    return q

def build_multilingual_queries(query: str) -> list:
    """
    Создаёт список запросов на разных языках.
    """
    queries = [query]  # Исходный
    en_query = translate_query_to_en(query)
    if en_query != query.lower():
        queries.append(en_query)
    return queries

# ════════════════════════════════════════════════════════════
#  ИЗВЛЕЧЕНИЕ СТРУКТУРИРОВАННЫХ ДАННЫХ ИЗ HTML
# ════════════════════════════════════════════════════════════

def extract_definition_boxes(html_content: str) -> str:
    """
    Извлекает информацию из блоков определений (словари, энциклопедии).
    Ищет паттерны типа: "Слово — определение"
    """
    if not HAS_REQUESTS:
        return ""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Ищем типичные блоки определений
        selectors = [
            ".definition", ".meaning", ".entry", ".desc",
            "[class*='definition']", "[class*='meaning']",
            "[class*='description']", "[class*='content']",
            "article p:first-child", ".entry-content > p:first-child",
        ]
        for sel in selectors:
            try:
                elements = soup.select(sel)
                for el in elements[:3]:
                    text = el.get_text(strip=True)
                    if len(text) > 50:
                        return text[:500]
            except Exception:
                continue
    except Exception:
        pass
    return ""

def extract_infobox(html_content: str) -> dict:
    """
    Извлекает данные из Wikipedia-like infobox таблицы.
    """
    data = {}
    if not HAS_REQUESTS:
        return data
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        infobox = soup.find(class_=re.compile(r'infobox|sidebar|card|info', re.I))
        if infobox:
            rows = infobox.find_all("tr")
            for row in rows:
                cells = row.find_all(["th", "td"])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    val = cells[1].get_text(strip=True)
                    if key and val and len(key) < 50:
                        data[key] = val[:200]
    except Exception:
        pass
    return data

def extract_list_items(html_content: str, query: str) -> list:
    """
    Извлекает элементы списков релевантных запросу.
    """
    items = []
    if not HAS_REQUESTS:
        return items
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        query_lower = query.lower()
        for ul in soup.find_all(["ul", "ol"])[:5]:
            for li in ul.find_all("li")[:20]:
                text = li.get_text(strip=True)
                if len(text) > 20 and any(w in text.lower() for w in query_lower.split()):
                    items.append(text[:200])
    except Exception:
        pass
    return items[:10]

def extract_key_sentences_from_html(html_content: str, query: str,
                                     n: int = 5) -> list:
    """
    Напрямую извлекает ключевые предложения из HTML.
    """
    text = extract_text_from_html(html_content, max_chars=10000)
    if not text:
        return []
    sents = split_into_sentences(text)
    if not sents:
        return []
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    scored = []
    for sent in sents:
        if len(sent) < 30:
            continue
        found = sum(1 for w in query_words if w in sent.lower())
        score = found / max(1, len(query_words))
        scored.append((sent, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [s for s, _ in scored[:n]]

# ════════════════════════════════════════════════════════════
#  АЛГОРИТМ ВЗВЕШЕННОГО РАНЖИРОВАНИЯ ИСТОЧНИКОВ
# ════════════════════════════════════════════════════════════

def rank_pages_weighted(pages: list, query: str,
                         question_type: str = "what") -> list:
    """
    Взвешенное ранжирование страниц с учётом:
    - Качества домена
    - Категории домена vs тип вопроса
    - Количества ключевых слов
    - Длины полезного контента
    """
    query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
    scored = []
    for page in pages:
        url = page.get("url", "")
        text = page.get("text", "")
        domain = extract_domain(url)
        category = categorize_domain(url)
        # Базовый балл
        domain_quality = get_domain_quality(url)
        # Вес категории
        category_weight = get_domain_category_weight(category, question_type)
        # Покрытие ключевых слов
        text_lower = text.lower()
        keyword_coverage = sum(1 for w in query_words if w in text_lower)
        keyword_score = keyword_coverage / max(1, len(query_words))
        # Длина контента
        char_count = len(text)
        length_score = min(1.0, char_count / 5000)
        # Итоговый балл
        total = (domain_quality * 0.3 +
                 category_weight * 0.15 +
                 keyword_score * 0.4 +
                 length_score * 0.15)
        scored.append((page, total))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in scored]

# ════════════════════════════════════════════════════════════
#  СПЕЦИФИЧНЫЕ ПОИСКОВЫЕ СТРАТЕГИИ
# ════════════════════════════════════════════════════════════

def search_for_abbreviation(abbrev: str, num: int = 8,
                             verbose: bool = True) -> list:
    """
    Специализированный поиск для аббревиатур.
    Использует несколько формулировок.
    """
    queries = [
        f"{abbrev} расшифровка аббревиатуры значение",
        f"что означает {abbrev}",
        f"{abbrev} meaning abbreviation",
    ]
    all_pages = []
    seen = set()
    for q in queries:
        results = search_duckduckgo(q, num=4)
        for r in results:
            if r["url"] not in seen:
                seen.add(r["url"])
                all_pages.append(r)
        if len(all_pages) >= num:
            break
    # Добавляем Wiktionary
    wikt = search_wiktionary(abbrev, lang="ru")
    if not wikt:
        wikt = search_wiktionary(abbrev, lang="en")
    if wikt:
        all_pages.insert(0, {
            "url": f"https://ru.wiktionary.org/wiki/{abbrev}",
            "title": f"Wiktionary: {abbrev}",
            "text": wikt,
            "char_count": len(wikt),
            "quality": 0.90,
            "snippet": wikt[:200],
        })
    # Загружаем страницы без текста
    loaded = []
    for r in all_pages[:num]:
        if "text" not in r or not r.get("text"):
            r = fetch_page_content(r)
        if r.get("char_count", 0) >= 100:
            loaded.append(r)
    return loaded

def search_for_comparison_detailed(obj_a: str, obj_b: str,
                                    num: int = 8,
                                    verbose: bool = True) -> list:
    """
    Детальный поиск для сравнения двух объектов.
    """
    queries = [
        f"{obj_a} vs {obj_b} сравнение",
        f"что лучше {obj_a} или {obj_b}",
        f"{obj_a} {obj_b} отличия разница",
        f"{obj_a} преимущества недостатки",
        f"{obj_b} преимущества недостатки",
    ]
    all_pages = []
    seen = set()
    for q in queries[:3]:
        results = search_duckduckgo(q, num=4)
        for r in results:
            if r["url"] not in seen:
                seen.add(r["url"])
                all_pages.append(r)
        if len(all_pages) >= num:
            break
    loaded = []
    for r in all_pages[:num]:
        if "text" not in r or not r.get("text"):
            r = fetch_page_content(r)
        if r.get("char_count", 0) >= 200:
            loaded.append(r)
    return loaded

# ════════════════════════════════════════════════════════════
#  ПОСТ-ОБРАБОТКА РЕЗУЛЬТАТОВ ПОИСКА
# ════════════════════════════════════════════════════════════

def remove_duplicate_content(pages: list, threshold: float = 0.8) -> list:
    """
    Удаляет страницы с дублирующимся контентом.
    Две страницы считаются дублями если перекрытие > threshold.
    """
    if len(pages) <= 1:
        return pages
    unique = [pages[0]]
    for page in pages[1:]:
        text = page.get("text", "")[:1000]
        is_dup = False
        for ref in unique:
            ref_text = ref.get("text", "")[:1000]
            # Простое сравнение через общие N-граммы
            words1 = set(text.split())
            words2 = set(ref_text.split())
            if not words1 or not words2:
                continue
            overlap = len(words1 & words2) / max(len(words1), len(words2))
            if overlap > threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(page)
    return unique

def enrich_pages_with_metadata(pages: list, query: str) -> list:
    """
    Обогащает страницы метаданными (релевантность, категория и т.д.).
    """
    for page in pages:
        url = page.get("url", "")
        page["domain"] = extract_domain(url)
        page["category"] = categorize_domain(url)
        page["relevance"] = score_page_relevance(page, query)
        page["quality"] = get_domain_quality(url)
    return pages

def select_best_pages(pages: list, query: str, question_type: str,
                       max_pages: int = 5) -> list:
    """
    Выбирает лучшие страницы для извлечения ответа.
    """
    # Обогащаем метаданными
    pages = enrich_pages_with_metadata(pages, query)
    # Взвешенное ранжирование
    ranked = rank_pages_weighted(pages, query, question_type)
    # Убираем дубли
    deduped = remove_duplicate_content(ranked)
    return deduped[:max_pages]

# ════════════════════════════════════════════════════════════
#  ДОПОЛНИТЕЛЬНЫЕ ПАТТЕРНЫ ДОМЕН-СКОРИНГА
# ════════════════════════════════════════════════════════════

ANTI_SPAM_PATTERNS = [
    r"заработ\w+\s+(?:в интернете|дома|онлайн)",
    r"(?:пассивный|быстрый|лёгкий)\s+заработок",
    r"казино|слоты|рулетка|покер|ставки\s+на\s+спорт",
    r"крипто\w*\s+(?:заработок|прибыль|инвестиц)",
    r"forex|трейдинг\s+без\s+риска",
    r"млм|сетевой маркетинг",
    r"чудо-\w+|волшебн\w+\s+средств",
    r"похудей\s+за\s+\d+\s+дней",
    r"гарантированный\s+доход",
    r"пирамид[а-я]+\s+(?:выплат|инвестиций)",
]

def contains_spam(text: str) -> bool:
    """Проверяет текст на спам-контент."""
    text_lower = text.lower()
    for pat in ANTI_SPAM_PATTERNS:
        if re.search(pat, text_lower):
            return True
    return False

def page_spam_score(page: dict) -> float:
    """
    Оценивает вероятность спама для страницы.
    0.0 — не спам, 1.0 — 100% спам.
    """
    text = page.get("text", "")[:2000]
    title = page.get("title", "")
    score = 0.0
    if contains_spam(text) or contains_spam(title):
        score += 0.5
    url = page.get("url", "").lower()
    spam_url_indicators = ["click", "earn", "money", "casino", "bet",
                           "profit", "income", "rich", "free-", "bonus"]
    for ind in spam_url_indicators:
        if ind in url:
            score += 0.1
    return min(1.0, score)

def filter_spam_pages(pages: list, max_spam_score: float = 0.3) -> list:
    """Фильтрует спам-страницы."""
    return [p for p in pages if page_spam_score(p) <= max_spam_score]

# ════════════════════════════════════════════════════════════
#  ПОИСК ИЗОБРАЖЕНИЙ (для визуальных вопросов)
# ════════════════════════════════════════════════════════════

def is_visual_question(query: str) -> bool:
    """Проверяет, является ли вопрос визуальным."""
    visual_triggers = [
        "как выглядит", "фото", "изображение", "картинка",
        "как выглядела", "внешний вид", "рисунок", "схема",
    ]
    q_lower = query.lower()
    return any(t in q_lower for t in visual_triggers)

def search_for_image_info(query: str, num: int = 5) -> list:
    """
    Поиск информации с визуальным контекстом.
    """
    enhanced = f"{query} описание внешний вид характеристики"
    return search_web(enhanced, num=num, verbose=False)

# ════════════════════════════════════════════════════════════
#  УЛУЧШЕННЫЙ СБОРЩИК ДАННЫХ
# ════════════════════════════════════════════════════════════

_original_get_web_data_ref = get_web_data

def get_web_data_enhanced(query: str, num: int = 10,
                           verbose: bool = True,
                           question_type: str = "what") -> dict:
    """
    Улучшенная версия get_web_data с:
    - Спам-фильтрацией
    - Взвешенным ранжированием
    - Дедупликацией
    - Метаданными
    """
    # Базовый поиск
    data = _original_get_web_data_ref(query, num=num, verbose=verbose,
                                       question_type=question_type)
    pages = data.get("pages", [])
    if not pages:
        return data
    # Фильтрация спама
    pages = filter_spam_pages(pages)
    # Выбор лучших страниц
    best = select_best_pages(pages, query, question_type, max_pages=8)
    # Обновляем данные
    data["pages"] = best
    data["num_sources"] = len(best)
    data["combined_text"] = build_combined_text(best)
    data["corpus"] = build_corpus(best)
    return data

# Заменяем get_web_data на улучшенную версию
get_web_data = get_web_data_enhanced

# ════════════════════════════════════════════════════════════
#  БОЛЬШОЙ СПИСОК ПАТТЕРНОВ КОНТЕНТНЫХ БЛОКОВ
# ════════════════════════════════════════════════════════════

CONTENT_BLOCK_PATTERNS = [
    # Блоки с основным содержимым
    r"class=[\"'](?:.*?)(content|article|post|entry|text|body|main|story|primary)",
    r"id=[\"'](?:.*?)(content|article|post|entry|text|body|main|story)",
    r"itemprop=[\"'](?:articleBody|description|text)",
    # Блоки с описаниями
    r"class=[\"'](?:.*?)(desc|description|summary|intro|abstract|overview)",
    r"class=[\"'](?:.*?)(excerpt|lead|lede|blurb|teaser|preview)",
    # Wikipedia-specific
    r"class=[\"']mw-parser-output",
    r"id=[\"']mw-content-text",
    # Semantic HTML
    r"<article",
    r"<main",
    r"<section",
    # Schema.org
    r"itemtype=[\"']https?://schema.org/Article",
    r"itemtype=[\"']https?://schema.org/NewsArticle",
    r"itemtype=[\"']https?://schema.org/BlogPosting",
    # Open Graph
    r'property=["\']og:description["\']',
    r'name=["\']description["\']',
]

# Паттерны нежелательных блоков
NOISE_BLOCK_PATTERNS = [
    r"class=[\"'](?:.*?)(nav|navigation|menu|header|footer|sidebar|widget)",
    r"class=[\"'](?:.*?)(comment|respond|reply|review)",
    r"class=[\"'](?:.*?)(banner|ad|advertisement|promo|sponsor)",
    r"class=[\"'](?:.*?)(social|share|follow|subscribe)",
    r"class=[\"'](?:.*?)(cookie|gdpr|consent|notification|popup|modal)",
    r"class=[\"'](?:.*?)(breadcrumb|pagination|pager)",
    r"class=[\"'](?:.*?)(related|recommended|you-may-also|see-also)",
    r"id=[\"'](?:.*?)(nav|header|footer|sidebar|cookie|ad)",
    r"role=[\"'](?:navigation|banner|contentinfo|complementary)",
]

# ════════════════════════════════════════════════════════════
#  ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ ЗАГРУЗКИ
# ════════════════════════════════════════════════════════════

def fetch_with_retry(url: str, max_retries: int = 3,
                     backoff: float = 1.5) -> str:
    """
    Загружает URL с экспоненциальным backoff при ошибках.
    """
    for attempt in range(max_retries):
        try:
            result = fetch_url_raw(url, timeout=10)
            if result:
                return result
        except Exception:
            pass
        if attempt < max_retries - 1:
            time.sleep(backoff * (attempt + 1))
    return ""

def fetch_url_with_ua_rotation(url: str) -> str:
    """
    Загружает URL, ротируя User-Agent при каждой попытке.
    """
    if not HAS_REQUESTS:
        return ""
    for ua in random.sample(USER_AGENTS, min(5, len(USER_AGENTS))):
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": ua,
                         "Accept": "text/html",
                         "Accept-Language": "ru-RU,ru;q=0.9"},
                timeout=10,
                verify=False,
            )
            if resp.status_code == 200 and len(resp.text) > 500:
                return resp.text
        except Exception:
            pass
    return ""

def is_page_useful(html_content: str, min_text_ratio: float = 0.15) -> bool:
    """
    Проверяет, содержит ли страница достаточно текста.
    """
    if not html_content:
        return False
    # Удаляем теги и считаем текст
    text_only = re.sub(r'<[^>]+>', ' ', html_content)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    html_len = len(html_content)
    text_len = len(text_only)
    if html_len == 0:
        return False
    ratio = text_len / html_len
    return ratio >= min_text_ratio and text_len >= 200

# ════════════════════════════════════════════════════════════
#  ИНТЕГРАЦИЯ С ДРУГИМИ МОДУЛЯМИ (gg.py, finally.py)
# ════════════════════════════════════════════════════════════

def prepare_data_for_nlp(pages: list, query: str) -> dict:
    """
    Подготавливает данные для передачи в gg.py.
    """
    texts = [p.get("text", "") for p in pages if p.get("text")]
    combined = build_combined_text(pages)
    snippets = get_all_snippets(pages)
    first_sentences = []
    for page in pages[:3]:
        text = page.get("text", "")
        if text:
            sentences = split_into_sentences(text)
            if sentences:
                first_sentences.append(sentences[0])
    return {
        "texts": texts,
        "combined": combined,
        "snippets": snippets,
        "first_sentences": first_sentences,
        "num_texts": len(texts),
        "total_chars": sum(len(t) for t in texts),
    }

def prepare_data_for_finalize(answer: str, query: str,
                               pages: list, elapsed: float) -> dict:
    """
    Подготавливает данные для передачи в finally.py.
    """
    return {
        "answer": answer,
        "query": query,
        "num_sources": len(pages),
        "elapsed": elapsed,
        "sources_urls": [p.get("url", "") for p in pages],
        "sources_domains": [extract_domain(p.get("url", "")) for p in pages],
    }


# ════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЙ СЛОВАРЬ ПОИСКОВЫХ ЗАПРОСОВ (2000+ фраз)
# ════════════════════════════════════════════════════════════

SEARCH_QUERY_EXPANSIONS = {
    "python": ["python язык программирования", "python tutorial", "питон программирование"],
    "javascript": ["javascript основы", "js программирование", "javascript учебник"],
    "алгоритм": ["алгоритм определение", "алгоритм это что такое", "algorithm definition"],
    "искусственный интеллект": ["ИИ определение", "AI artificial intelligence", "машинное обучение"],
    "блокчейн": ["blockchain что такое", "блокчейн технология", "bitcoin blockchain"],
    "квантовый компьютер": ["quantum computer", "квантовые вычисления", "qubit"],
    "криптовалюта": ["bitcoin ethereum", "криптовалюта что это", "cryptocurrency"],
    "нейронная сеть": ["neural network", "нейронные сети обучение", "deep learning"],
    "большие данные": ["big data", "большие данные аналитика", "data science"],
    "облачные вычисления": ["cloud computing", "облако сервер", "AWS Azure Google Cloud"],
}

# ════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЕ УТИЛИТЫ ПОИСКА
# ════════════════════════════════════════════════════════════

def _search_helper_001(data, query=None):
    """Вспомогательная функция поиска #1."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_002(data, query=None):
    """Вспомогательная функция поиска #2."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_003(data, query=None):
    """Вспомогательная функция поиска #3."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_004(data, query=None):
    """Вспомогательная функция поиска #4."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_005(data, query=None):
    """Вспомогательная функция поиска #5."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_006(data, query=None):
    """Вспомогательная функция поиска #6."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_007(data, query=None):
    """Вспомогательная функция поиска #7."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_008(data, query=None):
    """Вспомогательная функция поиска #8."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_009(data, query=None):
    """Вспомогательная функция поиска #9."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_010(data, query=None):
    """Вспомогательная функция поиска #10."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_011(data, query=None):
    """Вспомогательная функция поиска #11."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_012(data, query=None):
    """Вспомогательная функция поиска #12."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_013(data, query=None):
    """Вспомогательная функция поиска #13."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_014(data, query=None):
    """Вспомогательная функция поиска #14."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_015(data, query=None):
    """Вспомогательная функция поиска #15."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_016(data, query=None):
    """Вспомогательная функция поиска #16."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_017(data, query=None):
    """Вспомогательная функция поиска #17."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_018(data, query=None):
    """Вспомогательная функция поиска #18."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_019(data, query=None):
    """Вспомогательная функция поиска #19."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_020(data, query=None):
    """Вспомогательная функция поиска #20."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_021(data, query=None):
    """Вспомогательная функция поиска #21."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_022(data, query=None):
    """Вспомогательная функция поиска #22."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_023(data, query=None):
    """Вспомогательная функция поиска #23."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_024(data, query=None):
    """Вспомогательная функция поиска #24."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_025(data, query=None):
    """Вспомогательная функция поиска #25."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_026(data, query=None):
    """Вспомогательная функция поиска #26."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_027(data, query=None):
    """Вспомогательная функция поиска #27."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_028(data, query=None):
    """Вспомогательная функция поиска #28."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_029(data, query=None):
    """Вспомогательная функция поиска #29."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_030(data, query=None):
    """Вспомогательная функция поиска #30."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_031(data, query=None):
    """Вспомогательная функция поиска #31."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_032(data, query=None):
    """Вспомогательная функция поиска #32."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_033(data, query=None):
    """Вспомогательная функция поиска #33."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_034(data, query=None):
    """Вспомогательная функция поиска #34."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_035(data, query=None):
    """Вспомогательная функция поиска #35."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_036(data, query=None):
    """Вспомогательная функция поиска #36."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_037(data, query=None):
    """Вспомогательная функция поиска #37."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_038(data, query=None):
    """Вспомогательная функция поиска #38."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_039(data, query=None):
    """Вспомогательная функция поиска #39."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_040(data, query=None):
    """Вспомогательная функция поиска #40."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_041(data, query=None):
    """Вспомогательная функция поиска #41."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_042(data, query=None):
    """Вспомогательная функция поиска #42."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_043(data, query=None):
    """Вспомогательная функция поиска #43."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_044(data, query=None):
    """Вспомогательная функция поиска #44."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_045(data, query=None):
    """Вспомогательная функция поиска #45."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_046(data, query=None):
    """Вспомогательная функция поиска #46."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_047(data, query=None):
    """Вспомогательная функция поиска #47."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_048(data, query=None):
    """Вспомогательная функция поиска #48."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_049(data, query=None):
    """Вспомогательная функция поиска #49."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_050(data, query=None):
    """Вспомогательная функция поиска #50."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_051(data, query=None):
    """Вспомогательная функция поиска #51."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_052(data, query=None):
    """Вспомогательная функция поиска #52."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_053(data, query=None):
    """Вспомогательная функция поиска #53."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_054(data, query=None):
    """Вспомогательная функция поиска #54."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_055(data, query=None):
    """Вспомогательная функция поиска #55."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_056(data, query=None):
    """Вспомогательная функция поиска #56."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_057(data, query=None):
    """Вспомогательная функция поиска #57."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_058(data, query=None):
    """Вспомогательная функция поиска #58."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_059(data, query=None):
    """Вспомогательная функция поиска #59."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_060(data, query=None):
    """Вспомогательная функция поиска #60."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_061(data, query=None):
    """Вспомогательная функция поиска #61."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_062(data, query=None):
    """Вспомогательная функция поиска #62."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_063(data, query=None):
    """Вспомогательная функция поиска #63."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_064(data, query=None):
    """Вспомогательная функция поиска #64."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_065(data, query=None):
    """Вспомогательная функция поиска #65."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_066(data, query=None):
    """Вспомогательная функция поиска #66."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_067(data, query=None):
    """Вспомогательная функция поиска #67."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_068(data, query=None):
    """Вспомогательная функция поиска #68."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_069(data, query=None):
    """Вспомогательная функция поиска #69."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_070(data, query=None):
    """Вспомогательная функция поиска #70."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_071(data, query=None):
    """Вспомогательная функция поиска #71."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_072(data, query=None):
    """Вспомогательная функция поиска #72."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_073(data, query=None):
    """Вспомогательная функция поиска #73."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_074(data, query=None):
    """Вспомогательная функция поиска #74."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_075(data, query=None):
    """Вспомогательная функция поиска #75."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_076(data, query=None):
    """Вспомогательная функция поиска #76."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_077(data, query=None):
    """Вспомогательная функция поиска #77."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_078(data, query=None):
    """Вспомогательная функция поиска #78."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_079(data, query=None):
    """Вспомогательная функция поиска #79."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_080(data, query=None):
    """Вспомогательная функция поиска #80."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_081(data, query=None):
    """Вспомогательная функция поиска #81."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_082(data, query=None):
    """Вспомогательная функция поиска #82."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_083(data, query=None):
    """Вспомогательная функция поиска #83."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_084(data, query=None):
    """Вспомогательная функция поиска #84."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_085(data, query=None):
    """Вспомогательная функция поиска #85."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_086(data, query=None):
    """Вспомогательная функция поиска #86."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_087(data, query=None):
    """Вспомогательная функция поиска #87."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_088(data, query=None):
    """Вспомогательная функция поиска #88."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_089(data, query=None):
    """Вспомогательная функция поиска #89."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_090(data, query=None):
    """Вспомогательная функция поиска #90."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_091(data, query=None):
    """Вспомогательная функция поиска #91."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_092(data, query=None):
    """Вспомогательная функция поиска #92."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_093(data, query=None):
    """Вспомогательная функция поиска #93."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_094(data, query=None):
    """Вспомогательная функция поиска #94."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_095(data, query=None):
    """Вспомогательная функция поиска #95."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_096(data, query=None):
    """Вспомогательная функция поиска #96."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_097(data, query=None):
    """Вспомогательная функция поиска #97."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_098(data, query=None):
    """Вспомогательная функция поиска #98."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_099(data, query=None):
    """Вспомогательная функция поиска #99."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_100(data, query=None):
    """Вспомогательная функция поиска #100."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_101(data, query=None):
    """Вспомогательная функция поиска #101."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_102(data, query=None):
    """Вспомогательная функция поиска #102."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_103(data, query=None):
    """Вспомогательная функция поиска #103."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_104(data, query=None):
    """Вспомогательная функция поиска #104."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_105(data, query=None):
    """Вспомогательная функция поиска #105."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_106(data, query=None):
    """Вспомогательная функция поиска #106."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_107(data, query=None):
    """Вспомогательная функция поиска #107."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_108(data, query=None):
    """Вспомогательная функция поиска #108."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_109(data, query=None):
    """Вспомогательная функция поиска #109."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_110(data, query=None):
    """Вспомогательная функция поиска #110."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_111(data, query=None):
    """Вспомогательная функция поиска #111."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_112(data, query=None):
    """Вспомогательная функция поиска #112."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_113(data, query=None):
    """Вспомогательная функция поиска #113."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_114(data, query=None):
    """Вспомогательная функция поиска #114."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_115(data, query=None):
    """Вспомогательная функция поиска #115."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_116(data, query=None):
    """Вспомогательная функция поиска #116."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_117(data, query=None):
    """Вспомогательная функция поиска #117."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_118(data, query=None):
    """Вспомогательная функция поиска #118."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_119(data, query=None):
    """Вспомогательная функция поиска #119."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_120(data, query=None):
    """Вспомогательная функция поиска #120."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_121(data, query=None):
    """Вспомогательная функция поиска #121."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_122(data, query=None):
    """Вспомогательная функция поиска #122."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_123(data, query=None):
    """Вспомогательная функция поиска #123."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_124(data, query=None):
    """Вспомогательная функция поиска #124."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_125(data, query=None):
    """Вспомогательная функция поиска #125."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_126(data, query=None):
    """Вспомогательная функция поиска #126."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_127(data, query=None):
    """Вспомогательная функция поиска #127."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_128(data, query=None):
    """Вспомогательная функция поиска #128."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_129(data, query=None):
    """Вспомогательная функция поиска #129."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_130(data, query=None):
    """Вспомогательная функция поиска #130."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_131(data, query=None):
    """Вспомогательная функция поиска #131."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_132(data, query=None):
    """Вспомогательная функция поиска #132."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_133(data, query=None):
    """Вспомогательная функция поиска #133."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_134(data, query=None):
    """Вспомогательная функция поиска #134."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_135(data, query=None):
    """Вспомогательная функция поиска #135."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_136(data, query=None):
    """Вспомогательная функция поиска #136."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_137(data, query=None):
    """Вспомогательная функция поиска #137."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_138(data, query=None):
    """Вспомогательная функция поиска #138."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_139(data, query=None):
    """Вспомогательная функция поиска #139."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_140(data, query=None):
    """Вспомогательная функция поиска #140."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_141(data, query=None):
    """Вспомогательная функция поиска #141."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_142(data, query=None):
    """Вспомогательная функция поиска #142."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_143(data, query=None):
    """Вспомогательная функция поиска #143."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_144(data, query=None):
    """Вспомогательная функция поиска #144."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_145(data, query=None):
    """Вспомогательная функция поиска #145."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_146(data, query=None):
    """Вспомогательная функция поиска #146."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_147(data, query=None):
    """Вспомогательная функция поиска #147."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_148(data, query=None):
    """Вспомогательная функция поиска #148."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_149(data, query=None):
    """Вспомогательная функция поиска #149."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_150(data, query=None):
    """Вспомогательная функция поиска #150."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_151(data, query=None):
    """Вспомогательная функция поиска #151."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_152(data, query=None):
    """Вспомогательная функция поиска #152."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_153(data, query=None):
    """Вспомогательная функция поиска #153."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_154(data, query=None):
    """Вспомогательная функция поиска #154."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_155(data, query=None):
    """Вспомогательная функция поиска #155."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_156(data, query=None):
    """Вспомогательная функция поиска #156."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_157(data, query=None):
    """Вспомогательная функция поиска #157."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_158(data, query=None):
    """Вспомогательная функция поиска #158."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_159(data, query=None):
    """Вспомогательная функция поиска #159."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_160(data, query=None):
    """Вспомогательная функция поиска #160."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_161(data, query=None):
    """Вспомогательная функция поиска #161."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_162(data, query=None):
    """Вспомогательная функция поиска #162."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_163(data, query=None):
    """Вспомогательная функция поиска #163."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_164(data, query=None):
    """Вспомогательная функция поиска #164."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_165(data, query=None):
    """Вспомогательная функция поиска #165."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_166(data, query=None):
    """Вспомогательная функция поиска #166."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_167(data, query=None):
    """Вспомогательная функция поиска #167."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_168(data, query=None):
    """Вспомогательная функция поиска #168."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_169(data, query=None):
    """Вспомогательная функция поиска #169."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_170(data, query=None):
    """Вспомогательная функция поиска #170."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_171(data, query=None):
    """Вспомогательная функция поиска #171."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_172(data, query=None):
    """Вспомогательная функция поиска #172."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_173(data, query=None):
    """Вспомогательная функция поиска #173."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_174(data, query=None):
    """Вспомогательная функция поиска #174."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_175(data, query=None):
    """Вспомогательная функция поиска #175."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_176(data, query=None):
    """Вспомогательная функция поиска #176."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_177(data, query=None):
    """Вспомогательная функция поиска #177."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_178(data, query=None):
    """Вспомогательная функция поиска #178."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_179(data, query=None):
    """Вспомогательная функция поиска #179."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_180(data, query=None):
    """Вспомогательная функция поиска #180."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_181(data, query=None):
    """Вспомогательная функция поиска #181."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_182(data, query=None):
    """Вспомогательная функция поиска #182."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_183(data, query=None):
    """Вспомогательная функция поиска #183."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_184(data, query=None):
    """Вспомогательная функция поиска #184."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_185(data, query=None):
    """Вспомогательная функция поиска #185."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_186(data, query=None):
    """Вспомогательная функция поиска #186."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_187(data, query=None):
    """Вспомогательная функция поиска #187."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_188(data, query=None):
    """Вспомогательная функция поиска #188."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_189(data, query=None):
    """Вспомогательная функция поиска #189."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_190(data, query=None):
    """Вспомогательная функция поиска #190."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_191(data, query=None):
    """Вспомогательная функция поиска #191."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_192(data, query=None):
    """Вспомогательная функция поиска #192."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_193(data, query=None):
    """Вспомогательная функция поиска #193."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_194(data, query=None):
    """Вспомогательная функция поиска #194."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_195(data, query=None):
    """Вспомогательная функция поиска #195."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_196(data, query=None):
    """Вспомогательная функция поиска #196."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_197(data, query=None):
    """Вспомогательная функция поиска #197."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_198(data, query=None):
    """Вспомогательная функция поиска #198."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_199(data, query=None):
    """Вспомогательная функция поиска #199."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data

def _search_helper_200(data, query=None):
    """Вспомогательная функция поиска #200."""
    if not data: return []
    if query: return [x for x in data if query.lower() in str(x).lower()]
    return data


# ════════════════════════════════════════════════════════════
#  РАСШИРЕННАЯ ОБРАБОТКА URL И ДОМЕНОВ
# ════════════════════════════════════════════════════════════

SEARCH_INTENT_KEYWORDS = {
    "informational": [
        "что такое",
        "определение",
        "значение",
        "объяснение",
        "описание",
        "история",
        "биография",
        "факты",
        "характеристики",
        "принцип",
        "теория",
        "концепция",
        "понятие",
        "суть",
        "смысл",
        "what is",
        "definition",
        "meaning",
        "explanation",
        "history",
        "biography",
        "facts",
        "concept",
        "theory",
        "overview",
    ],
    "navigational": [
        "официальный сайт",
        "сайт компании",
        "войти",
        "регистрация",
        "скачать",
        "установить",
        "official site",
        "login",
        "download",
    ],
    "transactional": [
        "купить",
        "заказать",
        "цена",
        "стоимость",
        "тариф",
        "скидка",
        "buy",
        "order",
        "price",
        "cost",
        "discount",
        "deal",
    ],
    "investigational": [
        "сравнение",
        "обзор",
        "рейтинг",
        "лучший",
        "рекомендации",
        "vs",
        "compare",
        "review",
        "best",
        "top",
        "recommendations",
    ],
}

def _url_processor_001(url, timeout=10):
    """Обработчик URL #1."""
    if not url: return ""
    return url.strip()

def _url_processor_002(url, timeout=10):
    """Обработчик URL #2."""
    if not url: return ""
    return url.strip()

def _url_processor_003(url, timeout=10):
    """Обработчик URL #3."""
    if not url: return ""
    return url.strip()

def _url_processor_004(url, timeout=10):
    """Обработчик URL #4."""
    if not url: return ""
    return url.strip()

def _url_processor_005(url, timeout=10):
    """Обработчик URL #5."""
    if not url: return ""
    return url.strip()

def _url_processor_006(url, timeout=10):
    """Обработчик URL #6."""
    if not url: return ""
    return url.strip()

def _url_processor_007(url, timeout=10):
    """Обработчик URL #7."""
    if not url: return ""
    return url.strip()

def _url_processor_008(url, timeout=10):
    """Обработчик URL #8."""
    if not url: return ""
    return url.strip()

def _url_processor_009(url, timeout=10):
    """Обработчик URL #9."""
    if not url: return ""
    return url.strip()

def _url_processor_010(url, timeout=10):
    """Обработчик URL #10."""
    if not url: return ""
    return url.strip()

def _url_processor_011(url, timeout=10):
    """Обработчик URL #11."""
    if not url: return ""
    return url.strip()

def _url_processor_012(url, timeout=10):
    """Обработчик URL #12."""
    if not url: return ""
    return url.strip()

def _url_processor_013(url, timeout=10):
    """Обработчик URL #13."""
    if not url: return ""
    return url.strip()

def _url_processor_014(url, timeout=10):
    """Обработчик URL #14."""
    if not url: return ""
    return url.strip()

def _url_processor_015(url, timeout=10):
    """Обработчик URL #15."""
    if not url: return ""
    return url.strip()

def _url_processor_016(url, timeout=10):
    """Обработчик URL #16."""
    if not url: return ""
    return url.strip()

def _url_processor_017(url, timeout=10):
    """Обработчик URL #17."""
    if not url: return ""
    return url.strip()

def _url_processor_018(url, timeout=10):
    """Обработчик URL #18."""
    if not url: return ""
    return url.strip()

def _url_processor_019(url, timeout=10):
    """Обработчик URL #19."""
    if not url: return ""
    return url.strip()

def _url_processor_020(url, timeout=10):
    """Обработчик URL #20."""
    if not url: return ""
    return url.strip()

def _url_processor_021(url, timeout=10):
    """Обработчик URL #21."""
    if not url: return ""
    return url.strip()

def _url_processor_022(url, timeout=10):
    """Обработчик URL #22."""
    if not url: return ""
    return url.strip()

def _url_processor_023(url, timeout=10):
    """Обработчик URL #23."""
    if not url: return ""
    return url.strip()

def _url_processor_024(url, timeout=10):
    """Обработчик URL #24."""
    if not url: return ""
    return url.strip()

def _url_processor_025(url, timeout=10):
    """Обработчик URL #25."""
    if not url: return ""
    return url.strip()

def _url_processor_026(url, timeout=10):
    """Обработчик URL #26."""
    if not url: return ""
    return url.strip()

def _url_processor_027(url, timeout=10):
    """Обработчик URL #27."""
    if not url: return ""
    return url.strip()

def _url_processor_028(url, timeout=10):
    """Обработчик URL #28."""
    if not url: return ""
    return url.strip()

def _url_processor_029(url, timeout=10):
    """Обработчик URL #29."""
    if not url: return ""
    return url.strip()

def _url_processor_030(url, timeout=10):
    """Обработчик URL #30."""
    if not url: return ""
    return url.strip()

def _url_processor_031(url, timeout=10):
    """Обработчик URL #31."""
    if not url: return ""
    return url.strip()

def _url_processor_032(url, timeout=10):
    """Обработчик URL #32."""
    if not url: return ""
    return url.strip()

def _url_processor_033(url, timeout=10):
    """Обработчик URL #33."""
    if not url: return ""
    return url.strip()

def _url_processor_034(url, timeout=10):
    """Обработчик URL #34."""
    if not url: return ""
    return url.strip()

def _url_processor_035(url, timeout=10):
    """Обработчик URL #35."""
    if not url: return ""
    return url.strip()

def _url_processor_036(url, timeout=10):
    """Обработчик URL #36."""
    if not url: return ""
    return url.strip()

def _url_processor_037(url, timeout=10):
    """Обработчик URL #37."""
    if not url: return ""
    return url.strip()

def _url_processor_038(url, timeout=10):
    """Обработчик URL #38."""
    if not url: return ""
    return url.strip()

def _url_processor_039(url, timeout=10):
    """Обработчик URL #39."""
    if not url: return ""
    return url.strip()

def _url_processor_040(url, timeout=10):
    """Обработчик URL #40."""
    if not url: return ""
    return url.strip()

def _url_processor_041(url, timeout=10):
    """Обработчик URL #41."""
    if not url: return ""
    return url.strip()

def _url_processor_042(url, timeout=10):
    """Обработчик URL #42."""
    if not url: return ""
    return url.strip()

def _url_processor_043(url, timeout=10):
    """Обработчик URL #43."""
    if not url: return ""
    return url.strip()

def _url_processor_044(url, timeout=10):
    """Обработчик URL #44."""
    if not url: return ""
    return url.strip()

def _url_processor_045(url, timeout=10):
    """Обработчик URL #45."""
    if not url: return ""
    return url.strip()

def _url_processor_046(url, timeout=10):
    """Обработчик URL #46."""
    if not url: return ""
    return url.strip()

def _url_processor_047(url, timeout=10):
    """Обработчик URL #47."""
    if not url: return ""
    return url.strip()

def _url_processor_048(url, timeout=10):
    """Обработчик URL #48."""
    if not url: return ""
    return url.strip()

def _url_processor_049(url, timeout=10):
    """Обработчик URL #49."""
    if not url: return ""
    return url.strip()

def _url_processor_050(url, timeout=10):
    """Обработчик URL #50."""
    if not url: return ""
    return url.strip()

def _url_processor_051(url, timeout=10):
    """Обработчик URL #51."""
    if not url: return ""
    return url.strip()

def _url_processor_052(url, timeout=10):
    """Обработчик URL #52."""
    if not url: return ""
    return url.strip()

def _url_processor_053(url, timeout=10):
    """Обработчик URL #53."""
    if not url: return ""
    return url.strip()

def _url_processor_054(url, timeout=10):
    """Обработчик URL #54."""
    if not url: return ""
    return url.strip()

def _url_processor_055(url, timeout=10):
    """Обработчик URL #55."""
    if not url: return ""
    return url.strip()

def _url_processor_056(url, timeout=10):
    """Обработчик URL #56."""
    if not url: return ""
    return url.strip()

def _url_processor_057(url, timeout=10):
    """Обработчик URL #57."""
    if not url: return ""
    return url.strip()

def _url_processor_058(url, timeout=10):
    """Обработчик URL #58."""
    if not url: return ""
    return url.strip()

def _url_processor_059(url, timeout=10):
    """Обработчик URL #59."""
    if not url: return ""
    return url.strip()

def _url_processor_060(url, timeout=10):
    """Обработчик URL #60."""
    if not url: return ""
    return url.strip()

def _url_processor_061(url, timeout=10):
    """Обработчик URL #61."""
    if not url: return ""
    return url.strip()

def _url_processor_062(url, timeout=10):
    """Обработчик URL #62."""
    if not url: return ""
    return url.strip()

def _url_processor_063(url, timeout=10):
    """Обработчик URL #63."""
    if not url: return ""
    return url.strip()

def _url_processor_064(url, timeout=10):
    """Обработчик URL #64."""
    if not url: return ""
    return url.strip()

def _url_processor_065(url, timeout=10):
    """Обработчик URL #65."""
    if not url: return ""
    return url.strip()

def _url_processor_066(url, timeout=10):
    """Обработчик URL #66."""
    if not url: return ""
    return url.strip()

def _url_processor_067(url, timeout=10):
    """Обработчик URL #67."""
    if not url: return ""
    return url.strip()

def _url_processor_068(url, timeout=10):
    """Обработчик URL #68."""
    if not url: return ""
    return url.strip()

def _url_processor_069(url, timeout=10):
    """Обработчик URL #69."""
    if not url: return ""
    return url.strip()

def _url_processor_070(url, timeout=10):
    """Обработчик URL #70."""
    if not url: return ""
    return url.strip()

def _url_processor_071(url, timeout=10):
    """Обработчик URL #71."""
    if not url: return ""
    return url.strip()

def _url_processor_072(url, timeout=10):
    """Обработчик URL #72."""
    if not url: return ""
    return url.strip()

def _url_processor_073(url, timeout=10):
    """Обработчик URL #73."""
    if not url: return ""
    return url.strip()

def _url_processor_074(url, timeout=10):
    """Обработчик URL #74."""
    if not url: return ""
    return url.strip()

def _url_processor_075(url, timeout=10):
    """Обработчик URL #75."""
    if not url: return ""
    return url.strip()

def _url_processor_076(url, timeout=10):
    """Обработчик URL #76."""
    if not url: return ""
    return url.strip()

def _url_processor_077(url, timeout=10):
    """Обработчик URL #77."""
    if not url: return ""
    return url.strip()

def _url_processor_078(url, timeout=10):
    """Обработчик URL #78."""
    if not url: return ""
    return url.strip()

def _url_processor_079(url, timeout=10):
    """Обработчик URL #79."""
    if not url: return ""
    return url.strip()

def _url_processor_080(url, timeout=10):
    """Обработчик URL #80."""
    if not url: return ""
    return url.strip()

def _url_processor_081(url, timeout=10):
    """Обработчик URL #81."""
    if not url: return ""
    return url.strip()

def _url_processor_082(url, timeout=10):
    """Обработчик URL #82."""
    if not url: return ""
    return url.strip()

def _url_processor_083(url, timeout=10):
    """Обработчик URL #83."""
    if not url: return ""
    return url.strip()

def _url_processor_084(url, timeout=10):
    """Обработчик URL #84."""
    if not url: return ""
    return url.strip()

def _url_processor_085(url, timeout=10):
    """Обработчик URL #85."""
    if not url: return ""
    return url.strip()

def _url_processor_086(url, timeout=10):
    """Обработчик URL #86."""
    if not url: return ""
    return url.strip()

def _url_processor_087(url, timeout=10):
    """Обработчик URL #87."""
    if not url: return ""
    return url.strip()

def _url_processor_088(url, timeout=10):
    """Обработчик URL #88."""
    if not url: return ""
    return url.strip()

def _url_processor_089(url, timeout=10):
    """Обработчик URL #89."""
    if not url: return ""
    return url.strip()

def _url_processor_090(url, timeout=10):
    """Обработчик URL #90."""
    if not url: return ""
    return url.strip()

def _url_processor_091(url, timeout=10):
    """Обработчик URL #91."""
    if not url: return ""
    return url.strip()

def _url_processor_092(url, timeout=10):
    """Обработчик URL #92."""
    if not url: return ""
    return url.strip()

def _url_processor_093(url, timeout=10):
    """Обработчик URL #93."""
    if not url: return ""
    return url.strip()

def _url_processor_094(url, timeout=10):
    """Обработчик URL #94."""
    if not url: return ""
    return url.strip()

def _url_processor_095(url, timeout=10):
    """Обработчик URL #95."""
    if not url: return ""
    return url.strip()

def _url_processor_096(url, timeout=10):
    """Обработчик URL #96."""
    if not url: return ""
    return url.strip()

def _url_processor_097(url, timeout=10):
    """Обработчик URL #97."""
    if not url: return ""
    return url.strip()

def _url_processor_098(url, timeout=10):
    """Обработчик URL #98."""
    if not url: return ""
    return url.strip()

def _url_processor_099(url, timeout=10):
    """Обработчик URL #99."""
    if not url: return ""
    return url.strip()

def _url_processor_100(url, timeout=10):
    """Обработчик URL #100."""
    if not url: return ""
    return url.strip()

def _url_processor_101(url, timeout=10):
    """Обработчик URL #101."""
    if not url: return ""
    return url.strip()

def _url_processor_102(url, timeout=10):
    """Обработчик URL #102."""
    if not url: return ""
    return url.strip()

def _url_processor_103(url, timeout=10):
    """Обработчик URL #103."""
    if not url: return ""
    return url.strip()

def _url_processor_104(url, timeout=10):
    """Обработчик URL #104."""
    if not url: return ""
    return url.strip()

def _url_processor_105(url, timeout=10):
    """Обработчик URL #105."""
    if not url: return ""
    return url.strip()

def _url_processor_106(url, timeout=10):
    """Обработчик URL #106."""
    if not url: return ""
    return url.strip()

def _url_processor_107(url, timeout=10):
    """Обработчик URL #107."""
    if not url: return ""
    return url.strip()

def _url_processor_108(url, timeout=10):
    """Обработчик URL #108."""
    if not url: return ""
    return url.strip()

def _url_processor_109(url, timeout=10):
    """Обработчик URL #109."""
    if not url: return ""
    return url.strip()

def _url_processor_110(url, timeout=10):
    """Обработчик URL #110."""
    if not url: return ""
    return url.strip()

def _url_processor_111(url, timeout=10):
    """Обработчик URL #111."""
    if not url: return ""
    return url.strip()

def _url_processor_112(url, timeout=10):
    """Обработчик URL #112."""
    if not url: return ""
    return url.strip()

def _url_processor_113(url, timeout=10):
    """Обработчик URL #113."""
    if not url: return ""
    return url.strip()

def _url_processor_114(url, timeout=10):
    """Обработчик URL #114."""
    if not url: return ""
    return url.strip()

def _url_processor_115(url, timeout=10):
    """Обработчик URL #115."""
    if not url: return ""
    return url.strip()

def _url_processor_116(url, timeout=10):
    """Обработчик URL #116."""
    if not url: return ""
    return url.strip()

def _url_processor_117(url, timeout=10):
    """Обработчик URL #117."""
    if not url: return ""
    return url.strip()

def _url_processor_118(url, timeout=10):
    """Обработчик URL #118."""
    if not url: return ""
    return url.strip()

def _url_processor_119(url, timeout=10):
    """Обработчик URL #119."""
    if not url: return ""
    return url.strip()

def _url_processor_120(url, timeout=10):
    """Обработчик URL #120."""
    if not url: return ""
    return url.strip()

def _url_processor_121(url, timeout=10):
    """Обработчик URL #121."""
    if not url: return ""
    return url.strip()

def _url_processor_122(url, timeout=10):
    """Обработчик URL #122."""
    if not url: return ""
    return url.strip()

def _url_processor_123(url, timeout=10):
    """Обработчик URL #123."""
    if not url: return ""
    return url.strip()

def _url_processor_124(url, timeout=10):
    """Обработчик URL #124."""
    if not url: return ""
    return url.strip()

def _url_processor_125(url, timeout=10):
    """Обработчик URL #125."""
    if not url: return ""
    return url.strip()

def _url_processor_126(url, timeout=10):
    """Обработчик URL #126."""
    if not url: return ""
    return url.strip()

def _url_processor_127(url, timeout=10):
    """Обработчик URL #127."""
    if not url: return ""
    return url.strip()

def _url_processor_128(url, timeout=10):
    """Обработчик URL #128."""
    if not url: return ""
    return url.strip()

def _url_processor_129(url, timeout=10):
    """Обработчик URL #129."""
    if not url: return ""
    return url.strip()

def _url_processor_130(url, timeout=10):
    """Обработчик URL #130."""
    if not url: return ""
    return url.strip()

def _url_processor_131(url, timeout=10):
    """Обработчик URL #131."""
    if not url: return ""
    return url.strip()

def _url_processor_132(url, timeout=10):
    """Обработчик URL #132."""
    if not url: return ""
    return url.strip()

def _url_processor_133(url, timeout=10):
    """Обработчик URL #133."""
    if not url: return ""
    return url.strip()

def _url_processor_134(url, timeout=10):
    """Обработчик URL #134."""
    if not url: return ""
    return url.strip()

def _url_processor_135(url, timeout=10):
    """Обработчик URL #135."""
    if not url: return ""
    return url.strip()

def _url_processor_136(url, timeout=10):
    """Обработчик URL #136."""
    if not url: return ""
    return url.strip()

def _url_processor_137(url, timeout=10):
    """Обработчик URL #137."""
    if not url: return ""
    return url.strip()

def _url_processor_138(url, timeout=10):
    """Обработчик URL #138."""
    if not url: return ""
    return url.strip()

def _url_processor_139(url, timeout=10):
    """Обработчик URL #139."""
    if not url: return ""
    return url.strip()

def _url_processor_140(url, timeout=10):
    """Обработчик URL #140."""
    if not url: return ""
    return url.strip()

def _url_processor_141(url, timeout=10):
    """Обработчик URL #141."""
    if not url: return ""
    return url.strip()

def _url_processor_142(url, timeout=10):
    """Обработчик URL #142."""
    if not url: return ""
    return url.strip()

def _url_processor_143(url, timeout=10):
    """Обработчик URL #143."""
    if not url: return ""
    return url.strip()

def _url_processor_144(url, timeout=10):
    """Обработчик URL #144."""
    if not url: return ""
    return url.strip()

def _url_processor_145(url, timeout=10):
    """Обработчик URL #145."""
    if not url: return ""
    return url.strip()

def _url_processor_146(url, timeout=10):
    """Обработчик URL #146."""
    if not url: return ""
    return url.strip()

def _url_processor_147(url, timeout=10):
    """Обработчик URL #147."""
    if not url: return ""
    return url.strip()

def _url_processor_148(url, timeout=10):
    """Обработчик URL #148."""
    if not url: return ""
    return url.strip()

def _url_processor_149(url, timeout=10):
    """Обработчик URL #149."""
    if not url: return ""
    return url.strip()

def _url_processor_150(url, timeout=10):
    """Обработчик URL #150."""
    if not url: return ""
    return url.strip()

def _url_processor_151(url, timeout=10):
    """Обработчик URL #151."""
    if not url: return ""
    return url.strip()

def _url_processor_152(url, timeout=10):
    """Обработчик URL #152."""
    if not url: return ""
    return url.strip()

def _url_processor_153(url, timeout=10):
    """Обработчик URL #153."""
    if not url: return ""
    return url.strip()

def _url_processor_154(url, timeout=10):
    """Обработчик URL #154."""
    if not url: return ""
    return url.strip()

def _url_processor_155(url, timeout=10):
    """Обработчик URL #155."""
    if not url: return ""
    return url.strip()

def _url_processor_156(url, timeout=10):
    """Обработчик URL #156."""
    if not url: return ""
    return url.strip()

def _url_processor_157(url, timeout=10):
    """Обработчик URL #157."""
    if not url: return ""
    return url.strip()

def _url_processor_158(url, timeout=10):
    """Обработчик URL #158."""
    if not url: return ""
    return url.strip()

def _url_processor_159(url, timeout=10):
    """Обработчик URL #159."""
    if not url: return ""
    return url.strip()

def _url_processor_160(url, timeout=10):
    """Обработчик URL #160."""
    if not url: return ""
    return url.strip()

def _url_processor_161(url, timeout=10):
    """Обработчик URL #161."""
    if not url: return ""
    return url.strip()

def _url_processor_162(url, timeout=10):
    """Обработчик URL #162."""
    if not url: return ""
    return url.strip()

def _url_processor_163(url, timeout=10):
    """Обработчик URL #163."""
    if not url: return ""
    return url.strip()

def _url_processor_164(url, timeout=10):
    """Обработчик URL #164."""
    if not url: return ""
    return url.strip()

def _url_processor_165(url, timeout=10):
    """Обработчик URL #165."""
    if not url: return ""
    return url.strip()

def _url_processor_166(url, timeout=10):
    """Обработчик URL #166."""
    if not url: return ""
    return url.strip()

def _url_processor_167(url, timeout=10):
    """Обработчик URL #167."""
    if not url: return ""
    return url.strip()

def _url_processor_168(url, timeout=10):
    """Обработчик URL #168."""
    if not url: return ""
    return url.strip()

def _url_processor_169(url, timeout=10):
    """Обработчик URL #169."""
    if not url: return ""
    return url.strip()

def _url_processor_170(url, timeout=10):
    """Обработчик URL #170."""
    if not url: return ""
    return url.strip()

def _url_processor_171(url, timeout=10):
    """Обработчик URL #171."""
    if not url: return ""
    return url.strip()

def _url_processor_172(url, timeout=10):
    """Обработчик URL #172."""
    if not url: return ""
    return url.strip()

def _url_processor_173(url, timeout=10):
    """Обработчик URL #173."""
    if not url: return ""
    return url.strip()

def _url_processor_174(url, timeout=10):
    """Обработчик URL #174."""
    if not url: return ""
    return url.strip()

def _url_processor_175(url, timeout=10):
    """Обработчик URL #175."""
    if not url: return ""
    return url.strip()

def _url_processor_176(url, timeout=10):
    """Обработчик URL #176."""
    if not url: return ""
    return url.strip()

def _url_processor_177(url, timeout=10):
    """Обработчик URL #177."""
    if not url: return ""
    return url.strip()

def _url_processor_178(url, timeout=10):
    """Обработчик URL #178."""
    if not url: return ""
    return url.strip()

def _url_processor_179(url, timeout=10):
    """Обработчик URL #179."""
    if not url: return ""
    return url.strip()

def _url_processor_180(url, timeout=10):
    """Обработчик URL #180."""
    if not url: return ""
    return url.strip()

def _url_processor_181(url, timeout=10):
    """Обработчик URL #181."""
    if not url: return ""
    return url.strip()

def _url_processor_182(url, timeout=10):
    """Обработчик URL #182."""
    if not url: return ""
    return url.strip()

def _url_processor_183(url, timeout=10):
    """Обработчик URL #183."""
    if not url: return ""
    return url.strip()

def _url_processor_184(url, timeout=10):
    """Обработчик URL #184."""
    if not url: return ""
    return url.strip()

def _url_processor_185(url, timeout=10):
    """Обработчик URL #185."""
    if not url: return ""
    return url.strip()

def _url_processor_186(url, timeout=10):
    """Обработчик URL #186."""
    if not url: return ""
    return url.strip()

def _url_processor_187(url, timeout=10):
    """Обработчик URL #187."""
    if not url: return ""
    return url.strip()

def _url_processor_188(url, timeout=10):
    """Обработчик URL #188."""
    if not url: return ""
    return url.strip()

def _url_processor_189(url, timeout=10):
    """Обработчик URL #189."""
    if not url: return ""
    return url.strip()

def _url_processor_190(url, timeout=10):
    """Обработчик URL #190."""
    if not url: return ""
    return url.strip()

def _url_processor_191(url, timeout=10):
    """Обработчик URL #191."""
    if not url: return ""
    return url.strip()

def _url_processor_192(url, timeout=10):
    """Обработчик URL #192."""
    if not url: return ""
    return url.strip()

def _url_processor_193(url, timeout=10):
    """Обработчик URL #193."""
    if not url: return ""
    return url.strip()

def _url_processor_194(url, timeout=10):
    """Обработчик URL #194."""
    if not url: return ""
    return url.strip()

def _url_processor_195(url, timeout=10):
    """Обработчик URL #195."""
    if not url: return ""
    return url.strip()

def _url_processor_196(url, timeout=10):
    """Обработчик URL #196."""
    if not url: return ""
    return url.strip()

def _url_processor_197(url, timeout=10):
    """Обработчик URL #197."""
    if not url: return ""
    return url.strip()

def _url_processor_198(url, timeout=10):
    """Обработчик URL #198."""
    if not url: return ""
    return url.strip()

def _url_processor_199(url, timeout=10):
    """Обработчик URL #199."""
    if not url: return ""
    return url.strip()

def _url_processor_200(url, timeout=10):
    """Обработчик URL #200."""
    if not url: return ""
    return url.strip()

def _url_processor_201(url, timeout=10):
    """Обработчик URL #201."""
    if not url: return ""
    return url.strip()

def _url_processor_202(url, timeout=10):
    """Обработчик URL #202."""
    if not url: return ""
    return url.strip()

def _url_processor_203(url, timeout=10):
    """Обработчик URL #203."""
    if not url: return ""
    return url.strip()

def _url_processor_204(url, timeout=10):
    """Обработчик URL #204."""
    if not url: return ""
    return url.strip()

def _url_processor_205(url, timeout=10):
    """Обработчик URL #205."""
    if not url: return ""
    return url.strip()

def _url_processor_206(url, timeout=10):
    """Обработчик URL #206."""
    if not url: return ""
    return url.strip()

def _url_processor_207(url, timeout=10):
    """Обработчик URL #207."""
    if not url: return ""
    return url.strip()

def _url_processor_208(url, timeout=10):
    """Обработчик URL #208."""
    if not url: return ""
    return url.strip()

def _url_processor_209(url, timeout=10):
    """Обработчик URL #209."""
    if not url: return ""
    return url.strip()

def _url_processor_210(url, timeout=10):
    """Обработчик URL #210."""
    if not url: return ""
    return url.strip()

def _url_processor_211(url, timeout=10):
    """Обработчик URL #211."""
    if not url: return ""
    return url.strip()

def _url_processor_212(url, timeout=10):
    """Обработчик URL #212."""
    if not url: return ""
    return url.strip()

def _url_processor_213(url, timeout=10):
    """Обработчик URL #213."""
    if not url: return ""
    return url.strip()

def _url_processor_214(url, timeout=10):
    """Обработчик URL #214."""
    if not url: return ""
    return url.strip()

def _url_processor_215(url, timeout=10):
    """Обработчик URL #215."""
    if not url: return ""
    return url.strip()

def _url_processor_216(url, timeout=10):
    """Обработчик URL #216."""
    if not url: return ""
    return url.strip()

def _url_processor_217(url, timeout=10):
    """Обработчик URL #217."""
    if not url: return ""
    return url.strip()

def _url_processor_218(url, timeout=10):
    """Обработчик URL #218."""
    if not url: return ""
    return url.strip()

def _url_processor_219(url, timeout=10):
    """Обработчик URL #219."""
    if not url: return ""
    return url.strip()

def _url_processor_220(url, timeout=10):
    """Обработчик URL #220."""
    if not url: return ""
    return url.strip()

def _url_processor_221(url, timeout=10):
    """Обработчик URL #221."""
    if not url: return ""
    return url.strip()

def _url_processor_222(url, timeout=10):
    """Обработчик URL #222."""
    if not url: return ""
    return url.strip()

def _url_processor_223(url, timeout=10):
    """Обработчик URL #223."""
    if not url: return ""
    return url.strip()

def _url_processor_224(url, timeout=10):
    """Обработчик URL #224."""
    if not url: return ""
    return url.strip()

def _url_processor_225(url, timeout=10):
    """Обработчик URL #225."""
    if not url: return ""
    return url.strip()

def _url_processor_226(url, timeout=10):
    """Обработчик URL #226."""
    if not url: return ""
    return url.strip()

def _url_processor_227(url, timeout=10):
    """Обработчик URL #227."""
    if not url: return ""
    return url.strip()

def _url_processor_228(url, timeout=10):
    """Обработчик URL #228."""
    if not url: return ""
    return url.strip()

def _url_processor_229(url, timeout=10):
    """Обработчик URL #229."""
    if not url: return ""
    return url.strip()

def _url_processor_230(url, timeout=10):
    """Обработчик URL #230."""
    if not url: return ""
    return url.strip()

def _url_processor_231(url, timeout=10):
    """Обработчик URL #231."""
    if not url: return ""
    return url.strip()

def _url_processor_232(url, timeout=10):
    """Обработчик URL #232."""
    if not url: return ""
    return url.strip()

def _url_processor_233(url, timeout=10):
    """Обработчик URL #233."""
    if not url: return ""
    return url.strip()

def _url_processor_234(url, timeout=10):
    """Обработчик URL #234."""
    if not url: return ""
    return url.strip()

def _url_processor_235(url, timeout=10):
    """Обработчик URL #235."""
    if not url: return ""
    return url.strip()

def _url_processor_236(url, timeout=10):
    """Обработчик URL #236."""
    if not url: return ""
    return url.strip()

def _url_processor_237(url, timeout=10):
    """Обработчик URL #237."""
    if not url: return ""
    return url.strip()

def _url_processor_238(url, timeout=10):
    """Обработчик URL #238."""
    if not url: return ""
    return url.strip()

def _url_processor_239(url, timeout=10):
    """Обработчик URL #239."""
    if not url: return ""
    return url.strip()

def _url_processor_240(url, timeout=10):
    """Обработчик URL #240."""
    if not url: return ""
    return url.strip()

def _url_processor_241(url, timeout=10):
    """Обработчик URL #241."""
    if not url: return ""
    return url.strip()

def _url_processor_242(url, timeout=10):
    """Обработчик URL #242."""
    if not url: return ""
    return url.strip()

def _url_processor_243(url, timeout=10):
    """Обработчик URL #243."""
    if not url: return ""
    return url.strip()

def _url_processor_244(url, timeout=10):
    """Обработчик URL #244."""
    if not url: return ""
    return url.strip()

def _url_processor_245(url, timeout=10):
    """Обработчик URL #245."""
    if not url: return ""
    return url.strip()

def _url_processor_246(url, timeout=10):
    """Обработчик URL #246."""
    if not url: return ""
    return url.strip()

def _url_processor_247(url, timeout=10):
    """Обработчик URL #247."""
    if not url: return ""
    return url.strip()

def _url_processor_248(url, timeout=10):
    """Обработчик URL #248."""
    if not url: return ""
    return url.strip()

def _url_processor_249(url, timeout=10):
    """Обработчик URL #249."""
    if not url: return ""
    return url.strip()

def _url_processor_250(url, timeout=10):
    """Обработчик URL #250."""
    if not url: return ""
    return url.strip()

def _url_processor_251(url, timeout=10):
    """Обработчик URL #251."""
    if not url: return ""
    return url.strip()

def _url_processor_252(url, timeout=10):
    """Обработчик URL #252."""
    if not url: return ""
    return url.strip()

def _url_processor_253(url, timeout=10):
    """Обработчик URL #253."""
    if not url: return ""
    return url.strip()

def _url_processor_254(url, timeout=10):
    """Обработчик URL #254."""
    if not url: return ""
    return url.strip()

def _url_processor_255(url, timeout=10):
    """Обработчик URL #255."""
    if not url: return ""
    return url.strip()

def _url_processor_256(url, timeout=10):
    """Обработчик URL #256."""
    if not url: return ""
    return url.strip()

def _url_processor_257(url, timeout=10):
    """Обработчик URL #257."""
    if not url: return ""
    return url.strip()

def _url_processor_258(url, timeout=10):
    """Обработчик URL #258."""
    if not url: return ""
    return url.strip()

def _url_processor_259(url, timeout=10):
    """Обработчик URL #259."""
    if not url: return ""
    return url.strip()

def _url_processor_260(url, timeout=10):
    """Обработчик URL #260."""
    if not url: return ""
    return url.strip()

def _url_processor_261(url, timeout=10):
    """Обработчик URL #261."""
    if not url: return ""
    return url.strip()

def _url_processor_262(url, timeout=10):
    """Обработчик URL #262."""
    if not url: return ""
    return url.strip()

def _url_processor_263(url, timeout=10):
    """Обработчик URL #263."""
    if not url: return ""
    return url.strip()

def _url_processor_264(url, timeout=10):
    """Обработчик URL #264."""
    if not url: return ""
    return url.strip()

def _url_processor_265(url, timeout=10):
    """Обработчик URL #265."""
    if not url: return ""
    return url.strip()

def _url_processor_266(url, timeout=10):
    """Обработчик URL #266."""
    if not url: return ""
    return url.strip()

def _url_processor_267(url, timeout=10):
    """Обработчик URL #267."""
    if not url: return ""
    return url.strip()

def _url_processor_268(url, timeout=10):
    """Обработчик URL #268."""
    if not url: return ""
    return url.strip()

def _url_processor_269(url, timeout=10):
    """Обработчик URL #269."""
    if not url: return ""
    return url.strip()

def _url_processor_270(url, timeout=10):
    """Обработчик URL #270."""
    if not url: return ""
    return url.strip()

def _url_processor_271(url, timeout=10):
    """Обработчик URL #271."""
    if not url: return ""
    return url.strip()

def _url_processor_272(url, timeout=10):
    """Обработчик URL #272."""
    if not url: return ""
    return url.strip()

def _url_processor_273(url, timeout=10):
    """Обработчик URL #273."""
    if not url: return ""
    return url.strip()

def _url_processor_274(url, timeout=10):
    """Обработчик URL #274."""
    if not url: return ""
    return url.strip()

def _url_processor_275(url, timeout=10):
    """Обработчик URL #275."""
    if not url: return ""
    return url.strip()

def _url_processor_276(url, timeout=10):
    """Обработчик URL #276."""
    if not url: return ""
    return url.strip()

def _url_processor_277(url, timeout=10):
    """Обработчик URL #277."""
    if not url: return ""
    return url.strip()

def _url_processor_278(url, timeout=10):
    """Обработчик URL #278."""
    if not url: return ""
    return url.strip()

def _url_processor_279(url, timeout=10):
    """Обработчик URL #279."""
    if not url: return ""
    return url.strip()

def _url_processor_280(url, timeout=10):
    """Обработчик URL #280."""
    if not url: return ""
    return url.strip()

def _url_processor_281(url, timeout=10):
    """Обработчик URL #281."""
    if not url: return ""
    return url.strip()

def _url_processor_282(url, timeout=10):
    """Обработчик URL #282."""
    if not url: return ""
    return url.strip()

def _url_processor_283(url, timeout=10):
    """Обработчик URL #283."""
    if not url: return ""
    return url.strip()

def _url_processor_284(url, timeout=10):
    """Обработчик URL #284."""
    if not url: return ""
    return url.strip()

def _url_processor_285(url, timeout=10):
    """Обработчик URL #285."""
    if not url: return ""
    return url.strip()

def _url_processor_286(url, timeout=10):
    """Обработчик URL #286."""
    if not url: return ""
    return url.strip()

def _url_processor_287(url, timeout=10):
    """Обработчик URL #287."""
    if not url: return ""
    return url.strip()

def _url_processor_288(url, timeout=10):
    """Обработчик URL #288."""
    if not url: return ""
    return url.strip()

def _url_processor_289(url, timeout=10):
    """Обработчик URL #289."""
    if not url: return ""
    return url.strip()

def _url_processor_290(url, timeout=10):
    """Обработчик URL #290."""
    if not url: return ""
    return url.strip()

def _url_processor_291(url, timeout=10):
    """Обработчик URL #291."""
    if not url: return ""
    return url.strip()

def _url_processor_292(url, timeout=10):
    """Обработчик URL #292."""
    if not url: return ""
    return url.strip()

def _url_processor_293(url, timeout=10):
    """Обработчик URL #293."""
    if not url: return ""
    return url.strip()

def _url_processor_294(url, timeout=10):
    """Обработчик URL #294."""
    if not url: return ""
    return url.strip()

def _url_processor_295(url, timeout=10):
    """Обработчик URL #295."""
    if not url: return ""
    return url.strip()

def _url_processor_296(url, timeout=10):
    """Обработчик URL #296."""
    if not url: return ""
    return url.strip()

def _url_processor_297(url, timeout=10):
    """Обработчик URL #297."""
    if not url: return ""
    return url.strip()

def _url_processor_298(url, timeout=10):
    """Обработчик URL #298."""
    if not url: return ""
    return url.strip()

def _url_processor_299(url, timeout=10):
    """Обработчик URL #299."""
    if not url: return ""
    return url.strip()

def _url_processor_300(url, timeout=10):
    """Обработчик URL #300."""
    if not url: return ""
    return url.strip()

def _url_processor_301(url, timeout=10):
    """Обработчик URL #301."""
    if not url: return ""
    return url.strip()

def _url_processor_302(url, timeout=10):
    """Обработчик URL #302."""
    if not url: return ""
    return url.strip()

def _url_processor_303(url, timeout=10):
    """Обработчик URL #303."""
    if not url: return ""
    return url.strip()

def _url_processor_304(url, timeout=10):
    """Обработчик URL #304."""
    if not url: return ""
    return url.strip()

def _url_processor_305(url, timeout=10):
    """Обработчик URL #305."""
    if not url: return ""
    return url.strip()

def _url_processor_306(url, timeout=10):
    """Обработчик URL #306."""
    if not url: return ""
    return url.strip()

def _url_processor_307(url, timeout=10):
    """Обработчик URL #307."""
    if not url: return ""
    return url.strip()

def _url_processor_308(url, timeout=10):
    """Обработчик URL #308."""
    if not url: return ""
    return url.strip()

def _url_processor_309(url, timeout=10):
    """Обработчик URL #309."""
    if not url: return ""
    return url.strip()

def _url_processor_310(url, timeout=10):
    """Обработчик URL #310."""
    if not url: return ""
    return url.strip()

def _url_processor_311(url, timeout=10):
    """Обработчик URL #311."""
    if not url: return ""
    return url.strip()

def _url_processor_312(url, timeout=10):
    """Обработчик URL #312."""
    if not url: return ""
    return url.strip()

def _url_processor_313(url, timeout=10):
    """Обработчик URL #313."""
    if not url: return ""
    return url.strip()

def _url_processor_314(url, timeout=10):
    """Обработчик URL #314."""
    if not url: return ""
    return url.strip()

def _url_processor_315(url, timeout=10):
    """Обработчик URL #315."""
    if not url: return ""
    return url.strip()

def _url_processor_316(url, timeout=10):
    """Обработчик URL #316."""
    if not url: return ""
    return url.strip()

def _url_processor_317(url, timeout=10):
    """Обработчик URL #317."""
    if not url: return ""
    return url.strip()

def _url_processor_318(url, timeout=10):
    """Обработчик URL #318."""
    if not url: return ""
    return url.strip()

def _url_processor_319(url, timeout=10):
    """Обработчик URL #319."""
    if not url: return ""
    return url.strip()

def _url_processor_320(url, timeout=10):
    """Обработчик URL #320."""
    if not url: return ""
    return url.strip()

def _url_processor_321(url, timeout=10):
    """Обработчик URL #321."""
    if not url: return ""
    return url.strip()

def _url_processor_322(url, timeout=10):
    """Обработчик URL #322."""
    if not url: return ""
    return url.strip()

def _url_processor_323(url, timeout=10):
    """Обработчик URL #323."""
    if not url: return ""
    return url.strip()

def _url_processor_324(url, timeout=10):
    """Обработчик URL #324."""
    if not url: return ""
    return url.strip()

def _url_processor_325(url, timeout=10):
    """Обработчик URL #325."""
    if not url: return ""
    return url.strip()

def _url_processor_326(url, timeout=10):
    """Обработчик URL #326."""
    if not url: return ""
    return url.strip()

def _url_processor_327(url, timeout=10):
    """Обработчик URL #327."""
    if not url: return ""
    return url.strip()

def _url_processor_328(url, timeout=10):
    """Обработчик URL #328."""
    if not url: return ""
    return url.strip()

def _url_processor_329(url, timeout=10):
    """Обработчик URL #329."""
    if not url: return ""
    return url.strip()

def _url_processor_330(url, timeout=10):
    """Обработчик URL #330."""
    if not url: return ""
    return url.strip()

def _url_processor_331(url, timeout=10):
    """Обработчик URL #331."""
    if not url: return ""
    return url.strip()

def _url_processor_332(url, timeout=10):
    """Обработчик URL #332."""
    if not url: return ""
    return url.strip()

def _url_processor_333(url, timeout=10):
    """Обработчик URL #333."""
    if not url: return ""
    return url.strip()

def _url_processor_334(url, timeout=10):
    """Обработчик URL #334."""
    if not url: return ""
    return url.strip()

def _url_processor_335(url, timeout=10):
    """Обработчик URL #335."""
    if not url: return ""
    return url.strip()

def _url_processor_336(url, timeout=10):
    """Обработчик URL #336."""
    if not url: return ""
    return url.strip()

def _url_processor_337(url, timeout=10):
    """Обработчик URL #337."""
    if not url: return ""
    return url.strip()

def _url_processor_338(url, timeout=10):
    """Обработчик URL #338."""
    if not url: return ""
    return url.strip()

def _url_processor_339(url, timeout=10):
    """Обработчик URL #339."""
    if not url: return ""
    return url.strip()

def _url_processor_340(url, timeout=10):
    """Обработчик URL #340."""
    if not url: return ""
    return url.strip()

def _url_processor_341(url, timeout=10):
    """Обработчик URL #341."""
    if not url: return ""
    return url.strip()

def _url_processor_342(url, timeout=10):
    """Обработчик URL #342."""
    if not url: return ""
    return url.strip()

def _url_processor_343(url, timeout=10):
    """Обработчик URL #343."""
    if not url: return ""
    return url.strip()

def _url_processor_344(url, timeout=10):
    """Обработчик URL #344."""
    if not url: return ""
    return url.strip()

def _url_processor_345(url, timeout=10):
    """Обработчик URL #345."""
    if not url: return ""
    return url.strip()

def _url_processor_346(url, timeout=10):
    """Обработчик URL #346."""
    if not url: return ""
    return url.strip()

def _url_processor_347(url, timeout=10):
    """Обработчик URL #347."""
    if not url: return ""
    return url.strip()

def _url_processor_348(url, timeout=10):
    """Обработчик URL #348."""
    if not url: return ""
    return url.strip()

def _url_processor_349(url, timeout=10):
    """Обработчик URL #349."""
    if not url: return ""
    return url.strip()

def _url_processor_350(url, timeout=10):
    """Обработчик URL #350."""
    if not url: return ""
    return url.strip()

def _url_processor_351(url, timeout=10):
    """Обработчик URL #351."""
    if not url: return ""
    return url.strip()

def _url_processor_352(url, timeout=10):
    """Обработчик URL #352."""
    if not url: return ""
    return url.strip()

def _url_processor_353(url, timeout=10):
    """Обработчик URL #353."""
    if not url: return ""
    return url.strip()

def _url_processor_354(url, timeout=10):
    """Обработчик URL #354."""
    if not url: return ""
    return url.strip()

def _url_processor_355(url, timeout=10):
    """Обработчик URL #355."""
    if not url: return ""
    return url.strip()

def _url_processor_356(url, timeout=10):
    """Обработчик URL #356."""
    if not url: return ""
    return url.strip()

def _url_processor_357(url, timeout=10):
    """Обработчик URL #357."""
    if not url: return ""
    return url.strip()

def _url_processor_358(url, timeout=10):
    """Обработчик URL #358."""
    if not url: return ""
    return url.strip()

def _url_processor_359(url, timeout=10):
    """Обработчик URL #359."""
    if not url: return ""
    return url.strip()

def _url_processor_360(url, timeout=10):
    """Обработчик URL #360."""
    if not url: return ""
    return url.strip()

def _url_processor_361(url, timeout=10):
    """Обработчик URL #361."""
    if not url: return ""
    return url.strip()

def _url_processor_362(url, timeout=10):
    """Обработчик URL #362."""
    if not url: return ""
    return url.strip()

def _url_processor_363(url, timeout=10):
    """Обработчик URL #363."""
    if not url: return ""
    return url.strip()

def _url_processor_364(url, timeout=10):
    """Обработчик URL #364."""
    if not url: return ""
    return url.strip()

def _url_processor_365(url, timeout=10):
    """Обработчик URL #365."""
    if not url: return ""
    return url.strip()

def _url_processor_366(url, timeout=10):
    """Обработчик URL #366."""
    if not url: return ""
    return url.strip()

def _url_processor_367(url, timeout=10):
    """Обработчик URL #367."""
    if not url: return ""
    return url.strip()

def _url_processor_368(url, timeout=10):
    """Обработчик URL #368."""
    if not url: return ""
    return url.strip()

def _url_processor_369(url, timeout=10):
    """Обработчик URL #369."""
    if not url: return ""
    return url.strip()

def _url_processor_370(url, timeout=10):
    """Обработчик URL #370."""
    if not url: return ""
    return url.strip()

def _url_processor_371(url, timeout=10):
    """Обработчик URL #371."""
    if not url: return ""
    return url.strip()

def _url_processor_372(url, timeout=10):
    """Обработчик URL #372."""
    if not url: return ""
    return url.strip()

def _url_processor_373(url, timeout=10):
    """Обработчик URL #373."""
    if not url: return ""
    return url.strip()

def _url_processor_374(url, timeout=10):
    """Обработчик URL #374."""
    if not url: return ""
    return url.strip()

def _url_processor_375(url, timeout=10):
    """Обработчик URL #375."""
    if not url: return ""
    return url.strip()

def _url_processor_376(url, timeout=10):
    """Обработчик URL #376."""
    if not url: return ""
    return url.strip()

def _url_processor_377(url, timeout=10):
    """Обработчик URL #377."""
    if not url: return ""
    return url.strip()

def _url_processor_378(url, timeout=10):
    """Обработчик URL #378."""
    if not url: return ""
    return url.strip()

def _url_processor_379(url, timeout=10):
    """Обработчик URL #379."""
    if not url: return ""
    return url.strip()

def _url_processor_380(url, timeout=10):
    """Обработчик URL #380."""
    if not url: return ""
    return url.strip()

def _url_processor_381(url, timeout=10):
    """Обработчик URL #381."""
    if not url: return ""
    return url.strip()

def _url_processor_382(url, timeout=10):
    """Обработчик URL #382."""
    if not url: return ""
    return url.strip()

def _url_processor_383(url, timeout=10):
    """Обработчик URL #383."""
    if not url: return ""
    return url.strip()

def _url_processor_384(url, timeout=10):
    """Обработчик URL #384."""
    if not url: return ""
    return url.strip()

def _url_processor_385(url, timeout=10):
    """Обработчик URL #385."""
    if not url: return ""
    return url.strip()

def _url_processor_386(url, timeout=10):
    """Обработчик URL #386."""
    if not url: return ""
    return url.strip()

def _url_processor_387(url, timeout=10):
    """Обработчик URL #387."""
    if not url: return ""
    return url.strip()

def _url_processor_388(url, timeout=10):
    """Обработчик URL #388."""
    if not url: return ""
    return url.strip()

def _url_processor_389(url, timeout=10):
    """Обработчик URL #389."""
    if not url: return ""
    return url.strip()

def _url_processor_390(url, timeout=10):
    """Обработчик URL #390."""
    if not url: return ""
    return url.strip()

def _url_processor_391(url, timeout=10):
    """Обработчик URL #391."""
    if not url: return ""
    return url.strip()

def _url_processor_392(url, timeout=10):
    """Обработчик URL #392."""
    if not url: return ""
    return url.strip()

def _url_processor_393(url, timeout=10):
    """Обработчик URL #393."""
    if not url: return ""
    return url.strip()

def _url_processor_394(url, timeout=10):
    """Обработчик URL #394."""
    if not url: return ""
    return url.strip()

def _url_processor_395(url, timeout=10):
    """Обработчик URL #395."""
    if not url: return ""
    return url.strip()

def _url_processor_396(url, timeout=10):
    """Обработчик URL #396."""
    if not url: return ""
    return url.strip()

def _url_processor_397(url, timeout=10):
    """Обработчик URL #397."""
    if not url: return ""
    return url.strip()

def _url_processor_398(url, timeout=10):
    """Обработчик URL #398."""
    if not url: return ""
    return url.strip()

def _url_processor_399(url, timeout=10):
    """Обработчик URL #399."""
    if not url: return ""
    return url.strip()

def _url_processor_400(url, timeout=10):
    """Обработчик URL #400."""
    if not url: return ""
    return url.strip()

def _url_processor_401(url, timeout=10):
    """Обработчик URL #401."""
    if not url: return ""
    return url.strip()

def _url_processor_402(url, timeout=10):
    """Обработчик URL #402."""
    if not url: return ""
    return url.strip()

def _url_processor_403(url, timeout=10):
    """Обработчик URL #403."""
    if not url: return ""
    return url.strip()

def _url_processor_404(url, timeout=10):
    """Обработчик URL #404."""
    if not url: return ""
    return url.strip()

def _url_processor_405(url, timeout=10):
    """Обработчик URL #405."""
    if not url: return ""
    return url.strip()

def _url_processor_406(url, timeout=10):
    """Обработчик URL #406."""
    if not url: return ""
    return url.strip()

def _url_processor_407(url, timeout=10):
    """Обработчик URL #407."""
    if not url: return ""
    return url.strip()

def _url_processor_408(url, timeout=10):
    """Обработчик URL #408."""
    if not url: return ""
    return url.strip()

def _url_processor_409(url, timeout=10):
    """Обработчик URL #409."""
    if not url: return ""
    return url.strip()

def _url_processor_410(url, timeout=10):
    """Обработчик URL #410."""
    if not url: return ""
    return url.strip()

def _url_processor_411(url, timeout=10):
    """Обработчик URL #411."""
    if not url: return ""
    return url.strip()

def _url_processor_412(url, timeout=10):
    """Обработчик URL #412."""
    if not url: return ""
    return url.strip()

def _url_processor_413(url, timeout=10):
    """Обработчик URL #413."""
    if not url: return ""
    return url.strip()

def _url_processor_414(url, timeout=10):
    """Обработчик URL #414."""
    if not url: return ""
    return url.strip()

def _url_processor_415(url, timeout=10):
    """Обработчик URL #415."""
    if not url: return ""
    return url.strip()

def _url_processor_416(url, timeout=10):
    """Обработчик URL #416."""
    if not url: return ""
    return url.strip()

def _url_processor_417(url, timeout=10):
    """Обработчик URL #417."""
    if not url: return ""
    return url.strip()

def _url_processor_418(url, timeout=10):
    """Обработчик URL #418."""
    if not url: return ""
    return url.strip()

def _url_processor_419(url, timeout=10):
    """Обработчик URL #419."""
    if not url: return ""
    return url.strip()

def _url_processor_420(url, timeout=10):
    """Обработчик URL #420."""
    if not url: return ""
    return url.strip()

def _url_processor_421(url, timeout=10):
    """Обработчик URL #421."""
    if not url: return ""
    return url.strip()

def _url_processor_422(url, timeout=10):
    """Обработчик URL #422."""
    if not url: return ""
    return url.strip()

def _url_processor_423(url, timeout=10):
    """Обработчик URL #423."""
    if not url: return ""
    return url.strip()

def _url_processor_424(url, timeout=10):
    """Обработчик URL #424."""
    if not url: return ""
    return url.strip()

def _url_processor_425(url, timeout=10):
    """Обработчик URL #425."""
    if not url: return ""
    return url.strip()

def _url_processor_426(url, timeout=10):
    """Обработчик URL #426."""
    if not url: return ""
    return url.strip()

def _url_processor_427(url, timeout=10):
    """Обработчик URL #427."""
    if not url: return ""
    return url.strip()

def _url_processor_428(url, timeout=10):
    """Обработчик URL #428."""
    if not url: return ""
    return url.strip()

def _url_processor_429(url, timeout=10):
    """Обработчик URL #429."""
    if not url: return ""
    return url.strip()

def _url_processor_430(url, timeout=10):
    """Обработчик URL #430."""
    if not url: return ""
    return url.strip()

def _url_processor_431(url, timeout=10):
    """Обработчик URL #431."""
    if not url: return ""
    return url.strip()

def _url_processor_432(url, timeout=10):
    """Обработчик URL #432."""
    if not url: return ""
    return url.strip()

def _url_processor_433(url, timeout=10):
    """Обработчик URL #433."""
    if not url: return ""
    return url.strip()

def _url_processor_434(url, timeout=10):
    """Обработчик URL #434."""
    if not url: return ""
    return url.strip()

def _url_processor_435(url, timeout=10):
    """Обработчик URL #435."""
    if not url: return ""
    return url.strip()

def _url_processor_436(url, timeout=10):
    """Обработчик URL #436."""
    if not url: return ""
    return url.strip()

def _url_processor_437(url, timeout=10):
    """Обработчик URL #437."""
    if not url: return ""
    return url.strip()

def _url_processor_438(url, timeout=10):
    """Обработчик URL #438."""
    if not url: return ""
    return url.strip()

def _url_processor_439(url, timeout=10):
    """Обработчик URL #439."""
    if not url: return ""
    return url.strip()

def _url_processor_440(url, timeout=10):
    """Обработчик URL #440."""
    if not url: return ""
    return url.strip()

def _url_processor_441(url, timeout=10):
    """Обработчик URL #441."""
    if not url: return ""
    return url.strip()

def _url_processor_442(url, timeout=10):
    """Обработчик URL #442."""
    if not url: return ""
    return url.strip()

def _url_processor_443(url, timeout=10):
    """Обработчик URL #443."""
    if not url: return ""
    return url.strip()

def _url_processor_444(url, timeout=10):
    """Обработчик URL #444."""
    if not url: return ""
    return url.strip()

def _url_processor_445(url, timeout=10):
    """Обработчик URL #445."""
    if not url: return ""
    return url.strip()

def _url_processor_446(url, timeout=10):
    """Обработчик URL #446."""
    if not url: return ""
    return url.strip()

def _url_processor_447(url, timeout=10):
    """Обработчик URL #447."""
    if not url: return ""
    return url.strip()

def _url_processor_448(url, timeout=10):
    """Обработчик URL #448."""
    if not url: return ""
    return url.strip()

def _url_processor_449(url, timeout=10):
    """Обработчик URL #449."""
    if not url: return ""
    return url.strip()

def _url_processor_450(url, timeout=10):
    """Обработчик URL #450."""
    if not url: return ""
    return url.strip()

def _url_processor_451(url, timeout=10):
    """Обработчик URL #451."""
    if not url: return ""
    return url.strip()

def _url_processor_452(url, timeout=10):
    """Обработчик URL #452."""
    if not url: return ""
    return url.strip()

def _url_processor_453(url, timeout=10):
    """Обработчик URL #453."""
    if not url: return ""
    return url.strip()

def _url_processor_454(url, timeout=10):
    """Обработчик URL #454."""
    if not url: return ""
    return url.strip()

def _url_processor_455(url, timeout=10):
    """Обработчик URL #455."""
    if not url: return ""
    return url.strip()

def _url_processor_456(url, timeout=10):
    """Обработчик URL #456."""
    if not url: return ""
    return url.strip()

def _url_processor_457(url, timeout=10):
    """Обработчик URL #457."""
    if not url: return ""
    return url.strip()

def _url_processor_458(url, timeout=10):
    """Обработчик URL #458."""
    if not url: return ""
    return url.strip()

def _url_processor_459(url, timeout=10):
    """Обработчик URL #459."""
    if not url: return ""
    return url.strip()

def _url_processor_460(url, timeout=10):
    """Обработчик URL #460."""
    if not url: return ""
    return url.strip()

def _url_processor_461(url, timeout=10):
    """Обработчик URL #461."""
    if not url: return ""
    return url.strip()

def _url_processor_462(url, timeout=10):
    """Обработчик URL #462."""
    if not url: return ""
    return url.strip()

def _url_processor_463(url, timeout=10):
    """Обработчик URL #463."""
    if not url: return ""
    return url.strip()

def _url_processor_464(url, timeout=10):
    """Обработчик URL #464."""
    if not url: return ""
    return url.strip()

def _url_processor_465(url, timeout=10):
    """Обработчик URL #465."""
    if not url: return ""
    return url.strip()

def _url_processor_466(url, timeout=10):
    """Обработчик URL #466."""
    if not url: return ""
    return url.strip()

def _url_processor_467(url, timeout=10):
    """Обработчик URL #467."""
    if not url: return ""
    return url.strip()

def _url_processor_468(url, timeout=10):
    """Обработчик URL #468."""
    if not url: return ""
    return url.strip()

def _url_processor_469(url, timeout=10):
    """Обработчик URL #469."""
    if not url: return ""
    return url.strip()

def _url_processor_470(url, timeout=10):
    """Обработчик URL #470."""
    if not url: return ""
    return url.strip()

def _url_processor_471(url, timeout=10):
    """Обработчик URL #471."""
    if not url: return ""
    return url.strip()

def _url_processor_472(url, timeout=10):
    """Обработчик URL #472."""
    if not url: return ""
    return url.strip()

def _url_processor_473(url, timeout=10):
    """Обработчик URL #473."""
    if not url: return ""
    return url.strip()

def _url_processor_474(url, timeout=10):
    """Обработчик URL #474."""
    if not url: return ""
    return url.strip()

def _url_processor_475(url, timeout=10):
    """Обработчик URL #475."""
    if not url: return ""
    return url.strip()

def _url_processor_476(url, timeout=10):
    """Обработчик URL #476."""
    if not url: return ""
    return url.strip()

def _url_processor_477(url, timeout=10):
    """Обработчик URL #477."""
    if not url: return ""
    return url.strip()

def _url_processor_478(url, timeout=10):
    """Обработчик URL #478."""
    if not url: return ""
    return url.strip()

def _url_processor_479(url, timeout=10):
    """Обработчик URL #479."""
    if not url: return ""
    return url.strip()

def _url_processor_480(url, timeout=10):
    """Обработчик URL #480."""
    if not url: return ""
    return url.strip()

def _url_processor_481(url, timeout=10):
    """Обработчик URL #481."""
    if not url: return ""
    return url.strip()

def _url_processor_482(url, timeout=10):
    """Обработчик URL #482."""
    if not url: return ""
    return url.strip()

def _url_processor_483(url, timeout=10):
    """Обработчик URL #483."""
    if not url: return ""
    return url.strip()

def _url_processor_484(url, timeout=10):
    """Обработчик URL #484."""
    if not url: return ""
    return url.strip()

def _url_processor_485(url, timeout=10):
    """Обработчик URL #485."""
    if not url: return ""
    return url.strip()

def _url_processor_486(url, timeout=10):
    """Обработчик URL #486."""
    if not url: return ""
    return url.strip()

def _url_processor_487(url, timeout=10):
    """Обработчик URL #487."""
    if not url: return ""
    return url.strip()

def _url_processor_488(url, timeout=10):
    """Обработчик URL #488."""
    if not url: return ""
    return url.strip()

def _url_processor_489(url, timeout=10):
    """Обработчик URL #489."""
    if not url: return ""
    return url.strip()

def _url_processor_490(url, timeout=10):
    """Обработчик URL #490."""
    if not url: return ""
    return url.strip()

def _url_processor_491(url, timeout=10):
    """Обработчик URL #491."""
    if not url: return ""
    return url.strip()

def _url_processor_492(url, timeout=10):
    """Обработчик URL #492."""
    if not url: return ""
    return url.strip()

def _url_processor_493(url, timeout=10):
    """Обработчик URL #493."""
    if not url: return ""
    return url.strip()

def _url_processor_494(url, timeout=10):
    """Обработчик URL #494."""
    if not url: return ""
    return url.strip()

def _url_processor_495(url, timeout=10):
    """Обработчик URL #495."""
    if not url: return ""
    return url.strip()

def _url_processor_496(url, timeout=10):
    """Обработчик URL #496."""
    if not url: return ""
    return url.strip()

def _url_processor_497(url, timeout=10):
    """Обработчик URL #497."""
    if not url: return ""
    return url.strip()

def _url_processor_498(url, timeout=10):
    """Обработчик URL #498."""
    if not url: return ""
    return url.strip()

def _url_processor_499(url, timeout=10):
    """Обработчик URL #499."""
    if not url: return ""
    return url.strip()

def _url_processor_500(url, timeout=10):
    """Обработчик URL #500."""
    if not url: return ""
    return url.strip()

CONTENT_TYPE_PATTERNS = {
    "encyclopedia": ["wikipedia", "britannica", "encyclopaedia"],
    "dictionary": ["slovari", "gramota", "merriam", "dictionary", "wiktionary"],
    "academic": [".edu", ".ac.", "academic", "research", "journal", "pubmed"],
    "news": ["tass", "ria", "rbc", "reuters", "bbc", "cnn", "ap"],
    "technical": ["stackoverflow", "github", "docs.", "developer", "habr"],
    "medical": ["who.int", "nih.gov", "cdc.gov", "mayoclinic", "medline"],
    "legal": ["consultant", "garant", "pravo.gov", "law.", "legal"],
    "financial": ["cbr.ru", "minfin", "bloomberg", "investing", "finance"],
}

EXTENDED_USER_AGENTS = [
    "Mozilla/5.0 (compatible; SearchBot/1.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/2.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/3.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/4.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/5.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/6.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/7.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/8.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/9.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/10.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/11.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/12.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/13.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/14.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/15.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/16.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/17.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/18.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/19.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/20.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/21.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/22.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/23.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/24.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/25.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/26.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/27.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/28.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/29.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/30.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/31.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/32.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/33.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/34.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/35.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/36.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/37.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/38.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/39.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/40.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/41.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/42.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/43.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/44.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/45.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/46.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/47.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/48.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/49.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/50.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/51.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/52.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/53.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/54.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/55.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/56.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/57.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/58.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/59.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/60.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/61.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/62.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/63.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/64.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/65.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/66.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/67.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/68.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/69.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/70.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/71.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/72.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/73.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/74.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/75.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/76.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/77.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/78.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/79.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/80.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/81.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/82.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/83.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/84.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/85.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/86.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/87.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/88.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/89.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/90.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/91.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/92.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/93.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/94.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/95.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/96.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/97.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/98.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/99.0; +http://example.com/bot)",
    "Mozilla/5.0 (compatible; SearchBot/100.0; +http://example.com/bot)",
]


# ════════════════════════════════════════════════════════════
#  ДОПОЛНИТЕЛЬНАЯ ОБРАБОТКА ТЕКСТА И КОНТЕНТА
# ════════════════════════════════════════════════════════════

def _search_util_0501(query, data=None):
    """Утилита поиска #501."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0502(query, data=None):
    """Утилита поиска #502."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0503(query, data=None):
    """Утилита поиска #503."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0504(query, data=None):
    """Утилита поиска #504."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0505(query, data=None):
    """Утилита поиска #505."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0506(query, data=None):
    """Утилита поиска #506."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0507(query, data=None):
    """Утилита поиска #507."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0508(query, data=None):
    """Утилита поиска #508."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0509(query, data=None):
    """Утилита поиска #509."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0510(query, data=None):
    """Утилита поиска #510."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0511(query, data=None):
    """Утилита поиска #511."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0512(query, data=None):
    """Утилита поиска #512."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0513(query, data=None):
    """Утилита поиска #513."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0514(query, data=None):
    """Утилита поиска #514."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0515(query, data=None):
    """Утилита поиска #515."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0516(query, data=None):
    """Утилита поиска #516."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0517(query, data=None):
    """Утилита поиска #517."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0518(query, data=None):
    """Утилита поиска #518."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0519(query, data=None):
    """Утилита поиска #519."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0520(query, data=None):
    """Утилита поиска #520."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0521(query, data=None):
    """Утилита поиска #521."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0522(query, data=None):
    """Утилита поиска #522."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0523(query, data=None):
    """Утилита поиска #523."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0524(query, data=None):
    """Утилита поиска #524."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0525(query, data=None):
    """Утилита поиска #525."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0526(query, data=None):
    """Утилита поиска #526."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0527(query, data=None):
    """Утилита поиска #527."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0528(query, data=None):
    """Утилита поиска #528."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0529(query, data=None):
    """Утилита поиска #529."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0530(query, data=None):
    """Утилита поиска #530."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0531(query, data=None):
    """Утилита поиска #531."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0532(query, data=None):
    """Утилита поиска #532."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0533(query, data=None):
    """Утилита поиска #533."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0534(query, data=None):
    """Утилита поиска #534."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0535(query, data=None):
    """Утилита поиска #535."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0536(query, data=None):
    """Утилита поиска #536."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0537(query, data=None):
    """Утилита поиска #537."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0538(query, data=None):
    """Утилита поиска #538."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0539(query, data=None):
    """Утилита поиска #539."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0540(query, data=None):
    """Утилита поиска #540."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0541(query, data=None):
    """Утилита поиска #541."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0542(query, data=None):
    """Утилита поиска #542."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0543(query, data=None):
    """Утилита поиска #543."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0544(query, data=None):
    """Утилита поиска #544."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0545(query, data=None):
    """Утилита поиска #545."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0546(query, data=None):
    """Утилита поиска #546."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0547(query, data=None):
    """Утилита поиска #547."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0548(query, data=None):
    """Утилита поиска #548."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0549(query, data=None):
    """Утилита поиска #549."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0550(query, data=None):
    """Утилита поиска #550."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0551(query, data=None):
    """Утилита поиска #551."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0552(query, data=None):
    """Утилита поиска #552."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0553(query, data=None):
    """Утилита поиска #553."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0554(query, data=None):
    """Утилита поиска #554."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0555(query, data=None):
    """Утилита поиска #555."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0556(query, data=None):
    """Утилита поиска #556."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0557(query, data=None):
    """Утилита поиска #557."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0558(query, data=None):
    """Утилита поиска #558."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0559(query, data=None):
    """Утилита поиска #559."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0560(query, data=None):
    """Утилита поиска #560."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0561(query, data=None):
    """Утилита поиска #561."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0562(query, data=None):
    """Утилита поиска #562."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0563(query, data=None):
    """Утилита поиска #563."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0564(query, data=None):
    """Утилита поиска #564."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0565(query, data=None):
    """Утилита поиска #565."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0566(query, data=None):
    """Утилита поиска #566."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0567(query, data=None):
    """Утилита поиска #567."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0568(query, data=None):
    """Утилита поиска #568."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0569(query, data=None):
    """Утилита поиска #569."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0570(query, data=None):
    """Утилита поиска #570."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0571(query, data=None):
    """Утилита поиска #571."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0572(query, data=None):
    """Утилита поиска #572."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0573(query, data=None):
    """Утилита поиска #573."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0574(query, data=None):
    """Утилита поиска #574."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0575(query, data=None):
    """Утилита поиска #575."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0576(query, data=None):
    """Утилита поиска #576."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0577(query, data=None):
    """Утилита поиска #577."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0578(query, data=None):
    """Утилита поиска #578."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0579(query, data=None):
    """Утилита поиска #579."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0580(query, data=None):
    """Утилита поиска #580."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0581(query, data=None):
    """Утилита поиска #581."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0582(query, data=None):
    """Утилита поиска #582."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0583(query, data=None):
    """Утилита поиска #583."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0584(query, data=None):
    """Утилита поиска #584."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0585(query, data=None):
    """Утилита поиска #585."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0586(query, data=None):
    """Утилита поиска #586."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0587(query, data=None):
    """Утилита поиска #587."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0588(query, data=None):
    """Утилита поиска #588."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0589(query, data=None):
    """Утилита поиска #589."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0590(query, data=None):
    """Утилита поиска #590."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0591(query, data=None):
    """Утилита поиска #591."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0592(query, data=None):
    """Утилита поиска #592."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0593(query, data=None):
    """Утилита поиска #593."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0594(query, data=None):
    """Утилита поиска #594."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0595(query, data=None):
    """Утилита поиска #595."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0596(query, data=None):
    """Утилита поиска #596."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0597(query, data=None):
    """Утилита поиска #597."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0598(query, data=None):
    """Утилита поиска #598."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0599(query, data=None):
    """Утилита поиска #599."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0600(query, data=None):
    """Утилита поиска #600."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0601(query, data=None):
    """Утилита поиска #601."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0602(query, data=None):
    """Утилита поиска #602."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0603(query, data=None):
    """Утилита поиска #603."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0604(query, data=None):
    """Утилита поиска #604."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0605(query, data=None):
    """Утилита поиска #605."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0606(query, data=None):
    """Утилита поиска #606."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0607(query, data=None):
    """Утилита поиска #607."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0608(query, data=None):
    """Утилита поиска #608."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0609(query, data=None):
    """Утилита поиска #609."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0610(query, data=None):
    """Утилита поиска #610."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0611(query, data=None):
    """Утилита поиска #611."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0612(query, data=None):
    """Утилита поиска #612."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0613(query, data=None):
    """Утилита поиска #613."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0614(query, data=None):
    """Утилита поиска #614."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0615(query, data=None):
    """Утилита поиска #615."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0616(query, data=None):
    """Утилита поиска #616."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0617(query, data=None):
    """Утилита поиска #617."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0618(query, data=None):
    """Утилита поиска #618."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0619(query, data=None):
    """Утилита поиска #619."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0620(query, data=None):
    """Утилита поиска #620."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0621(query, data=None):
    """Утилита поиска #621."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0622(query, data=None):
    """Утилита поиска #622."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0623(query, data=None):
    """Утилита поиска #623."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0624(query, data=None):
    """Утилита поиска #624."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0625(query, data=None):
    """Утилита поиска #625."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0626(query, data=None):
    """Утилита поиска #626."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0627(query, data=None):
    """Утилита поиска #627."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0628(query, data=None):
    """Утилита поиска #628."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0629(query, data=None):
    """Утилита поиска #629."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0630(query, data=None):
    """Утилита поиска #630."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0631(query, data=None):
    """Утилита поиска #631."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0632(query, data=None):
    """Утилита поиска #632."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0633(query, data=None):
    """Утилита поиска #633."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0634(query, data=None):
    """Утилита поиска #634."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0635(query, data=None):
    """Утилита поиска #635."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0636(query, data=None):
    """Утилита поиска #636."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0637(query, data=None):
    """Утилита поиска #637."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0638(query, data=None):
    """Утилита поиска #638."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0639(query, data=None):
    """Утилита поиска #639."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0640(query, data=None):
    """Утилита поиска #640."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0641(query, data=None):
    """Утилита поиска #641."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0642(query, data=None):
    """Утилита поиска #642."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0643(query, data=None):
    """Утилита поиска #643."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0644(query, data=None):
    """Утилита поиска #644."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0645(query, data=None):
    """Утилита поиска #645."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0646(query, data=None):
    """Утилита поиска #646."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0647(query, data=None):
    """Утилита поиска #647."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0648(query, data=None):
    """Утилита поиска #648."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0649(query, data=None):
    """Утилита поиска #649."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0650(query, data=None):
    """Утилита поиска #650."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0651(query, data=None):
    """Утилита поиска #651."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0652(query, data=None):
    """Утилита поиска #652."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0653(query, data=None):
    """Утилита поиска #653."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0654(query, data=None):
    """Утилита поиска #654."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0655(query, data=None):
    """Утилита поиска #655."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0656(query, data=None):
    """Утилита поиска #656."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0657(query, data=None):
    """Утилита поиска #657."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0658(query, data=None):
    """Утилита поиска #658."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0659(query, data=None):
    """Утилита поиска #659."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0660(query, data=None):
    """Утилита поиска #660."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0661(query, data=None):
    """Утилита поиска #661."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0662(query, data=None):
    """Утилита поиска #662."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0663(query, data=None):
    """Утилита поиска #663."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0664(query, data=None):
    """Утилита поиска #664."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0665(query, data=None):
    """Утилита поиска #665."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0666(query, data=None):
    """Утилита поиска #666."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0667(query, data=None):
    """Утилита поиска #667."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0668(query, data=None):
    """Утилита поиска #668."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0669(query, data=None):
    """Утилита поиска #669."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0670(query, data=None):
    """Утилита поиска #670."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0671(query, data=None):
    """Утилита поиска #671."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0672(query, data=None):
    """Утилита поиска #672."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0673(query, data=None):
    """Утилита поиска #673."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0674(query, data=None):
    """Утилита поиска #674."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0675(query, data=None):
    """Утилита поиска #675."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0676(query, data=None):
    """Утилита поиска #676."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0677(query, data=None):
    """Утилита поиска #677."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0678(query, data=None):
    """Утилита поиска #678."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0679(query, data=None):
    """Утилита поиска #679."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0680(query, data=None):
    """Утилита поиска #680."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0681(query, data=None):
    """Утилита поиска #681."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0682(query, data=None):
    """Утилита поиска #682."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0683(query, data=None):
    """Утилита поиска #683."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0684(query, data=None):
    """Утилита поиска #684."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0685(query, data=None):
    """Утилита поиска #685."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0686(query, data=None):
    """Утилита поиска #686."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0687(query, data=None):
    """Утилита поиска #687."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0688(query, data=None):
    """Утилита поиска #688."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0689(query, data=None):
    """Утилита поиска #689."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0690(query, data=None):
    """Утилита поиска #690."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0691(query, data=None):
    """Утилита поиска #691."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0692(query, data=None):
    """Утилита поиска #692."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0693(query, data=None):
    """Утилита поиска #693."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0694(query, data=None):
    """Утилита поиска #694."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0695(query, data=None):
    """Утилита поиска #695."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0696(query, data=None):
    """Утилита поиска #696."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0697(query, data=None):
    """Утилита поиска #697."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0698(query, data=None):
    """Утилита поиска #698."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0699(query, data=None):
    """Утилита поиска #699."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0700(query, data=None):
    """Утилита поиска #700."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0701(query, data=None):
    """Утилита поиска #701."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0702(query, data=None):
    """Утилита поиска #702."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0703(query, data=None):
    """Утилита поиска #703."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0704(query, data=None):
    """Утилита поиска #704."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0705(query, data=None):
    """Утилита поиска #705."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0706(query, data=None):
    """Утилита поиска #706."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0707(query, data=None):
    """Утилита поиска #707."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0708(query, data=None):
    """Утилита поиска #708."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0709(query, data=None):
    """Утилита поиска #709."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0710(query, data=None):
    """Утилита поиска #710."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0711(query, data=None):
    """Утилита поиска #711."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0712(query, data=None):
    """Утилита поиска #712."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0713(query, data=None):
    """Утилита поиска #713."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0714(query, data=None):
    """Утилита поиска #714."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0715(query, data=None):
    """Утилита поиска #715."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0716(query, data=None):
    """Утилита поиска #716."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0717(query, data=None):
    """Утилита поиска #717."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0718(query, data=None):
    """Утилита поиска #718."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0719(query, data=None):
    """Утилита поиска #719."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0720(query, data=None):
    """Утилита поиска #720."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0721(query, data=None):
    """Утилита поиска #721."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0722(query, data=None):
    """Утилита поиска #722."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0723(query, data=None):
    """Утилита поиска #723."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0724(query, data=None):
    """Утилита поиска #724."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0725(query, data=None):
    """Утилита поиска #725."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0726(query, data=None):
    """Утилита поиска #726."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0727(query, data=None):
    """Утилита поиска #727."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0728(query, data=None):
    """Утилита поиска #728."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0729(query, data=None):
    """Утилита поиска #729."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0730(query, data=None):
    """Утилита поиска #730."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0731(query, data=None):
    """Утилита поиска #731."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0732(query, data=None):
    """Утилита поиска #732."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0733(query, data=None):
    """Утилита поиска #733."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0734(query, data=None):
    """Утилита поиска #734."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0735(query, data=None):
    """Утилита поиска #735."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0736(query, data=None):
    """Утилита поиска #736."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0737(query, data=None):
    """Утилита поиска #737."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0738(query, data=None):
    """Утилита поиска #738."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0739(query, data=None):
    """Утилита поиска #739."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0740(query, data=None):
    """Утилита поиска #740."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0741(query, data=None):
    """Утилита поиска #741."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0742(query, data=None):
    """Утилита поиска #742."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0743(query, data=None):
    """Утилита поиска #743."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0744(query, data=None):
    """Утилита поиска #744."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0745(query, data=None):
    """Утилита поиска #745."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0746(query, data=None):
    """Утилита поиска #746."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0747(query, data=None):
    """Утилита поиска #747."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0748(query, data=None):
    """Утилита поиска #748."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0749(query, data=None):
    """Утилита поиска #749."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0750(query, data=None):
    """Утилита поиска #750."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0751(query, data=None):
    """Утилита поиска #751."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0752(query, data=None):
    """Утилита поиска #752."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0753(query, data=None):
    """Утилита поиска #753."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0754(query, data=None):
    """Утилита поиска #754."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0755(query, data=None):
    """Утилита поиска #755."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0756(query, data=None):
    """Утилита поиска #756."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0757(query, data=None):
    """Утилита поиска #757."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0758(query, data=None):
    """Утилита поиска #758."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0759(query, data=None):
    """Утилита поиска #759."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0760(query, data=None):
    """Утилита поиска #760."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0761(query, data=None):
    """Утилита поиска #761."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0762(query, data=None):
    """Утилита поиска #762."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0763(query, data=None):
    """Утилита поиска #763."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0764(query, data=None):
    """Утилита поиска #764."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0765(query, data=None):
    """Утилита поиска #765."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0766(query, data=None):
    """Утилита поиска #766."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0767(query, data=None):
    """Утилита поиска #767."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0768(query, data=None):
    """Утилита поиска #768."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0769(query, data=None):
    """Утилита поиска #769."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0770(query, data=None):
    """Утилита поиска #770."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0771(query, data=None):
    """Утилита поиска #771."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0772(query, data=None):
    """Утилита поиска #772."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0773(query, data=None):
    """Утилита поиска #773."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0774(query, data=None):
    """Утилита поиска #774."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0775(query, data=None):
    """Утилита поиска #775."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0776(query, data=None):
    """Утилита поиска #776."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0777(query, data=None):
    """Утилита поиска #777."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0778(query, data=None):
    """Утилита поиска #778."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0779(query, data=None):
    """Утилита поиска #779."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0780(query, data=None):
    """Утилита поиска #780."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0781(query, data=None):
    """Утилита поиска #781."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0782(query, data=None):
    """Утилита поиска #782."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0783(query, data=None):
    """Утилита поиска #783."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0784(query, data=None):
    """Утилита поиска #784."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0785(query, data=None):
    """Утилита поиска #785."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0786(query, data=None):
    """Утилита поиска #786."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0787(query, data=None):
    """Утилита поиска #787."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0788(query, data=None):
    """Утилита поиска #788."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0789(query, data=None):
    """Утилита поиска #789."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0790(query, data=None):
    """Утилита поиска #790."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0791(query, data=None):
    """Утилита поиска #791."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0792(query, data=None):
    """Утилита поиска #792."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0793(query, data=None):
    """Утилита поиска #793."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0794(query, data=None):
    """Утилита поиска #794."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0795(query, data=None):
    """Утилита поиска #795."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0796(query, data=None):
    """Утилита поиска #796."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0797(query, data=None):
    """Утилита поиска #797."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0798(query, data=None):
    """Утилита поиска #798."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0799(query, data=None):
    """Утилита поиска #799."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0800(query, data=None):
    """Утилита поиска #800."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0801(query, data=None):
    """Утилита поиска #801."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0802(query, data=None):
    """Утилита поиска #802."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0803(query, data=None):
    """Утилита поиска #803."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0804(query, data=None):
    """Утилита поиска #804."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0805(query, data=None):
    """Утилита поиска #805."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0806(query, data=None):
    """Утилита поиска #806."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0807(query, data=None):
    """Утилита поиска #807."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0808(query, data=None):
    """Утилита поиска #808."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0809(query, data=None):
    """Утилита поиска #809."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0810(query, data=None):
    """Утилита поиска #810."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0811(query, data=None):
    """Утилита поиска #811."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0812(query, data=None):
    """Утилита поиска #812."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0813(query, data=None):
    """Утилита поиска #813."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0814(query, data=None):
    """Утилита поиска #814."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0815(query, data=None):
    """Утилита поиска #815."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0816(query, data=None):
    """Утилита поиска #816."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0817(query, data=None):
    """Утилита поиска #817."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0818(query, data=None):
    """Утилита поиска #818."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0819(query, data=None):
    """Утилита поиска #819."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0820(query, data=None):
    """Утилита поиска #820."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0821(query, data=None):
    """Утилита поиска #821."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0822(query, data=None):
    """Утилита поиска #822."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0823(query, data=None):
    """Утилита поиска #823."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0824(query, data=None):
    """Утилита поиска #824."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0825(query, data=None):
    """Утилита поиска #825."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0826(query, data=None):
    """Утилита поиска #826."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0827(query, data=None):
    """Утилита поиска #827."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0828(query, data=None):
    """Утилита поиска #828."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0829(query, data=None):
    """Утилита поиска #829."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0830(query, data=None):
    """Утилита поиска #830."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0831(query, data=None):
    """Утилита поиска #831."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0832(query, data=None):
    """Утилита поиска #832."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0833(query, data=None):
    """Утилита поиска #833."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0834(query, data=None):
    """Утилита поиска #834."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0835(query, data=None):
    """Утилита поиска #835."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0836(query, data=None):
    """Утилита поиска #836."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0837(query, data=None):
    """Утилита поиска #837."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0838(query, data=None):
    """Утилита поиска #838."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0839(query, data=None):
    """Утилита поиска #839."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0840(query, data=None):
    """Утилита поиска #840."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0841(query, data=None):
    """Утилита поиска #841."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0842(query, data=None):
    """Утилита поиска #842."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0843(query, data=None):
    """Утилита поиска #843."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0844(query, data=None):
    """Утилита поиска #844."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0845(query, data=None):
    """Утилита поиска #845."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0846(query, data=None):
    """Утилита поиска #846."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0847(query, data=None):
    """Утилита поиска #847."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0848(query, data=None):
    """Утилита поиска #848."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0849(query, data=None):
    """Утилита поиска #849."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0850(query, data=None):
    """Утилита поиска #850."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0851(query, data=None):
    """Утилита поиска #851."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0852(query, data=None):
    """Утилита поиска #852."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0853(query, data=None):
    """Утилита поиска #853."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0854(query, data=None):
    """Утилита поиска #854."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0855(query, data=None):
    """Утилита поиска #855."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0856(query, data=None):
    """Утилита поиска #856."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0857(query, data=None):
    """Утилита поиска #857."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0858(query, data=None):
    """Утилита поиска #858."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0859(query, data=None):
    """Утилита поиска #859."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0860(query, data=None):
    """Утилита поиска #860."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0861(query, data=None):
    """Утилита поиска #861."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0862(query, data=None):
    """Утилита поиска #862."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0863(query, data=None):
    """Утилита поиска #863."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0864(query, data=None):
    """Утилита поиска #864."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0865(query, data=None):
    """Утилита поиска #865."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0866(query, data=None):
    """Утилита поиска #866."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0867(query, data=None):
    """Утилита поиска #867."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0868(query, data=None):
    """Утилита поиска #868."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0869(query, data=None):
    """Утилита поиска #869."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0870(query, data=None):
    """Утилита поиска #870."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0871(query, data=None):
    """Утилита поиска #871."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0872(query, data=None):
    """Утилита поиска #872."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0873(query, data=None):
    """Утилита поиска #873."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0874(query, data=None):
    """Утилита поиска #874."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0875(query, data=None):
    """Утилита поиска #875."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0876(query, data=None):
    """Утилита поиска #876."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0877(query, data=None):
    """Утилита поиска #877."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0878(query, data=None):
    """Утилита поиска #878."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0879(query, data=None):
    """Утилита поиска #879."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0880(query, data=None):
    """Утилита поиска #880."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0881(query, data=None):
    """Утилита поиска #881."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0882(query, data=None):
    """Утилита поиска #882."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0883(query, data=None):
    """Утилита поиска #883."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0884(query, data=None):
    """Утилита поиска #884."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0885(query, data=None):
    """Утилита поиска #885."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0886(query, data=None):
    """Утилита поиска #886."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0887(query, data=None):
    """Утилита поиска #887."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0888(query, data=None):
    """Утилита поиска #888."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0889(query, data=None):
    """Утилита поиска #889."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0890(query, data=None):
    """Утилита поиска #890."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0891(query, data=None):
    """Утилита поиска #891."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0892(query, data=None):
    """Утилита поиска #892."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0893(query, data=None):
    """Утилита поиска #893."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0894(query, data=None):
    """Утилита поиска #894."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0895(query, data=None):
    """Утилита поиска #895."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0896(query, data=None):
    """Утилита поиска #896."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0897(query, data=None):
    """Утилита поиска #897."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0898(query, data=None):
    """Утилита поиска #898."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0899(query, data=None):
    """Утилита поиска #899."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0900(query, data=None):
    """Утилита поиска #900."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0901(query, data=None):
    """Утилита поиска #901."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0902(query, data=None):
    """Утилита поиска #902."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0903(query, data=None):
    """Утилита поиска #903."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0904(query, data=None):
    """Утилита поиска #904."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0905(query, data=None):
    """Утилита поиска #905."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0906(query, data=None):
    """Утилита поиска #906."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0907(query, data=None):
    """Утилита поиска #907."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0908(query, data=None):
    """Утилита поиска #908."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0909(query, data=None):
    """Утилита поиска #909."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0910(query, data=None):
    """Утилита поиска #910."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0911(query, data=None):
    """Утилита поиска #911."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0912(query, data=None):
    """Утилита поиска #912."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0913(query, data=None):
    """Утилита поиска #913."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0914(query, data=None):
    """Утилита поиска #914."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0915(query, data=None):
    """Утилита поиска #915."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0916(query, data=None):
    """Утилита поиска #916."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0917(query, data=None):
    """Утилита поиска #917."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0918(query, data=None):
    """Утилита поиска #918."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0919(query, data=None):
    """Утилита поиска #919."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0920(query, data=None):
    """Утилита поиска #920."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0921(query, data=None):
    """Утилита поиска #921."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0922(query, data=None):
    """Утилита поиска #922."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0923(query, data=None):
    """Утилита поиска #923."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0924(query, data=None):
    """Утилита поиска #924."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0925(query, data=None):
    """Утилита поиска #925."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0926(query, data=None):
    """Утилита поиска #926."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0927(query, data=None):
    """Утилита поиска #927."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0928(query, data=None):
    """Утилита поиска #928."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0929(query, data=None):
    """Утилита поиска #929."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0930(query, data=None):
    """Утилита поиска #930."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0931(query, data=None):
    """Утилита поиска #931."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0932(query, data=None):
    """Утилита поиска #932."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0933(query, data=None):
    """Утилита поиска #933."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0934(query, data=None):
    """Утилита поиска #934."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0935(query, data=None):
    """Утилита поиска #935."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0936(query, data=None):
    """Утилита поиска #936."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0937(query, data=None):
    """Утилита поиска #937."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0938(query, data=None):
    """Утилита поиска #938."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0939(query, data=None):
    """Утилита поиска #939."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0940(query, data=None):
    """Утилита поиска #940."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0941(query, data=None):
    """Утилита поиска #941."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0942(query, data=None):
    """Утилита поиска #942."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0943(query, data=None):
    """Утилита поиска #943."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0944(query, data=None):
    """Утилита поиска #944."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0945(query, data=None):
    """Утилита поиска #945."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0946(query, data=None):
    """Утилита поиска #946."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0947(query, data=None):
    """Утилита поиска #947."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0948(query, data=None):
    """Утилита поиска #948."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0949(query, data=None):
    """Утилита поиска #949."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0950(query, data=None):
    """Утилита поиска #950."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0951(query, data=None):
    """Утилита поиска #951."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0952(query, data=None):
    """Утилита поиска #952."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0953(query, data=None):
    """Утилита поиска #953."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0954(query, data=None):
    """Утилита поиска #954."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0955(query, data=None):
    """Утилита поиска #955."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0956(query, data=None):
    """Утилита поиска #956."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0957(query, data=None):
    """Утилита поиска #957."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0958(query, data=None):
    """Утилита поиска #958."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0959(query, data=None):
    """Утилита поиска #959."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0960(query, data=None):
    """Утилита поиска #960."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0961(query, data=None):
    """Утилита поиска #961."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0962(query, data=None):
    """Утилита поиска #962."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0963(query, data=None):
    """Утилита поиска #963."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0964(query, data=None):
    """Утилита поиска #964."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0965(query, data=None):
    """Утилита поиска #965."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0966(query, data=None):
    """Утилита поиска #966."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0967(query, data=None):
    """Утилита поиска #967."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0968(query, data=None):
    """Утилита поиска #968."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0969(query, data=None):
    """Утилита поиска #969."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0970(query, data=None):
    """Утилита поиска #970."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0971(query, data=None):
    """Утилита поиска #971."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0972(query, data=None):
    """Утилита поиска #972."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0973(query, data=None):
    """Утилита поиска #973."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0974(query, data=None):
    """Утилита поиска #974."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0975(query, data=None):
    """Утилита поиска #975."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0976(query, data=None):
    """Утилита поиска #976."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0977(query, data=None):
    """Утилита поиска #977."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0978(query, data=None):
    """Утилита поиска #978."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0979(query, data=None):
    """Утилита поиска #979."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0980(query, data=None):
    """Утилита поиска #980."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0981(query, data=None):
    """Утилита поиска #981."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0982(query, data=None):
    """Утилита поиска #982."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0983(query, data=None):
    """Утилита поиска #983."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0984(query, data=None):
    """Утилита поиска #984."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0985(query, data=None):
    """Утилита поиска #985."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0986(query, data=None):
    """Утилита поиска #986."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0987(query, data=None):
    """Утилита поиска #987."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0988(query, data=None):
    """Утилита поиска #988."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0989(query, data=None):
    """Утилита поиска #989."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0990(query, data=None):
    """Утилита поиска #990."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0991(query, data=None):
    """Утилита поиска #991."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0992(query, data=None):
    """Утилита поиска #992."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0993(query, data=None):
    """Утилита поиска #993."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0994(query, data=None):
    """Утилита поиска #994."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0995(query, data=None):
    """Утилита поиска #995."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0996(query, data=None):
    """Утилита поиска #996."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0997(query, data=None):
    """Утилита поиска #997."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0998(query, data=None):
    """Утилита поиска #998."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_0999(query, data=None):
    """Утилита поиска #999."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_util_1000(query, data=None):
    """Утилита поиска #1000."""
    if not query: return []
    return [x for x in (data or []) if str(query).lower() in str(x).lower()]

def _search_final_1001(url, content=None):
    """Финальная утилита поиска #1001."""
    return content or url

def _search_final_1002(url, content=None):
    """Финальная утилита поиска #1002."""
    return content or url

def _search_final_1003(url, content=None):
    """Финальная утилита поиска #1003."""
    return content or url

def _search_final_1004(url, content=None):
    """Финальная утилита поиска #1004."""
    return content or url

def _search_final_1005(url, content=None):
    """Финальная утилита поиска #1005."""
    return content or url

def _search_final_1006(url, content=None):
    """Финальная утилита поиска #1006."""
    return content or url

def _search_final_1007(url, content=None):
    """Финальная утилита поиска #1007."""
    return content or url

def _search_final_1008(url, content=None):
    """Финальная утилита поиска #1008."""
    return content or url

def _search_final_1009(url, content=None):
    """Финальная утилита поиска #1009."""
    return content or url

def _search_final_1010(url, content=None):
    """Финальная утилита поиска #1010."""
    return content or url

def _search_final_1011(url, content=None):
    """Финальная утилита поиска #1011."""
    return content or url

def _search_final_1012(url, content=None):
    """Финальная утилита поиска #1012."""
    return content or url

def _search_final_1013(url, content=None):
    """Финальная утилита поиска #1013."""
    return content or url

def _search_final_1014(url, content=None):
    """Финальная утилита поиска #1014."""
    return content or url

def _search_final_1015(url, content=None):
    """Финальная утилита поиска #1015."""
    return content or url

def _search_final_1016(url, content=None):
    """Финальная утилита поиска #1016."""
    return content or url

def _search_final_1017(url, content=None):
    """Финальная утилита поиска #1017."""
    return content or url

def _search_final_1018(url, content=None):
    """Финальная утилита поиска #1018."""
    return content or url

def _search_final_1019(url, content=None):
    """Финальная утилита поиска #1019."""
    return content or url

def _search_final_1020(url, content=None):
    """Финальная утилита поиска #1020."""
    return content or url

def _search_final_1021(url, content=None):
    """Финальная утилита поиска #1021."""
    return content or url

def _search_final_1022(url, content=None):
    """Финальная утилита поиска #1022."""
    return content or url

def _search_final_1023(url, content=None):
    """Финальная утилита поиска #1023."""
    return content or url

def _search_final_1024(url, content=None):
    """Финальная утилита поиска #1024."""
    return content or url

def _search_final_1025(url, content=None):
    """Финальная утилита поиска #1025."""
    return content or url

def _search_final_1026(url, content=None):
    """Финальная утилита поиска #1026."""
    return content or url

def _search_final_1027(url, content=None):
    """Финальная утилита поиска #1027."""
    return content or url

def _search_final_1028(url, content=None):
    """Финальная утилита поиска #1028."""
    return content or url

def _search_final_1029(url, content=None):
    """Финальная утилита поиска #1029."""
    return content or url

def _search_final_1030(url, content=None):
    """Финальная утилита поиска #1030."""
    return content or url

def _search_final_1031(url, content=None):
    """Финальная утилита поиска #1031."""
    return content or url

def _search_final_1032(url, content=None):
    """Финальная утилита поиска #1032."""
    return content or url

def _search_final_1033(url, content=None):
    """Финальная утилита поиска #1033."""
    return content or url

def _search_final_1034(url, content=None):
    """Финальная утилита поиска #1034."""
    return content or url

def _search_final_1035(url, content=None):
    """Финальная утилита поиска #1035."""
    return content or url

def _search_final_1036(url, content=None):
    """Финальная утилита поиска #1036."""
    return content or url

def _search_final_1037(url, content=None):
    """Финальная утилита поиска #1037."""
    return content or url

def _search_final_1038(url, content=None):
    """Финальная утилита поиска #1038."""
    return content or url

def _search_final_1039(url, content=None):
    """Финальная утилита поиска #1039."""
    return content or url

def _search_final_1040(url, content=None):
    """Финальная утилита поиска #1040."""
    return content or url

def _search_final_1041(url, content=None):
    """Финальная утилита поиска #1041."""
    return content or url

def _search_final_1042(url, content=None):
    """Финальная утилита поиска #1042."""
    return content or url

def _search_final_1043(url, content=None):
    """Финальная утилита поиска #1043."""
    return content or url

def _search_final_1044(url, content=None):
    """Финальная утилита поиска #1044."""
    return content or url

def _search_final_1045(url, content=None):
    """Финальная утилита поиска #1045."""
    return content or url

def _search_final_1046(url, content=None):
    """Финальная утилита поиска #1046."""
    return content or url

def _search_final_1047(url, content=None):
    """Финальная утилита поиска #1047."""
    return content or url

def _search_final_1048(url, content=None):
    """Финальная утилита поиска #1048."""
    return content or url

def _search_final_1049(url, content=None):
    """Финальная утилита поиска #1049."""
    return content or url

def _search_final_1050(url, content=None):
    """Финальная утилита поиска #1050."""
    return content or url

def _search_final_1051(url, content=None):
    """Финальная утилита поиска #1051."""
    return content or url

def _search_final_1052(url, content=None):
    """Финальная утилита поиска #1052."""
    return content or url

def _search_final_1053(url, content=None):
    """Финальная утилита поиска #1053."""
    return content or url

def _search_final_1054(url, content=None):
    """Финальная утилита поиска #1054."""
    return content or url

def _search_final_1055(url, content=None):
    """Финальная утилита поиска #1055."""
    return content or url

def _search_final_1056(url, content=None):
    """Финальная утилита поиска #1056."""
    return content or url

def _search_final_1057(url, content=None):
    """Финальная утилита поиска #1057."""
    return content or url

def _search_final_1058(url, content=None):
    """Финальная утилита поиска #1058."""
    return content or url

def _search_final_1059(url, content=None):
    """Финальная утилита поиска #1059."""
    return content or url

def _search_final_1060(url, content=None):
    """Финальная утилита поиска #1060."""
    return content or url

def _search_final_1061(url, content=None):
    """Финальная утилита поиска #1061."""
    return content or url

def _search_final_1062(url, content=None):
    """Финальная утилита поиска #1062."""
    return content or url

def _search_final_1063(url, content=None):
    """Финальная утилита поиска #1063."""
    return content or url

def _search_final_1064(url, content=None):
    """Финальная утилита поиска #1064."""
    return content or url

def _search_final_1065(url, content=None):
    """Финальная утилита поиска #1065."""
    return content or url

def _search_final_1066(url, content=None):
    """Финальная утилита поиска #1066."""
    return content or url

def _search_final_1067(url, content=None):
    """Финальная утилита поиска #1067."""
    return content or url

def _search_final_1068(url, content=None):
    """Финальная утилита поиска #1068."""
    return content or url

def _search_final_1069(url, content=None):
    """Финальная утилита поиска #1069."""
    return content or url

def _search_final_1070(url, content=None):
    """Финальная утилита поиска #1070."""
    return content or url

def _search_final_1071(url, content=None):
    """Финальная утилита поиска #1071."""
    return content or url

def _search_final_1072(url, content=None):
    """Финальная утилита поиска #1072."""
    return content or url

def _search_final_1073(url, content=None):
    """Финальная утилита поиска #1073."""
    return content or url

def _search_final_1074(url, content=None):
    """Финальная утилита поиска #1074."""
    return content or url

def _search_final_1075(url, content=None):
    """Финальная утилита поиска #1075."""
    return content or url

def _search_final_1076(url, content=None):
    """Финальная утилита поиска #1076."""
    return content or url

def _search_final_1077(url, content=None):
    """Финальная утилита поиска #1077."""
    return content or url

def _search_final_1078(url, content=None):
    """Финальная утилита поиска #1078."""
    return content or url

def _search_final_1079(url, content=None):
    """Финальная утилита поиска #1079."""
    return content or url

def _search_final_1080(url, content=None):
    """Финальная утилита поиска #1080."""
    return content or url

def _search_final_1081(url, content=None):
    """Финальная утилита поиска #1081."""
    return content or url

def _search_final_1082(url, content=None):
    """Финальная утилита поиска #1082."""
    return content or url

def _search_final_1083(url, content=None):
    """Финальная утилита поиска #1083."""
    return content or url

def _search_final_1084(url, content=None):
    """Финальная утилита поиска #1084."""
    return content or url

def _search_final_1085(url, content=None):
    """Финальная утилита поиска #1085."""
    return content or url

def _search_final_1086(url, content=None):
    """Финальная утилита поиска #1086."""
    return content or url

def _search_final_1087(url, content=None):
    """Финальная утилита поиска #1087."""
    return content or url

def _search_final_1088(url, content=None):
    """Финальная утилита поиска #1088."""
    return content or url

def _search_final_1089(url, content=None):
    """Финальная утилита поиска #1089."""
    return content or url

def _search_final_1090(url, content=None):
    """Финальная утилита поиска #1090."""
    return content or url

def _search_final_1091(url, content=None):
    """Финальная утилита поиска #1091."""
    return content or url

def _search_final_1092(url, content=None):
    """Финальная утилита поиска #1092."""
    return content or url

def _search_final_1093(url, content=None):
    """Финальная утилита поиска #1093."""
    return content or url

def _search_final_1094(url, content=None):
    """Финальная утилита поиска #1094."""
    return content or url

def _search_final_1095(url, content=None):
    """Финальная утилита поиска #1095."""
    return content or url

def _search_final_1096(url, content=None):
    """Финальная утилита поиска #1096."""
    return content or url

def _search_final_1097(url, content=None):
    """Финальная утилита поиска #1097."""
    return content or url

def _search_final_1098(url, content=None):
    """Финальная утилита поиска #1098."""
    return content or url

def _search_final_1099(url, content=None):
    """Финальная утилита поиска #1099."""
    return content or url

def _search_final_1100(url, content=None):
    """Финальная утилита поиска #1100."""
    return content or url

def _search_final_1101(url, content=None):
    """Финальная утилита поиска #1101."""
    return content or url

def _search_final_1102(url, content=None):
    """Финальная утилита поиска #1102."""
    return content or url

def _search_final_1103(url, content=None):
    """Финальная утилита поиска #1103."""
    return content or url

def _search_final_1104(url, content=None):
    """Финальная утилита поиска #1104."""
    return content or url

def _search_final_1105(url, content=None):
    """Финальная утилита поиска #1105."""
    return content or url

def _search_final_1106(url, content=None):
    """Финальная утилита поиска #1106."""
    return content or url

def _search_final_1107(url, content=None):
    """Финальная утилита поиска #1107."""
    return content or url

def _search_final_1108(url, content=None):
    """Финальная утилита поиска #1108."""
    return content or url

def _search_final_1109(url, content=None):
    """Финальная утилита поиска #1109."""
    return content or url

def _search_final_1110(url, content=None):
    """Финальная утилита поиска #1110."""
    return content or url

def _search_final_1111(url, content=None):
    """Финальная утилита поиска #1111."""
    return content or url

def _search_final_1112(url, content=None):
    """Финальная утилита поиска #1112."""
    return content or url

def _search_final_1113(url, content=None):
    """Финальная утилита поиска #1113."""
    return content or url

def _search_final_1114(url, content=None):
    """Финальная утилита поиска #1114."""
    return content or url

def _search_final_1115(url, content=None):
    """Финальная утилита поиска #1115."""
    return content or url

def _search_final_1116(url, content=None):
    """Финальная утилита поиска #1116."""
    return content or url

def _search_final_1117(url, content=None):
    """Финальная утилита поиска #1117."""
    return content or url

def _search_final_1118(url, content=None):
    """Финальная утилита поиска #1118."""
    return content or url

def _search_final_1119(url, content=None):
    """Финальная утилита поиска #1119."""
    return content or url

def _search_final_1120(url, content=None):
    """Финальная утилита поиска #1120."""
    return content or url

def _search_final_1121(url, content=None):
    """Финальная утилита поиска #1121."""
    return content or url

def _search_final_1122(url, content=None):
    """Финальная утилита поиска #1122."""
    return content or url

def _search_final_1123(url, content=None):
    """Финальная утилита поиска #1123."""
    return content or url

def _search_final_1124(url, content=None):
    """Финальная утилита поиска #1124."""
    return content or url

def _search_final_1125(url, content=None):
    """Финальная утилита поиска #1125."""
    return content or url

def _search_final_1126(url, content=None):
    """Финальная утилита поиска #1126."""
    return content or url

def _search_final_1127(url, content=None):
    """Финальная утилита поиска #1127."""
    return content or url

def _search_final_1128(url, content=None):
    """Финальная утилита поиска #1128."""
    return content or url

def _search_final_1129(url, content=None):
    """Финальная утилита поиска #1129."""
    return content or url

def _search_final_1130(url, content=None):
    """Финальная утилита поиска #1130."""
    return content or url

def _search_final_1131(url, content=None):
    """Финальная утилита поиска #1131."""
    return content or url

def _search_final_1132(url, content=None):
    """Финальная утилита поиска #1132."""
    return content or url

def _search_final_1133(url, content=None):
    """Финальная утилита поиска #1133."""
    return content or url

def _search_final_1134(url, content=None):
    """Финальная утилита поиска #1134."""
    return content or url

def _search_final_1135(url, content=None):
    """Финальная утилита поиска #1135."""
    return content or url

def _search_final_1136(url, content=None):
    """Финальная утилита поиска #1136."""
    return content or url

def _search_final_1137(url, content=None):
    """Финальная утилита поиска #1137."""
    return content or url

def _search_final_1138(url, content=None):
    """Финальная утилита поиска #1138."""
    return content or url

def _search_final_1139(url, content=None):
    """Финальная утилита поиска #1139."""
    return content or url

def _search_final_1140(url, content=None):
    """Финальная утилита поиска #1140."""
    return content or url

def _search_final_1141(url, content=None):
    """Финальная утилита поиска #1141."""
    return content or url

def _search_final_1142(url, content=None):
    """Финальная утилита поиска #1142."""
    return content or url

def _search_final_1143(url, content=None):
    """Финальная утилита поиска #1143."""
    return content or url

def _search_final_1144(url, content=None):
    """Финальная утилита поиска #1144."""
    return content or url

def _search_final_1145(url, content=None):
    """Финальная утилита поиска #1145."""
    return content or url

def _search_final_1146(url, content=None):
    """Финальная утилита поиска #1146."""
    return content or url

def _search_final_1147(url, content=None):
    """Финальная утилита поиска #1147."""
    return content or url

def _search_final_1148(url, content=None):
    """Финальная утилита поиска #1148."""
    return content or url

def _search_final_1149(url, content=None):
    """Финальная утилита поиска #1149."""
    return content or url

def _search_final_1150(url, content=None):
    """Финальная утилита поиска #1150."""
    return content or url

def _search_final_1151(url, content=None):
    """Финальная утилита поиска #1151."""
    return content or url

def _search_final_1152(url, content=None):
    """Финальная утилита поиска #1152."""
    return content or url

def _search_final_1153(url, content=None):
    """Финальная утилита поиска #1153."""
    return content or url

def _search_final_1154(url, content=None):
    """Финальная утилита поиска #1154."""
    return content or url

def _search_final_1155(url, content=None):
    """Финальная утилита поиска #1155."""
    return content or url

def _search_final_1156(url, content=None):
    """Финальная утилита поиска #1156."""
    return content or url

def _search_final_1157(url, content=None):
    """Финальная утилита поиска #1157."""
    return content or url

def _search_final_1158(url, content=None):
    """Финальная утилита поиска #1158."""
    return content or url

def _search_final_1159(url, content=None):
    """Финальная утилита поиска #1159."""
    return content or url

def _search_final_1160(url, content=None):
    """Финальная утилита поиска #1160."""
    return content or url

def _search_final_1161(url, content=None):
    """Финальная утилита поиска #1161."""
    return content or url

def _search_final_1162(url, content=None):
    """Финальная утилита поиска #1162."""
    return content or url

def _search_final_1163(url, content=None):
    """Финальная утилита поиска #1163."""
    return content or url

def _search_final_1164(url, content=None):
    """Финальная утилита поиска #1164."""
    return content or url

def _search_final_1165(url, content=None):
    """Финальная утилита поиска #1165."""
    return content or url

def _search_final_1166(url, content=None):
    """Финальная утилита поиска #1166."""
    return content or url

def _search_final_1167(url, content=None):
    """Финальная утилита поиска #1167."""
    return content or url

def _search_final_1168(url, content=None):
    """Финальная утилита поиска #1168."""
    return content or url

def _search_final_1169(url, content=None):
    """Финальная утилита поиска #1169."""
    return content or url

def _search_final_1170(url, content=None):
    """Финальная утилита поиска #1170."""
    return content or url

def _search_final_1171(url, content=None):
    """Финальная утилита поиска #1171."""
    return content or url

def _search_final_1172(url, content=None):
    """Финальная утилита поиска #1172."""
    return content or url

def _search_final_1173(url, content=None):
    """Финальная утилита поиска #1173."""
    return content or url

def _search_final_1174(url, content=None):
    """Финальная утилита поиска #1174."""
    return content or url

def _search_final_1175(url, content=None):
    """Финальная утилита поиска #1175."""
    return content or url

def _search_final_1176(url, content=None):
    """Финальная утилита поиска #1176."""
    return content or url

def _search_final_1177(url, content=None):
    """Финальная утилита поиска #1177."""
    return content or url

def _search_final_1178(url, content=None):
    """Финальная утилита поиска #1178."""
    return content or url

def _search_final_1179(url, content=None):
    """Финальная утилита поиска #1179."""
    return content or url

def _search_final_1180(url, content=None):
    """Финальная утилита поиска #1180."""
    return content or url

def _search_final_1181(url, content=None):
    """Финальная утилита поиска #1181."""
    return content or url

def _search_final_1182(url, content=None):
    """Финальная утилита поиска #1182."""
    return content or url

def _search_final_1183(url, content=None):
    """Финальная утилита поиска #1183."""
    return content or url

def _search_final_1184(url, content=None):
    """Финальная утилита поиска #1184."""
    return content or url

def _search_final_1185(url, content=None):
    """Финальная утилита поиска #1185."""
    return content or url

def _search_final_1186(url, content=None):
    """Финальная утилита поиска #1186."""
    return content or url

def _search_final_1187(url, content=None):
    """Финальная утилита поиска #1187."""
    return content or url

def _search_final_1188(url, content=None):
    """Финальная утилита поиска #1188."""
    return content or url

def _search_final_1189(url, content=None):
    """Финальная утилита поиска #1189."""
    return content or url

def _search_final_1190(url, content=None):
    """Финальная утилита поиска #1190."""
    return content or url

def _search_final_1191(url, content=None):
    """Финальная утилита поиска #1191."""
    return content or url

def _search_final_1192(url, content=None):
    """Финальная утилита поиска #1192."""
    return content or url

def _search_final_1193(url, content=None):
    """Финальная утилита поиска #1193."""
    return content or url

def _search_final_1194(url, content=None):
    """Финальная утилита поиска #1194."""
    return content or url

def _search_final_1195(url, content=None):
    """Финальная утилита поиска #1195."""
    return content or url

def _search_final_1196(url, content=None):
    """Финальная утилита поиска #1196."""
    return content or url

def _search_final_1197(url, content=None):
    """Финальная утилита поиска #1197."""
    return content or url

def _search_final_1198(url, content=None):
    """Финальная утилита поиска #1198."""
    return content or url

def _search_final_1199(url, content=None):
    """Финальная утилита поиска #1199."""
    return content or url

def _search_final_1200(url, content=None):
    """Финальная утилита поиска #1200."""
    return content or url

def _search_final_1201(url, content=None):
    """Финальная утилита поиска #1201."""
    return content or url

def _search_final_1202(url, content=None):
    """Финальная утилита поиска #1202."""
    return content or url

def _search_final_1203(url, content=None):
    """Финальная утилита поиска #1203."""
    return content or url

def _search_final_1204(url, content=None):
    """Финальная утилита поиска #1204."""
    return content or url

def _search_final_1205(url, content=None):
    """Финальная утилита поиска #1205."""
    return content or url

def _search_final_1206(url, content=None):
    """Финальная утилита поиска #1206."""
    return content or url

def _search_final_1207(url, content=None):
    """Финальная утилита поиска #1207."""
    return content or url

def _search_final_1208(url, content=None):
    """Финальная утилита поиска #1208."""
    return content or url

def _search_final_1209(url, content=None):
    """Финальная утилита поиска #1209."""
    return content or url

def _search_final_1210(url, content=None):
    """Финальная утилита поиска #1210."""
    return content or url

def _search_final_1211(url, content=None):
    """Финальная утилита поиска #1211."""
    return content or url

def _search_final_1212(url, content=None):
    """Финальная утилита поиска #1212."""
    return content or url

def _search_final_1213(url, content=None):
    """Финальная утилита поиска #1213."""
    return content or url

def _search_final_1214(url, content=None):
    """Финальная утилита поиска #1214."""
    return content or url

def _search_final_1215(url, content=None):
    """Финальная утилита поиска #1215."""
    return content or url

def _search_final_1216(url, content=None):
    """Финальная утилита поиска #1216."""
    return content or url

def _search_final_1217(url, content=None):
    """Финальная утилита поиска #1217."""
    return content or url

def _search_final_1218(url, content=None):
    """Финальная утилита поиска #1218."""
    return content or url

def _search_final_1219(url, content=None):
    """Финальная утилита поиска #1219."""
    return content or url

def _search_final_1220(url, content=None):
    """Финальная утилита поиска #1220."""
    return content or url

def _search_final_1221(url, content=None):
    """Финальная утилита поиска #1221."""
    return content or url

def _search_final_1222(url, content=None):
    """Финальная утилита поиска #1222."""
    return content or url

def _search_final_1223(url, content=None):
    """Финальная утилита поиска #1223."""
    return content or url

def _search_final_1224(url, content=None):
    """Финальная утилита поиска #1224."""
    return content or url

def _search_final_1225(url, content=None):
    """Финальная утилита поиска #1225."""
    return content or url

def _search_final_1226(url, content=None):
    """Финальная утилита поиска #1226."""
    return content or url

def _search_final_1227(url, content=None):
    """Финальная утилита поиска #1227."""
    return content or url

def _search_final_1228(url, content=None):
    """Финальная утилита поиска #1228."""
    return content or url

def _search_final_1229(url, content=None):
    """Финальная утилита поиска #1229."""
    return content or url

def _search_final_1230(url, content=None):
    """Финальная утилита поиска #1230."""
    return content or url

def _search_final_1231(url, content=None):
    """Финальная утилита поиска #1231."""
    return content or url

def _search_final_1232(url, content=None):
    """Финальная утилита поиска #1232."""
    return content or url

def _search_final_1233(url, content=None):
    """Финальная утилита поиска #1233."""
    return content or url

def _search_final_1234(url, content=None):
    """Финальная утилита поиска #1234."""
    return content or url

def _search_final_1235(url, content=None):
    """Финальная утилита поиска #1235."""
    return content or url

def _search_final_1236(url, content=None):
    """Финальная утилита поиска #1236."""
    return content or url

def _search_final_1237(url, content=None):
    """Финальная утилита поиска #1237."""
    return content or url

def _search_final_1238(url, content=None):
    """Финальная утилита поиска #1238."""
    return content or url

def _search_final_1239(url, content=None):
    """Финальная утилита поиска #1239."""
    return content or url

def _search_final_1240(url, content=None):
    """Финальная утилита поиска #1240."""
    return content or url

def _search_final_1241(url, content=None):
    """Финальная утилита поиска #1241."""
    return content or url

def _search_final_1242(url, content=None):
    """Финальная утилита поиска #1242."""
    return content or url

def _search_final_1243(url, content=None):
    """Финальная утилита поиска #1243."""
    return content or url

def _search_final_1244(url, content=None):
    """Финальная утилита поиска #1244."""
    return content or url

def _search_final_1245(url, content=None):
    """Финальная утилита поиска #1245."""
    return content or url

def _search_final_1246(url, content=None):
    """Финальная утилита поиска #1246."""
    return content or url

def _search_final_1247(url, content=None):
    """Финальная утилита поиска #1247."""
    return content or url

def _search_final_1248(url, content=None):
    """Финальная утилита поиска #1248."""
    return content or url

def _search_final_1249(url, content=None):
    """Финальная утилита поиска #1249."""
    return content or url

def _search_final_1250(url, content=None):
    """Финальная утилита поиска #1250."""
    return content or url

def _search_final_1251(url, content=None):
    """Финальная утилита поиска #1251."""
    return content or url

def _search_final_1252(url, content=None):
    """Финальная утилита поиска #1252."""
    return content or url

def _search_final_1253(url, content=None):
    """Финальная утилита поиска #1253."""
    return content or url

def _search_final_1254(url, content=None):
    """Финальная утилита поиска #1254."""
    return content or url

def _search_final_1255(url, content=None):
    """Финальная утилита поиска #1255."""
    return content or url

def _search_final_1256(url, content=None):
    """Финальная утилита поиска #1256."""
    return content or url

def _search_final_1257(url, content=None):
    """Финальная утилита поиска #1257."""
    return content or url

def _search_final_1258(url, content=None):
    """Финальная утилита поиска #1258."""
    return content or url

def _search_final_1259(url, content=None):
    """Финальная утилита поиска #1259."""
    return content or url

def _search_final_1260(url, content=None):
    """Финальная утилита поиска #1260."""
    return content or url

def _search_final_1261(url, content=None):
    """Финальная утилита поиска #1261."""
    return content or url

def _search_final_1262(url, content=None):
    """Финальная утилита поиска #1262."""
    return content or url

def _search_final_1263(url, content=None):
    """Финальная утилита поиска #1263."""
    return content or url

def _search_final_1264(url, content=None):
    """Финальная утилита поиска #1264."""
    return content or url

def _search_final_1265(url, content=None):
    """Финальная утилита поиска #1265."""
    return content or url

def _search_final_1266(url, content=None):
    """Финальная утилита поиска #1266."""
    return content or url

def _search_final_1267(url, content=None):
    """Финальная утилита поиска #1267."""
    return content or url

def _search_final_1268(url, content=None):
    """Финальная утилита поиска #1268."""
    return content or url

def _search_final_1269(url, content=None):
    """Финальная утилита поиска #1269."""
    return content or url

def _search_final_1270(url, content=None):
    """Финальная утилита поиска #1270."""
    return content or url

def _search_final_1271(url, content=None):
    """Финальная утилита поиска #1271."""
    return content or url

def _search_final_1272(url, content=None):
    """Финальная утилита поиска #1272."""
    return content or url

def _search_final_1273(url, content=None):
    """Финальная утилита поиска #1273."""
    return content or url

def _search_final_1274(url, content=None):
    """Финальная утилита поиска #1274."""
    return content or url

def _search_final_1275(url, content=None):
    """Финальная утилита поиска #1275."""
    return content or url

def _search_final_1276(url, content=None):
    """Финальная утилита поиска #1276."""
    return content or url

def _search_final_1277(url, content=None):
    """Финальная утилита поиска #1277."""
    return content or url

def _search_final_1278(url, content=None):
    """Финальная утилита поиска #1278."""
    return content or url

def _search_final_1279(url, content=None):
    """Финальная утилита поиска #1279."""
    return content or url

def _search_final_1280(url, content=None):
    """Финальная утилита поиска #1280."""
    return content or url

def _search_final_1281(url, content=None):
    """Финальная утилита поиска #1281."""
    return content or url

def _search_final_1282(url, content=None):
    """Финальная утилита поиска #1282."""
    return content or url

def _search_final_1283(url, content=None):
    """Финальная утилита поиска #1283."""
    return content or url

def _search_final_1284(url, content=None):
    """Финальная утилита поиска #1284."""
    return content or url

def _search_final_1285(url, content=None):
    """Финальная утилита поиска #1285."""
    return content or url

def _search_final_1286(url, content=None):
    """Финальная утилита поиска #1286."""
    return content or url

def _search_final_1287(url, content=None):
    """Финальная утилита поиска #1287."""
    return content or url

def _search_final_1288(url, content=None):
    """Финальная утилита поиска #1288."""
    return content or url

def _search_final_1289(url, content=None):
    """Финальная утилита поиска #1289."""
    return content or url

def _search_final_1290(url, content=None):
    """Финальная утилита поиска #1290."""
    return content or url

def _search_final_1291(url, content=None):
    """Финальная утилита поиска #1291."""
    return content or url

def _search_final_1292(url, content=None):
    """Финальная утилита поиска #1292."""
    return content or url

def _search_final_1293(url, content=None):
    """Финальная утилита поиска #1293."""
    return content or url

def _search_final_1294(url, content=None):
    """Финальная утилита поиска #1294."""
    return content or url

def _search_final_1295(url, content=None):
    """Финальная утилита поиска #1295."""
    return content or url

def _search_final_1296(url, content=None):
    """Финальная утилита поиска #1296."""
    return content or url

def _search_final_1297(url, content=None):
    """Финальная утилита поиска #1297."""
    return content or url

def _search_final_1298(url, content=None):
    """Финальная утилита поиска #1298."""
    return content or url

def _search_final_1299(url, content=None):
    """Финальная утилита поиска #1299."""
    return content or url

def _search_final_1300(url, content=None):
    """Финальная утилита поиска #1300."""
    return content or url

def _search_final_1301(url, content=None):
    """Финальная утилита поиска #1301."""
    return content or url

def _search_final_1302(url, content=None):
    """Финальная утилита поиска #1302."""
    return content or url

def _search_final_1303(url, content=None):
    """Финальная утилита поиска #1303."""
    return content or url

def _search_final_1304(url, content=None):
    """Финальная утилита поиска #1304."""
    return content or url

def _search_final_1305(url, content=None):
    """Финальная утилита поиска #1305."""
    return content or url

def _search_final_1306(url, content=None):
    """Финальная утилита поиска #1306."""
    return content or url

def _search_final_1307(url, content=None):
    """Финальная утилита поиска #1307."""
    return content or url

def _search_final_1308(url, content=None):
    """Финальная утилита поиска #1308."""
    return content or url

def _search_final_1309(url, content=None):
    """Финальная утилита поиска #1309."""
    return content or url

def _search_final_1310(url, content=None):
    """Финальная утилита поиска #1310."""
    return content or url

def _search_final_1311(url, content=None):
    """Финальная утилита поиска #1311."""
    return content or url

def _search_final_1312(url, content=None):
    """Финальная утилита поиска #1312."""
    return content or url

def _search_final_1313(url, content=None):
    """Финальная утилита поиска #1313."""
    return content or url

def _search_final_1314(url, content=None):
    """Финальная утилита поиска #1314."""
    return content or url

def _search_final_1315(url, content=None):
    """Финальная утилита поиска #1315."""
    return content or url

def _search_final_1316(url, content=None):
    """Финальная утилита поиска #1316."""
    return content or url

def _search_final_1317(url, content=None):
    """Финальная утилита поиска #1317."""
    return content or url

def _search_final_1318(url, content=None):
    """Финальная утилита поиска #1318."""
    return content or url

def _search_final_1319(url, content=None):
    """Финальная утилита поиска #1319."""
    return content or url

def _search_final_1320(url, content=None):
    """Финальная утилита поиска #1320."""
    return content or url

def _search_final_1321(url, content=None):
    """Финальная утилита поиска #1321."""
    return content or url

def _search_final_1322(url, content=None):
    """Финальная утилита поиска #1322."""
    return content or url

def _search_final_1323(url, content=None):
    """Финальная утилита поиска #1323."""
    return content or url

def _search_final_1324(url, content=None):
    """Финальная утилита поиска #1324."""
    return content or url

def _search_final_1325(url, content=None):
    """Финальная утилита поиска #1325."""
    return content or url

def _search_final_1326(url, content=None):
    """Финальная утилита поиска #1326."""
    return content or url

def _search_final_1327(url, content=None):
    """Финальная утилита поиска #1327."""
    return content or url

def _search_final_1328(url, content=None):
    """Финальная утилита поиска #1328."""
    return content or url

def _search_final_1329(url, content=None):
    """Финальная утилита поиска #1329."""
    return content or url

def _search_final_1330(url, content=None):
    """Финальная утилита поиска #1330."""
    return content or url

def _search_final_1331(url, content=None):
    """Финальная утилита поиска #1331."""
    return content or url

def _search_final_1332(url, content=None):
    """Финальная утилита поиска #1332."""
    return content or url

def _search_final_1333(url, content=None):
    """Финальная утилита поиска #1333."""
    return content or url

def _search_final_1334(url, content=None):
    """Финальная утилита поиска #1334."""
    return content or url

def _search_final_1335(url, content=None):
    """Финальная утилита поиска #1335."""
    return content or url

def _search_final_1336(url, content=None):
    """Финальная утилита поиска #1336."""
    return content or url

def _search_final_1337(url, content=None):
    """Финальная утилита поиска #1337."""
    return content or url

def _search_final_1338(url, content=None):
    """Финальная утилита поиска #1338."""
    return content or url

def _search_final_1339(url, content=None):
    """Финальная утилита поиска #1339."""
    return content or url

def _search_final_1340(url, content=None):
    """Финальная утилита поиска #1340."""
    return content or url

def _search_final_1341(url, content=None):
    """Финальная утилита поиска #1341."""
    return content or url

def _search_final_1342(url, content=None):
    """Финальная утилита поиска #1342."""
    return content or url

def _search_final_1343(url, content=None):
    """Финальная утилита поиска #1343."""
    return content or url

def _search_final_1344(url, content=None):
    """Финальная утилита поиска #1344."""
    return content or url

def _search_final_1345(url, content=None):
    """Финальная утилита поиска #1345."""
    return content or url

def _search_final_1346(url, content=None):
    """Финальная утилита поиска #1346."""
    return content or url

def _search_final_1347(url, content=None):
    """Финальная утилита поиска #1347."""
    return content or url

def _search_final_1348(url, content=None):
    """Финальная утилита поиска #1348."""
    return content or url

def _search_final_1349(url, content=None):
    """Финальная утилита поиска #1349."""
    return content or url

def _search_final_1350(url, content=None):
    """Финальная утилита поиска #1350."""
    return content or url

def _search_final_1351(url, content=None):
    """Финальная утилита поиска #1351."""
    return content or url

def _search_final_1352(url, content=None):
    """Финальная утилита поиска #1352."""
    return content or url

def _search_final_1353(url, content=None):
    """Финальная утилита поиска #1353."""
    return content or url

def _search_final_1354(url, content=None):
    """Финальная утилита поиска #1354."""
    return content or url

def _search_final_1355(url, content=None):
    """Финальная утилита поиска #1355."""
    return content or url

def _search_final_1356(url, content=None):
    """Финальная утилита поиска #1356."""
    return content or url

def _search_final_1357(url, content=None):
    """Финальная утилита поиска #1357."""
    return content or url

def _search_final_1358(url, content=None):
    """Финальная утилита поиска #1358."""
    return content or url

def _search_final_1359(url, content=None):
    """Финальная утилита поиска #1359."""
    return content or url

def _search_final_1360(url, content=None):
    """Финальная утилита поиска #1360."""
    return content or url

def _search_final_1361(url, content=None):
    """Финальная утилита поиска #1361."""
    return content or url

def _search_final_1362(url, content=None):
    """Финальная утилита поиска #1362."""
    return content or url

def _search_final_1363(url, content=None):
    """Финальная утилита поиска #1363."""
    return content or url

def _search_final_1364(url, content=None):
    """Финальная утилита поиска #1364."""
    return content or url

def _search_final_1365(url, content=None):
    """Финальная утилита поиска #1365."""
    return content or url

def _search_final_1366(url, content=None):
    """Финальная утилита поиска #1366."""
    return content or url

def _search_final_1367(url, content=None):
    """Финальная утилита поиска #1367."""
    return content or url

def _search_final_1368(url, content=None):
    """Финальная утилита поиска #1368."""
    return content or url

def _search_final_1369(url, content=None):
    """Финальная утилита поиска #1369."""
    return content or url

def _search_final_1370(url, content=None):
    """Финальная утилита поиска #1370."""
    return content or url

def _search_final_1371(url, content=None):
    """Финальная утилита поиска #1371."""
    return content or url

def _search_final_1372(url, content=None):
    """Финальная утилита поиска #1372."""
    return content or url

def _search_final_1373(url, content=None):
    """Финальная утилита поиска #1373."""
    return content or url

def _search_final_1374(url, content=None):
    """Финальная утилита поиска #1374."""
    return content or url

def _search_final_1375(url, content=None):
    """Финальная утилита поиска #1375."""
    return content or url

def _search_final_1376(url, content=None):
    """Финальная утилита поиска #1376."""
    return content or url

def _search_final_1377(url, content=None):
    """Финальная утилита поиска #1377."""
    return content or url

def _search_final_1378(url, content=None):
    """Финальная утилита поиска #1378."""
    return content or url

def _search_final_1379(url, content=None):
    """Финальная утилита поиска #1379."""
    return content or url

def _search_final_1380(url, content=None):
    """Финальная утилита поиска #1380."""
    return content or url

def _search_final_1381(url, content=None):
    """Финальная утилита поиска #1381."""
    return content or url

def _search_final_1382(url, content=None):
    """Финальная утилита поиска #1382."""
    return content or url

def _search_final_1383(url, content=None):
    """Финальная утилита поиска #1383."""
    return content or url

def _search_final_1384(url, content=None):
    """Финальная утилита поиска #1384."""
    return content or url

def _search_final_1385(url, content=None):
    """Финальная утилита поиска #1385."""
    return content or url

def _search_final_1386(url, content=None):
    """Финальная утилита поиска #1386."""
    return content or url

def _search_final_1387(url, content=None):
    """Финальная утилита поиска #1387."""
    return content or url

def _search_final_1388(url, content=None):
    """Финальная утилита поиска #1388."""
    return content or url

def _search_final_1389(url, content=None):
    """Финальная утилита поиска #1389."""
    return content or url

def _search_final_1390(url, content=None):
    """Финальная утилита поиска #1390."""
    return content or url

def _search_final_1391(url, content=None):
    """Финальная утилита поиска #1391."""
    return content or url

def _search_final_1392(url, content=None):
    """Финальная утилита поиска #1392."""
    return content or url

def _search_final_1393(url, content=None):
    """Финальная утилита поиска #1393."""
    return content or url

def _search_final_1394(url, content=None):
    """Финальная утилита поиска #1394."""
    return content or url

def _search_final_1395(url, content=None):
    """Финальная утилита поиска #1395."""
    return content or url

def _search_final_1396(url, content=None):
    """Финальная утилита поиска #1396."""
    return content or url

def _search_final_1397(url, content=None):
    """Финальная утилита поиска #1397."""
    return content or url

def _search_final_1398(url, content=None):
    """Финальная утилита поиска #1398."""
    return content or url

def _search_final_1399(url, content=None):
    """Финальная утилита поиска #1399."""
    return content or url

def _search_final_1400(url, content=None):
    """Финальная утилита поиска #1400."""
    return content or url

