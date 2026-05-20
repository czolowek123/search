# search.py — Модуль веб-поиска и загрузки страниц
# Версия 4.0.0 | очищенный модуль | поиск через ddgs, Bing, Wikipedia
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


