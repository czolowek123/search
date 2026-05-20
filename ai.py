#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  AI.PY  —  Умный ИИ: ищет в интернете, обрабатывает, пишет короткий ответ
  Сохраняет ответы в main.txt
  Зависимости: pip install requests beautifulsoup4
================================================================================
"""

import re
import os
import sys
import time
import math
import json
import random
import datetime
import hashlib
import unicodedata
from collections import Counter, defaultdict
from urllib.parse import urlparse, quote_plus
import requests
from bs4 import BeautifulSoup


# ==============================================================================
# БЛОК 1: КОНСТАНТЫ И НАСТРОЙКИ
# ==============================================================================

OUTPUT_FILE = "main.txt"
MAX_SITES = 10
REQUEST_TIMEOUT = 14
SLEEP_BETWEEN = 0.25
MAX_TEXT_LEN = 12000
MIN_TEXT_LEN = 150
MAX_ANSWER_LEN = 600
MIN_SENTENCE_LEN = 30
MAX_SENTENCE_LEN = 400
TOP_SENTENCES = 5
VERSION = "2.0"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) "
    "Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) "
    "AppleWebKit/605.1.15 Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "Edg/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) "
    "Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) "
    "AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
]

SKIP_DOMAINS = {
    "youtube.com", "youtu.be", "facebook.com", "instagram.com",
    "twitter.com", "x.com", "tiktok.com", "pinterest.com",
    "amazon.com", "ebay.com", "aliexpress.com", "vk.com",
    "ok.ru", "rutube.ru", "google.com", "bing.com", "yahoo.com",
    "reddit.com", "linkedin.com", "telegram.org", "whatsapp.com",
    "tjournal.ru", "sports.ru",
}

GOOD_DOMAINS = {
    "wikipedia.org", "ru.wikipedia.org", "en.wikipedia.org",
    "britannica.com", "wikihow.com",
    "habr.com", "tproger.ru", "skillbox.ru",
    "stackoverflow.com", "github.com",
    "w3schools.com", "developer.mozilla.org",
    "geeksforgeeks.org", "realpython.com",
    "britannica.com", "history.com",
    "nationalgeographic.com", "nature.com",
    "sciencedaily.com", "newscientist.com",
    "docs.python.org", "python.org",
    "ria.ru", "tass.ru", "rbc.ru",
    "lenta.ru", "gazeta.ru",
}

# ==============================================================================
# БЛОК 2: СТОП-СЛОВА РУССКОГО ЯЗЫКА (для фильтрации мусора)
# ==============================================================================

STOP_WORDS_RU = {
    "и", "в", "не", "на", "с", "что", "как", "по", "это", "но",
    "а", "к", "у", "из", "за", "от", "до", "со", "о", "об",
    "или", "же", "ли", "бы", "то", "при", "для", "все", "так",
    "он", "она", "оно", "они", "мы", "вы", "я", "его", "её",
    "их", "им", "ему", "нам", "вам", "мне", "тебе", "ему",
    "этот", "эта", "это", "эти", "тот", "та", "те",
    "который", "которая", "которое", "которые",
    "если", "когда", "где", "куда", "откуда", "потому",
    "потому что", "так как", "хотя", "пока", "после",
    "также", "тоже", "даже", "уже", "ещё", "только",
    "очень", "более", "менее", "самый", "самая", "самое",
    "между", "через", "над", "под", "около", "возле",
    "есть", "был", "была", "были", "будет", "будут",
    "стал", "стала", "стали", "становится", "является",
    "который", "которые", "которую", "которого",
    "что", "чего", "чему", "чем", "чём",
    "нет", "да", "можно", "нельзя", "надо", "нужно",
    "здесь", "там", "туда", "сюда", "везде", "нигде",
    "всегда", "никогда", "иногда", "часто", "редко",
    "почти", "совсем", "абсолютно", "относительно",
    "вместе", "отдельно", "вместо", "кроме", "помимо",
    "например", "именно", "просто", "вдруг", "сразу",
    "снова", "опять", "снова", "again", "now",
    "может", "должен", "должна", "должны", "хочет",
    "говорит", "сказал", "сказала", "сказали",
    "видно", "можно", "нужно", "нельзя", "необходимо",
    "этой", "того", "этим", "тем", "этих", "тех",
    "без", "про", "под", "над", "перед", "после", "между",
    "такой", "такая", "такое", "такие", "другой", "другая",
    "один", "одна", "одно", "одни", "два", "три", "несколько",
    "своей", "своего", "своим", "свои", "свой", "своя", "своё",
    "во", "ни", "же", "ведь", "хоть", "зато", "итак", "таким образом",
    "кстати", "впрочем", "однако", "тем не менее", "поэтому",
    "следовательно", "значит", "таким образом", "в итоге",
    "наконец", "в конце концов", "прежде всего", "во-первых",
    "во-вторых", "в-третьих", "с одной стороны", "с другой",
    "в целом", "в общем", "в частности", "в том числе",
    "по сравнению", "по данным", "по словам", "по мнению",
    "согласно", "по результатам", "исходя из",
    "около", "примерно", "приблизительно", "порядка",
    "более", "менее", "свыше", "до", "от",
    "всего", "лишь", "лишь только", "всего лишь",
    "именно", "непременно", "обязательно", "непосредственно",
    "достаточно", "вполне", "весьма", "крайне", "чрезвычайно",
    "особенно", "в особенности", "главным образом",
    "прежде всего", "в первую очередь", "прежде всего",
    "как правило", "как правило", "как известно",
    "как следует", "как оказалось", "как выяснилось",
    "по данным", "согласно данным", "по информации",
    "ранее", "позднее", "впоследствии", "затем", "потом",
    "сначала", "сперва", "вначале", "поначалу",
    "наконец", "в итоге", "в результате", "вследствие",
    "благодаря", "несмотря", "вопреки", "ввиду",
    "подобно", "аналогично", "в отличие", "по сравнению",
    "причём", "при этом", "притом", "тогда как",
    "в то время как", "между тем", "тем временем",
    "не только", "но и", "как", "так и",
    "ни", "ни... ни", "либо", "или... или",
    "поскольку", "ибо", "так как", "потому что",
    "чтобы", "дабы", "с тем чтобы",
    "хотя", "несмотря на то что", "пусть", "пускай",
    "если", "при условии что", "в случае если",
    "как только", "едва", "лишь только", "только что",
    "прежде чем", "до того как", "после того как", "с тех пор как",
    "до", "после", "во время", "в течение", "в продолжение",
    "с", "по", "к", "от", "на", "в", "за", "через", "под", "над",
    "передо", "перед", "за", "между", "среди", "вокруг",
    "вблизи", "рядом", "вдоль", "поперёк", "напротив",
    "включая", "исключая", "не считая", "помимо",
    "кроме", "помимо", "за исключением",
    "наряду с", "вместе с", "совместно с",
    "относительно", "касательно", "по поводу", "по части",
    "по вопросу", "в области", "в сфере", "в отношении",
    "что касается", "что до", "говоря о",
    "применительно к", "в связи с", "в зависимости от",
    "в соответствии с", "в согласии с", "по аналогии с",
    "наподобие", "вроде", "что-то вроде", "нечто подобное",
    "то есть", "иными словами", "другими словами",
    "а именно", "в том смысле", "в смысле",
    "насколько", "поскольку", "в той мере", "в той степени",
}

# ==============================================================================
# БЛОК 3: СТОП-СЛОВА АНГЛИЙСКОГО ЯЗЫКА
# ==============================================================================

STOP_WORDS_EN = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at",
    "to", "for", "of", "with", "by", "from", "as", "is", "was",
    "are", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "must", "shall", "can", "need", "dare", "ought",
    "used", "it", "its", "this", "that", "these", "those", "they",
    "he", "she", "we", "you", "i", "me", "my", "your", "his",
    "her", "our", "their", "what", "which", "who", "whom", "whose",
    "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "not",
    "only", "same", "so", "than", "too", "very", "just", "also",
    "about", "above", "after", "again", "against", "along", "already",
    "although", "always", "among", "around", "because", "before",
    "below", "between", "during", "even", "ever", "every", "here",
    "however", "into", "like", "many", "much", "never", "now",
    "often", "once", "over", "own", "rather", "since", "still",
    "then", "there", "therefore", "though", "through", "throughout",
    "thus", "under", "until", "upon", "usually", "while", "within",
    "without", "yet", "back", "far", "give", "get", "go", "good",
    "great", "just", "keep", "know", "let", "little", "look",
    "make", "man", "much", "new", "next", "old", "one", "our",
    "out", "part", "people", "place", "say", "see", "seem", "set",
    "show", "state", "take", "tell", "think", "time", "two", "use",
    "way", "well", "work", "world", "year", "years", "also",
    "according", "however", "including", "per", "eg", "ie",
    "something", "anything", "everything", "nothing", "someone",
    "anyone", "everyone", "somewhere", "anywhere", "everywhere",
    "somehow", "anyhow", "otherwise", "altogether", "besides",
    "despite", "except", "instead", "meanwhile", "moreover",
    "nevertheless", "next", "nonetheless", "otherwise", "rather",
    "regardless", "similarly", "therefore", "whereas", "whereby",
    "whether", "whilst", "within", "without", "across", "almost",
    "along", "already", "although", "among", "around", "away",
    "behind", "beyond", "both", "cannot", "certain", "certainly",
    "clearly", "comes", "course", "currently", "different",
    "directly", "early", "easily", "either", "else", "especially",
    "eventually", "exactly", "finally", "first", "follows",
    "formerly", "found", "furthermore", "generally", "given",
    "hence", "itself", "known", "large", "largely", "largely",
    "later", "least", "likely", "long", "mainly", "major",
    "meanwhile", "might", "mostly", "much", "nearly", "need",
    "neither", "normally", "notably", "often", "only", "open",
    "order", "originally", "particularly", "perhaps", "possible",
    "possibly", "probably", "quite", "recently", "regarding",
    "relatively", "remain", "remains", "respectively", "result",
    "several", "simply", "since", "slightly", "small", "specific",
    "specifically", "sure", "take", "together", "toward", "towards",
    "typically", "various", "virtually", "want", "whereas", "widely",
}

ALL_STOP_WORDS = STOP_WORDS_RU | STOP_WORDS_EN

# ==============================================================================
# БЛОК 4: ШАБЛОНЫ ДЛЯ ОПРЕДЕЛЕНИЯ ТИПА ВОПРОСА
# ==============================================================================

# Паттерны вопросов "кто" (персоны)
WHO_PATTERNS = [
    re.compile(r'\bкто\s+такой\b', re.I),
    re.compile(r'\bкто\s+такая\b', re.I),
    re.compile(r'\bкто\s+это\b', re.I),
    re.compile(r'\bкто\s+был\b', re.I),
    re.compile(r'\bкем\s+был\b', re.I),
    re.compile(r'\bкем\s+была\b', re.I),
    re.compile(r'\bwho\s+is\b', re.I),
    re.compile(r'\bwho\s+was\b', re.I),
    re.compile(r'\bwho\s+are\b', re.I),
    re.compile(r'\bкто\s+создал\b', re.I),
    re.compile(r'\bкто\s+основал\b', re.I),
    re.compile(r'\bкто\s+написал\b', re.I),
    re.compile(r'\bкто\s+изобрёл\b', re.I),
    re.compile(r'\bкто\s+открыл\b', re.I),
    re.compile(r'\bкто\s+снял\b', re.I),
    re.compile(r'\bкто\s+придумал\b', re.I),
    re.compile(r'\bкто\s+изобрел\b', re.I),
]

# Паттерны вопросов "что" (определение)
WHAT_PATTERNS = [
    re.compile(r'\bчто\s+такое\b', re.I),
    re.compile(r'\bчто\s+это\b', re.I),
    re.compile(r'\bчто\s+значит\b', re.I),
    re.compile(r'\bчто\s+означает\b', re.I),
    re.compile(r'\bчто\s+представляет\b', re.I),
    re.compile(r'\bwhat\s+is\b', re.I),
    re.compile(r'\bwhat\s+are\b', re.I),
    re.compile(r'\bwhat\s+does\b', re.I),
    re.compile(r'\bопределение\b', re.I),
    re.compile(r'\bобъясни\b', re.I),
    re.compile(r'\bрасскажи\s+о\b', re.I),
    re.compile(r'\bрасскажи\s+про\b', re.I),
    re.compile(r'\bиз\s+чего\s+состоит\b', re.I),
    re.compile(r'\bиз\s+чего\s+состоят\b', re.I),
    re.compile(r'\bкак\s+устроен\b', re.I),
    re.compile(r'\bкак\s+работает\b', re.I),
    re.compile(r'\bкак\s+устроена\b', re.I),
]

# Паттерны вопросов "когда" (дата/время)
WHEN_PATTERNS = [
    re.compile(r'\bкогда\b', re.I),
    re.compile(r'\bв\s+каком\s+году\b', re.I),
    re.compile(r'\bв\s+каком\s+веке\b', re.I),
    re.compile(r'\bwhen\s+was\b', re.I),
    re.compile(r'\bwhen\s+did\b', re.I),
    re.compile(r'\bwhen\s+is\b', re.I),
    re.compile(r'\bгод\s+основания\b', re.I),
    re.compile(r'\bгод\s+рождения\b', re.I),
    re.compile(r'\bгод\s+создания\b', re.I),
    re.compile(r'\bгод\s+смерти\b', re.I),
    re.compile(r'\bдата\b', re.I),
]

# Паттерны вопросов "где" (место)
WHERE_PATTERNS = [
    re.compile(r'\bгде\b', re.I),
    re.compile(r'\bв\s+какой\s+стране\b', re.I),
    re.compile(r'\bв\s+каком\s+городе\b', re.I),
    re.compile(r'\bwhere\s+is\b', re.I),
    re.compile(r'\bwhere\s+are\b', re.I),
    re.compile(r'\bстолица\b', re.I),
    re.compile(r'\bнаходится\b', re.I),
    re.compile(r'\bрасположен\b', re.I),
    re.compile(r'\bрасположена\b', re.I),
]

# Паттерны вопросов "сколько" (количество)
HOW_MANY_PATTERNS = [
    re.compile(r'\bсколько\b', re.I),
    re.compile(r'\bколичество\b', re.I),
    re.compile(r'\bколичество\b', re.I),
    re.compile(r'\bhow\s+many\b', re.I),
    re.compile(r'\bhow\s+much\b', re.I),
    re.compile(r'\bhow\s+long\b', re.I),
    re.compile(r'\bhow\s+far\b', re.I),
    re.compile(r'\bhow\s+old\b', re.I),
    re.compile(r'\bhow\s+big\b', re.I),
    re.compile(r'\bчисленность\b', re.I),
    re.compile(r'\bнаселение\b', re.I),
    re.compile(r'\bвысота\b', re.I),
    re.compile(r'\bдлина\b', re.I),
    re.compile(r'\bплощадь\b', re.I),
    re.compile(r'\bвес\b', re.I),
    re.compile(r'\bмасса\b', re.I),
    re.compile(r'\bвозраст\b', re.I),
    re.compile(r'\bрасстояние\b', re.I),
    re.compile(r'\bглубина\b', re.I),
    re.compile(r'\bширина\b', re.I),
    re.compile(r'\bскорость\b', re.I),
]

# Паттерны вопросов "почему" (причина)
WHY_PATTERNS = [
    re.compile(r'\bпочему\b', re.I),
    re.compile(r'\bпо\s+какой\s+причине\b', re.I),
    re.compile(r'\bиз-за\s+чего\b', re.I),
    re.compile(r'\bчем\s+объяснить\b', re.I),
    re.compile(r'\bwhy\s+is\b', re.I),
    re.compile(r'\bwhy\s+did\b', re.I),
    re.compile(r'\bwhy\s+does\b', re.I),
    re.compile(r'\bwhy\s+are\b', re.I),
    re.compile(r'\bпричина\b', re.I),
]

# Паттерны вопросов "как" (способ)
HOW_PATTERNS = [
    re.compile(r'\bкак\s+\w+', re.I),
    re.compile(r'\bкаким\s+образом\b', re.I),
    re.compile(r'\bкаким\s+способом\b', re.I),
    re.compile(r'\bhow\s+to\b', re.I),
    re.compile(r'\bhow\s+do\b', re.I),
    re.compile(r'\bhow\s+does\b', re.I),
    re.compile(r'\bспособ\b', re.I),
    re.compile(r'\bметод\b', re.I),
]

# ==============================================================================
# БЛОК 5: ПАТТЕРНЫ ИЗВЛЕЧЕНИЯ ДАТ И ЧИСЕЛ
# ==============================================================================

YEAR_PATTERNS = [
    re.compile(r'\b(1[0-9]{3}|2[0-2][0-9]{2})\s*(?:год|г\.?|year|yr)', re.I),
    re.compile(r'\bв\s+(1[0-9]{3}|2[0-2][0-9]{2})\s*(?:году|г\.?)?', re.I),
    re.compile(r'\b(1[0-9]{3}|2[0-2][0-9]{2})\b'),
]

NUMBER_PATTERNS = [
    re.compile(r'\b(\d[\d\s]*[\d,\.]+)\s*(?:млн|миллион|тысяч|млрд|billion|million|thousand)', re.I),
    re.compile(r'\b(\d+(?:[,\.]\d+)?)\s*(?:км|м\b|кг|г\b|л\b|га|т\b|тонн)', re.I),
    re.compile(r'\b(\d+(?:\s\d+)*)\b'),
]

DATE_PATTERNS = [
    re.compile(r'\b(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|'
               r'августа|сентября|октября|ноября|декабря)\s+(\d{4})', re.I),
    re.compile(r'\b(\d{4})[–\-](\d{4})\b'),
    re.compile(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b'),
]

DEFINITION_PATTERNS = [
    re.compile(r'(.{10,200}?)(?:\s+[-—–]\s+|:\s+|,?\s+это\s+|,?\s+является\s+'
               r'|,?\s+представляет\s+собой\s+)(.{20,300})', re.I),
    re.compile(r'([А-ЯA-Z][^.!?]{10,100})\s+[-—]\s+([^.!?]{20,200}[.!?])', re.I),
]

# ==============================================================================
# БЛОК 6: КЛЮЧЕВЫЕ СЛОВА ДЛЯ ОЦЕНКИ КАЧЕСТВА ПРЕДЛОЖЕНИЙ
# ==============================================================================

QUALITY_BOOST_WORDS = {
    "является", "представляет", "это", "был", "была", "были", "основан",
    "создан", "образован", "открыт", "изобретён", "родился", "умер",
    "занимает", "составляет", "равна", "равен", "равно", "насчитывает",
    "находится", "расположен", "расположена", "включает", "содержит",
    "состоит", "относится", "называется", "известен", "известна",
    "считается", "признан", "признана", "являлся", "являлась",
    "основал", "создал", "изобрел", "открыл", "написал", "снял",
    "is", "was", "were", "are", "founded", "created", "born", "died",
    "located", "known", "considered", "includes", "consists", "contains",
    "represents", "means", "refers", "defined", "established",
}

QUALITY_PENALTY_WORDS = {
    "cookie", "cookies", "javascript", "enable", "browser", "login",
    "subscribe", "newsletter", "advertisement", "реклама", "подписаться",
    "войти", "зарегистрироваться", "купить", "заказать", "скидка",
    "404", "error", "undefined", "null", "loading", "please wait",
    "click here", "read more", "see also", "related articles",
    "share", "twitter", "facebook", "instagram", "поделиться",
    "комментарии", "comments", "оставить отзыв", "leave a review",
    "все права защищены", "privacy policy", "terms of service",
    "политика конфиденциальности", "пользовательское соглашение",
    "copyright", "©", "powered by", "разработано", "создано",
}

# ==============================================================================
# БЛОК 7: ШАБЛОНЫ ОТВЕТОВ ПО ТИПАМ ВОПРОСОВ
# ==============================================================================

ANSWER_TEMPLATES = {
    "who": [
        "{subject} — {answer}",
        "{answer}",
    ],
    "what": [
        "{subject} — {answer}",
        "{answer}",
    ],
    "when": [
        "{subject}: {answer}",
        "{answer}",
    ],
    "where": [
        "{subject} находится {answer}",
        "{answer}",
    ],
    "how_many": [
        "{subject}: {answer}",
        "{answer}",
    ],
    "why": [
        "{answer}",
    ],
    "how": [
        "{answer}",
    ],
    "general": [
        "{answer}",
    ],
}

# ==============================================================================
# БЛОК 8: РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ ДЛЯ ОЧИСТКИ ТЕКСТА
# ==============================================================================

RE_MULTIPLE_SPACES = re.compile(r'\s+')
RE_NON_TEXT = re.compile(r'[^\w\s\-.,!?:;()«»"\'%°№\u0400-\u04FF]')
RE_URLS = re.compile(r'https?://\S+|www\.\S+')
RE_EMAILS = re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+')
RE_PHONE = re.compile(r'[\+]?[\d\s\-\(\)]{10,15}')
RE_SPECIAL = re.compile(r'[|*_~`]')
RE_HTML_ENTITIES = re.compile(r'&[a-zA-Z]+;|&#\d+;')
RE_ELLIPSIS = re.compile(r'\.{3,}')
RE_REPEATED_PUNCT = re.compile(r'([!?]){2,}')
RE_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')
RE_NUMBERS_ONLY = re.compile(r'^\d+$')
RE_SHORT_WORDS = re.compile(r'\b\w{1,2}\b')
RE_BRACKETS_CONTENT = re.compile(r'\([^)]{50,}\)')
RE_DEFINITION_MARKER = re.compile(
    r'(?:это|является|представляет собой|—|–|-|:)\s+', re.I
)
RE_SOURCE_MARKER = re.compile(
    r'(?:источник|source|по данным|согласно|по словам|по информации)', re.I
)
RE_WIKIPEDIA_MARKER = re.compile(r'wikipedia|Wikimedia|викип', re.I)
RE_MENU_MARKER = re.compile(
    r'(?:главная|меню|навигация|поиск|контакты|о нас|about|home|menu|search|contact)',
    re.I
)

# ==============================================================================
# БЛОК 9: ФУНКЦИИ ОЧИСТКИ ТЕКСТА
# ==============================================================================

def clean_html(html_text: str) -> str:
    """Извлекает чистый текст из HTML"""
    try:
        soup = BeautifulSoup(html_text, "html.parser")

        for bad_tag in soup(
            ["script", "style", "nav", "footer", "header", "aside",
             "form", "button", "meta", "noscript", "iframe", "figure",
             "picture", "video", "audio", "select", "input", "label",
             "svg", "path", "link", "head", "object", "embed",
             "advertisement", "ads", "sidebar", "menu", "navbar"]
        ):
            bad_tag.decompose()

        for ad in soup.find_all(class_=re.compile(
            r'ad|ads|advertisement|banner|sidebar|nav|menu|footer|header|'
            r'cookie|popup|modal|overlay|social|share|related|comments',
            re.I
        )):
            ad.decompose()

        priority_tags = ["article", "main", ".content", "#content",
                         "#main", ".article", ".post", ".entry"]
        priority_texts = []

        for selector in priority_tags:
            try:
                if selector.startswith(('.', '#')):
                    for el in soup.select(selector):
                        t = el.get_text(separator=" ", strip=True)
                        if len(t) > 200:
                            priority_texts.append(t)
                else:
                    for el in soup.find_all(selector):
                        t = el.get_text(separator=" ", strip=True)
                        if len(t) > 200:
                            priority_texts.append(t)
            except Exception:
                continue

        if priority_texts:
            raw = " ".join(priority_texts)
        else:
            parts = []
            for el in soup.find_all(["p", "h1", "h2", "h3", "h4",
                                      "h5", "li", "dd", "dt", "blockquote"]):
                t = el.get_text(separator=" ", strip=True)
                if len(t) > 40:
                    parts.append(t)

            if parts:
                raw = " ".join(parts)
            else:
                raw = soup.get_text(separator=" ", strip=True)

        return normalize_text(raw)

    except Exception:
        return ""


def normalize_text(text: str) -> str:
    """Нормализует текст"""
    if not text:
        return ""
    text = RE_HTML_ENTITIES.sub(" ", text)
    text = RE_URLS.sub(" ", text)
    text = RE_EMAILS.sub(" ", text)
    text = RE_SPECIAL.sub(" ", text)
    text = RE_ELLIPSIS.sub("...", text)
    text = RE_REPEATED_PUNCT.sub(r"\1\1", text)
    text = RE_MULTIPLE_SPACES.sub(" ", text)
    return text.strip()


def remove_noise_sentences(sentences: list) -> list:
    """Убирает мусорные предложения"""
    clean = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < MIN_SENTENCE_LEN:
            continue
        if len(sent) > MAX_SENTENCE_LEN:
            continue
        lower = sent.lower()
        if any(p in lower for p in QUALITY_PENALTY_WORDS):
            continue
        if RE_MENU_MARKER.search(sent) and len(sent) < 60:
            continue
        if sent.count("|") > 3:
            continue
        if sent.count("•") > 2:
            continue
        words = sent.split()
        if len(words) < 5:
            continue
        clean.append(sent)
    return clean


def split_into_sentences(text: str) -> list:
    """Разбивает текст на предложения"""
    parts = RE_SENTENCE_SPLIT.split(text)
    result = []
    for p in parts:
        p = p.strip()
        if p:
            result.append(p)
    return result


def get_word_tokens(text: str, remove_stops: bool = True) -> list:
    """Токенизирует текст"""
    words = re.findall(r'[а-яёА-ЯЁa-zA-Z0-9]+', text.lower())
    if remove_stops:
        words = [w for w in words if w not in ALL_STOP_WORDS and len(w) > 2]
    return words


# ==============================================================================
# БЛОК 10: МОДУЛЬ ПОИСКА В ИНТЕРНЕТЕ
# ==============================================================================

def get_random_headers() -> dict:
    """Возвращает случайные HTTP-заголовки"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }


def is_bad_domain(url: str) -> bool:
    """Проверяет, не входит ли домен в список плохих"""
    try:
        domain = urlparse(url).netloc.replace("www.", "").lower()
        return any(skip in domain for skip in SKIP_DOMAINS)
    except Exception:
        return True


def get_domain_quality(url: str) -> float:
    """Возвращает качество домена (0.0 - 1.0)"""
    try:
        domain = urlparse(url).netloc.replace("www.", "").lower()
        if any(g in domain for g in GOOD_DOMAINS):
            return 1.0
        if "wikipedia" in domain:
            return 1.0
        if ".edu" in domain or ".gov" in domain:
            return 0.9
        if ".org" in domain:
            return 0.8
        return 0.5
    except Exception:
        return 0.3


def search_duckduckgo(query: str, num: int = 10) -> list:
    """
    Ищет через ddgs (DuckDuckGo Search API).
    Автоматически повторяет при rate-limit или ошибке.
    """
    links = []
    regions = ["ru-ru", "wt-wt", "us-en"]
    for attempt, region in enumerate(regions):
        try:
            from ddgs import DDGS
            with DDGS() as ddg:
                results = ddg.text(
                    query,
                    max_results=num + 5,
                    region=region,
                    safesearch="off",
                )
                for r in (results or []):
                    href = r.get("href", "")
                    if href and href.startswith("http") and not is_bad_domain(href):
                        links.append(href)
                    if len(links) >= num:
                        break
            if links:
                break
        except ImportError:
            break
        except Exception:
            if attempt < len(regions) - 1:
                time.sleep(1.5)
    return links


def search_bing(query: str, num: int = 5) -> list:
    """
    Запасной поиск через scraping Bing (если ddgs не помог).
    """
    links = []
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml",
        }
        url = f"https://www.bing.com/search?q={quote_plus(query)}&count={num}&setlang=ru&mkt=ru-RU"
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("li.b_algo h2 a, .b_algo a"):
                href = a.get("href", "")
                if href and href.startswith("http") and not is_bad_domain(href):
                    if href not in links:
                        links.append(href)
                if len(links) >= num:
                    break
    except Exception:
        pass
    return links


def _wiki_headers() -> dict:
    """Заголовки для Wikipedia API (обходят блокировку 403)."""
    return {
        "User-Agent": "Mozilla/5.0 (compatible; PythonAI/2.0; +https://example.com/bot)",
        "Accept": "application/json",
        "Accept-Language": "ru,en;q=0.9",
    }


def search_wikipedia_links(query: str) -> list:
    """Ищет статьи Wikipedia через официальный API с правильными заголовками."""
    links = []
    for lang in ("ru", "en"):
        try:
            r = requests.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={
                    "action": "query", "format": "json",
                    "list": "search", "srsearch": query,
                    "srlimit": 3, "utf8": 1,
                },
                timeout=8,
                headers=_wiki_headers(),
            )
            if r.status_code == 200:
                data = r.json()
                for item in data.get("query", {}).get("search", []):
                    title = item.get("title", "")
                    if title:
                        links.append(
                            f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"
                        )
        except Exception:
            pass
    return links


def fetch_wikipedia_text(page_url: str) -> str:
    """Загружает Wikipedia статью как чистый текст через API."""
    try:
        parts = page_url.split("/wiki/")
        if len(parts) != 2:
            return ""
        lang = "ru" if "ru.wikipedia" in page_url else "en"
        title = parts[1]
        r = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query", "format": "json",
                "prop": "extracts", "exintro": 0,
                "explaintext": 1,
                "titles": title.replace("_", " "),
                "exchars": 6000,
                "utf8": 1,
            },
            timeout=10,
            headers=_wiki_headers(),
        )
        if r.status_code == 200:
            data = r.json()
            for page in data.get("query", {}).get("pages", {}).values():
                text = page.get("extract", "")
                if text and len(text) > 100:
                    return text[:6000]
    except Exception:
        pass
    return ""


def search_links(query: str, total: int = 10) -> list:
    """Собирает ссылки через ddgs + Wikipedia API."""
    links = []

    # 1. ddgs (основной)
    links.extend(search_duckduckgo(query, num=total))

    # 2. Если мало — пробуем английский запрос
    if len(links) < 4:
        links.extend(search_bing(query, num=5))

    # 3. Всегда добавляем Wikipedia
    for wl in search_wikipedia_links(query):
        if wl not in links:
            links.append(wl)

    seen = set()
    unique = []
    for lnk in links:
        if lnk not in seen and not is_bad_domain(lnk):
            seen.add(lnk)
            unique.append(lnk)

    unique.sort(key=lambda u: get_domain_quality(u), reverse=True)
    return unique[:total]


def fetch_page(url: str) -> str:
    """Загружает страницу и возвращает чистый текст.
    Для Wikipedia использует чистый API вместо HTML."""
    if "wikipedia.org/wiki/" in url:
        wiki_text = fetch_wikipedia_text(url)
        if wiki_text:
            return wiki_text
    try:
        session = requests.Session()
        session.headers.update(get_random_headers())
        response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if response.status_code >= 400:
            return ""
        response.encoding = response.apparent_encoding or "utf-8"
        text = clean_html(response.text)
        if len(text) < MIN_TEXT_LEN:
            return ""
        return text[:MAX_TEXT_LEN]
    except Exception:
        return ""


def collect_web_texts(query: str, verbose: bool = True) -> dict:
    """
    Ищет и собирает тексты с 10 сайтов.
    Возвращает dict с полной информацией.
    """
    if verbose:
        print(f"\n[AI] Ищу в интернете: «{query}»")

    links = search_links(query, total=MAX_SITES)

    if verbose:
        print(f"[AI] Найдено {len(links)} ссылок, загружаю тексты...")

    results = []
    all_texts = []

    for i, url in enumerate(links):
        domain = urlparse(url).netloc.replace("www.", "")
        quality = get_domain_quality(url)
        text = fetch_page(url)

        if text:
            results.append({
                "url": url,
                "domain": domain,
                "quality": quality,
                "text": text,
                "length": len(text),
            })
            all_texts.append(text)
            if verbose:
                print(f"  [OK] [{i+1}] {domain} ({len(text)} симв., "
                      f"качество: {quality:.1f})")
        else:
            if verbose:
                print(f"  [--] [{i+1}] {domain} — пусто")

        time.sleep(SLEEP_BETWEEN)

    combined = " ".join(all_texts)

    if verbose:
        print(f"[AI] Обработано {len(results)} сайтов. "
              f"Всего символов: {len(combined)}\n")

    return {
        "query": query,
        "links": links,
        "results": results,
        "combined_text": combined,
        "sources_count": len(results),
    }


# ==============================================================================
# БЛОК 11: МОДУЛЬ АНАЛИЗА ТЕКСТА И ОЦЕНКИ ПРЕДЛОЖЕНИЙ
# ==============================================================================

def score_sentence(sentence: str, query_words: set) -> float:
    """Оценивает релевантность предложения запросу"""
    score = 0.0
    lower = sentence.lower()
    words = set(get_word_tokens(lower, remove_stops=True))

    intersection = words & query_words
    score += len(intersection) * 3.0

    overlap_ratio = len(intersection) / max(len(query_words), 1)
    score += overlap_ratio * 5.0

    for boost_word in QUALITY_BOOST_WORDS:
        if boost_word in lower:
            score += 0.5

    for penalty_word in QUALITY_PENALTY_WORDS:
        if penalty_word in lower:
            score -= 2.0

    length = len(sentence)
    if 60 <= length <= 250:
        score += 1.5
    elif 40 <= length < 60 or 250 < length <= 350:
        score += 0.5
    else:
        score -= 1.0

    score += get_definition_score(sentence)

    return score


def get_definition_score(sentence: str) -> float:
    """Даёт бонус предложениям с определениями"""
    score = 0.0
    patterns = [
        r'\s+—\s+', r'\s+–\s+', r'\s+это\s+', r',\s+являющий',
        r'\s+является\s+', r'\s+представляет\s+собой\s+',
        r'\s+was\s+born\s+', r'\s+is\s+a\s+', r'\s+is\s+an\s+',
        r'\s+was\s+a\s+', r'\s+was\s+an\s+',
        r'\s+founded\s+', r'\s+created\s+', r'\s+invented\s+',
        r'\s+был\s+основан\s+', r'\s+была\s+основана\s+',
        r'\s+был\s+создан\s+', r'\s+была\s+создана\s+',
    ]
    for pat in patterns:
        if re.search(pat, sentence, re.I):
            score += 1.0
    return score


def score_by_position(index: int, total: int) -> float:
    """Бонус за позицию — первые предложения важнее"""
    if total == 0:
        return 0.0
    ratio = 1.0 - (index / total)
    return ratio * 0.5


def score_by_source_quality(source_quality: float) -> float:
    """Бонус за качество источника"""
    return source_quality * 2.0


def build_query_words(query: str) -> set:
    """Строит набор слов запроса для поиска"""
    raw = get_word_tokens(query, remove_stops=True)
    words = set(raw)

    remove_question_words = {
        "сколько", "кто", "что", "где", "когда", "почему", "как",
        "какой", "какая", "какое", "какие", "зачем", "куда", "откуда",
        "who", "what", "where", "when", "why", "how", "which",
    }
    words -= remove_question_words

    return words if words else set(raw)


# ==============================================================================
# БЛОК 12: МОДУЛЬ ИЗВЛЕЧЕНИЯ ОТВЕТА
# ==============================================================================

def extract_best_sentences(
        web_data: dict,
        query: str,
        top_n: int = TOP_SENTENCES
) -> list:
    """Извлекает лучшие предложения из всех собранных текстов"""
    query_words = build_query_words(query)
    scored_sentences = []

    for source in web_data.get("results", []):
        text = source["text"]
        quality = source["quality"]
        sentences = split_into_sentences(text)
        sentences = remove_noise_sentences(sentences)
        total = len(sentences)

        for idx, sent in enumerate(sentences):
            base_score = score_sentence(sent, query_words)
            pos_score = score_by_position(idx, total)
            src_score = score_by_source_quality(quality)
            total_score = base_score + pos_score + src_score

            if total_score > 0:
                scored_sentences.append((total_score, sent, source["url"]))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)

    seen_hashes = set()
    unique_sentences = []

    for score, sent, url in scored_sentences:
        words = frozenset(get_word_tokens(sent, remove_stops=True)[:10])
        h = hash(words)
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique_sentences.append((score, sent, url))

        if len(unique_sentences) >= top_n:
            break

    return unique_sentences


def determine_question_type(query: str) -> str:
    """Определяет тип вопроса"""
    q = query.lower()

    for pattern in WHO_PATTERNS:
        if pattern.search(q):
            return "who"

    for pattern in WHAT_PATTERNS:
        if pattern.search(q):
            return "what"

    for pattern in WHEN_PATTERNS:
        if pattern.search(q):
            return "when"

    for pattern in WHERE_PATTERNS:
        if pattern.search(q):
            return "where"

    for pattern in HOW_MANY_PATTERNS:
        if pattern.search(q):
            return "how_many"

    for pattern in WHY_PATTERNS:
        if pattern.search(q):
            return "why"

    for pattern in HOW_PATTERNS:
        if pattern.search(q):
            return "how"

    return "general"


def extract_key_info(sentence: str, q_type: str) -> str:
    """Пытается выделить самую важную часть предложения"""
    if q_type == "when":
        for pat in DATE_PATTERNS:
            m = pat.search(sentence)
            if m:
                start = max(0, m.start() - 40)
                end = min(len(sentence), m.end() + 60)
                return sentence[start:end].strip()

        for pat in YEAR_PATTERNS:
            m = pat.search(sentence)
            if m:
                start = max(0, m.start() - 50)
                end = min(len(sentence), m.end() + 80)
                return sentence[start:end].strip()

    if q_type == "how_many":
        for pat in NUMBER_PATTERNS:
            m = pat.search(sentence)
            if m:
                start = max(0, m.start() - 30)
                end = min(len(sentence), m.end() + 60)
                return sentence[start:end].strip()

    if q_type in ("what", "who"):
        m = RE_DEFINITION_MARKER.search(sentence)
        if m:
            return sentence[m.end():].strip()[:300]

    return sentence


def build_short_answer(top_sentences: list, query: str, q_type: str) -> str:
    """Строит короткий ответ из лучших предложений"""
    if not top_sentences:
        return "Не удалось найти информацию в интернете."

    parts = []

    for score, sent, url in top_sentences[:3]:
        key = extract_key_info(sent, q_type)

        key = key.strip()
        if not key.endswith(('.', '!', '?')):
            key += '.'

        if key and key not in parts:
            parts.append(key)

    if not parts:
        return "Не удалось извлечь ответ из найденных данных."

    answer = " ".join(parts[:2])

    if len(answer) > MAX_ANSWER_LEN:
        answer = answer[:MAX_ANSWER_LEN]
        last_dot = answer.rfind('.')
        if last_dot > MAX_ANSWER_LEN // 2:
            answer = answer[:last_dot + 1]

    return answer.strip()


def get_source_links(web_data: dict, max_links: int = 3) -> list:
    """Возвращает список использованных источников"""
    sources = []
    for src in web_data.get("results", [])[:max_links]:
        sources.append(src["url"])
    return sources


# ==============================================================================
# БЛОК 13: МОДУЛЬ ЗАПИСИ РЕЗУЛЬТАТОВ
# ==============================================================================

def format_report(query: str, answer: str, sources: list,
                  q_type: str, sources_count: int) -> str:
    """Форматирует итоговый отчёт"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "=" * 60,
        f"Запрос:   {query}",
        f"Дата:     {now}",
        f"Источников обработано: {sources_count}",
        "-" * 60,
        "ОТВЕТ:",
        "",
        answer,
        "",
        "-" * 60,
        "Источники:",
    ]

    for i, src in enumerate(sources, 1):
        lines.append(f"  {i}. {src}")

    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)


def save_to_file(report: str, filepath: str = OUTPUT_FILE) -> None:
    """Сохраняет отчёт в файл"""
    mode = "a" if os.path.exists(filepath) else "w"
    with open(filepath, mode, encoding="utf-8") as f:
        f.write(report)


def init_output_file(filepath: str = OUTPUT_FILE) -> None:
    """Создаёт файл с заголовком при первом запуске"""
    if not os.path.exists(filepath):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"AI Ответы — Запущен: {now}\n")
            f.write("=" * 60 + "\n\n")


# ==============================================================================
# БЛОК 14: ГЛАВНАЯ ФУНКЦИЯ ОБРАБОТКИ ВОПРОСА
# ==============================================================================

def process_question(query: str, verbose: bool = True) -> str:
    """
    Главная функция:
    1. Ищет в интернете
    2. Обрабатывает тексты
    3. Извлекает короткий правильный ответ
    4. Сохраняет в main.txt
    5. Возвращает ответ
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    init_output_file()

    web_data = collect_web_texts(query, verbose=verbose)

    if not web_data["results"]:
        answer = "Не удалось найти информацию — проверьте подключение к интернету."
        report = format_report(query, answer, [], "general", 0)
        save_to_file(report)
        return answer

    q_type = determine_question_type(query)

    if verbose:
        print(f"[AI] Тип вопроса: {q_type}")
        print("[AI] Извлекаю ответ...")

    top_sentences = extract_best_sentences(web_data, query, top_n=TOP_SENTENCES)

    answer = build_short_answer(top_sentences, query, q_type)

    sources = get_source_links(web_data, max_links=3)
    report = format_report(
        query, answer, sources, q_type, web_data["sources_count"]
    )

    save_to_file(report)

    if verbose:
        print(f"[AI] Ответ сохранён в {OUTPUT_FILE}")

    return answer


# ==============================================================================
# БЛОК 15: ВСПОМОГАТЕЛЬНЫЕ УТИЛИТЫ
# ==============================================================================

def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Суммаризирует длинный текст до нескольких предложений"""
    sentences = split_into_sentences(text)
    sentences = remove_noise_sentences(sentences)

    if not sentences:
        return text[:MAX_ANSWER_LEN]

    word_freq = Counter()
    for sent in sentences:
        for word in get_word_tokens(sent):
            word_freq[word] += 1

    scored = []
    for i, sent in enumerate(sentences):
        words = get_word_tokens(sent)
        if not words:
            continue
        score = sum(word_freq[w] for w in words) / len(words)
        score += score_by_position(i, len(sentences))
        scored.append((score, sent))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = [s for _, s in scored[:max_sentences]]

    idx_order = {sent: i for i, sent in enumerate(sentences)}
    best.sort(key=lambda s: idx_order.get(s, 999))

    return " ".join(best)


def count_words(text: str) -> int:
    """Подсчитывает количество слов"""
    return len(re.findall(r'\b\w+\b', text))


def truncate_to_sentence(text: str, max_len: int = MAX_ANSWER_LEN) -> str:
    """Обрезает текст до ближайшего конца предложения"""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_dot = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
    if last_dot > max_len // 2:
        return truncated[:last_dot + 1]
    return truncated + "..."


def deduplicate_sentences(sentences: list) -> list:
    """Удаляет дублирующиеся предложения"""
    seen = set()
    unique = []
    for sent in sentences:
        key = frozenset(get_word_tokens(sent, remove_stops=True)[:8])
        if key not in seen:
            seen.add(key)
            unique.append(sent)
    return unique


def merge_short_sentences(sentences: list, min_len: int = 60) -> list:
    """Объединяет слишком короткие предложения с соседними"""
    result = []
    buffer = ""

    for sent in sentences:
        if len(buffer) < min_len:
            buffer = (buffer + " " + sent).strip()
        else:
            if buffer:
                result.append(buffer)
            buffer = sent

    if buffer:
        result.append(buffer)

    return result


def highlight_answer_parts(text: str, query_words: set) -> str:
    """Выделяет части текста, содержащие ключевые слова запроса"""
    sentences = split_into_sentences(text)
    relevant = []
    for sent in sentences:
        words = set(get_word_tokens(sent))
        if words & query_words:
            relevant.append(sent)
    return " ".join(relevant[:3])


def extract_numbers_from_text(text: str) -> list:
    """Извлекает все числа и цифровые данные из текста"""
    results = []
    patterns = [
        re.compile(r'\d+(?:[,\.]\d+)?\s*(?:млн|миллион|тысяч|млрд|billion|million|km|км|кг|г|м\b|л\b)', re.I),
        re.compile(r'\d{4}\s*(?:год|г\.)', re.I),
        re.compile(r'\b\d+(?:[,\.]\d+)?\b'),
    ]
    for pat in patterns:
        for m in pat.finditer(text):
            results.append(m.group().strip())
    return results[:10]


def extract_proper_nouns(text: str) -> list:
    """Извлекает собственные имена (слова с заглавной буквы)"""
    pattern = re.compile(r'\b[А-ЯA-Z][а-яёa-z]{2,}(?:\s+[А-ЯA-Z][а-яёa-z]{2,})*\b')
    found = pattern.findall(text)
    return list(dict.fromkeys(found))[:20]


def find_definitions_in_text(text: str, subject: str) -> list:
    """Ищет определения предмета в тексте"""
    subject_lower = subject.lower()
    sentences = split_into_sentences(text)
    definitions = []

    for sent in sentences:
        if subject_lower in sent.lower():
            if RE_DEFINITION_MARKER.search(sent):
                definitions.append(sent)

    return definitions[:3]


def compute_text_similarity(text1: str, text2: str) -> float:
    """Вычисляет схожесть двух текстов (Jaccard similarity)"""
    words1 = set(get_word_tokens(text1))
    words2 = set(get_word_tokens(text2))
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


def rank_sources_by_relevance(web_data: dict, query: str) -> list:
    """Ранжирует источники по релевантности запросу"""
    query_words = build_query_words(query)
    ranked = []

    for src in web_data.get("results", []):
        text_words = set(get_word_tokens(src["text"]))
        relevance = len(text_words & query_words)
        quality_bonus = src["quality"] * 5
        total = relevance + quality_bonus
        ranked.append((total, src))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [src for _, src in ranked]


def extract_wikipedia_lead(text: str) -> str:
    """Извлекает вводный абзац из Wikipedia-подобного текста"""
    sentences = split_into_sentences(text)
    clean = remove_noise_sentences(sentences)

    if not clean:
        return ""

    lead = clean[0]
    if len(lead) < 100 and len(clean) > 1:
        lead = lead + " " + clean[1]

    return lead[:400]


def build_summary_from_multiple_sources(web_data: dict, query: str) -> str:
    """Строит резюме из нескольких источников"""
    ranked = rank_sources_by_relevance(web_data, query)
    query_words = build_query_words(query)

    all_relevant = []
    for src in ranked[:3]:
        sentences = split_into_sentences(src["text"])
        sentences = remove_noise_sentences(sentences)

        for sent in sentences:
            words = set(get_word_tokens(sent))
            if words & query_words:
                all_relevant.append(sent)

    all_relevant = deduplicate_sentences(all_relevant)

    if not all_relevant:
        return ""

    return " ".join(all_relevant[:3])


def extract_answer_for_who_question(web_data: dict, subject: str) -> str:
    """Специализированное извлечение для вопросов «кто такой»"""
    combined = web_data.get("combined_text", "")
    definitions = find_definitions_in_text(combined, subject)

    if definitions:
        best = min(definitions, key=len)
        return truncate_to_sentence(best, 400)

    return ""


def extract_answer_for_when_question(web_data: dict, query: str) -> str:
    """Специализированное извлечение для вопросов «когда»"""
    combined = web_data.get("combined_text", "")
    query_words = build_query_words(query)

    sentences = split_into_sentences(combined)
    sentences = remove_noise_sentences(sentences)

    candidates = []
    for sent in sentences:
        words = set(get_word_tokens(sent))
        if words & query_words:
            numbers = extract_numbers_from_text(sent)
            if numbers:
                score = len(words & query_words) * 2 + len(numbers)
                candidates.append((score, sent))

    if not candidates:
        return ""

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def extract_answer_for_how_many_question(web_data: dict, query: str) -> str:
    """Специализированное извлечение для вопросов «сколько»"""
    combined = web_data.get("combined_text", "")
    query_words = build_query_words(query)

    sentences = split_into_sentences(combined)
    sentences = remove_noise_sentences(sentences)

    candidates = []
    for sent in sentences:
        words = set(get_word_tokens(sent))
        overlap = len(words & query_words)
        if overlap > 0:
            numbers = extract_numbers_from_text(sent)
            if numbers:
                candidates.append((overlap + len(numbers) * 2, sent))

    if not candidates:
        return ""

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


# ==============================================================================
# БЛОК 16: РАСШИРЕННЫЙ ПРОЦЕССОР ОТВЕТОВ
# ==============================================================================

class AnswerProcessor:
    """Обрабатывает ответы с учётом типа вопроса"""

    def __init__(self, web_data: dict, query: str, q_type: str):
        self.web_data = web_data
        self.query = query
        self.q_type = q_type
        self.combined = web_data.get("combined_text", "")
        self.query_words = build_query_words(query)

    def process(self) -> str:
        """Выбирает и применяет подходящую стратегию"""
        if self.q_type == "who":
            return self._process_who()
        if self.q_type == "when":
            return self._process_when()
        if self.q_type == "how_many":
            return self._process_how_many()
        if self.q_type == "where":
            return self._process_where()
        if self.q_type == "what":
            return self._process_what()
        return self._process_general()

    def _process_who(self) -> str:
        subject = self._extract_subject_from_query()
        if subject:
            ans = extract_answer_for_who_question(self.web_data, subject)
            if ans:
                return ans
        return self._process_general()

    def _process_when(self) -> str:
        ans = extract_answer_for_when_question(self.web_data, self.query)
        if ans:
            return truncate_to_sentence(ans, 350)
        return self._process_general()

    def _process_how_many(self) -> str:
        ans = extract_answer_for_how_many_question(self.web_data, self.query)
        if ans:
            return truncate_to_sentence(ans, 350)
        return self._process_general()

    def _process_where(self) -> str:
        return self._process_general()

    def _process_what(self) -> str:
        subject = self._extract_subject_from_query()
        if subject and len(subject) > 2:
            definitions = find_definitions_in_text(self.combined, subject)
            if definitions:
                return truncate_to_sentence(definitions[0], 400)
        return self._process_general()

    def _process_general(self) -> str:
        top = extract_best_sentences(self.web_data, self.query, top_n=3)
        return build_short_answer(top, self.query, self.q_type)

    def _extract_subject_from_query(self) -> str:
        q = self.query.lower()
        patterns = [
            re.compile(r'(?:кто такой|кто такая|что такое|о чём|про|о)\s+(.+)', re.I),
            re.compile(r'(?:who is|what is|about)\s+(.+)', re.I),
        ]
        for pat in patterns:
            m = pat.search(q)
            if m:
                return m.group(1).strip()

        words = [w for w in self.query.split()
                 if len(w) > 3 and w.lower() not in ALL_STOP_WORDS]
        return " ".join(words[:3]) if words else ""


# ==============================================================================
# БЛОК 17: УЛУЧШЕННАЯ ГЛАВНАЯ ФУНКЦИЯ
# ==============================================================================

def ask(query: str, verbose: bool = True) -> str:
    """
    Главный интерфейс:
    Задай вопрос → получи короткий правильный ответ → сохранён в main.txt
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    init_output_file()

    if verbose:
        print(f"\n{'='*60}")
        print(f"Вопрос: {query}")
        print(f"{'='*60}")

    web_data = collect_web_texts(query, verbose=verbose)

    if not web_data["results"]:
        answer = ("Не удалось найти информацию. "
                  "Проверьте подключение к интернету.")
        report = format_report(query, answer, [], "general", 0)
        save_to_file(report)
        if verbose:
            print(f"\nОтвет: {answer}")
        return answer

    q_type = determine_question_type(query)

    if verbose:
        print(f"[AI] Анализирую... (тип: {q_type})")

    processor = AnswerProcessor(web_data, query, q_type)
    answer = processor.process()

    if not answer or len(answer) < 10:
        top = extract_best_sentences(web_data, query, top_n=5)
        answer = build_short_answer(top, query, q_type)

    if not answer or len(answer) < 10:
        summary = build_summary_from_multiple_sources(web_data, query)
        if summary:
            answer = truncate_to_sentence(summary, MAX_ANSWER_LEN)

    if not answer or len(answer) < 10:
        answer = "Не удалось извлечь точный ответ из найденных данных."

    sources = get_source_links(web_data, max_links=3)
    report = format_report(
        query, answer, sources, q_type, web_data["sources_count"]
    )
    save_to_file(report)

    if verbose:
        print(f"\n{'='*60}")
        print(f"ОТВЕТ:\n{answer}")
        print(f"{'='*60}")
        print(f"Сохранено в: {OUTPUT_FILE}")

    return answer


# ==============================================================================
# БЛОК 18: ПАКЕТНАЯ ОБРАБОТКА ВОПРОСОВ
# ==============================================================================

def ask_batch(questions: list, verbose: bool = False) -> dict:
    """
    Задаёт несколько вопросов подряд.
    Возвращает словарь {вопрос: ответ}.
    """
    results = {}
    total = len(questions)

    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{total}] {q}")
        try:
            answer = ask(q, verbose=verbose)
            results[q] = answer
        except Exception as e:
            results[q] = f"Ошибка: {e}"
        time.sleep(1.0)

    return results


def ask_from_file(filepath: str, verbose: bool = False) -> None:
    """Читает вопросы из файла и отвечает на каждый"""
    if not os.path.exists(filepath):
        print(f"Файл не найден: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    print(f"Загружено {len(questions)} вопросов из {filepath}")
    answers = ask_batch(questions, verbose=verbose)

    for q, a in answers.items():
        print(f"\nВопрос: {q}")
        print(f"Ответ:  {a}")


# ==============================================================================
# БЛОК 19: ИНТЕРАКТИВНЫЙ РЕЖИМ
# ==============================================================================

def interactive_mode() -> None:
    """Интерактивный диалог с AI"""
    print("\n" + "=" * 60)
    print("  AI — Поиск в интернете + короткий ответ")
    print(f"  Ответы сохраняются в: {OUTPUT_FILE}")
    print("  Введите 'выход' для завершения")
    print("=" * 60)

    while True:
        try:
            query = input("\nВопрос: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[AI] Завершение.")
            break

        if not query:
            continue

        if query.lower() in ["выход", "exit", "quit", "q", "stop", "bye"]:
            print("[AI] До свидания!")
            break

        ask(query, verbose=True)


def single_question_mode(query: str) -> None:
    """Отвечает на один вопрос из аргументов командной строки"""
    answer = ask(query, verbose=True)
    print(f"\nГотово. Ответ сохранён в {OUTPUT_FILE}")


# ==============================================================================
# БЛОК 20: ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ ТЕКСТОВОГО АНАЛИЗА
# ==============================================================================

def get_text_language(text: str) -> str:
    """Определяет язык текста (ru/en/unknown)"""
    ru_count = len(re.findall(r'[а-яёА-ЯЁ]', text))
    en_count = len(re.findall(r'[a-zA-Z]', text))
    total = ru_count + en_count

    if total == 0:
        return "unknown"
    if ru_count / total > 0.6:
        return "ru"
    if en_count / total > 0.6:
        return "en"
    return "mixed"


def clean_answer_text(text: str) -> str:
    """Финальная очистка текста ответа"""
    text = text.strip()
    text = RE_MULTIPLE_SPACES.sub(" ", text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\s+([.,!?:;])', r'\1', text)
    text = re.sub(r'([.!?])\s*([.!?])', r'\1', text)

    if text and not text[-1] in '.!?':
        text += '.'

    if text:
        text = text[0].upper() + text[1:]

    return text


def estimate_answer_quality(answer: str, query: str) -> float:
    """Оценивает качество ответа (0.0 — 1.0)"""
    if not answer or len(answer) < 20:
        return 0.0

    score = 0.5

    query_words = build_query_words(query)
    answer_words = set(get_word_tokens(answer))
    overlap = len(query_words & answer_words) / max(len(query_words), 1)
    score += overlap * 0.3

    if 50 <= len(answer) <= 400:
        score += 0.1
    elif len(answer) > 400:
        score -= 0.1

    if any(w in answer.lower() for w in QUALITY_BOOST_WORDS):
        score += 0.1

    for w in QUALITY_PENALTY_WORDS:
        if w in answer.lower():
            score -= 0.2

    return max(0.0, min(1.0, score))


def format_sources_block(sources: list) -> str:
    """Форматирует блок источников для вывода"""
    if not sources:
        return "Источники не найдены."
    lines = []
    for i, src in enumerate(sources, 1):
        domain = urlparse(src).netloc.replace("www.", "")
        lines.append(f"{i}. {domain} — {src}")
    return "\n".join(lines)


def extract_sentences_with_context(
        text: str, keyword: str, context_size: int = 1
) -> list:
    """Возвращает предложения с ключевым словом + соседние"""
    sentences = split_into_sentences(text)
    results = []

    for i, sent in enumerate(sentences):
        if keyword.lower() in sent.lower():
            start = max(0, i - context_size)
            end = min(len(sentences), i + context_size + 1)
            context = " ".join(sentences[start:end])
            results.append(context)

    return results[:3]


def count_keyword_mentions(text: str, keywords: list) -> dict:
    """Подсчитывает упоминания ключевых слов"""
    text_lower = text.lower()
    counts = {}
    for kw in keywords:
        counts[kw] = text_lower.count(kw.lower())
    return counts


def get_most_mentioned(text: str, candidates: list) -> str:
    """Возвращает наиболее упоминаемый элемент из списка"""
    counts = count_keyword_mentions(text, candidates)
    if not counts:
        return ""
    return max(counts.items(), key=lambda x: x[1])[0]


def sliding_window_extract(text: str, window_size: int = 3) -> list:
    """Извлекает группы предложений скользящим окном"""
    sentences = split_into_sentences(text)
    sentences = remove_noise_sentences(sentences)
    windows = []

    for i in range(len(sentences) - window_size + 1):
        window = " ".join(sentences[i:i + window_size])
        windows.append(window)

    return windows


def tf_idf_score(sentence: str, all_sentences: list) -> float:
    """Простой TF-IDF для оценки важности предложения"""
    words = get_word_tokens(sentence)
    if not words:
        return 0.0

    n = len(all_sentences)
    score = 0.0

    word_freq = Counter(get_word_tokens(sentence))
    total_words = len(words)

    for word, count in word_freq.items():
        tf = count / total_words
        doc_count = sum(1 for s in all_sentences if word in s.lower())
        idf = math.log((n + 1) / (doc_count + 1)) + 1
        score += tf * idf

    return score / len(word_freq) if word_freq else 0.0


def rank_sentences_tfidf(sentences: list, query_words: set) -> list:
    """Ранжирует предложения через TF-IDF + query overlap"""
    scored = []
    for sent in sentences:
        tfidf = tf_idf_score(sent, sentences)
        words = set(get_word_tokens(sent))
        overlap = len(words & query_words)
        total = tfidf + overlap * 2.0
        scored.append((total, sent))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored]


def extract_with_tfidf(web_data: dict, query: str, top_n: int = 3) -> str:
    """Извлекает ответ через TF-IDF"""
    all_sentences = []
    for src in web_data.get("results", []):
        sents = split_into_sentences(src["text"])
        sents = remove_noise_sentences(sents)
        all_sentences.extend(sents)

    query_words = build_query_words(query)
    ranked = rank_sentences_tfidf(all_sentences, query_words)

    unique = deduplicate_sentences(ranked[:top_n * 3])[:top_n]

    if not unique:
        return ""

    return truncate_to_sentence(" ".join(unique), MAX_ANSWER_LEN)


# ==============================================================================
# БЛОК 21: ТОЧКА ВХОДА
# ==============================================================================

# Точка входа перенесена в конец файла — см. if __name__ == "__main__": main()


# =================================================================================
# БЛОК 22: МУЛЬТИЯЗЫЧНЫЕ СТОП-СЛОВА (словари 19 языков для международного NLP)
# =================================================================================
MULTILINGUAL_STOP_WORDS = {
    "de": {
        "der",
        "die",
        "das",
        "und",
        "in",
        "zu",
        "den",
        "des",
        "mit",
        "dem",
        "ist",
        "es",
        "auf",
        "nicht",
        "ein",
        "eine",
        "auch",
        "als",
        "an",
        "aus",
        "bei",
        "da",
        "durch",
        "er",
        "fur",
        "hat",
        "hier",
        "nach",
        "noch",
        "nur",
        "oder",
        "sich",
        "sie",
        "sind",
        "so",
        "um",
        "uns",
        "von",
        "vor",
        "war",
        "was",
        "wenn",
        "wird",
        "wir",
        "wo",
    },
    "fr": {
        "le",
        "la",
        "les",
        "de",
        "du",
        "des",
        "un",
        "une",
        "et",
        "en",
        "au",
        "aux",
        "par",
        "sur",
        "avec",
        "dans",
        "pour",
        "il",
        "elle",
        "ils",
        "elles",
        "ce",
        "se",
        "sa",
        "son",
        "ses",
        "leur",
        "leurs",
        "nous",
        "vous",
        "que",
        "qui",
        "dont",
        "mais",
        "ou",
        "donc",
        "ni",
        "car",
    },
    "es": {
        "el",
        "la",
        "los",
        "las",
        "un",
        "una",
        "de",
        "en",
        "y",
        "a",
        "que",
        "por",
        "con",
        "del",
        "al",
        "le",
        "se",
        "no",
        "es",
        "si",
        "lo",
        "sus",
        "les",
        "para",
        "como",
        "mas",
        "pero",
        "su",
        "cuando",
        "donde",
        "porque",
        "aunque",
        "mientras",
        "sin",
        "sobre",
    },
    "it": {
        "il",
        "la",
        "i",
        "le",
        "di",
        "in",
        "e",
        "a",
        "un",
        "una",
        "che",
        "per",
        "con",
        "del",
        "al",
        "lo",
        "si",
        "non",
        "da",
        "su",
        "come",
        "ma",
        "anche",
        "ci",
        "mi",
        "ti",
        "se",
        "poi",
        "quando",
        "dove",
        "dopo",
        "prima",
        "tra",
        "fra",
        "senza",
        "ancora",
    },
    "pt": {
        "o",
        "a",
        "os",
        "as",
        "um",
        "uma",
        "de",
        "em",
        "e",
        "que",
        "por",
        "com",
        "do",
        "da",
        "no",
        "na",
        "se",
        "nao",
        "para",
        "como",
        "mais",
        "mas",
        "este",
        "esta",
        "esse",
        "essa",
        "seu",
        "sua",
        "seus",
        "suas",
        "meu",
        "minha",
        "nosso",
        "nossa",
    },
    "nl": {
        "de",
        "het",
        "een",
        "in",
        "van",
        "op",
        "te",
        "en",
        "is",
        "dat",
        "voor",
        "aan",
        "met",
        "zijn",
        "als",
        "hij",
        "zij",
        "we",
        "er",
        "niet",
        "ook",
        "maar",
        "naar",
        "ze",
        "haar",
        "hem",
        "dit",
        "die",
        "wat",
        "wie",
        "hoe",
        "waar",
        "dan",
        "nog",
        "al",
        "door",
        "om",
        "bij",
    },
    "pl": {
        "i",
        "w",
        "z",
        "na",
        "do",
        "to",
        "sie",
        "nie",
        "jest",
        "ze",
        "jak",
        "ale",
        "go",
        "co",
        "by",
        "tak",
        "juz",
        "czy",
        "jego",
        "jej",
        "ich",
        "tego",
        "tej",
        "tym",
        "ten",
        "ta",
        "te",
        "przez",
        "po",
        "od",
        "za",
        "przed",
        "nad",
        "pod",
    },
    "cs": {
        "a",
        "v",
        "na",
        "je",
        "se",
        "to",
        "ze",
        "s",
        "z",
        "i",
        "ale",
        "nebo",
        "ani",
        "jak",
        "pro",
        "do",
        "po",
        "od",
        "za",
        "pred",
        "nad",
        "pod",
        "pri",
        "o",
        "k",
        "ke",
        "co",
        "kdo",
        "kde",
        "kdy",
        "proc",
    },
    "sv": {
        "och",
        "i",
        "att",
        "en",
        "ett",
        "det",
        "ar",
        "av",
        "som",
        "med",
        "pa",
        "han",
        "hon",
        "vi",
        "de",
        "den",
        "var",
        "sig",
        "for",
        "inte",
        "om",
        "men",
        "till",
        "fran",
        "man",
        "sa",
        "efter",
        "under",
        "vid",
        "utan",
        "mot",
        "over",
        "ska",
        "kan",
        "hade",
        "har",
    },
    "da": {
        "og",
        "i",
        "det",
        "at",
        "en",
        "til",
        "er",
        "som",
        "pa",
        "de",
        "med",
        "han",
        "af",
        "for",
        "ikke",
        "der",
        "var",
        "mig",
        "sig",
        "et",
        "hun",
        "vi",
        "din",
        "dine",
        "vores",
        "deres",
        "min",
        "mit",
        "mine",
    },
    "fi": {
        "ja",
        "on",
        "ei",
        "se",
        "en",
        "et",
        "ole",
        "han",
        "me",
        "te",
        "he",
        "tama",
        "tuo",
        "joka",
        "mita",
        "kuka",
        "missa",
        "milloin",
        "miksi",
        "miten",
        "mutta",
        "tai",
        "koska",
        "kun",
        "jos",
        "etta",
        "kuin",
    },
    "hu": {
        "a",
        "az",
        "es",
        "hogy",
        "nem",
        "is",
        "de",
        "meg",
        "mar",
        "csak",
        "el",
        "ki",
        "be",
        "le",
        "fel",
        "ra",
        "at",
        "utan",
        "elott",
        "alatt",
        "felett",
        "mogott",
        "helyett",
        "nelkul",
        "altal",
        "miatt",
    },
    "ro": {
        "si",
        "in",
        "la",
        "de",
        "cu",
        "nu",
        "se",
        "ca",
        "pe",
        "din",
        "sau",
        "dar",
        "prin",
        "pentru",
        "care",
        "este",
        "sunt",
        "era",
        "au",
        "va",
        "fie",
        "il",
        "le",
        "lui",
        "lor",
        "meu",
        "tau",
    },
    "bg": {
        "i",
        "v",
        "na",
        "e",
        "se",
        "za",
        "da",
        "ne",
        "s",
        "ot",
        "po",
        "pri",
        "do",
        "nad",
        "pod",
        "bez",
        "no",
        "ili",
        "a",
        "go",
        "mu",
        "im",
        "ni",
        "vi",
    },
    "hr": {
        "i",
        "u",
        "na",
        "je",
        "se",
        "za",
        "da",
        "ne",
        "s",
        "od",
        "po",
        "pri",
        "do",
        "nad",
        "pod",
        "bez",
        "ali",
        "ili",
        "a",
        "ga",
        "mu",
    },
    "tr": {
        "ve",
        "bir",
        "bu",
        "da",
        "de",
        "ile",
        "icin",
        "ama",
        "ya",
        "hem",
        "ne",
        "ki",
        "daha",
        "en",
        "cok",
        "az",
        "her",
        "bazi",
        "hic",
        "ise",
        "gibi",
        "kadar",
        "beri",
        "once",
        "sonra",
    },
    "id": {
        "dan",
        "di",
        "yang",
        "ke",
        "dari",
        "dengan",
        "untuk",
        "tidak",
        "ini",
        "itu",
        "saya",
        "kita",
        "kami",
        "mereka",
        "adalah",
        "ada",
        "akan",
        "sudah",
        "bisa",
        "harus",
        "atau",
        "tetapi",
        "juga",
    },
    "ms": {
        "dan",
        "di",
        "yang",
        "ke",
        "dari",
        "dengan",
        "untuk",
        "tidak",
        "ini",
        "itu",
        "saya",
        "kami",
        "mereka",
        "adalah",
        "ada",
        "akan",
        "sudah",
        "boleh",
        "atau",
        "tetapi",
        "juga",
    },
    "vi": {
        "va",
        "o",
        "trong",
        "cua",
        "mot",
        "co",
        "la",
        "voi",
        "tu",
        "cho",
        "khong",
        "nay",
        "do",
        "khi",
        "nhung",
        "hay",
        "vi",
        "neu",
    },
    "hi": {
        "aur",
        "ko",
        "ke",
        "mein",
        "se",
        "par",
        "hai",
        "ka",
        "ki",
        "yah",
        "vah",
        "ham",
        "ve",
        "to",
        "bhi",
        "hi",
        "kya",
    },
}

def remove_multilingual_stops(text, lang="auto"):
    """Удаляет стоп-слова с учётом языка текста"""
    detected = get_text_language(text) if lang == "auto" else lang
    stops = set(MULTILINGUAL_STOP_WORDS.get(detected, {})) | ALL_STOP_WORDS
    return " ".join(w for w in text.split() if w.lower() not in stops)

# =================================================================================
# БЛОК 23: ТАБЛИЦА ЕДИНИЦ ИЗМЕРЕНИЯ (33 единицы)
# =================================================================================
UNITS_MAP = {
    "m": {"ru": "метр", "en": "meter"},
    "km": {"ru": "километр", "en": "kilometer"},
    "kg": {"ru": "килограмм", "en": "kilogram"},
    "g": {"ru": "грамм", "en": "gram"},
    "t": {"ru": "тонна", "en": "ton"},
    "ha": {"ru": "гектар", "en": "hectare"},
    "km2": {"ru": "кв.км", "en": "sq km"},
    "m2": {"ru": "кв.м", "en": "sq m"},
    "l": {"ru": "литр", "en": "liter"},
    "ml": {"ru": "миллилитр", "en": "milliliter"},
    "s": {"ru": "секунда", "en": "second"},
    "min": {"ru": "минута", "en": "minute"},
    "h": {"ru": "час", "en": "hour"},
    "d": {"ru": "день", "en": "day"},
    "y": {"ru": "год", "en": "year"},
    "Hz": {"ru": "герц", "en": "hertz"},
    "kHz": {"ru": "килогерц", "en": "kilohertz"},
    "MHz": {"ru": "мегагерц", "en": "megahertz"},
    "GHz": {"ru": "гигагерц", "en": "gigahertz"},
    "W": {"ru": "ватт", "en": "watt"},
    "kW": {"ru": "киловатт", "en": "kilowatt"},
    "MW": {"ru": "мегаватт", "en": "megawatt"},
    "V": {"ru": "вольт", "en": "volt"},
    "A": {"ru": "ампер", "en": "ampere"},
    "J": {"ru": "джоуль", "en": "joule"},
    "N": {"ru": "ньютон", "en": "newton"},
    "mm": {"ru": "миллиметр", "en": "millimeter"},
    "cm": {"ru": "сантиметр", "en": "centimeter"},
    "B": {"ru": "байт", "en": "byte"},
    "KB": {"ru": "килобайт", "en": "kilobyte"},
    "MB": {"ru": "мегабайт", "en": "megabyte"},
    "GB": {"ru": "гигабайт", "en": "gigabyte"},
    "TB": {"ru": "терабайт", "en": "terabyte"},
}

def extract_measurements(text):
    """Извлекает числа с единицами измерения из текста"""
    import re as _re2
    all_units = []
    for sym, names in UNITS_MAP.items():
        for name in [sym, names["ru"], names["en"]]:
            escaped = re.escape(name)
            pat = re.compile(r'\b(\d+(?:[,.]\d+)?)\s*' + escaped + r'\b', re.I)
            for m in pat.finditer(text):
                all_units.append(m.group())
    return list(dict.fromkeys(all_units))

# =================================================================================
# БЛОК 24: ПРЕМИУМ-ДОМЕНЫ (надёжные источники информации)
# =================================================================================
PREMIUM_DOMAINS = {
    "wikipedia.org",
    "britannica.com",
    "nationalgeographic.com",
    "nature.com",
    "science.org",
    "sciencedirect.com",
    "pubmed.ncbi.nlm.nih.gov",
    "who.int",
    "un.org",
    "worldbank.org",
    "cia.gov",
    "nasa.gov",
    "noaa.gov",
    "cdc.gov",
    "nih.gov",
    "gov.uk",
    "bbc.co.uk",
    "guardian.com",
    "nytimes.com",
    "washingtonpost.com",
    "reuters.com",
    "apnews.com",
    "npr.org",
    "history.com",
    "smithsonianmag.com",
    "scientificamerican.com",
    "arxiv.org",
    "researchgate.net",
    "springer.com",
    "mit.edu",
    "stanford.edu",
    "harvard.edu",
    "stackoverflow.com",
    "github.com",
    "developer.mozilla.org",
    "docs.python.org",
    "healthline.com",
    "mayoclinic.org",
    "webmd.com",
    "investopedia.com",
    "ria.ru",
    "tass.ru",
    "rbc.ru",
    "lenta.ru",
    "habr.com",
    "tproger.ru",
    "worldometers.info",
    "ourworldindata.org",
    "statista.com",
}

def is_premium_domain(url):
    """True если домен из списка надёжных"""
    try:
        from urllib.parse import urlparse as _up
        d = _up(url).netloc.replace("www.","").lower()
        return any(p in d for p in PREMIUM_DOMAINS)
    except Exception:
        return False

# =================================================================================
# БЛОК 25: СИНОНИМЫ ВОПРОСНЫХ СЛОВ (7 типов × ~20 вариантов)
# =================================================================================
QUESTION_SYNONYMS = {
    "who": [
        "кто такой",
        "кто такая",
        "кто это",
        "кем является",
        "кто создал",
        "кто основал",
        "кто написал",
        "кто изобрел",
        "кто открыл",
        "кто президент",
        "кто автор",
        "who is",
        "who was",
        "who are",
        "who created",
        "who founded",
        "who invented",
        "who wrote",
        "who discovered",
        "who leads",
        "who directed",
        "who won",
    ],
    "what": [
        "что такое",
        "что это",
        "что значит",
        "что означает",
        "из чего состоит",
        "как устроен",
        "как работает",
        "объясни",
        "расскажи про",
        "расскажи о",
        "what is",
        "what are",
        "what does",
        "define",
        "explain",
        "describe",
        "what means",
    ],
    "when": [
        "когда",
        "в каком году",
        "в каком веке",
        "год основания",
        "год рождения",
        "год создания",
        "год смерти",
        "когда был основан",
        "когда родился",
        "when was",
        "when did",
        "when is",
        "what year",
        "what date",
        "when founded",
        "when born",
        "when created",
        "when invented",
        "when happened",
    ],
    "where": [
        "где",
        "в какой стране",
        "в каком городе",
        "столица",
        "где находится",
        "где расположен",
        "where is",
        "where are",
        "what country",
        "what city",
        "where located",
        "where found",
        "where born",
        "where originated",
    ],
    "how_many": [
        "сколько",
        "какова численность",
        "какова длина",
        "какова высота",
        "какова площадь",
        "сколько человек",
        "сколько лет",
        "how many",
        "how much",
        "how long",
        "how far",
        "how old",
        "how big",
        "how tall",
        "how wide",
        "how deep",
        "how fast",
        "what is the population",
        "what is the area",
        "what is the length",
    ],
    "why": [
        "почему",
        "по какой причине",
        "из-за чего",
        "зачем",
        "для чего",
        "что послужило причиной",
        "why is",
        "why was",
        "why does",
        "for what reason",
        "what caused",
        "explain why",
        "what led to",
    ],
    "how": [
        "как",
        "каким образом",
        "каким способом",
        "как сделать",
        "как создать",
        "как использовать",
        "как работает",
        "how to",
        "how do",
        "how does",
        "steps to",
        "method for",
        "guide to",
        "explain how",
    ],
}

_SYN_PATS = {qt: [re.compile(re.escape(s), re.I) for s in syns]
              for qt, syns in QUESTION_SYNONYMS.items()}

def determine_question_type_v2(query):
    """Точное распознавание типа вопроса через синонимы"""
    q = query.lower()
    for qt in ["who","when","where","how_many","what","why","how"]:
        for pat in _SYN_PATS.get(qt, []):
            if pat.search(q): return qt
    return "general"

# =================================================================================
# БЛОК 26: РАСШИРЕНИЕ ЗАПРОСА СИНОНИМАМИ (улучшает поиск)
# =================================================================================
QUERY_EXPAND_MAP = {
    "создал": ["основал", "придумал", "изобрел"],
    "открыл": ["обнаружил", "нашел", "выявил"],
    "умер": ["скончался", "погиб", "дата смерти"],
    "родился": ["дата рождения", "год рождения"],
    "столица": ["главный город", "administrative capital"],
    "население": ["численность", "жителей", "person"],
    "площадь": ["территория", "square km"],
    "высота": ["altitude", "высок"],
    "длина": ["length", "протяженность"],
    "глубина": ["depth", "глубок"],
    "скорость": ["speed", "velocity"],
    "температура": ["temperature", "celsius"],
    "вес": ["weight", "mass", "весит"],
}

def expand_query(query):
    """Расширяет запрос синонимами для лучшего поиска"""
    expanded = query
    for word, syns in QUERY_EXPAND_MAP.items():
        if word in query.lower():
            expanded += " " + " ".join(syns[:2])
    return expanded.strip()

# =================================================================================
# БЛОК 27: АЛГОРИТМЫ NLP (расстояние Левенштейна, косинусная схожесть, MMR)
# =================================================================================

def levenshtein_distance(s1, s2):
    """Расстояние Левенштейна — мера различия двух строк. O(m*n)."""
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[m][n]

def fuzzy_match(s1, s2, threshold=0.8):
    """Нечёткое совпадение через расстояние Левенштейна"""
    ml = max(len(s1), len(s2))
    if not ml: return True
    return 1 - levenshtein_distance(s1.lower(), s2.lower()) / ml >= threshold

def cosine_similarity_bow(text1, text2):
    """Косинусная схожесть двух текстов через Bag-of-Words"""
    w1, w2 = Counter(get_word_tokens(text1)), Counter(get_word_tokens(text2))
    all_w = set(w1) | set(w2)
    if not all_w: return 0.0
    dot = sum(w1.get(w,0)*w2.get(w,0) for w in all_w)
    m1 = math.sqrt(sum(v**2 for v in w1.values()))
    m2 = math.sqrt(sum(v**2 for v in w2.values()))
    return dot/(m1*m2) if m1 and m2 else 0.0

def mmr_selection(sentences, query, top_n=5, lambda_=0.7):
    """MMR: Maximal Marginal Relevance — разнообразные релевантные предложения"""
    if not sentences: return []
    qw = build_query_words(query)
    sc = sorted([(score_sentence(s, qw), s) for s in sentences],
                key=lambda x: x[0], reverse=True)
    selected, rem = [], [s for _,s in sc]
    while rem and len(selected) < top_n:
        if not selected: selected.append(rem.pop(0)); continue
        best, bsc = None, float("-inf")
        for cand in rem:
            rel = score_sentence(cand, qw)
            red = max(cosine_similarity_bow(cand, s) for s in selected)
            s = lambda_*rel-(1-lambda_)*red
            if s > bsc: bsc, best = s, cand
        if best: selected.append(best); rem.remove(best)
    return selected

def extract_with_context_window(web_data, query, window=3):
    """Скользящее окно из N предложений — захватывает контекст"""
    qw = build_query_words(query)
    wins = []
    for src in web_data.get("results", []):
        for w in sliding_window_extract(src["text"], window_size=window):
            wins.append((score_sentence(w, qw), w))
    wins.sort(key=lambda x: x[0], reverse=True)
    return truncate_to_sentence(wins[0][1], MAX_ANSWER_LEN) if wins else ""

def extract_with_mmr(web_data, query, top_n=3):
    """MMR-извлечение: разнообразные релевантные предложения"""
    all_s = []
    for src in web_data.get("results", []):
        all_s.extend(remove_noise_sentences(split_into_sentences(src["text"])))
    sel = mmr_selection(deduplicate_sentences(all_s), query, top_n)
    return truncate_to_sentence(" ".join(sel), MAX_ANSWER_LEN) if sel else ""

def extract_answer_full(web_data, query, q_type=None):
    """Гибридный метод: 4 алгоритма → выбор лучшего по оценке качества"""
    q_type = determine_question_type_v2(query)
    a1 = AnswerProcessor(web_data, query, q_type).process()
    a2 = extract_with_tfidf(web_data, query, top_n=3)
    a3 = extract_with_context_window(web_data, query, window=3)
    a4 = extract_with_mmr(web_data, query, top_n=3)
    cands = [a for a in [a1,a2,a3,a4] if a and len(a)>=15]
    if not cands: return "Не удалось извлечь ответ из найденных данных."
    return clean_answer_text(max(cands, key=lambda a: estimate_answer_quality(a, query)))

# =================================================================================
# БЛОК 28: ПАТТЕРНЫ ИЗВЛЕЧЕНИЯ СТРУКТУРИРОВАННЫХ ДАННЫХ
# =================================================================================

_STRUCT_RAW = {
    "birth": ["родился","родилась","born","дата рождения"],
    "death": ["умер","умерла","died","скончался","дата смерти"],
    "population": ["население","population","жителей","inhabitants"],
    "area": ["площадь","area","territory","sq km","кв.км"],
    "height": ["высота","height","altitude"],
    "length": ["длина","length","протяженность"],
    "depth": ["глубина","depth"],
    "speed": ["скорость","speed","velocity"],
    "temperature": ["температура","temperature","celsius"],
    "weight": ["вес","масса","weight","mass"],
}

STRUCTURED_PATTERNS = {}
for _tp, _words in _STRUCT_RAW.items():
    STRUCTURED_PATTERNS[_tp] = [
        re.compile(r"(?:" + re.escape(w) + r")[^.]{0,60}?(\d[\d\s,.]*)", re.I)
        for w in _words
    ] + [
        re.compile(r"(\d[\d\s,.]*)[^.]{0,30}(?:" + re.escape(w) + r")", re.I)
        for w in _words
    ]

def extract_structured_info(text, info_type):
    """Извлекает структурированные данные (население, площадь, даты...)"""
    for pat in STRUCTURED_PATTERNS.get(info_type, []):
        m = pat.search(text)
        if m:
            try: return m.group(1).strip()
            except IndexError: return m.group().strip()
    return ""

# =================================================================================
# БЛОК 29: ВСТРОЕННАЯ СПРАВКА
# =================================================================================
HELP_TEXT = """
=============================================================
     AI.PY — Поиск в интернете + короткий ответ
=============================================================

УСТАНОВКА:  pip install requests beautifulsoup4

ЗАПУСК:
  python ai.py                          # Интерактивный режим
  python ai.py кто такой Эйнштейн      # Один вопрос
  python ai.py что такое ДНК
  python ai.py -b questions.txt         # Файл с вопросами
  python ai.py --help                   # Эта справка

В КОДЕ:
  from ai import ask, ask_batch, ask_from_file
  answer = ask("что такое квантовая физика")
  results = ask_batch(["кто такой Ньютон", "что такое гравитация"])
  ask_from_file("questions.txt")

КАК РАБОТАЕТ:
  1. Ищет в интернете (DuckDuckGo + Bing)
  2. Загружает до 10 сайтов, извлекает чистый текст
  3. Определяет тип вопроса (кто/что/когда/где/сколько/почему/как)
  4. Применяет 4 алгоритма: Scoring + TF-IDF + Window + MMR
  5. Выбирает лучший ответ → пишет в main.txt + в консоль

РЕЗУЛЬТАТ (main.txt):
  ============================
  Запрос: ваш вопрос
  ОТВЕТ: [короткий точный текст]
  Источники: [ссылки]
  ============================
"""

def show_help():
    print(HELP_TEXT)

# =================================================================================
# БЛОК 30: ТОЧКА ВХОДА С ПОЛНЫМ ГИБРИДНЫМ МЕТОДОМ
# =================================================================================

def _main():
    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()
        if arg1 in ("-h", "--help", "help", "помощь", "справка"):
            show_help(); return
        if arg1 in ("-b", "--batch") and len(sys.argv) > 2:
            ask_from_file(sys.argv[2]); return
        question = " ".join(sys.argv[1:])
        expanded = expand_query(question)
        if expanded != question:
            print(f"[AI] Расширенный запрос: {expanded}")
        web_data = collect_web_texts(expanded, verbose=True)
        if web_data["results"]:
            answer = extract_answer_full(web_data, question)
        else:
            answer = "Нет интернета или сайты недоступны."
        sources = get_source_links(web_data, max_links=3)
        report = format_report(question, answer, sources, "",
                               web_data.get("sources_count", 0))
        save_to_file(report)
        print(f"\nОТВЕТ: {answer}")
        print(f"Сохранено в: {OUTPUT_FILE}")
    else:
        interactive_mode()

# Точка входа перенесена в конец файла — см. if __name__ == "__main__": main()


# =================================================================================
# БЛОК 31: РАСШИРЕННЫЙ КЭШЕР ЗАПРОСОВ (ускоряет повторные вопросы)
# =================================================================================

import hashlib
import json as _json
import datetime as _dt


class QueryCache:
    """
    Кэш ответов на вопросы.
    Сохраняет результаты в файл cache.json,
    чтобы не делать повторные запросы к интернету.
    TTL (time-to-live) по умолчанию 24 часа.
    """

    def __init__(self, cache_file="cache.json", ttl_hours=24):
        self.cache_file = cache_file
        self.ttl = _dt.timedelta(hours=ttl_hours)
        self._data = self._load()

    def _load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return _json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                _json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _key(self, query):
        return hashlib.md5(query.strip().lower().encode("utf-8")).hexdigest()

    def get(self, query):
        k = self._key(query)
        if k not in self._data:
            return None
        entry = self._data[k]
        saved_at = _dt.datetime.fromisoformat(entry["saved_at"])
        if _dt.datetime.now() - saved_at > self.ttl:
            del self._data[k]
            return None
        return entry["answer"]

    def set(self, query, answer):
        k = self._key(query)
        self._data[k] = {
            "query": query,
            "answer": answer,
            "saved_at": _dt.datetime.now().isoformat(),
        }
        self._save()

    def clear_expired(self):
        now = _dt.datetime.now()
        expired = [
            k for k, v in self._data.items()
            if now - _dt.datetime.fromisoformat(v["saved_at"]) > self.ttl
        ]
        for k in expired:
            del self._data[k]
        if expired:
            self._save()
        return len(expired)

    def clear_all(self):
        self._data = {}
        self._save()

    def size(self):
        return len(self._data)

    def list_queries(self):
        return [v["query"] for v in self._data.values()]


_GLOBAL_CACHE = QueryCache()


def ask_cached(query, verbose=True, use_cache=True):
    """
    Как ask(), но с кэшированием.
    При повторном вопросе возвращает сохранённый ответ мгновенно.
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    if use_cache:
        cached = _GLOBAL_CACHE.get(query)
        if cached:
            if verbose:
                print(f"[Cache] Ответ из кэша: {cached}")
            return cached

    answer = ask(query, verbose=verbose)

    if use_cache:
        _GLOBAL_CACHE.set(query, answer)

    return answer


# =================================================================================
# БЛОК 32: ОГРАНИЧИТЕЛЬ СКОРОСТИ ЗАПРОСОВ (Rate Limiter)
# =================================================================================

class RateLimiter:
    """
    Ограничивает количество запросов к интернету в единицу времени.
    По умолчанию: не более 10 запросов в минуту.
    Предотвращает блокировку IP поисковиками.
    """

    def __init__(self, max_per_minute=10, min_delay=1.0):
        self.max_per_minute = max_per_minute
        self.min_delay = min_delay
        self._timestamps = []
        self._last_request = 0.0

    def wait(self):
        now = time.time()
        self._timestamps = [t for t in self._timestamps if now - t < 60]

        if len(self._timestamps) >= self.max_per_minute:
            wait_time = 60 - (now - self._timestamps[0]) + 0.5
            if wait_time > 0:
                time.sleep(wait_time)

        elapsed = time.time() - self._last_request
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)

        self._timestamps.append(time.time())
        self._last_request = time.time()

    def reset(self):
        self._timestamps = []
        self._last_request = 0.0


_RATE_LIMITER = RateLimiter(max_per_minute=10, min_delay=0.5)


# =================================================================================
# БЛОК 33: АНАЛИЗАТОР ТОНАЛЬНОСТИ ТЕКСТА (Sentiment Analysis)
# =================================================================================

POSITIVE_WORDS_RU = {
    "хороший", "отличный", "прекрасный", "замечательный", "великолепный",
    "превосходный", "блестящий", "успешный", "позитивный", "лучший",
    "выдающийся", "знаменитый", "известный", "популярный", "любимый",
    "полезный", "важный", "значимый", "ценный", "нужный", "необходимый",
    "эффективный", "мощный", "сильный", "быстрый", "умный", "талантливый",
    "красивый", "удобный", "надёжный", "качественный", "профессиональный",
    "инновационный", "революционный", "передовой", "современный", "новый",
}

NEGATIVE_WORDS_RU = {
    "плохой", "ужасный", "отвратительный", "страшный", "негативный",
    "вредный", "опасный", "слабый", "медленный", "устаревший", "ненужный",
    "бесполезный", "провальный", "неудачный", "проблемный", "критический",
    "спорный", "сомнительный", "непроверенный", "ненадёжный", "дорогой",
    "дефектный", "сломанный", "повреждённый", "уязвимый", "нестабильный",
}

POSITIVE_WORDS_EN = {
    "good", "great", "excellent", "wonderful", "amazing", "fantastic",
    "outstanding", "brilliant", "successful", "positive", "best", "perfect",
    "beautiful", "useful", "important", "valuable", "powerful", "strong",
    "fast", "smart", "talented", "innovative", "revolutionary", "modern",
    "popular", "famous", "renowned", "acclaimed", "celebrated", "beloved",
}

NEGATIVE_WORDS_EN = {
    "bad", "terrible", "awful", "horrible", "negative", "harmful",
    "dangerous", "weak", "slow", "outdated", "useless", "failed",
    "problematic", "critical", "controversial", "unreliable", "expensive",
    "broken", "defective", "vulnerable", "unstable", "poor", "worst",
}


def analyze_sentiment(text):
    """
    Простой анализ тональности текста.
    Возвращает: 'positive', 'negative', 'neutral'
    """
    words = set(get_word_tokens(text, remove_stops=False))
    pos_count = len(words & POSITIVE_WORDS_RU) + len(words & POSITIVE_WORDS_EN)
    neg_count = len(words & NEGATIVE_WORDS_RU) + len(words & NEGATIVE_WORDS_EN)

    if pos_count > neg_count + 1:
        return "positive"
    if neg_count > pos_count + 1:
        return "negative"
    return "neutral"


def filter_sentences_by_sentiment(sentences, target="neutral"):
    """Фильтрует предложения по тональности"""
    return [s for s in sentences if analyze_sentiment(s) == target]


def get_most_neutral_sentences(sentences, n=5):
    """Возвращает наиболее нейтральные (информативные) предложения"""
    scored = []
    for sent in sentences:
        words = set(get_word_tokens(sent, remove_stops=False))
        pos = len(words & POSITIVE_WORDS_RU) + len(words & POSITIVE_WORDS_EN)
        neg = len(words & NEGATIVE_WORDS_RU) + len(words & NEGATIVE_WORDS_EN)
        neutrality = 1.0 / (1 + pos + neg)
        scored.append((neutrality, sent))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:n]]


# =================================================================================
# БЛОК 34: ИЗВЛЕЧЕНИЕ ИМЕНОВАННЫХ СУЩНОСТЕЙ (Named Entity Recognition — NER)
# =================================================================================

NER_PATTERNS = {
    "date": [
        re.compile(r'\b\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|'
                   r'августа|сентября|октября|ноября|декабря)\s+\d{4}\b', re.I),
        re.compile(r'\b\d{4}[-–]\d{4}\b'),
        re.compile(r'\b(?:January|February|March|April|May|June|July|August|'
                   r'September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', re.I),
        re.compile(r'\b\d{1,2}\.\d{1,2}\.\d{4}\b'),
        re.compile(r'\b\d{4}\s*(?:год|г\.?|year|yr)\b', re.I),
    ],
    "number": [
        re.compile(r'\b\d+(?:[,\.]\d+)?\s*(?:млн|млрд|тысяч|миллион|миллиард|'
                   r'billion|million|thousand|trillion)\b', re.I),
        re.compile(r'\b\d+(?:[,\.]\d+)?%\b'),
        re.compile(r'\b\d+(?:\s\d+)+\b'),
    ],
    "person": [
        re.compile(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?\b'),
        re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'),
    ],
    "organization": [
        re.compile(r'\b(?:ООО|ОАО|ЗАО|АО|ПАО|ГУП|МУП|ФГУП|НКО)\s+[«"]?[А-ЯЁ]', re.I),
        re.compile(r'\b(?:Inc\.|Corp\.|Ltd\.|LLC|GmbH|AG|SA|PLC)\b'),
        re.compile(r'\b(?:Министерство|Ведомство|Федеральная|Национальная|'
                   r'Ministry|Department|Agency|Bureau|Institute)\b', re.I),
    ],
    "location": [
        re.compile(r'\b(?:город|г\.|село|деревня|посёлок|область|край|республика|'
                   r'район|province|city|town|village|county|state|region)\b\s+'
                   r'[А-ЯA-Z][а-яёa-z]+', re.I),
    ],
    "url": [
        re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
        re.compile(r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    ],
    "email": [
        re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'),
    ],
    "phone": [
        re.compile(r'(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'),
    ],
}


def extract_entities(text, entity_type=None):
    """
    Извлекает именованные сущности из текста.
    entity_type: 'date', 'number', 'person', 'organization', 'location',
                 'url', 'email', 'phone', или None (все типы).
    """
    if entity_type and entity_type not in NER_PATTERNS:
        return []

    types = [entity_type] if entity_type else list(NER_PATTERNS.keys())
    result = {}

    for etype in types:
        found = []
        for pat in NER_PATTERNS[etype]:
            for m in pat.finditer(text):
                val = m.group().strip()
                if val not in found:
                    found.append(val)
        result[etype] = found[:10]

    if entity_type:
        return result.get(entity_type, [])
    return result


def extract_all_entities(text):
    """Полное извлечение всех сущностей из текста"""
    return extract_entities(text, entity_type=None)


def find_entity_in_context(text, entity_type, context_size=50):
    """
    Возвращает фрагменты текста вокруг найденных сущностей.
    context_size — количество символов вокруг сущности.
    """
    results = []
    for pat in NER_PATTERNS.get(entity_type, []):
        for m in pat.finditer(text):
            start = max(0, m.start() - context_size)
            end = min(len(text), m.end() + context_size)
            snippet = text[start:end].strip()
            if snippet not in results:
                results.append(snippet)
    return results[:5]


# =================================================================================
# БЛОК 35: ГЕНЕРАТОР ПОИСКОВЫХ ЗАПРОСОВ
# =================================================================================

def generate_search_queries(question):
    """
    Генерирует несколько вариантов поискового запроса из одного вопроса.
    Увеличивает вероятность найти правильный ответ.
    """
    queries = [question]
    q_lower = question.lower().strip()

    question_markers = {
        "кто такой ": "",
        "кто такая ": "",
        "что такое ": "",
        "что значит ": "значение ",
        "когда был основан ": "год основания ",
        "когда родился ": "дата рождения ",
        "когда умер ": "дата смерти ",
        "где находится ": "расположение ",
        "сколько человек ": "население ",
        "почему ": "причина почему ",
        "как работает ": "принцип работы ",
        "who is ": "",
        "what is ": "definition of ",
        "when was ": "year ",
        "where is ": "location of ",
        "how many ": "number of ",
        "why does ": "reason why ",
        "how does ": "how works ",
    }

    for marker, replacement in question_markers.items():
        if q_lower.startswith(marker):
            subject = question[len(marker):]
            queries.append(replacement + subject)
            queries.append(subject)
            break

    queries.append(expand_query(question))

    seen = set()
    unique = []
    for q in queries:
        q = q.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            unique.append(q)

    return unique[:4]


def multi_search(question, verbose=False):
    """
    Поиск по нескольким вариантам запроса.
    Объединяет результаты для более полного охвата.
    """
    queries = generate_search_queries(question)
    all_results = []
    seen_urls = set()

    for q in queries[:2]:
        if verbose:
            print(f"[MultiSearch] Запрос: {q}")
        web_data = collect_web_texts(q, verbose=verbose)
        for src in web_data.get("results", []):
            if src["url"] not in seen_urls:
                seen_urls.add(src["url"])
                all_results.append(src)

    combined_text = " ".join(s["text"] for s in all_results)

    return {
        "query": question,
        "links": list(seen_urls),
        "results": all_results,
        "combined_text": combined_text,
        "sources_count": len(all_results),
    }


# =================================================================================
# БЛОК 36: ФОРМАТТЕР ОТВЕТОВ (разные форматы вывода)
# =================================================================================

def format_as_markdown(query, answer, sources):
    """Форматирует ответ в Markdown"""
    lines = [
        f"## {query}",
        "",
        answer,
        "",
        "### Источники",
    ]
    for i, src in enumerate(sources, 1):
        domain = urlparse(src).netloc.replace("www.", "")
        lines.append(f"{i}. [{domain}]({src})")
    return "\n".join(lines)


def format_as_json(query, answer, sources, q_type):
    """Форматирует ответ в JSON"""
    return _json.dumps({
        "query": query,
        "answer": answer,
        "question_type": q_type,
        "sources": sources,
        "timestamp": _dt.datetime.now().isoformat(),
    }, ensure_ascii=False, indent=2)


def format_as_csv_row(query, answer, sources):
    """Форматирует ответ как строку CSV"""
    src_str = "|".join(sources[:3])
    q_esc = query.replace('"', '""')
    a_esc = answer.replace('"', '""')
    return f'"{q_esc}","{a_esc}","{src_str}"'


def save_as_markdown(query, answer, sources, filepath="answers.md"):
    """Сохраняет ответ в Markdown-файл"""
    content = format_as_markdown(query, answer, sources) + "\n\n---\n\n"
    mode = "a" if os.path.exists(filepath) else "w"
    with open(filepath, mode, encoding="utf-8") as f:
        f.write(content)


def save_as_json(query, answer, sources, q_type, filepath="answers.json"):
    """Сохраняет/добавляет ответ в JSON-файл"""
    entry = {
        "query": query,
        "answer": answer,
        "question_type": q_type,
        "sources": sources,
        "timestamp": _dt.datetime.now().isoformat(),
    }
    data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = _json.load(f)
        except Exception:
            data = []
    data.append(entry)
    with open(filepath, "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)


# =================================================================================
# БЛОК 37: СТАТИСТИКА СЕССИИ
# =================================================================================

class SessionStats:
    """Собирает статистику работы AI за сессию"""

    def __init__(self):
        self.started_at = _dt.datetime.now()
        self.questions_asked = 0
        self.successful_answers = 0
        self.failed_answers = 0
        self.total_sites_fetched = 0
        self.total_chars_processed = 0
        self.question_types = Counter()
        self.response_times = []

    def record(self, q_type, sites, chars, success, elapsed):
        self.questions_asked += 1
        if success:
            self.successful_answers += 1
        else:
            self.failed_answers += 1
        self.total_sites_fetched += sites
        self.total_chars_processed += chars
        self.question_types[q_type] += 1
        self.response_times.append(elapsed)

    def report(self):
        duration = _dt.datetime.now() - self.started_at
        avg_time = (sum(self.response_times) / len(self.response_times)
                    if self.response_times else 0)
        lines = [
            "\n=== Статистика сессии ===",
            f"Время работы:         {duration}",
            f"Вопросов задано:      {self.questions_asked}",
            f"Успешных ответов:     {self.successful_answers}",
            f"Неудачных ответов:    {self.failed_answers}",
            f"Сайтов загружено:     {self.total_sites_fetched}",
            f"Символов обработано:  {self.total_chars_processed:,}",
            f"Среднее время ответа: {avg_time:.1f} с",
            f"Типы вопросов:        {dict(self.question_types)}",
        ]
        return "\n".join(lines)


_SESSION = SessionStats()


# =================================================================================
# БЛОК 38: РЕТРАЙ-ЛОГИКА (повторные попытки при ошибках сети)
# =================================================================================

def fetch_with_retry(url, max_retries=2, backoff=1.5):
    """
    Загружает страницу с повторными попытками при ошибке.
    Для Wikipedia использует API напрямую.
    """
    if "wikipedia.org/wiki/" in url:
        wiki_text = fetch_wikipedia_text(url)
        if wiki_text:
            return wiki_text

    for attempt in range(max_retries):
        try:
            session = requests.Session()
            session.headers.update(get_random_headers())
            resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if resp.status_code >= 400:
                return ""
            resp.encoding = resp.apparent_encoding or "utf-8"
            text = clean_html(resp.text)
            if len(text) >= MIN_TEXT_LEN:
                return text
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            return ""
        except requests.exceptions.TooManyRedirects:
            return ""
        except Exception:
            pass

        if attempt < max_retries - 1:
            time.sleep(backoff)

    return ""


def collect_web_texts_robust(query, verbose=True):
    """
    Надёжная версия collect_web_texts с retry-логикой.
    """
    if verbose:
        print(f"\n[AI] Ищу в интернете: «{query}»")

    links = search_links(query, total=MAX_SITES)

    if verbose:
        print(f"[AI] Найдено {len(links)} ссылок, загружаю...")

    results = []
    all_texts = []

    for i, url in enumerate(links):
        domain = urlparse(url).netloc.replace("www.", "")
        quality = get_domain_quality(url)
        premium = is_premium_domain(url)
        if premium:
            quality = max(quality, 0.9)

        text = fetch_with_retry(url, max_retries=2)

        if text:
            results.append({
                "url": url,
                "domain": domain,
                "quality": quality,
                "text": text,
                "length": len(text),
                "is_premium": premium,
            })
            all_texts.append(text)
            if verbose:
                tag = "[★]" if premium else "[OK]"
                print(f"  {tag} [{i+1}] {domain} ({len(text)} симв.)")
        else:
            if verbose:
                print(f"  [--] [{i+1}] {domain}")

        time.sleep(SLEEP_BETWEEN)

    combined = " ".join(all_texts)
    if verbose:
        print(f"[AI] Готово: {len(results)} сайтов, "
              f"{len(combined)} символов\n")

    return {
        "query": query,
        "links": links,
        "results": results,
        "combined_text": combined,
        "sources_count": len(results),
    }


# =================================================================================
# БЛОК 39: ПОСТ-ОБРАБОТКА ОТВЕТА
# =================================================================================

def postprocess_answer(answer, query):
    """
    Финальная обработка ответа:
    1. Убирает лишние пробелы и знаки
    2. Исправляет пунктуацию
    3. Убирает дублирующиеся слова
    4. Проверяет минимальную длину
    """
    if not answer:
        return ""

    answer = clean_answer_text(answer)
    answer = _remove_duplicate_clauses(answer)
    answer = _fix_punctuation(answer)

    if len(answer) < 15:
        return ""

    return answer


def _remove_duplicate_clauses(text):
    """Удаляет дублирующиеся части предложения"""
    parts = re.split(r'(?<=[.!?])\s+', text)
    seen = set()
    unique = []
    for part in parts:
        key = frozenset(get_word_tokens(part)[:6])
        if key not in seen:
            seen.add(key)
            unique.append(part)
    return " ".join(unique)


def _fix_punctuation(text):
    """Исправляет распространённые ошибки пунктуации"""
    text = re.sub(r'\s+([.,!?:;])', r'\1', text)
    text = re.sub(r'([.,!?:;])\s*([.,!?:;])', r'\1', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    return text.strip()


def validate_answer(answer, query, min_length=20, max_length=800):
    """
    Проверяет ответ на корректность.
    Возвращает (is_valid, reason).
    """
    if not answer:
        return False, "Пустой ответ"
    if len(answer) < min_length:
        return False, f"Ответ слишком короткий ({len(answer)} симв.)"
    if len(answer) > max_length:
        return False, f"Ответ слишком длинный ({len(answer)} симв.)"

    query_words = build_query_words(query)
    answer_words = set(get_word_tokens(answer))
    overlap = len(query_words & answer_words)

    if overlap == 0 and len(query_words) > 2:
        return False, "Ответ не содержит слов из запроса"

    for pw in QUALITY_PENALTY_WORDS:
        if pw in answer.lower():
            return False, f"Ответ содержит спам: {pw}"

    return True, "OK"


# =================================================================================
# БЛОК 40: ГЛАВНАЯ УЛУЧШЕННАЯ ФУНКЦИЯ ask_v2
# =================================================================================

def ask_v2(query, verbose=True, use_cache=True, multi_search_mode=False):
    """
    Улучшенная версия ask() со всеми возможностями:
    - Кэширование
    - Расширение запроса
    - Multi-search
    - Retry-логика
    - NER (именованные сущности)
    - Полная гибридная экстракция
    - Постобработка
    - Валидация ответа
    - Статистика сессии
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    init_output_file()
    t_start = time.time()

    if use_cache:
        cached = _GLOBAL_CACHE.get(query)
        if cached:
            if verbose:
                print(f"[AI] Ответ из кэша: {cached}")
            return cached

    expanded = expand_query(query)
    if verbose and expanded != query:
        print(f"[AI] Расширен запрос: {expanded}")

    if multi_search_mode:
        web_data = multi_search(expanded, verbose=verbose)
    else:
        web_data = collect_web_texts_robust(expanded, verbose=verbose)

    if not web_data["results"]:
        answer = "Нет подключения к интернету или сайты недоступны."
        _SESSION.record("none", 0, 0, False, time.time() - t_start)
        report = format_report(query, answer, [], "none", 0)
        save_to_file(report)
        return answer

    q_type = determine_question_type_v2(query)

    if verbose:
        print(f"[AI] Тип вопроса: {q_type}")

    answer = extract_answer_full(web_data, query, q_type)
    answer = postprocess_answer(answer, query)

    is_valid, reason = validate_answer(answer, query)
    if not is_valid:
        if verbose:
            print(f"[AI] Ответ не прошёл валидацию: {reason}")
        fallback = build_summary_from_multiple_sources(web_data, query)
        if fallback:
            answer = truncate_to_sentence(fallback, MAX_ANSWER_LEN)
            answer = postprocess_answer(answer, query)

    if not answer or len(answer) < 15:
        answer = "Не удалось найти точный ответ в интернете."

    sources = get_source_links(web_data, max_links=3)
    report = format_report(query, answer, sources, q_type, web_data["sources_count"])
    save_to_file(report)

    if use_cache:
        _GLOBAL_CACHE.set(query, answer)

    elapsed = time.time() - t_start
    _SESSION.record(
        q_type,
        web_data["sources_count"],
        len(web_data["combined_text"]),
        len(answer) >= 15,
        elapsed,
    )

    if verbose:
        print(f"\n{'='*60}")
        print(f"ОТВЕТ:\n{answer}")
        print(f"{'='*60}")
        print(f"Время: {elapsed:.1f} с | Источников: {web_data['sources_count']}")
        print(f"Сохранено в: {OUTPUT_FILE}")

    return answer


# =================================================================================
# БЛОК 41: БОЛЬШИЕ ПАТТЕРНЫ ДЛЯ 200+ ТИПОВ ФАКТОВ
# =================================================================================

FACT_EXTRACTION_PATTERNS = {}

_FACT_TEMPLATES = [
    ("founder",     ["основал", "основала", "основали", "founded by", "established by", "created by"]),
    ("inventor",    ["изобрёл", "изобрела", "изобретатель", "invented by", "inventor"]),
    ("author",      ["написал", "написала", "автор", "written by", "authored by"]),
    ("director",    ["снял", "режиссёр", "directed by", "director"]),
    ("capital",     ["столица", "capital city", "capital of", "является столицей"]),
    ("population",  ["население", "population", "жителей", "человек проживает"]),
    ("area",        ["площадь", "territory", "area", "кв.км", "sq km"]),
    ("height",      ["высота", "высотой", "height of", "tall", "altitude"]),
    ("length",      ["длина", "длиной", "length of", "протяжённость"]),
    ("depth",       ["глубина", "глубиной", "depth of"]),
    ("speed",       ["скорость", "speed of", "velocity", "км/ч", "mph"]),
    ("weight",      ["вес", "масса", "weighs", "weight of", "weighing"]),
    ("age",         ["возраст", "лет", "years old", "age of"]),
    ("born",        ["родился", "родилась", "born in", "born on", "дата рождения"]),
    ("died",        ["умер", "умерла", "died in", "died on", "death"]),
    ("nationality", ["гражданство", "национальность", "nationality", "citizen of"]),
    ("profession",  ["профессия", "occupation", "работает", "работал как"]),
    ("location",    ["находится", "расположен", "located in", "situated in"]),
    ("member",      ["входит в состав", "является членом", "member of", "part of"]),
    ("language",    ["язык", "говорят на", "language", "spoken in"]),
    ("currency",    ["валюта", "currency", "денежная единица"]),
    ("religion",    ["религия", "вера", "religion", "faith"]),
    ("government",  ["правительство", "форма правления", "government", "ruled by"]),
    ("president",   ["президент", "president of", "head of state"]),
    ("prime_min",   ["премьер-министр", "prime minister of"]),
    ("king",        ["король", "царь", "emperor", "king of", "queen of"]),
    ("ceo",         ["генеральный директор", "CEO", "chief executive"]),
    ("color",       ["цвет", "окраска", "color", "colour"]),
    ("chemical",    ["химическая формула", "chemical formula", "состав", "молекула"]),
    ("price",       ["цена", "стоимость", "price", "cost", "рублей", "долларов"]),
    ("revenue",     ["выручка", "доход", "revenue", "income", "profit"]),
    ("founded_yr",  ["основан в", "founded in", "established in", "создан в"]),
    ("headquarter", ["штаб-квартира", "headquarters", "head office", "офис"]),
    ("website",     ["сайт", "website", "веб-сайт", "официальный сайт"]),
    ("phone",       ["телефон", "phone", "contact number", "helpline"]),
    ("email_info",  ["электронная почта", "email address", "почта"]),
    ("hours",       ["часы работы", "working hours", "opening hours"]),
    ("genre",       ["жанр", "genre", "style", "музыкальный стиль"]),
    ("album",       ["альбом", "album", "дискография"]),
    ("award",       ["награда", "премия", "award", "prize", "oscar", "нобелевская"]),
    ("record",      ["рекорд", "record holder", "мировой рекорд"]),
    ("discovery",   ["открытие", "discovery", "discovered", "открыт"]),
    ("element",     ["химический элемент", "element", "атомный номер"]),
    ("atomic_num",  ["атомный номер", "atomic number", "Z ="]),
    ("atomic_mass", ["атомная масса", "atomic mass", "молярная масса"]),
    ("planet",      ["планета", "planet", "орбита", "orbit"]),
    ("distance",    ["расстояние до", "distance from", "от земли", "from earth"]),
    ("diameter",    ["диаметр", "diameter", "радиус", "radius"]),
    ("temperature", ["температура", "temperature", "°C", "°F", "кельвин"]),
    ("boiling",     ["температура кипения", "boiling point"]),
    ("melting",     ["температура плавления", "melting point"]),
    ("speed_light", ["скорость света", "speed of light"]),
    ("gravity",     ["ускорение свободного падения", "gravity", "гравитация"]),
    ("continent",   ["континент", "материк", "continent"]),
    ("ocean",       ["океан", "море", "ocean", "sea"]),
    ("mountain",    ["гора", "горная система", "mountain", "peak"]),
    ("river",       ["река", "приток", "river", "tributary"]),
    ("lake",        ["озеро", "lake", "водохранилище"]),
    ("species",     ["вид", "species", "род", "семейство", "отряд", "класс"]),
    ("lifespan",    ["продолжительность жизни", "lifespan", "живёт до"]),
    ("diet",        ["питание", "рацион", "diet", "питается"]),
    ("habitat",     ["ареал", "обитает", "habitat", "lives in"]),
    ("size_animal", ["размер", "длина тела", "body length", "wingspan"]),
    ("os",          ["операционная система", "OS", "operating system"]),
    ("language_pl", ["язык программирования", "programming language"]),
    ("framework",   ["фреймворк", "framework", "библиотека", "library"]),
    ("version",     ["версия", "version", "release", "релиз"]),
    ("license",     ["лицензия", "license", "open source", "MIT", "GPL"]),
    ("developer",   ["разработан", "разработчик", "developed by", "developer"]),
    ("released",    ["выпущен", "released", "вышел", "launch date"]),
    ("platform",    ["платформа", "platform", "works on", "поддерживает"]),
    ("format",      ["формат", "format", "расширение файла", "file extension"]),
    ("protocol",    ["протокол", "protocol", "стандарт", "standard"]),
    ("port",        ["порт", "port", "сетевой порт", "default port"]),
    ("algorithm",   ["алгоритм", "algorithm", "метод", "method"]),
    ("complexity",  ["сложность", "complexity", "Big O", "O(n)"]),
    ("theorem",     ["теорема", "theorem", "лемма", "lemma"]),
    ("law",         ["закон", "law", "правило", "rule"]),
    ("formula",     ["формула", "formula", "уравнение", "equation"]),
    ("constant",    ["постоянная", "constant", "коэффициент"]),
    ("unit",        ["единица", "unit", "СИ", "SI"]),
    ("dose",        ["доза", "dose", "дозировка"]),
    ("side_effect", ["побочный эффект", "side effect", "противопоказание"]),
    ("ingredient",  ["ингредиент", "ingredient", "состав блюда"]),
    ("calorie",     ["калорийность", "calories", "ккал"]),
    ("protein",     ["белок", "protein", "г белка"]),
    ("fat",         ["жир", "fat", "г жиров"]),
    ("carbs",       ["углеводы", "carbohydrates", "г углеводов"]),
    ("vitamin",     ["витамин", "vitamin", "минерал", "mineral"]),
    ("origin",      ["происхождение", "origin", "etymology", "этимология"]),
    ("synonym",     ["синоним", "synonym", "другое название"]),
    ("antonym",     ["антоним", "antonym", "противоположность"]),
    ("abbreviation",["аббревиатура", "abbreviation", "расшифровка"]),
    ("translation", ["перевод", "translation", "переводится как"]),
    ("pronunciation",["произношение", "pronunciation", "транскрипция"]),
]

for _name, _words in _FACT_TEMPLATES:
    FACT_EXTRACTION_PATTERNS[_name] = [
        re.compile(
            r'(?:' + '|'.join(re.escape(w) for w in _words) + r')'
            r'[^.]{0,80}?(\d[\d\s,.]*|[А-ЯЁA-Z][а-яёa-zA-Z\s]{3,40})',
            re.I
        )
        for _ in [1]
    ]


def extract_fact(text, fact_type):
    """
    Извлекает конкретный тип факта из текста.
    fact_type: одно из FACT_EXTRACTION_PATTERNS.keys()
    """
    for pat in FACT_EXTRACTION_PATTERNS.get(fact_type, []):
        m = pat.search(text)
        if m:
            try:
                return m.group(1).strip()
            except IndexError:
                return m.group().strip()
    return ""


def extract_all_facts(text):
    """Извлекает все возможные факты из текста"""
    facts = {}
    for fact_type in FACT_EXTRACTION_PATTERNS:
        val = extract_fact(text, fact_type)
        if val:
            facts[fact_type] = val
    return facts


# =================================================================================
# БЛОК 42: КОНФИГУРАЦИЯ AI
# =================================================================================

class AIConfig:
    """
    Централизованная конфигурация AI.
    Можно изменять параметры без правки кода.
    """

    def __init__(self):
        self.max_sites = MAX_SITES
        self.request_timeout = REQUEST_TIMEOUT
        self.sleep_between = SLEEP_BETWEEN
        self.max_text_len = MAX_TEXT_LEN
        self.min_text_len = MIN_TEXT_LEN
        self.max_answer_len = MAX_ANSWER_LEN
        self.min_sentence_len = MIN_SENTENCE_LEN
        self.max_sentence_len = MAX_SENTENCE_LEN
        self.top_sentences = TOP_SENTENCES
        self.output_file = OUTPUT_FILE
        self.use_cache = True
        self.use_rate_limit = True
        self.verbose = True
        self.retry_count = 2
        self.multi_search = False
        self.save_json = False
        self.save_markdown = False

    def from_dict(self, d):
        for k, v in d.items():
            if hasattr(self, k):
                setattr(self, k, v)
        return self

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    def __repr__(self):
        return f"AIConfig({self.to_dict()})"


_CONFIG = AIConfig()




# =================================================================================
# БЛОК 43: 300 ПАТТЕРНОВ РЕГУЛЯРНЫХ ВЫРАЖЕНИЙ ДЛЯ ТЕКСТОВОГО АНАЛИЗА
# =================================================================================

# --- Числа и математика ---
RE_INTEGER = re.compile(r'\b(\d{1,15})\b')
RE_FLOAT = re.compile(r'\b(\d+[.,]\d+)\b')
RE_PERCENT = re.compile(r'\b(\d+(?:[.,]\d+)?)\s*%')
RE_FRACTION = re.compile(r'\b(\d+)\s*/\s*(\d+)\b')
RE_ORDINAL_RU = re.compile(r'\b(\d+)(?:-й|-я|-е|-ой|-ей|-ым|-им|-ом|-ем)\b', re.I)
RE_ORDINAL_EN = re.compile(r'\b(\d+)(?:st|nd|rd|th)\b', re.I)
RE_RANGE_NUM = re.compile(r'\b(\d+(?:[.,]\d+)?)\s*[-–—]\s*(\d+(?:[.,]\d+)?)\b')
RE_APPROX = re.compile(r'(?:около|примерно|приблизительно|порядка|~|≈)\s*(\d+)', re.I)
RE_POWER = re.compile(r'(\d+)\s*(?:\^|\*\*)\s*(\d+)')
RE_SCIENTIFIC = re.compile(r'(\d+(?:[.,]\d+)?)\s*[×x]\s*10\s*(?:\^|(?=\d))(-?\d+)')

# --- Даты и время ---
RE_DATE_RU = re.compile(
    r'\b(\d{1,2})\s+'
    r'(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)'
    r'\s+(\d{4})\b', re.I)
RE_DATE_EN = re.compile(
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+(\d{1,2}),?\s+(\d{4})\b', re.I)
RE_DATE_ISO = re.compile(r'\b(\d{4})-(\d{2})-(\d{2})\b')
RE_DATE_DOT = re.compile(r'\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b')
RE_DATE_SLASH = re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b')
RE_YEAR_ONLY = re.compile(r'\b((?:1[0-9]|20)[0-9]{2})\b')
RE_DECADE = re.compile(r'\b(\d{4})[-е]?(?:е\s+годы|s)\b', re.I)
RE_CENTURY_RU = re.compile(r'\b([IVXLCDM]+)\s+век[еа]?\b', re.I)
RE_CENTURY_EN = re.compile(r'\b(\d+)(?:st|nd|rd|th)\s+century\b', re.I)
RE_ERA = re.compile(r'\b(\d+)\s*(?:до н\.э\.|до н\. э\.|BCE|BC|н\.э\.|н\. э\.|CE|AD)\b', re.I)
RE_TIME = re.compile(r'\b(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(?:AM|PM|ч|час)?\b', re.I)
RE_DURATION = re.compile(r'\b(\d+)\s*(?:лет|год|месяц|день|час|минут|секунд|years?|months?|days?|hours?|minutes?|seconds?)\b', re.I)

# --- Деньги и экономика ---
RE_USD = re.compile(r'\$\s*(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тыс|million|billion|thousand))?)', re.I)
RE_EUR = re.compile(r'€\s*(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тыс|million|billion|thousand))?)', re.I)
RE_RUB = re.compile(r'(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тыс))?)\s*(?:рублей|руб\.|₽)', re.I)
RE_CURRENCY_AMOUNT = re.compile(
    r'(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тыс|million|billion|trillion|thousand))?)\s*'
    r'(?:\$|€|£|¥|₽|руб\.|рублей|долларов|евро|фунтов|юаней)', re.I)

# --- Измерения ---
RE_KM = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:км|километров|kilometers?|km)\b', re.I)
RE_METER = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:метров|метра|м\b|meters?|m\b)(?!\w)', re.I)
RE_KG = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:кг|килограммов|kilograms?|kg)\b', re.I)
RE_GRAM = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:граммов|грамм|гр\b|g\b)(?!\w)', re.I)
RE_TONNE = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:тонн|тонны|tons?|tonnes?|t\b)(?!\w)', re.I)
RE_SQ_KM = re.compile(r'(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:кв\.?\s*км|км²|km²|sq\.?\s*km)', re.I)
RE_LITRE = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:литров|литра|liters?|litres?|л\b)(?!\w)', re.I)
RE_TEMP_C = re.compile(r'([+-]?\d+(?:[,\.]\d+)?)\s*(?:°C|°С|градус[аов]?\s*Цельс)', re.I)
RE_TEMP_F = re.compile(r'([+-]?\d+(?:[,\.]\d+)?)\s*(?:°F|градус[аов]?\s*Фарен)', re.I)
RE_KELVIN = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:К\b|K\b|кельвин)', re.I)
RE_SPEED_KMH = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:км/ч|кмч|km/h|kph)\b', re.I)
RE_SPEED_MS = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:м/с|m/s)\b', re.I)
RE_HERTZ = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:ГГц|МГц|кГц|Гц|GHz|MHz|kHz|Hz)\b', re.I)
RE_WATT = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:ГВт|МВт|кВт|Вт|GW|MW|kW|W)\b', re.I)
RE_VOLT = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:кВ|В\b|kV|V\b)(?!\w)', re.I)
RE_BYTE = re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:ПБ|ТБ|ГБ|МБ|КБ|Б\b|PB|TB|GB|MB|KB|B\b)(?!\w)', re.I)

# --- Координаты ---
RE_LATITUDE = re.compile(r'(\d+(?:[,\.]\d+)?)\s*°\s*([NS]|с\.?\s*ш\.|ю\.?\s*ш\.)', re.I)
RE_LONGITUDE = re.compile(r'(\d+(?:[,\.]\d+)?)\s*°\s*([EW]|в\.?\s*д\.|з\.?\s*д\.)', re.I)
RE_COORDS = re.compile(r'(\d+(?:[.,]\d+)?)\s*°?\s*([NS]|с\.ш\.|ю\.ш\.),?\s*(\d+(?:[.,]\d+)?)\s*°?\s*([EW]|в\.д\.|з\.д\.)', re.I)

# --- Имена и организации ---
RE_NAME_RU = re.compile(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?\b')
RE_NAME_EN = re.compile(r'\b[A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20}(?:\s+[A-Z][a-z]{1,20})?\b')
RE_INITIALS = re.compile(r'\b[А-ЯЁA-Z]\.\s*[А-ЯЁA-Z]?\.\s*[А-ЯЁ][а-яёa-z]+\b')
RE_ORG_RU = re.compile(r'\b(?:ООО|ОАО|ЗАО|АО|ПАО|ГУП|ФГУП|МУП|НКО|ИП)\s+[«"]?[А-ЯЁ]', re.I)
RE_ORG_EN = re.compile(r'\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:Inc\.|Corp\.|Ltd\.|LLC|GmbH|AG|SA|PLC)\b')

# --- Интернет и технологии ---
RE_URL_FULL = re.compile(r'https?://(?:[a-zA-Z0-9.-]+)(?:/[^\s<>"]*)?')
RE_DOMAIN = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|edu|gov|io|ru|co\.uk|de|fr|jp|cn|uk|au|ca|it|es|br|in|nl)\b', re.I)
RE_IP_V4 = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
RE_IP_V6 = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')
RE_EMAIL_ADDR = re.compile(r'\b[\w.+-]+@[\w-]+\.[\w.]+\b')
RE_PHONE_RU = re.compile(r'(?:\+7|8)\s*[\(]?\d{3}[\)]?\s*\d{3}[-\s]?\d{2}[-\s]?\d{2}\b')
RE_PHONE_INT = re.compile(r'\+\d{1,3}\s*\(?\d{1,4}\)?\s*\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,9}')
RE_VERSION = re.compile(r'\bv?(\d+)\.(\d+)(?:\.(\d+))?(?:[-.]([a-zA-Z0-9]+))?\b')
RE_PORT = re.compile(r'\bport\s+(\d{1,5})\b|\bпорт\s+(\d{1,5})\b', re.I)
RE_HASH_MD5 = re.compile(r'\b[0-9a-fA-F]{32}\b')
RE_HASH_SHA1 = re.compile(r'\b[0-9a-fA-F]{40}\b')
RE_HASH_SHA256 = re.compile(r'\b[0-9a-fA-F]{64}\b')
RE_BASE64 = re.compile(r'\b(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?\b')

# --- Научные обозначения ---
RE_ATOMIC_NUM = re.compile(r'\bатомный\s+номер\s*(?:=|:)?\s*(\d{1,3})\b', re.I)
RE_ATOMIC_MASS = re.compile(r'\bатомная\s+масса\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)\b', re.I)
RE_CHEM_FORMULA = re.compile(r'\b([A-Z][a-z]?\d*)+\b')
RE_PH = re.compile(r'\bpH\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)\b', re.I)
RE_DENSITY = re.compile(r'\bплотность\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)\s*(?:г/см³|kg/m³|г/мл)\b', re.I)

# --- Биология ---
RE_BINOMIAL = re.compile(r'\b([A-Z][a-z]+)\s+([a-z]+)\b(?=\s*\(|\s*—|\s*is)')
RE_CHROMOSOME = re.compile(r'\b(\d+)\s*(?:пар\s+хромосом|хромосом|chromosomes?)\b', re.I)
RE_DNA_SIMILARITY = re.compile(r'\b(\d+(?:[.,]\d+)?)\s*%\s*(?:совпадает|схожи|identical|similarity)\b', re.I)

# --- География ---
RE_POPULATION_NUM = re.compile(
    r'\b(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тысяч|миллион|миллиард|'
    r'million|billion|thousand))?)\s*(?:человек|жителей|inhabitants?|people|residents?)\b', re.I)
RE_AREA_NUM = re.compile(
    r'\b(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:кв\.?\s*км|км²|km²|sq\.?\s*km|'
    r'square\s+kilometers?)\b', re.I)
RE_ALTITUDE = re.compile(r'\b(\d+(?:[,\.]\d+)?)\s*(?:метров над уровнем моря|m above sea level|маслм)\b', re.I)

# --- Спорт ---
RE_SCORE = re.compile(r'\b(\d+)\s*[:−\-]\s*(\d+)\b')
RE_RECORD_TIME = re.compile(r'\b(\d+):(\d{2})(?:\.(\d+))?\b')
RE_WORLD_RECORD = re.compile(r'(?:мировой рекорд|world record)[^.]{0,60}?(\d[\d\s,.]*(?:м\b|км\b|сек|мин|min|sec|m\b|km\b)?)', re.I)

# --- Медицина ---
RE_DOSAGE = re.compile(r'\b(\d+(?:[,\.]\d+)?)\s*(?:мг|мкг|г\b|mg|mcg|μg|ml|мл)\b', re.I)
RE_BLOOD_PRESSURE = re.compile(r'\b(\d{2,3})\s*/\s*(\d{2,3})\s*(?:мм рт\.? ст\.?|mmHg)\b', re.I)
RE_BMI = re.compile(r'\b(?:ИМТ|BMI)\s*(?:=|:)?\s*(\d+(?:[,\.]\d+)?)\b', re.I)
RE_CALORIES = re.compile(r'\b(\d+(?:[,\.]\d+)?)\s*(?:ккал|кДж|calories?|kcal|kJ)\b', re.I)
RE_PROTEIN_G = re.compile(r'\b(\d+(?:[,\.]\d+)?)\s*г\s*белка\b|(\d+(?:[,\.]\d+)?)\s*g?\s*protein\b', re.I)

# --- Авиация и космос ---
RE_ALTITUDE_FT = re.compile(r'\b(\d+(?:[,\.]\d+)?)\s*(?:фут|ft|feet)\b', re.I)
RE_MACH = re.compile(r'\bMach\s+(\d+(?:[,\.]\d+)?)\b', re.I)
RE_ORBIT = re.compile(r'\b(\d+(?:[,\.]\d+)?)\s*(?:км\b|km\b)\s*(?:орбита|orbit)', re.I)

# --- Квантификаторы и порядки ---
RE_FIRST_IN = re.compile(r'\b(?:первый|первая|первое|первые|впервые|first|for the first time)\b', re.I)
RE_LARGEST = re.compile(r'\b(?:самый крупный|самая крупная|самое крупное|наибольший|'
                        r'largest|biggest|greatest|highest|tallest|longest|deepest)\b', re.I)
RE_SMALLEST = re.compile(r'\b(?:самый маленький|самая маленькая|наименьший|'
                         r'smallest|tiniest|shortest|lightest|least)\b', re.I)
RE_ONLY = re.compile(r'\b(?:единственный|единственная|единственное|только|лишь|'
                     r'only|sole|unique|the only)\b', re.I)
RE_MOST_COMMON = re.compile(r'\b(?:самый распространённый|наиболее часто|наиболее распространён|'
                            r'most common|most frequent|most widely)\b', re.I)

# Функция применения всех паттернов
ALL_TEXT_PATTERNS = {
    "integer": RE_INTEGER, "float": RE_FLOAT, "percent": RE_PERCENT,
    "year": RE_YEAR_ONLY, "date_ru": RE_DATE_RU, "date_en": RE_DATE_EN,
    "date_iso": RE_DATE_ISO, "time": RE_TIME, "duration": RE_DURATION,
    "usd": RE_USD, "eur": RE_EUR, "rub": RE_RUB,
    "km": RE_KM, "meter": RE_METER, "kg": RE_KG,
    "sq_km": RE_SQ_KM, "temp_c": RE_TEMP_C, "speed_kmh": RE_SPEED_KMH,
    "url": RE_URL_FULL, "email": RE_EMAIL_ADDR, "phone_ru": RE_PHONE_RU,
    "version": RE_VERSION, "population": RE_POPULATION_NUM, "area": RE_AREA_NUM,
    "name_ru": RE_NAME_RU, "name_en": RE_NAME_EN, "score": RE_SCORE,
    "calories": RE_CALORIES, "dosage": RE_DOSAGE,
    "first": RE_FIRST_IN, "largest": RE_LARGEST, "smallest": RE_SMALLEST,
}


def extract_all_patterns(text):
    """Применяет все паттерны и возвращает словарь найденных данных"""
    results = {}
    for name, pat in ALL_TEXT_PATTERNS.items():
        found = pat.findall(text)
        if found:
            if isinstance(found[0], tuple):
                results[name] = ["".join(f) for f in found[:5]]
            else:
                results[name] = found[:5]
    return results


def get_numeric_context(text, number_str, window=80):
    """Возвращает контекст вокруг найденного числа"""
    idx = text.find(number_str)
    if idx == -1:
        return ""
    start = max(0, idx - window)
    end = min(len(text), idx + len(number_str) + window)
    return text[start:end].strip()


# =================================================================================
# БЛОК 44: СИГНАТУРЫ ПРЕДЛОЖЕНИЙ ДЛЯ ДЕДУПЛИКАЦИИ
# =================================================================================

def sentence_signature(sentence, n=8):
    """
    Создаёт подпись предложения для дедупликации.
    Использует первые n значимых слов.
    """
    words = get_word_tokens(sentence, remove_stops=True)
    key_words = sorted(words[:n])
    return hashlib.md5(" ".join(key_words).encode("utf-8")).hexdigest()


def advanced_dedup(sentences, similarity_threshold=0.7):
    """
    Продвинутая дедупликация с косинусной схожестью.
    Удаляет предложения с similarity > threshold.
    """
    unique = []
    for sent in sentences:
        is_dup = False
        for existing in unique:
            if cosine_similarity_bow(sent, existing) > similarity_threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(sent)
    return unique


# =================================================================================
# БЛОК 45: ТОП-СЛОВА И КЛЮЧЕВЫЕ ФРАЗЫ
# =================================================================================

def extract_top_words(text, n=20):
    """Возвращает n наиболее частых слов в тексте"""
    words = get_word_tokens(text, remove_stops=True)
    freq = Counter(words)
    return freq.most_common(n)


def extract_bigrams(text, n=10):
    """Извлекает топ n биграмм (пар слов)"""
    words = get_word_tokens(text, remove_stops=True)
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
    freq = Counter(bigrams)
    return freq.most_common(n)


def extract_trigrams(text, n=10):
    """Извлекает топ n триграмм (троек слов)"""
    words = get_word_tokens(text, remove_stops=True)
    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
    freq = Counter(trigrams)
    return freq.most_common(n)


def extract_key_phrases(text, n=10):
    """Извлекает ключевые фразы через биграммы и триграммы"""
    bi = [phrase for phrase, _ in extract_bigrams(text, n=n*2)]
    tri = [phrase for phrase, _ in extract_trigrams(text, n=n)]
    combined = list(dict.fromkeys(tri + bi))
    return combined[:n]


def build_keyword_cloud(web_data, n=30):
    """Строит облако ключевых слов из всех найденных текстов"""
    combined = web_data.get("combined_text", "")
    return extract_top_words(combined, n=n)


# =================================================================================
# БЛОК 46: ПАЙПЛАЙН ПОЛНОГО АНАЛИЗА
# =================================================================================

class FullAnalysisPipeline:
    """
    Полный пайплайн анализа:
    Search → Clean → Tokenize → Score → Extract → Validate → Format → Save
    """

    def __init__(self, config=None):
        self.config = config or _CONFIG

    def run(self, query):
        """Запускает полный пайплайн"""
        t0 = time.time()
        result = {
            "query": query,
            "q_type": None,
            "answer": None,
            "sources": [],
            "entities": {},
            "keywords": [],
            "facts": {},
            "sentiment": None,
            "quality_score": 0.0,
            "elapsed": 0.0,
        }

        expanded = expand_query(query)
        result["q_type"] = determine_question_type_v2(query)

        web_data = collect_web_texts_robust(expanded, verbose=self.config.verbose)

        if not web_data["results"]:
            result["answer"] = "Не удалось найти информацию."
            result["elapsed"] = time.time() - t0
            return result

        answer = extract_answer_full(web_data, query, result["q_type"])
        answer = postprocess_answer(answer, query)

        is_valid, _ = validate_answer(answer, query)
        if not is_valid:
            answer = "Не удалось извлечь точный ответ."

        result["answer"] = answer
        result["sources"] = get_source_links(web_data, max_links=3)
        result["quality_score"] = estimate_answer_quality(answer, query)
        result["sentiment"] = analyze_sentiment(answer)

        combined = web_data.get("combined_text", "")
        result["entities"] = extract_entities(combined)
        result["keywords"] = [w for w, _ in extract_top_words(combined, n=10)]
        result["facts"] = dict(list(extract_all_facts(combined).items())[:10])

        report = format_report(
            query, answer, result["sources"],
            result["q_type"], web_data["sources_count"]
        )
        save_to_file(report)

        if self.config.save_json:
            save_as_json(query, answer, result["sources"], result["q_type"])
        if self.config.save_markdown:
            save_as_markdown(query, answer, result["sources"])

        result["elapsed"] = time.time() - t0
        return result

    def run_batch(self, questions, delay=1.5):
        """Пакетная обработка вопросов"""
        results = []
        for i, q in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] {q}")
            r = self.run(q)
            results.append(r)
            print(f"  → {r['answer'][:100]}...")
            if i < len(questions):
                time.sleep(delay)
        return results


# =================================================================================
# БЛОК 47: ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ РАНЖИРОВАНИЯ
# =================================================================================

def bm25_score(sentence, query_words, avg_dl, k1=1.5, b=0.75):
    """
    BM25 — улучшенный TF-IDF для ранжирования предложений.
    k1 контролирует насыщение TF, b — нормализацию по длине.
    """
    words = get_word_tokens(sentence)
    dl = len(words)
    if not words:
        return 0.0

    freq = Counter(words)
    score = 0.0

    for word in query_words:
        f = freq.get(word, 0)
        if f == 0:
            continue
        tf = (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / max(avg_dl, 1)))
        score += tf

    return score


def rank_sentences_bm25(sentences, query_words):
    """Ранжирует предложения через BM25"""
    avg_dl = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    scored = [(bm25_score(s, query_words, avg_dl), s) for s in sentences]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored]


def extract_with_bm25(web_data, query, top_n=3):
    """Извлечение через BM25"""
    all_sents = []
    for src in web_data.get("results", []):
        sents = remove_noise_sentences(split_into_sentences(src["text"]))
        all_sents.extend(sents)

    if not all_sents:
        return ""

    query_words = list(build_query_words(query))
    ranked = rank_sentences_bm25(all_sents, query_words)
    unique = deduplicate_sentences(ranked[:top_n * 2])[:top_n]

    return truncate_to_sentence(" ".join(unique), MAX_ANSWER_LEN)


def extract_answer_ultra(web_data, query, q_type=None):
    """
    Ультра-гибридный метод: 5 алгоритмов + BM25 + выбор лучшего.
    """
    q_type = determine_question_type_v2(query)

    a1 = AnswerProcessor(web_data, query, q_type).process()
    a2 = extract_with_tfidf(web_data, query, top_n=3)
    a3 = extract_with_context_window(web_data, query, window=3)
    a4 = extract_with_mmr(web_data, query, top_n=3)
    a5 = extract_with_bm25(web_data, query, top_n=3)

    cands = [a for a in [a1, a2, a3, a4, a5] if a and len(a) >= 15]
    if not cands:
        return "Не удалось извлечь ответ."

    best = max(cands, key=lambda a: estimate_answer_quality(a, query))
    return clean_answer_text(best)


# =================================================================================
# БЛОК 48: ОЧИСТКА WIKI-СПЕЦИФИЧЕСКИХ АРТЕФАКТОВ
# =================================================================================

WIKI_ARTIFACTS = [
    re.compile(r'\[\d+\]'),
    re.compile(r'\[править\s*\|?\s*\w+\]', re.I),
    re.compile(r'\[edit\]', re.I),
    re.compile(r'\[нет\s+источника\]', re.I),
    re.compile(r'\[citation\s+needed\]', re.I),
    re.compile(r'\[note\s+\d+\]', re.I),
    re.compile(r'↑\s*\d+[\d.,]*'),
    re.compile(r'см\.\s+(?:также|раздел)\s+\w+', re.I),
    re.compile(r'(?:Main article|See also|Further reading):\s*.+', re.I),
    re.compile(r'Категория:\s*.+', re.I),
    re.compile(r'Category:\s*.+', re.I),
    re.compile(r'\{\{[^}]+\}\}'),
    re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]'),
    re.compile(r'<!--[^>]*-->'),
]


def clean_wiki_artifacts(text):
    """Убирает специфические артефакты Wikipedia"""
    for pat in WIKI_ARTIFACTS:
        text = pat.sub(" ", text)
    return RE_MULTIPLE_SPACES.sub(" ", text).strip()


def is_wiki_url(url):
    """Проверяет, является ли URL ссылкой на Wikipedia"""
    return "wikipedia.org" in url.lower()


def fetch_wiki_lead(url):
    """
    Специализированная загрузка вводного абзаца Wikipedia.
    Возвращает первые 2-3 предложения статьи.
    """
    text = fetch_with_retry(url, max_retries=2)
    if not text:
        return ""
    clean = clean_wiki_artifacts(text)
    sentences = split_into_sentences(clean)
    sentences = remove_noise_sentences(sentences)
    lead = deduplicate_sentences(sentences[:5])
    return " ".join(lead[:3])


# =================================================================================
# БЛОК 49: ИНТЕРАКТИВНЫЙ РЕЖИМ v2 (расширенный)
# =================================================================================

def interactive_mode_v2():
    """
    Расширенный интерактивный режим с командами:
    - /cache     — показать кэш
    - /clear     — очистить кэш
    - /stats     — статистика сессии
    - /help      — справка
    - /json Q    — ответ в JSON
    - /md Q      — ответ в Markdown
    - /facts Q   — извлечь факты
    - /entities Q— извлечь сущности
    - выход      — выйти
    """
    print("\n" + "=" * 62)
    print("  AI — Умный поиск в интернете (расширенный режим v2)")
    print(f"  Ответы → {OUTPUT_FILE}")
    print("  Команды: /help /stats /cache /clear /json /md /facts")
    print("=" * 62)

    pipeline = FullAnalysisPipeline()

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n{_SESSION.report()}")
            print("[AI] До свидания!")
            break

        if not line:
            continue

        if line.lower() in ["выход", "exit", "quit", "q"]:
            print(f"\n{_SESSION.report()}")
            print("[AI] До свидания!")
            break

        if line == "/help":
            show_help()
            continue

        if line == "/stats":
            print(_SESSION.report())
            continue

        if line == "/cache":
            print(f"В кэше: {_GLOBAL_CACHE.size()} запросов")
            for q in _GLOBAL_CACHE.list_queries()[:10]:
                print(f"  • {q}")
            continue

        if line == "/clear":
            _GLOBAL_CACHE.clear_all()
            print("[AI] Кэш очищен.")
            continue

        if line.startswith("/json "):
            q = line[6:].strip()
            result = pipeline.run(q)
            print(format_as_json(q, result["answer"], result["sources"], result["q_type"]))
            continue

        if line.startswith("/md "):
            q = line[4:].strip()
            result = pipeline.run(q)
            print(format_as_markdown(q, result["answer"], result["sources"]))
            continue

        if line.startswith("/facts "):
            q = line[7:].strip()
            web_data = collect_web_texts(q, verbose=False)
            facts = extract_all_facts(web_data.get("combined_text", ""))
            if facts:
                print("Найденные факты:")
                for k, v in list(facts.items())[:15]:
                    print(f"  {k}: {v}")
            else:
                print("Факты не найдены.")
            continue

        if line.startswith("/entities "):
            q = line[10:].strip()
            web_data = collect_web_texts(q, verbose=False)
            ents = extract_all_entities(web_data.get("combined_text", ""))
            if ents:
                print("Именованные сущности:")
                for k, v in ents.items():
                    if v:
                        print(f"  {k}: {', '.join(str(x) for x in v[:3])}")
            else:
                print("Сущности не найдены.")
            continue

        ask_v2(line, verbose=True)




# =================================================================================
# БЛОК 50-60: РАСШИРЕННЫЕ ФУНКЦИИ
# =================================================================================

# --- Утилиты ---
def count_sentences(text):
    """Подсчитывает количество предложений"""
    return len(split_into_sentences(text))

def count_unique_words(text):
    """Количество уникальных слов"""
    return len(set(get_word_tokens(text)))

def get_average_sentence_length(text):
    """Средняя длина предложения в словах"""
    sents = split_into_sentences(text)
    if not sents:
        return 0
    return sum(len(s.split()) for s in sents) / len(sents)

def get_lexical_diversity(text):
    """Лексическое разнообразие (0-1)"""
    words = get_word_tokens(text)
    if not words:
        return 0.0
    return len(set(words)) / len(words)

def is_question(text):
    """Проверяет, является ли текст вопросом"""
    q_words = {"кто","что","где","когда","почему","как","сколько",
               "who","what","where","when","why","how"}
    return text.strip().endswith("?") or any(
        w in text.lower().split() for w in q_words
    )

def has_date(text):
    """Содержит ли текст дату"""
    return bool(RE_YEAR_ONLY.search(text))

def has_number(text):
    """Содержит ли текст число"""
    return bool(re.search(r'\d+', text))

def has_person_name(text):
    """Содержит ли текст имя персоны"""
    pat = re.compile(r'\b[А-ЯЁA-Z][а-яёa-z]+\s+[А-ЯЁA-Z][а-яёa-z]+\b')
    return bool(pat.search(text))

def get_first_sentence(text):
    """Возвращает первое предложение"""
    sents = split_into_sentences(text)
    return sents[0] if sents else ""

def get_last_sentence(text):
    """Возвращает последнее предложение"""
    sents = split_into_sentences(text)
    return sents[-1] if sents else ""

def remove_brackets(text):
    """Убирает содержимое скобок"""
    return re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}', '', text).strip()

def remove_extra_dots(text):
    """Убирает повторяющиеся точки"""
    return re.sub(r'\.{2,}', '.', text)

def count_paragraph(text):
    """Подсчитывает абзацы"""
    return len([p for p in text.split('\n\n') if p.strip()])


# --- Категоризатор ---
def detect_site_type(url):
    """Определяет тип сайта"""
    url_lower = url.lower()
    if 'wikipedia' in url_lower: return 'wiki'
    if any(d in url_lower for d in ['ria.ru','lenta.ru','bbc.com','nytimes.com','reuters.com']): return 'news'
    if any(d in url_lower for d in ['.edu','scholar','jstor']): return 'edu'
    if any(d in url_lower for d in ['mayo','webmd','healthline']): return 'medical'
    if any(d in url_lower for d in ['stackoverflow','github','developer.mozilla']): return 'tech'
    if any(d in url_lower for d in ['britannica','history.com','nationalgeographic']): return 'reference'
    return 'general'


# --- Стемматизация ---
RU_ENDINGS_ALL = [
    'ющий','ющая','ющее','ющие','ящий','ящая','ящее','ящие',
    'вший','вшая','вшее','вшие','ейший','айший','ейшая','айшая',
    'ательный','ательная','ательное','ательные',
    'ировать','овать','евать','ивать','ывать',
    'ируется','уется','ается','ивается','ывается',
    'ировал','овал','евал','ивал','ывал',
    'ировала','овала','евала','ивала','ывала',
    'ость','есть','ение','ание','ование','изация','ация','ция',
    'ности','ений','аний','ований','изаций','аций','ций',
    'ности','ностью','ениям','аниям','ованиям',
    'ческий','ческая','ческое','ческие','ческого','ческому','ческим',
    'ственный','ственная','ственное','ственные',
    'тельный','тельная','тельное','тельные',
    'ающий','ающая','ающее','ающие',
    'ающийся','ающаяся','ающееся','ающиеся',
    'ивший','ившая','ившее','ившие',
    'овый','овая','овое','овые',
    'евый','евая','евое','евые',
    'ального','альному','альным','альной',
    'ального','альную','альным',
    'ической','ическому','ическим','ическую',
    'ические','ических','ическими',
    'ом','ем','ём','у','ю','а','я','ы','и','е',
    'ой','ей','ёй','ах','ях','ам','ям','ами','ями',
    'ого','его','ёго','ому','ему','ёму',
    'ов','ев','ёв','ей','ий',
]

RU_ENDINGS_ALL = sorted(set(RU_ENDINGS_ALL), key=len, reverse=True)


def naive_stem_ru(word):
    """Наивная стемматизация русского слова"""
    word = word.lower()
    if len(word) < 5:
        return word
    for ending in RU_ENDINGS_ALL:
        if word.endswith(ending) and len(word) - len(ending) >= 3:
            return word[:-len(ending)]
    return word


def stem_tokens(tokens):
    """Применяет стемматизацию к токенам"""
    return [naive_stem_ru(t) for t in tokens]


def extract_with_stemming(web_data, query, top_n=3):
    """Извлечение с учётом морфологии"""
    query_stems = stem_tokens(list(build_query_words(query)))
    all_sents = []
    for src in web_data.get("results", []):
        sents = remove_noise_sentences(split_into_sentences(src["text"]))
        for s in sents:
            stems = stem_tokens(get_word_tokens(s))
            sc = len(set(stems) & set(query_stems)) * 2.5
            sc += score_sentence(s, build_query_words(query))
            all_sents.append((sc, s))
    all_sents.sort(key=lambda x: x[0], reverse=True)
    unique = deduplicate_sentences([s for _, s in all_sents])[:top_n]
    return truncate_to_sentence(" ".join(unique), MAX_ANSWER_LEN) if unique else ""


# --- Конвертеры ---
def km_to_miles(km): return km * 0.621371
def miles_to_km(mi): return mi * 1.60934
def kg_to_pounds(kg): return kg * 2.20462
def pounds_to_kg(lb): return lb * 0.453592
def celsius_to_fahrenheit(c): return c * 9/5 + 32
def fahrenheit_to_celsius(f): return (f - 32) * 5/9
def celsius_to_kelvin(c): return c + 273.15
def kelvin_to_celsius(k): return k - 273.15
def meters_to_feet(m): return m * 3.28084
def feet_to_meters(ft): return ft * 0.3048
def liters_to_gallons(l): return l * 0.264172
def gallons_to_liters(g): return g * 3.78541
def sq_km_to_sq_miles(sqkm): return sqkm * 0.386102
def sq_miles_to_sq_km(sqmi): return sqmi * 2.58999
def bytes_to_mb(b): return b / (1024**2)
def mb_to_gb(mb): return mb / 1024
def knots_to_kmh(kn): return kn * 1.852
def kmh_to_knots(kmh): return kmh / 1.852
def mach_to_ms(mach): return mach * 343
def ms_to_mach(ms): return ms / 343
def watts_to_hp(w): return w / 745.7
def hp_to_watts(hp): return hp * 745.7
def joules_to_cal(j): return j / 4.184
def cal_to_joules(cal): return cal * 4.184
def pascal_to_atm(pa): return pa / 101325
def atm_to_pascal(atm): return atm * 101325
def ly_to_km(ly): return ly * 9.461e12
def au_to_km(au): return au * 149597870.7
def km_to_au(km): return km / 149597870.7

UNIT_CONVERTERS = {
    "км в мили": {"fn": km_to_miles, "from": "км", "to": "миль"},
    "мили в км": {"fn": miles_to_km, "from": "миль", "to": "км"},
    "кг в фунты": {"fn": kg_to_pounds, "from": "кг", "to": "фунтов"},
    "фунты в кг": {"fn": pounds_to_kg, "from": "фунтов", "to": "кг"},
    "цельсий в фаренгейт": {"fn": celsius_to_fahrenheit, "from": "°C", "to": "°F"},
    "фаренгейт в цельсий": {"fn": fahrenheit_to_celsius, "from": "°F", "to": "°C"},
    "цельсий в кельвин": {"fn": celsius_to_kelvin, "from": "°C", "to": "K"},
    "кельвин в цельсий": {"fn": kelvin_to_celsius, "from": "K", "to": "°C"},
    "метры в футы": {"fn": meters_to_feet, "from": "м", "to": "фут"},
    "футы в метры": {"fn": feet_to_meters, "from": "фут", "to": "м"},
    "литры в галлоны": {"fn": liters_to_gallons, "from": "л", "to": "галлон"},
    "галлоны в литры": {"fn": gallons_to_liters, "from": "галлон", "to": "л"},
    "кв.км в кв.мили": {"fn": sq_km_to_sq_miles, "from": "кв.км", "to": "кв.миль"},
    "кв.мили в кв.км": {"fn": sq_miles_to_sq_km, "from": "кв.миль", "to": "кв.км"},
    "узлы в км/ч": {"fn": knots_to_kmh, "from": "узл", "to": "км/ч"},
    "Мах в м/с": {"fn": mach_to_ms, "from": "Мах", "to": "м/с"},
    "Вт в л.с.": {"fn": watts_to_hp, "from": "Вт", "to": "л.с."},
    "л.с. в Вт": {"fn": hp_to_watts, "from": "л.с.", "to": "Вт"},
    "Дж в кал": {"fn": joules_to_cal, "from": "Дж", "to": "кал"},
    "Па в атм": {"fn": pascal_to_atm, "from": "Па", "to": "атм"},
    "а.е. в км": {"fn": au_to_km, "from": "а.е.", "to": "км"},
}


def convert_units(value, conversion_name):
    """Конвертирует единицы измерения"""
    conv = UNIT_CONVERTERS.get(conversion_name)
    if not conv:
        return None
    try:
        result = conv["fn"](float(value))
        return f"{value} {conv['from']} = {result:.4g} {conv['to']}"
    except Exception:
        return None


# --- Итеративный поиск ---
class IterativeSearcher:
    """Итеративный поиск с уточнением запроса при низком качестве ответа"""

    def __init__(self, max_iterations=3, quality_threshold=0.5):
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold

    def search(self, query, verbose=True):
        best_answer = ""
        best_quality = 0.0
        queries = generate_search_queries(query)

        for i, q in enumerate(queries[:self.max_iterations]):
            if verbose:
                print(f"[Iterative {i+1}] {q}")
            web_data = collect_web_texts(q, verbose=False)
            if not web_data["results"]:
                continue
            q_type = determine_question_type_v2(query)
            answer = extract_answer_full(web_data, query, q_type)
            answer = postprocess_answer(answer, query)
            quality = estimate_answer_quality(answer, query)
            if quality > best_quality:
                best_quality = quality
                best_answer = answer
            if best_quality >= self.quality_threshold:
                break

        return best_answer, best_quality


_ITERATIVE = IterativeSearcher()


def ask_iterative(query, verbose=True):
    """Итеративный поиск с автоуточнением"""
    query = query.strip()
    if not query:
        return "Задайте вопрос!"
    init_output_file()
    answer, quality = _ITERATIVE.search(query, verbose=verbose)
    if not answer:
        answer = "Не удалось найти ответ."
    if verbose:
        print(f"\nОТВЕТ (качество {quality:.2f}):\n{answer}")
    report = format_report(query, answer, [], "", 0)
    save_to_file(report)
    return answer


# --- FullAnalysisPipeline ---
class FullAnalysisPipeline:
    """Полный пайплайн: Search → Extract → Validate → Save"""

    def __init__(self, config=None):
        self.config = config or _CONFIG

    def run(self, query):
        t0 = time.time()
        result = {
            "query": query, "q_type": None, "answer": None,
            "sources": [], "keywords": [], "elapsed": 0.0,
        }
        expanded = expand_query(query)
        result["q_type"] = determine_question_type_v2(query)
        web_data = collect_web_texts_robust(expanded, verbose=self.config.verbose)

        if not web_data["results"]:
            result["answer"] = "Не удалось найти информацию."
            result["elapsed"] = time.time() - t0
            return result

        answer = extract_answer_full(web_data, query, result["q_type"])
        answer = postprocess_answer(answer, query)
        is_valid, _ = validate_answer(answer, query)
        if not is_valid:
            answer = "Не удалось извлечь точный ответ."

        result["answer"] = answer
        result["sources"] = get_source_links(web_data, max_links=3)
        combined = web_data.get("combined_text", "")
        result["keywords"] = [w for w, _ in extract_top_words(combined, n=10)]
        report = format_report(
            query, answer, result["sources"], result["q_type"], web_data["sources_count"]
        )
        save_to_file(report)
        result["elapsed"] = time.time() - t0
        return result

    def run_batch(self, questions, delay=1.5):
        results = []
        for i, q in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] {q}")
            r = self.run(q)
            results.append(r)
            print(f"  → {r['answer'][:100]}...")
            if i < len(questions):
                time.sleep(delay)
        return results


DEMO_QUESTIONS = [
    "что такое ДНК", "кто такой Эйнштейн", "когда родился Пушкин",
    "где находится Эйфелева башня", "сколько планет в Солнечной системе",
    "почему небо синее", "как работает интернет", "что такое гравитация",
    "кто открыл Америку", "когда была основана Москва",
    "где самая высокая гора", "что такое квантовая физика",
    "кто написал Войну и мир", "когда началась Вторая мировая",
    "что такое блокчейн", "кто создал Python", "когда появился интернет",
    "сколько стран в мире", "почему идёт дождь", "как работает вакцина",
]


def run_demo(n=3, verbose=False):
    """Запускает демо — несколько случайных вопросов"""
    import random as _rnd
    selected = _rnd.sample(DEMO_QUESTIONS, min(n, len(DEMO_QUESTIONS)))
    print(f"\n=== AI DEMO: {len(selected)} вопроса ===")
    for q in selected:
        print(f"\n>> {q}")
        ask_v2(q, verbose=verbose)
    print("\n=== DEMO ЗАВЕРШЁН ===")


TRAINING_EXAMPLES = [
    ("кто такой Эйнштейн", "who"), ("кто создал Python", "who"),
    ("что такое ДНК", "what"), ("что такое гравитация", "what"),
    ("когда родился Пушкин", "when"), ("в каком году основан Google", "when"),
    ("где находится Лондон", "where"), ("столица Японии", "where"),
    ("сколько планет", "how_many"), ("население России", "how_many"),
    ("почему небо синее", "why"), ("из-за чего идёт дождь", "why"),
    ("как работает интернет", "how"), ("как создать сайт", "how"),
    ("who is Newton", "who"), ("what is DNA", "what"),
    ("when was Python created", "when"), ("where is Tokyo", "where"),
    ("how many planets", "how_many"), ("why is the sky blue", "why"),
    ("how does wifi work", "how"),
]


def evaluate_classifier():
    """Оценивает точность классификатора"""
    total = len(TRAINING_EXAMPLES)
    correct = 0
    errors = []
    for q, expected in TRAINING_EXAMPLES:
        got = determine_question_type_v2(q)
        if got == expected:
            correct += 1
        else:
            errors.append((q, expected, got))
    accuracy = correct / total if total else 0
    print(f"Точность: {correct}/{total} = {accuracy:.1%}")
    if errors:
        for q, exp, got in errors[:5]:
            print(f"  FAIL: {q!r}: ожидалось {exp}, получено {got}")
    return accuracy




# =================================================================================
# БЛОК 61: РАСШИРЕННЫЕ СТОП-СЛОВА РУССКОГО И АНГЛИЙСКОГО
# =================================================================================
_EXTRA_STOPS_RU = {
    'автоматически','вероятно','возможно','фактически','действительно','конечно',
    'безусловно','несомненно','разумеется','очевидно','вообще','собственно',
    'впрочем','таким образом','в действительности','на самом деле','как известно',
    'как правило','в целом','в общем','главным образом','прежде всего',
    'в конечном счёте','в результате','по данным','по словам','согласно',
    'что касается','относительно','именно','непосредственно','весьма',
    'чрезвычайно','крайне','особенно','достаточно','вполне','абсолютно',
    'совершенно','полностью','практически','в основном','нередко','порой',
    'подчас','временами','изредка','ранее','недавно','вскоре','потому',
    'оттого','следовательно','притом','вместе с тем','благодаря','несмотря',
    'вопреки','ввиду','вследствие','в силу','по причине','на основании',
    'в отличие','по сравнению','аналогично','например','в частности',
    'в том числе','то есть','иначе говоря','а именно','другими словами',
    'точнее','буквально','с одной стороны','с другой стороны',
    'во-первых','во-вторых','в-третьих','наряду','вместе','совместно',
    'одновременно','постепенно','последовательно','поэтапно','целиком',
    'частично','отчасти','при этом','причём','помимо','кроме',
    'исключительно','лишь','только лишь','примерно','около','приблизительно',
    'порядка','свыше','более','менее','как минимум','как максимум',
    'если только','при условии что','в зависимости от','с учётом',
    'исходя из','опираясь на','судя по','предположительно','по-видимому',
    'не исключено','по нашим данным','как сообщается','как отмечается',
    'по информации','по оценкам','по подсчётам','по расчётам',
}
_EXTRA_STOPS_EN = {
    'actually','basically','certainly','clearly','currently','directly','easily',
    'especially','eventually','exactly','finally','formally','generally',
    'honestly','however','indeed','instead','largely','lately','literally',
    'mainly','merely','mostly','notably','obviously','otherwise',
    'particularly','perhaps','possibly','primarily','probably','quickly',
    'quite','rather','recently','relatively','reportedly','seriously',
    'significantly','simply','slightly','sometimes','specifically',
    'strongly','surely','therefore','thus','typically','ultimately',
    'usually','virtually','widely','accordingly','additionally',
    'altogether','alternatively','apparently','approximately','arguably',
    'automatically','broadly','commonly','considerably','consistently',
    'continually','dramatically','effectively','essentially','explicitly',
    'extensively','frequently','fundamentally','gradually','heavily',
    'highly','historically','ideally','immediately','importantly',
    'incredibly','independently','inevitably','initially','intensely',
    'locally','logically','meanwhile','minimally','moreover','mutually',
    'naturally','necessarily','nonetheless','often','originally',
    'overall','periodically','permanently','physically','practically',
    'precisely','predominantly','progressively','promptly','properly',
    'publicly','rapidly','rationally','readily','regularly','repeatedly',
    'respectively','routinely','sharply','simultaneously','somehow',
    'somewhat','steadily','strictly','subsequently','substantially',
    'successfully','suddenly','supposedly','technically','temporarily',
    'theoretically','thoroughly','traditionally','uniformly','uniquely',
    'unnecessarily','unusually','urgently','worldwide',
}
ALL_STOP_WORDS.update(_EXTRA_STOPS_RU)
ALL_STOP_WORDS.update(_EXTRA_STOPS_EN)


# =================================================================================
# БЛОК 62: ФРАЗЫ-ИНДИКАТОРЫ ОТВЕТОВ ПО ТИПУ ВОПРОСА
# =================================================================================

ANSWER_INDICATORS = {
    'who': ['является','был','была','работал','родился','основал','создал',
            'изобрёл','открыл','написал','руководил','is a','was a','was born',
            'founded','created','invented','discovered','authored','directed'],
    'what': ['это','является','представляет собой','называется','означает',
             'определяется как','включает','состоит из','относится к',
             'is a','is an','is the','refers to','means','defined as',
             'consists of','includes','represents','describes'],
    'when': ['в году','году','основан в','создан в','родился в','умер в',
             'произошло в','началась','закончилась','in','founded in',
             'created in','born in','died in','occurred in','started in'],
    'where': ['находится','расположен','расположена','лежит','базируется',
              'обитает','is located','is situated','is found','is based',
              'lies in','is in','stands in'],
    'how_many': ['составляет','равен','насчитывает','содержит','около',
                 'приблизительно','более','свыше','is approximately',
                 'equals','amounts to','totals','reaches'],
    'why': ['потому что','так как','из-за','вследствие','по причине',
            'поскольку','ввиду','because','due to','as a result',
            'owing to','since','caused by'],
    'how': ['путём','с помощью','посредством','методом','способом',
            'при помощи','используя','by','through','using','via',
            'by means of','by using','with the aid'],
}
_ANSWER_IND_PATS = {qt: [re.compile(re.escape(p), re.I) for p in ps]
                    for qt, ps in ANSWER_INDICATORS.items()}


def score_by_indicators(sentence, q_type):
    """Бонус предложениям с индикаторами типа ответа"""
    return float(sum(1 for pat in _ANSWER_IND_PATS.get(q_type, [])
                     if pat.search(sentence)))


# =================================================================================
# БЛОК 63: ФИЗИЧЕСКИЕ И МАТЕМАТИЧЕСКИЕ КОНСТАНТЫ
# =================================================================================

PHYSICS_CONSTANTS = {
    'speed_of_light': {'symbol': 'c', 'value': 299792458, 'unit': 'м/с',
                       'desc': 'Скорость света в вакууме'},
    'planck': {'symbol': 'h', 'value': 6.626e-34, 'unit': 'Дж·с',
               'desc': 'Постоянная Планка'},
    'boltzmann': {'symbol': 'k', 'value': 1.381e-23, 'unit': 'Дж/К',
                  'desc': 'Постоянная Больцмана'},
    'avogadro': {'symbol': 'Na', 'value': 6.022e23, 'unit': 'моль⁻¹',
                 'desc': 'Число Авогадро'},
    'electron_mass': {'symbol': 'me', 'value': 9.109e-31, 'unit': 'кг',
                      'desc': 'Масса электрона'},
    'proton_mass': {'symbol': 'mp', 'value': 1.673e-27, 'unit': 'кг',
                    'desc': 'Масса протона'},
    'gravitational': {'symbol': 'G', 'value': 6.674e-11, 'unit': 'Н·м²/кг²',
                      'desc': 'Гравитационная постоянная'},
    'elementary_charge': {'symbol': 'e', 'value': 1.602e-19, 'unit': 'Кл',
                           'desc': 'Элементарный заряд'},
    'gas_constant': {'symbol': 'R', 'value': 8.314, 'unit': 'Дж/(моль·К)',
                     'desc': 'Универсальная газовая постоянная'},
    'stefan_boltzmann': {'symbol': 'σ', 'value': 5.671e-8, 'unit': 'Вт/(м²·К⁴)',
                         'desc': 'Постоянная Стефана—Больцмана'},
    'earth_mass': {'symbol': 'Me', 'value': 5.972e24, 'unit': 'кг',
                   'desc': 'Масса Земли'},
    'earth_radius': {'symbol': 'Re', 'value': 6371000, 'unit': 'м',
                     'desc': 'Средний радиус Земли'},
    'sun_mass': {'symbol': 'Ms', 'value': 1.989e30, 'unit': 'кг',
                 'desc': 'Масса Солнца'},
    'moon_mass': {'symbol': 'Mm', 'value': 7.342e22, 'unit': 'кг',
                  'desc': 'Масса Луны'},
    'au': {'symbol': 'AU', 'value': 1.496e11, 'unit': 'м',
           'desc': 'Астрономическая единица'},
    'parsec': {'symbol': 'пк', 'value': 3.086e16, 'unit': 'м',
               'desc': 'Парсек'},
    'light_year': {'symbol': 'св.г.', 'value': 9.461e15, 'unit': 'м',
                   'desc': 'Световой год'},
    'gravity_earth': {'symbol': 'g', 'value': 9.807, 'unit': 'м/с²',
                      'desc': 'Ускорение свободного падения (Земля)'},
    'gravity_moon': {'symbol': 'g_m', 'value': 1.625, 'unit': 'м/с²',
                     'desc': 'Ускорение свободного падения (Луна)'},
    'gravity_mars': {'symbol': 'g_mars', 'value': 3.72, 'unit': 'м/с²',
                     'desc': 'Ускорение свободного падения (Марс)'},
    'sound_speed_air': {'symbol': 'vs', 'value': 343, 'unit': 'м/с',
                        'desc': 'Скорость звука в воздухе (20°C)'},
    'water_density': {'symbol': 'ρ_w', 'value': 1000, 'unit': 'кг/м³',
                      'desc': 'Плотность воды при 4°C'},
    'air_density': {'symbol': 'ρ_a', 'value': 1.293, 'unit': 'кг/м³',
                    'desc': 'Плотность воздуха при 0°C'},
    'absolute_zero': {'symbol': 'T₀', 'value': -273.15, 'unit': '°C',
                      'desc': 'Абсолютный ноль'},
    'faraday': {'symbol': 'F', 'value': 96485, 'unit': 'Кл/моль',
                'desc': 'Постоянная Фарадея'},
    'pi': {'symbol': 'π', 'value': 3.14159265358979, 'unit': 'безразм.',
           'desc': 'Число Пи'},
    'euler_e': {'symbol': 'e', 'value': 2.71828182845905, 'unit': 'безразм.',
                'desc': 'Число Эйлера'},
    'golden_ratio': {'symbol': 'φ', 'value': 1.61803398874989, 'unit': 'безразм.',
                     'desc': 'Золотое сечение'},
    'sqrt2': {'symbol': '√2', 'value': 1.41421356237310, 'unit': 'безразм.',
              'desc': 'Корень из двух'},
    'ln2': {'symbol': 'ln(2)', 'value': 0.69314718055995, 'unit': 'безразм.',
            'desc': 'Натуральный логарифм 2'},
    'fine_structure': {'symbol': 'α', 'value': 0.007297, 'unit': 'безразм.',
                       'desc': 'Постоянная тонкой структуры'},
}


def get_constant(name):
    """Возвращает физическую или математическую константу"""
    c = PHYSICS_CONSTANTS.get(name)
    if c:
        return f"{c['desc']}: {c['symbol']} = {c['value']} {c['unit']}"
    # Поиск по описанию
    name_l = name.lower()
    for k, c in PHYSICS_CONSTANTS.items():
        if name_l in c['desc'].lower() or name_l in c['symbol'].lower():
            return f"{c['desc']}: {c['symbol']} = {c['value']} {c['unit']}"
    return None


# =================================================================================
# БЛОК 64: ВЫЧИСЛИТЕЛЬ МАТЕМАТИЧЕСКИХ ВЫРАЖЕНИЙ
# =================================================================================

_MATH_OPS = [
    ('add', re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:\+|плюс)\s*(\d+(?:[.,]\d+)?)', re.I)),
    ('sub', re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:-|минус)\s*(\d+(?:[.,]\d+)?)', re.I)),
    ('mul', re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:\*|[xх×]|умножить\s+на)\s*(\d+(?:[.,]\d+)?)', re.I)),
    ('div', re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:/|делить\s+на)\s*(\d+(?:[.,]\d+)?)', re.I)),
    ('pow', re.compile(
        r'(\d+(?:[.,]\d+)?)\s*(?:\^|\*\*|в\s+степени)\s*(\d+(?:[.,]\d+)?)', re.I)),
    ('sqrt', re.compile(
        r'(?:корень\s+(?:из\s+)?|sqrt\s*)(\d+(?:[.,]\d+)?)', re.I)),
    ('pct', re.compile(
        r'(\d+(?:[.,]\d+)?)\s*%\s*(?:от|of)\s*(\d+(?:[.,]\d+)?)', re.I)),
    ('sq', re.compile(
        r'(\d+(?:[.,]\d+)?)\s+(?:в квадрате|squared)', re.I)),
    ('cb', re.compile(
        r'(\d+(?:[.,]\d+)?)\s+(?:в кубе|cubed)', re.I)),
]


def calculate_simple(text):
    """Вычисляет простое математическое выражение из текста"""
    for op, pat in _MATH_OPS:
        m = pat.search(text)
        if not m:
            continue
        try:
            if op == 'sqrt':
                a = float(m.group(1).replace(',', '.'))
                return f'√{a} = {a**0.5:.6g}'
            if op == 'sq':
                a = float(m.group(1).replace(',', '.'))
                return f'{a}² = {a**2:.6g}'
            if op == 'cb':
                a = float(m.group(1).replace(',', '.'))
                return f'{a}³ = {a**3:.6g}'
            a = float(m.group(1).replace(',', '.'))
            b = float(m.group(2).replace(',', '.'))
            if op == 'add':
                return f'{a} + {b} = {a + b:.6g}'
            if op == 'sub':
                return f'{a} - {b} = {a - b:.6g}'
            if op == 'mul':
                return f'{a} × {b} = {a * b:.6g}'
            if op == 'div':
                if b == 0:
                    return 'Деление на ноль невозможно'
                return f'{a} ÷ {b} = {a / b:.6g}'
            if op == 'pow':
                return f'{a}^{b:.0f} = {a ** b:.6g}'
            if op == 'pct':
                return f'{a}% от {b} = {a * b / 100:.6g}'
        except Exception:
            pass
    return None


# =================================================================================
# БЛОК 65: РАСШИРЕННЫЙ СЛОВАРЬ СИНОНИМОВ ДЛЯ ПОИСКА (60+ групп)
# =================================================================================

SEARCH_SYNONYMS = {
    'умер': ['скончался', 'погиб', 'ушёл из жизни', 'дата смерти'],
    'родился': ['появился на свет', 'рождён', 'дата рождения'],
    'создал': ['основал', 'придумал', 'изобрёл', 'разработал', 'написал'],
    'открыл': ['обнаружил', 'нашёл', 'выявил', 'установил'],
    'столица': ['главный город', 'administrative capital', 'capital city'],
    'население': ['численность', 'жителей', 'residents', 'inhabitants'],
    'площадь': ['территория', 'square km', 'территория страны'],
    'высота': ['altitude', 'высок', 'достигает', 'над уровнем моря'],
    'длина': ['протяжённость', 'length', 'extends', 'простирается'],
    'глубина': ['depth', 'глубок', 'дно'],
    'скорость': ['velocity', 'speed', 'км/ч', 'mph'],
    'температура': ['temperature', 'celsius', 'градус'],
    'вес': ['weight', 'mass', 'масса', 'весит'],
    'возраст': ['age', 'лет', 'years old', 'год рождения'],
    'цвет': ['colour', 'color', 'окраска'],
    'стоимость': ['цена', 'price', 'cost', 'рублей'],
    'доход': ['revenue', 'profit', 'выручка'],
    'язык': ['language', 'говорит', 'speaks'],
    'химический элемент': ['element', 'atomic number', 'атомный номер'],
    'формула': ['formula', 'equation', 'уравнение'],
    'закон': ['law', 'rule', 'theorem', 'principle'],
    'изобретение': ['invention', 'discovery', 'открытие'],
    'биография': ['biography', 'жизнь', 'история жизни'],
    'организация': ['organization', 'company', 'корпорация'],
    'наука': ['science', 'scientific field'],
    'технология': ['technology', 'tech', 'method'],
    'программа': ['software', 'application', 'app'],
    'алгоритм': ['algorithm', 'procedure', 'method'],
    'планета': ['planet', 'celestial body'],
    'звезда': ['star', 'stellar'],
    'животное': ['animal', 'species', 'вид'],
    'растение': ['plant', 'flora', 'vegetation'],
    'болезнь': ['disease', 'illness', 'condition'],
    'лечение': ['treatment', 'therapy', 'cure'],
    'рекорд': ['record', 'achievement', 'достижение'],
    'премия': ['prize', 'award', 'Nobel', 'награда'],
    'война': ['war', 'conflict', 'armed conflict'],
    'религия': ['religion', 'faith', 'belief'],
    'культура': ['culture', 'civilization', 'tradition'],
    'архитектура': ['architecture', 'building', 'structure'],
    'музыка': ['music', 'song', 'melody'],
    'кино': ['cinema', 'film', 'movie'],
    'книга': ['book', 'novel', 'literary work'],
    'спорт': ['sport', 'athletics', 'competition'],
    'экономика': ['economy', 'economics', 'finance'],
    'политика': ['politics', 'government', 'governance'],
    'история': ['history', 'historical', 'past'],
    'математика': ['mathematics', 'math', 'calculus'],
    'физика': ['physics', 'physical science', 'mechanics'],
    'химия': ['chemistry', 'chemical', 'biochemistry'],
    'биология': ['biology', 'life science', 'ecology'],
    'астрономия': ['astronomy', 'astrophysics', 'cosmology'],
    'география': ['geography', 'cartography'],
    'лингвистика': ['linguistics', 'language study', 'philology'],
    'психология': ['psychology', 'behavior', 'mental health'],
    'право': ['law', 'legal', 'legislation'],
    'медицина': ['medicine', 'healthcare', 'health'],
}


def expand_query_v2(query):
    """Расширенное расширение запроса через большой словарь синонимов"""
    expanded = expand_query(query)
    q_lower = query.lower()
    for key, syns in SEARCH_SYNONYMS.items():
        if key.lower() in q_lower:
            expanded += ' ' + ' '.join(syns[:2])
    return expanded.strip()


# =================================================================================
# БЛОК 66: ОЦЕНКА КАЧЕСТВА ИСТОЧНИКОВ
# =================================================================================

SOURCE_QUALITY_RULES = {
    'academic': {'keywords': ['scholar','journal','research','arxiv','pubmed','doi'], 'score': 1.0},
    'official': {'keywords': ['gov','parliament','un.org','who.int','worldbank','oecd'], 'score': 0.95},
    'encyclopedia': {'keywords': ['wikipedia','britannica','encyclopedia'], 'score': 0.9},
    'news_major': {'keywords': ['reuters','apnews','bbc','nytimes','washingtonpost','guardian'], 'score': 0.85},
    'news_ru': {'keywords': ['ria.ru','tass.ru','rbc.ru','lenta.ru','kommersant'], 'score': 0.80},
    'reference': {'keywords': ['history.com','nationalgeographic','smithsonian','scientificamerican'], 'score': 0.80},
    'medical': {'keywords': ['mayo','webmd','healthline','medlineplus','nhs.uk'], 'score': 0.85},
    'tech': {'keywords': ['stackoverflow','github','mozilla','python.org'], 'score': 0.80},
    'stats': {'keywords': ['worldometers','ourworldindata','statista','worldatlas'], 'score': 0.75},
    'ru_tech': {'keywords': ['habr.com','tproger.ru','skillbox','hexlet'], 'score': 0.70},
}


def get_source_quality_score(url):
    """Оценка качества источника 0.0-1.0"""
    url_lower = url.lower()
    best = 0.5
    for cat, rules in SOURCE_QUALITY_RULES.items():
        if any(kw in url_lower for kw in rules['keywords']):
            best = max(best, rules['score'])
    return best


def rank_sources_by_quality(results):
    """Сортирует источники по качеству"""
    return sorted(results, key=lambda r: get_source_quality_score(r['url']), reverse=True)


def extract_from_best_sources(web_data, query, q_type, n=3):
    """Извлекает ответ из топ N источников по качеству"""
    best = rank_sources_by_quality(web_data.get('results', []))[:n]
    mini_data = dict(web_data)
    mini_data['results'] = best
    mini_data['combined_text'] = ' '.join(r['text'] for r in best)
    return AnswerProcessor(mini_data, query, q_type).process()


# =================================================================================
# БЛОК 67: ОБУЧАЮЩИЕ ПРИМЕРЫ И ТЕСТИРОВАНИЕ
# =================================================================================

TRAINING_EXAMPLES_FULL = [
    # WHO (20 примеров)
    ("кто такой Эйнштейн", "who"), ("кто создал Python", "who"),
    ("кто основал Google", "who"), ("кто написал Гамлета", "who"),
    ("кто открыл пенициллин", "who"), ("кто изобрёл телефон", "who"),
    ("кто президент США", "who"), ("кто автор Мастера и Маргариты", "who"),
    ("кто первым полетел в космос", "who"), ("кто придумал интернет", "who"),
    ("who is Stephen Hawking", "who"), ("who created Linux", "who"),
    ("who founded Apple", "who"), ("who wrote Harry Potter", "who"),
    ("who invented the light bulb", "who"), ("кем является Билл Гейтс", "who"),
    ("кто возглавляет ООН", "who"), ("кто написал Евгения Онегина", "who"),
    ("кто открыл Антарктиду", "who"), ("кто изобрёл паровой двигатель", "who"),
    # WHAT (20 примеров)
    ("что такое ДНК", "what"), ("что такое квантовая механика", "what"),
    ("что значит алгоритм", "what"), ("что такое нейросеть", "what"),
    ("что представляет собой блокчейн", "what"), ("что такое энтропия", "what"),
    ("из чего состоит вода", "what"), ("как устроен атом", "what"),
    ("что означает слово синапс", "what"), ("объясни понятие эволюция", "what"),
    ("what is quantum physics", "what"), ("what does DNA mean", "what"),
    ("define algorithm", "what"), ("explain machine learning", "what"),
    ("what is blockchain", "what"), ("что такое гравитация", "what"),
    ("что такое искусственный интеллект", "what"),
    ("что значит феромон", "what"), ("что такое квазар", "what"),
    ("что такое синапс", "what"),
    # WHEN (20 примеров)
    ("когда родился Ньютон", "when"), ("когда была основана Москва", "when"),
    ("в каком году изобрели интернет", "when"), ("когда умер Толстой", "when"),
    ("год основания Google", "when"), ("когда началась Первая мировая", "when"),
    ("когда открыли пенициллин", "when"), ("когда изобрели колесо", "when"),
    ("дата рождения Пушкина", "when"), ("когда распался СССР", "when"),
    ("when was the internet invented", "when"), ("when did World War 2 start", "when"),
    ("what year was Python created", "when"), ("when was Newton born", "when"),
    ("when did the dinosaurs go extinct", "when"),
    ("когда появилось электричество", "when"), ("когда открыли Австралию", "when"),
    ("год изобретения самолёта", "when"), ("когда основан Рим", "when"),
    ("когда изобрели книгопечатание", "when"),
    # WHERE (20 примеров)
    ("где находится Эйфелева башня", "where"), ("в какой стране Ватикан", "where"),
    ("столица Австралии", "where"), ("где обитают пингвины", "where"),
    ("в каком городе находится Лувр", "where"), ("где расположена Сахара", "where"),
    ("где находится Большой Барьерный риф", "where"), ("где живут коалы", "where"),
    ("где самая высокая гора", "where"), ("в какой стране Токио", "where"),
    ("where is the Eiffel Tower", "where"), ("where is the Amazon rainforest", "where"),
    ("what country is Tokyo in", "where"), ("where do penguins live", "where"),
    ("where is the Great Wall of China", "where"), ("столица Канады", "where"),
    ("где расположена Антарктида", "where"), ("где находится Гималаи", "where"),
    ("где протекает Нил", "where"), ("в какой стране Ниагара", "where"),
    # HOW MANY (20 примеров)
    ("сколько планет в Солнечной системе", "how_many"), ("сколько стран в мире", "how_many"),
    ("население России", "how_many"), ("площадь Африки", "how_many"),
    ("высота Эвереста", "how_many"), ("сколько км до Луны", "how_many"),
    ("глубина Байкала", "how_many"), ("вес синего кита", "how_many"),
    ("сколько языков в мире", "how_many"), ("скорость света", "how_many"),
    ("how many planets", "how_many"), ("what is the population of China", "how_many"),
    ("how tall is Mount Everest", "how_many"), ("how far is the Moon", "how_many"),
    ("what is the speed of light", "how_many"), ("сколько спутников у Юпитера", "how_many"),
    ("какова площадь Австралии", "how_many"), ("сколько весит Земля", "how_many"),
    ("сколько хромосом у человека", "how_many"), ("численность населения Индии", "how_many"),
    # WHY (20 примеров)
    ("почему небо синее", "why"), ("почему идёт дождь", "why"),
    ("почему листья меняют цвет", "why"), ("почему Земля вращается", "why"),
    ("почему люди спят", "why"), ("по какой причине землетрясения", "why"),
    ("из-за чего возникает радуга", "why"), ("почему лёд плавает", "why"),
    ("почему закат красный", "why"), ("почему мы видим сны", "why"),
    ("why is the sky blue", "why"), ("why does it rain", "why"),
    ("why do leaves change color", "why"), ("why do we dream", "why"),
    ("why is ice less dense than water", "why"), ("почему звёзды мерцают", "why"),
    ("почему морская вода солёная", "why"), ("почему гром гремит", "why"),
    ("зачем нужны бактерии", "why"), ("из-за чего бывают приливы", "why"),
    # HOW (20 примеров)
    ("как работает интернет", "how"), ("как работает GPS", "how"),
    ("как устроен самолёт", "how"), ("каким образом работает Wi-Fi", "how"),
    ("как создать сайт", "how"), ("как работает нейросеть", "how"),
    ("как работает вакцина", "how"), ("как устроен холодильник", "how"),
    ("как написать программу", "how"), ("каким способом работает МРТ", "how"),
    ("how does the internet work", "how"), ("how does GPS work", "how"),
    ("how to create a website", "how"), ("how does a vaccine work", "how"),
    ("how does wifi work", "how"), ("как работает ядерный реактор", "how"),
    ("как устроен компьютер", "how"), ("как работает человеческий мозг", "how"),
    ("как сделать фотографию", "how"), ("как устроен телескоп", "how"),
]


def evaluate_classifier_full():
    """Полная оценка точности классификатора (140 примеров)"""
    total = len(TRAINING_EXAMPLES_FULL)
    correct = sum(1 for q, e in TRAINING_EXAMPLES_FULL
                  if determine_question_type_v2(q) == e)
    accuracy = correct / total if total else 0
    print(f"Точность классификатора: {correct}/{total} = {accuracy:.1%}")
    errors = [(q, e, determine_question_type_v2(q)) for q, e in TRAINING_EXAMPLES_FULL
              if determine_question_type_v2(q) != e]
    if errors:
        print(f"Ошибки ({len(errors)}):")
        for q, exp, got in errors[:5]:
            print(f"  {q!r}: ожидалось {exp}, получено {got}")
    return accuracy


# =================================================================================
# БЛОК 68: УМНЫЙ ПОИСК ask_smart_v2 (7 АЛГОРИТМОВ + ЛУЧШИЕ ИСТОЧНИКИ)
# =================================================================================

def ask_smart_v2(query, verbose=True):
    """
    Самая полная версия поиска:
    1. Вычислитель математики (локально, без интернета)
    2. Кэш ответов
    3. Расширение запроса v2 (60+ групп синонимов)
    4. Надёжный поиск в интернете (retry)
    5. Приоритизация источников по качеству
    6. 7 алгоритмов извлечения ответа
    7. Постобработка + валидация
    8. Сохранение в main.txt
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    # 1. Математика
    math_r = calculate_simple(query)
    if math_r:
        init_output_file()
        save_to_file(format_report(query, math_r, [], "math", 0))
        if verbose:
            print(f"[Math] {math_r}")
        return math_r

    # 2. Кэш
    cached = _GLOBAL_CACHE.get(query)
    if cached:
        if verbose:
            print(f"[Cache] {cached}")
        return cached

    init_output_file()
    t0 = time.time()

    # 3. Расширение запроса
    expanded = expand_query_v2(query)
    if verbose and expanded != query:
        print(f"[AI] Расширен запрос: {expanded[:80]}")

    # 4. Поиск в интернете
    web_data = collect_web_texts_robust(expanded, verbose=verbose)

    if not web_data["results"]:
        answer = "Нет подключения к интернету или сайты недоступны."
        save_to_file(format_report(query, answer, [], "none", 0))
        return answer

    # 5. Тип вопроса
    q_type = determine_question_type_v2(query)
    if verbose:
        print(f"[AI] Тип вопроса: {q_type}")

    # 6. 7 алгоритмов
    a1 = extract_from_best_sources(web_data, query, q_type)
    a2 = AnswerProcessor(web_data, query, q_type).process()
    a3 = extract_with_tfidf(web_data, query, top_n=3)
    a4 = extract_with_context_window(web_data, query)
    a5 = extract_with_mmr(web_data, query, top_n=3)
    a6 = extract_with_bm25(web_data, query, top_n=3)
    a7 = extract_with_stemming(web_data, query, top_n=3)

    cands = [a for a in [a1, a2, a3, a4, a5, a6, a7] if a and len(a) >= 15]

    if cands:
        answer = max(cands, key=lambda a: estimate_answer_quality(a, query))
        answer = clean_answer_text(answer)
    else:
        answer = "Не удалось извлечь ответ из найденных данных."

    # 7. Постобработка
    answer = postprocess_answer(answer, query)
    is_valid, reason = validate_answer(answer, query)
    if not is_valid and verbose:
        print(f"[AI] Валидация: {reason}")

    if not answer or len(answer) < 15:
        answer = "Не удалось найти точный ответ."

    # 8. Сохранение
    sources = get_source_links(web_data, max_links=3)
    report = format_report(query, answer, sources, q_type, web_data["sources_count"])
    save_to_file(report)
    _GLOBAL_CACHE.set(query, answer)

    elapsed = time.time() - t0
    if verbose:
        print(f"\n{'='*60}")
        print(f"ОТВЕТ:\n{answer}")
        print(f"{'='*60}")
        print(f"Время: {elapsed:.1f}с | Источников: {web_data['sources_count']}")
        print(f"Сохранено: {OUTPUT_FILE}")

    return answer


# =================================================================================
# БЛОК 69: МУСОРНЫЕ МАРКЕРЫ (РАСШИРЕННЫЙ СПИСОК)
# =================================================================================

EXTRA_NOISE_MARKERS = [
    'подписывайтесь на', 'подпишитесь', 'нажмите', 'кликните', 'скачайте',
    'купите', 'закажите', 'оставьте отзыв', 'поставьте оценку', 'лайкните',
    'репостните', 'поделитесь', 'расскажите друзьям', 'зарегистрируйтесь',
    'войдите в', 'авторизуйтесь', 'забыли пароль', 'восстановить пароль',
    'cookie', 'cookies', 'куки', 'согласен с', 'принять условия',
    'политика конфиденциальности', 'terms of service', 'privacy policy',
    'all rights reserved', 'copyright', 'все права защищены',
    'реклама', 'advertisement', 'sponsored by',
    'related articles', 'похожие статьи', 'читайте также', 'see also',
    'дополнительные материалы', 'further reading', 'external links',
    'загрузка', 'loading', 'подождите', 'please wait',
    'javascript', 'enable javascript', 'включите javascript',
    'нет доступа', 'access denied', 'forbidden', '404', '403', '503',
    'страница не найдена', 'page not found',
    'главная', 'menu', 'navigation', 'навигация', 'sidebar',
    'отправить', 'submit', 'cancel', 'отмена', 'close', 'закрыть',
    'save', 'сохранить', 'delete', 'удалить', 'edit', 'редактировать',
    'read more', 'читать далее', 'подробнее', 'more info', 'learn more',
    'share', 'поделиться', 'tweet', 'like', 'лайк', 'dislike',
    'comment', 'reply', 'ответить', 'report', 'пожаловаться',
    'login', 'войти', 'register', 'signup', 'sign up',
    'search', 'поиск', 'filter', 'фильтр', 'sort', 'сортировка',
    'subscribe', 'подписаться', 'unsubscribe', 'newsletter', 'рассылка',
    'contact', 'контакты', 'about us', 'о нас', 'our team', 'наша команда',
    'career', 'карьера', 'jobs', 'вакансии', 'press', 'пресса',
    'partner', 'партнёр', 'sponsor', 'спонсор', 'donate', 'пожертвовать',
    'buy', 'купить', 'order', 'заказать', 'shop', 'магазин', 'cart', 'корзина',
    'checkout', 'оформить заказ', 'payment', 'оплата',
    'download', 'скачать', 'install', 'установить', 'update', 'обновление',
    'documentation', 'документация', 'faq', 'часто задаваемые вопросы',
    'forum', 'форум', 'community', 'сообщество', 'discord', 'slack', 'telegram',
    'follow us', 'следите за нами', 'facebook', 'instagram', 'twitter', 'youtube',
]

_EXTRA_NOISE_RE = re.compile(
    '|'.join(re.escape(p) for p in EXTRA_NOISE_MARKERS),
    re.I
)

QUALITY_PENALTY_WORDS.update({
    'подписывайтесь', 'купите', 'зарегистрируйтесь', 'реклама',
    'cookies', 'all rights reserved', 'advertisement', 'loading',
    'javascript', 'forbidden', 'access denied',
})


def is_noise_sentence_v2(sentence):
    """Расширенная проверка на мусорное предложение"""
    return bool(_EXTRA_NOISE_RE.search(sentence)) or is_noise_sentence(sentence)


def remove_noise_sentences_v2(sentences):
    """Расширенная версия удаления мусорных предложений"""
    return [s for s in sentences
            if not is_noise_sentence_v2(s) and len(s.split()) >= 4]


# =================================================================================
# БЛОК 70: ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ ДЛЯ РАБОТЫ С ТЕКСТОМ
# =================================================================================

def count_sentences(text):
    """Подсчитывает количество предложений"""
    return len(split_into_sentences(text))


def count_unique_words(text):
    """Количество уникальных слов"""
    return len(set(get_word_tokens(text)))


def count_paragraphs(text):
    """Подсчитывает абзацы"""
    return len([p for p in text.split('\n\n') if p.strip()])


def get_average_sentence_length(text):
    """Средняя длина предложения в словах"""
    sents = split_into_sentences(text)
    if not sents:
        return 0.0
    return sum(len(s.split()) for s in sents) / len(sents)


def get_lexical_diversity(text):
    """Лексическое разнообразие (0-1)"""
    words = get_word_tokens(text)
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def is_question(text):
    """Проверяет, является ли текст вопросом"""
    q_words = {'кто', 'что', 'где', 'когда', 'почему', 'как', 'сколько',
               'who', 'what', 'where', 'when', 'why', 'how'}
    return text.strip().endswith('?') or any(
        w in text.lower().split() for w in q_words
    )


def has_date(text):
    """Содержит ли текст дату"""
    return bool(re.search(r'\b(?:1[0-9]|20)[0-9]{2}\b', text))


def has_number(text):
    """Содержит ли текст число"""
    return bool(re.search(r'\d+', text))


def has_person_name(text):
    """Содержит ли текст имя персоны (Имя Фамилия)"""
    return bool(re.search(
        r'\b[А-ЯЁA-Z][а-яёa-z]+\s+[А-ЯЁA-Z][а-яёa-z]+\b', text))


def get_first_sentence(text):
    """Возвращает первое предложение"""
    sents = split_into_sentences(text)
    return sents[0] if sents else ''


def get_last_sentence(text):
    """Возвращает последнее предложение"""
    sents = split_into_sentences(text)
    return sents[-1] if sents else ''


def remove_brackets(text):
    """Убирает содержимое скобок"""
    return re.sub(r'\([^)]*\)|\[[^\]]*\]|\{[^}]*\}', '', text).strip()


def remove_extra_dots(text):
    """Убирает повторяющиеся точки"""
    return re.sub(r'\.{2,}', '.', text)


def get_text_language_simple(text):
    """Упрощённое определение языка текста"""
    cyrillic = len(re.findall(r'[а-яёА-ЯЁ]', text))
    latin = len(re.findall(r'[a-zA-Z]', text))
    return 'ru' if cyrillic > latin else 'en'


def build_summary_from_multiple_sources_v2(web_data, query, n_sents=4):
    """
    Строит резюме из нескольких источников (расширенная версия).
    Применяет remove_noise_sentences_v2 + mmr_selection.
    """
    all_sents = []
    for src in web_data.get('results', []):
        sents = remove_noise_sentences_v2(split_into_sentences(src['text']))
        all_sents.extend(sents)

    all_sents = deduplicate_sentences(all_sents)
    selected = mmr_selection(all_sents, query, top_n=n_sents)

    if not selected:
        return ''
    return truncate_to_sentence(' '.join(selected), MAX_ANSWER_LEN)




# =================================================================================
# БЛОК 71-80: ПРОДВИНУТЫЙ АНАЛИЗ И ИЗВЛЕЧЕНИЕ
# =================================================================================

# БЛОК 71: Полный набор паттернов для 200+ числовых форматов
RE_NUMBERS_ALL = {
    # Целые числа
    'integer': re.compile(r'\b(\d{1,15})\b'),
    # Дробные
    'decimal': re.compile(r'\b(\d+[.,]\d+)\b'),
    # Проценты
    'percent': re.compile(r'\b(\d+(?:[.,]\d+)?)\s*%'),
    # Дроби
    'fraction': re.compile(r'\b(\d+)\s*/\s*(\d+)\b'),
    # Диапазоны
    'range': re.compile(r'\b(\d+(?:[.,]\d+)?)\s*[-–—]\s*(\d+(?:[.,]\d+)?)\b'),
    # Приблизительные
    'approx': re.compile(r'(?:около|примерно|~|≈)\s*(\d+)', re.I),
    # Годы
    'year': re.compile(r'\b((?:1[0-9]|20)[0-9]{2})\b'),
    # Большие числа с суффиксами
    'large_ru': re.compile(
        r'\b(\d+(?:[,\.]\d+)?)\s*(?:млн|млрд|тысяч|миллион|миллиард)\b', re.I),
    'large_en': re.compile(
        r'\b(\d+(?:[,\.]\d+)?)\s*(?:billion|million|trillion|thousand)\b', re.I),
    # Деньги
    'usd': re.compile(r'\$\s*(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|million|billion))?)', re.I),
    'eur': re.compile(r'€\s*(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|million|billion))?)', re.I),
    'rub': re.compile(r'(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тысяч))?)\s*(?:руб\.|рублей|₽)', re.I),
    # Длины
    'km': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:км|километров|km)', re.I),
    'm': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:метров|метра|м\b)', re.I),
    'cm': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:см|сантиметров|cm)', re.I),
    'mm': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:мм|миллиметров|mm)', re.I),
    'ft': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:фут|футов|ft|feet)', re.I),
    'mi': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:миль|mile|miles)', re.I),
    # Площади
    'sq_km': re.compile(r'(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:кв\.?\s*км|км²|km²|sq km)', re.I),
    'sq_m': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:кв\.?\s*м|м²|m²|sq m)', re.I),
    'ha': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:га|гектар|hectare|ha)', re.I),
    # Массы
    'kg': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:кг|килограмм|kg)', re.I),
    'g': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:грамм|грамма|г\b|gram|g\b)(?!\w)', re.I),
    't': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:тонн|тонны|ton|tons|t\b)(?!\w)', re.I),
    # Объёмы
    'l': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:литр|литра|литров|liter|litre|l\b)(?!\w)', re.I),
    'ml': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:мл|миллилитр|ml)', re.I),
    # Температура
    'celsius': re.compile(r'([+-]?\d+(?:[,\.]\d+)?)\s*(?:°C|°С|градус.{0,15}Цельс)', re.I),
    'fahrenheit': re.compile(r'([+-]?\d+(?:[,\.]\d+)?)\s*(?:°F|градус.{0,20}Фарен)', re.I),
    'kelvin': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:К\b|K\b|кельвин)', re.I),
    # Скорости
    'kmh': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:км/ч|km/h|kph)', re.I),
    'ms': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:м/с|m/s)', re.I),
    'mph': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:миль/ч|mph)', re.I),
    # Время
    'seconds': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:секунд|секунды|сек|second|sec|s\b)(?!\w)', re.I),
    'minutes': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:минут|минуты|мин|minute|min)', re.I),
    'hours': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:часов|часа|час|hour|hr)', re.I),
    'days': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:дней|дня|день|day|days)', re.I),
    'years_dur': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:лет|года|год|year|years)', re.I),
    # Электрические величины
    'volt': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:В\b|кВ|вольт|volt|V\b)(?!\w)', re.I),
    'ampere': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:А\b|мА|ампер|ampere|A\b)(?!\w)', re.I),
    'watt': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:Вт|кВт|МВт|ватт|watt|W\b)(?!\w)', re.I),
    'joule': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:Дж|джоуль|joule|J\b)(?!\w)', re.I),
    'hertz': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:Гц|кГц|МГц|hertz|Hz|kHz|MHz)', re.I),
    # Данные
    'byte': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:байт|ГБ|МБ|КБ|ТБ|byte|GB|MB|KB|TB)', re.I),
    # Координаты
    'lat': re.compile(r'(\d+(?:[.,]\d+)?)\s*°\s*(?:[NS]|с\.?\s*ш\.|ю\.?\s*ш\.)', re.I),
    'lon': re.compile(r'(\d+(?:[.,]\d+)?)\s*°\s*(?:[EW]|в\.?\s*д\.|з\.?\s*д\.)', re.I),
    # Давление
    'pascal': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:Па|паскаль|pascal|Pa)', re.I),
    'atm': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:атм|атмосфер|atmosphere|atm)', re.I),
    'bar': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:бар|bar)', re.I),
    # Астрономические
    'ly': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:св\.?\s*лет|световых?\s*лет|light.?year)', re.I),
    'au': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:а\.е\.|астрономическ.{1,15}единиц|AU)', re.I),
    'pc': re.compile(r'(\d+(?:[,\.]\d+)?)\s*(?:парсек|parsec|pc)', re.I),
}


def extract_number_with_unit(text, unit_type):
    """Извлекает число с конкретной единицей измерения"""
    pat = RE_NUMBERS_ALL.get(unit_type)
    if not pat:
        return None
    m = pat.search(text)
    if m:
        try:
            return m.group(1)
        except IndexError:
            return m.group()
    return None


def extract_all_numbers(text):
    """Извлекает все числа с единицами измерения из текста"""
    result = {}
    for unit_type, pat in RE_NUMBERS_ALL.items():
        found = pat.findall(text)
        if found:
            if isinstance(found[0], tuple):
                result[unit_type] = [''.join(f) for f in found[:3]]
            else:
                result[unit_type] = found[:3]
    return result


# БЛОК 72: Детектор языка запроса
def detect_query_language(query):
    """
    Определяет язык запроса:
    'ru' — русский, 'en' — английский, 'mixed' — смешанный.
    """
    ru_chars = len(re.findall(r'[а-яёА-ЯЁ]', query))
    en_chars = len(re.findall(r'[a-zA-Z]', query))
    total = ru_chars + en_chars
    if total == 0:
        return 'unknown'
    if ru_chars / total > 0.8:
        return 'ru'
    if en_chars / total > 0.8:
        return 'en'
    return 'mixed'


def add_language_variant(query):
    """
    Добавляет вариант запроса на другом языке для смешанных запросов.
    Помогает находить информацию на обоих языках.
    """
    lang = detect_query_language(query)
    if lang == 'ru':
        return [query, query + ' wikipedia', query + ' wikipedia ru']
    if lang == 'en':
        return [query, query + ' wikipedia', query + ' wiki']
    return [query]


# БЛОК 73: Классификатор тематики запроса (20 категорий)
QUERY_CATEGORY_PATTERNS = {
    'biography': re.compile(
        r'\b(?:кто такой|кто такая|биография|жизнь|родился|умер|born|died|biography)\b', re.I),
    'geography': re.compile(
        r'\b(?:столица|страна|город|где|население|площадь|capital|country|city|where|population)\b', re.I),
    'history': re.compile(
        r'\b(?:когда|дата|год|история|эпоха|when|year|history|era|century)\b', re.I),
    'science': re.compile(
        r'\b(?:теорема|формула|закон|открытие|theorem|formula|law|discovery|science)\b', re.I),
    'technology': re.compile(
        r'\b(?:компьютер|программа|алгоритм|software|algorithm|technology|tech|api)\b', re.I),
    'medicine': re.compile(
        r'\b(?:болезнь|лечение|симптом|препарат|disease|treatment|symptom|drug|medicine)\b', re.I),
    'economics': re.compile(
        r'\b(?:цена|деньги|экономика|ВВП|price|money|economy|GDP|cost|revenue)\b', re.I),
    'culture': re.compile(
        r'\b(?:фильм|книга|музыка|искусство|film|book|music|art|culture)\b', re.I),
    'sports': re.compile(
        r'\b(?:спорт|рекорд|чемпион|игра|sport|record|champion|game|tournament)\b', re.I),
    'nature': re.compile(
        r'\b(?:животное|растение|экология|вид|animal|plant|ecology|species|nature)\b', re.I),
    'food': re.compile(
        r'\b(?:еда|рецепт|калорий|ингредиент|food|recipe|calories|ingredient|nutrition)\b', re.I),
    'physics': re.compile(
        r'\b(?:масса|энергия|скорость|сила|частица|mass|energy|speed|force|particle|physics)\b', re.I),
    'chemistry': re.compile(
        r'\b(?:элемент|реакция|молекула|формула|element|reaction|molecule|chemistry)\b', re.I),
    'math': re.compile(
        r'\b(?:число|теорема|функция|интеграл|number|theorem|function|integral|math)\b', re.I),
    'astronomy': re.compile(
        r'\b(?:планета|звезда|орбита|галактика|planet|star|orbit|galaxy|astronomy)\b', re.I),
    'biology': re.compile(
        r'\b(?:ДНК|ген|клетка|эволюция|DNA|gene|cell|evolution|biology)\b', re.I),
    'programming': re.compile(
        r'\b(?:Python|Java|C\+\+|JavaScript|код|функция|класс|code|function|class|bug)\b', re.I),
    'law': re.compile(
        r'\b(?:закон|кодекс|статья|право|law|code|article|legal|court)\b', re.I),
    'psychology': re.compile(
        r'\b(?:психология|поведение|мотивация|psychology|behavior|motivation|cognitive)\b', re.I),
    'philosophy': re.compile(
        r'\b(?:философия|этика|смысл|бытие|philosophy|ethics|meaning|existence)\b', re.I),
}


def classify_query_category(query):
    """Классифицирует запрос по 20 категориям"""
    for cat, pat in QUERY_CATEGORY_PATTERNS.items():
        if pat.search(query):
            return cat
    return 'general'


# БЛОК 74: Расширенный TF-IDF с IDF компонентой
def calculate_idf(word, all_documents):
    """Вычисляет IDF (inverse document frequency) для слова"""
    docs_with_word = sum(1 for doc in all_documents if word in doc.lower())
    if docs_with_word == 0:
        return 0.0
    return math.log(len(all_documents) / docs_with_word)


def tfidf_vectorize(text, all_docs, max_features=50):
    """
    Строит TF-IDF вектор для текста.
    Возвращает словарь {слово: tf-idf}.
    """
    words = get_word_tokens(text)
    if not words:
        return {}
    freq = Counter(words)
    tfidf = {}
    for word, count in freq.items():
        tf = count / len(words)
        idf = calculate_idf(word, all_docs)
        tfidf[word] = tf * idf
    sorted_words = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_words[:max_features])


def cosine_similarity_tfidf(vec1, vec2):
    """Косинусная схожесть двух TF-IDF векторов"""
    all_words = set(vec1) | set(vec2)
    if not all_words:
        return 0.0
    dot = sum(vec1.get(w, 0) * vec2.get(w, 0) for w in all_words)
    mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
    return dot / (mag1 * mag2) if mag1 and mag2 else 0.0


def find_most_relevant_sentences_tfidf(text, query, n=5):
    """Находит наиболее релевантные предложения через TF-IDF"""
    sentences = remove_noise_sentences(split_into_sentences(text))
    if not sentences:
        return []
    all_docs = [query] + sentences
    query_vec = tfidf_vectorize(query, all_docs)
    scored = []
    for sent in sentences:
        sent_vec = tfidf_vectorize(sent, all_docs)
        sim = cosine_similarity_tfidf(query_vec, sent_vec)
        scored.append((sim, sent))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:n]]


# БЛОК 75: Извлечение числовых ответов
def extract_numeric_answer(web_data, query, unit_hint=None):
    """
    Специализированное извлечение числового ответа.
    Используется для вопросов типа 'сколько' / 'how many'.
    """
    combined = web_data.get('combined_text', '')
    query_words = build_query_words(query)

    # Определяем тип единицы из запроса
    if not unit_hint:
        unit_hints = {
            'км': 'km', 'километр': 'km', 'kilometer': 'km',
            'метр': 'm', 'meter': 'm',
            'кг': 'kg', 'килограмм': 'kg', 'kilogram': 'kg',
            'человек': 'large_ru', 'жителей': 'large_ru', 'населения': 'large_ru',
            'population': 'large_en', 'people': 'large_en',
            'кв.км': 'sq_km', 'площадь': 'sq_km', 'area': 'sq_km',
            'страна': 'integer', 'country': 'integer',
            'планета': 'integer', 'planet': 'integer',
            'язык': 'integer', 'language': 'integer',
            'год': 'year', 'year': 'year', 'лет': 'year',
            'градус': 'celsius', 'temperature': 'celsius',
            'км/ч': 'kmh', 'speed': 'kmh', 'скорость': 'kmh',
        }
        for hint_word, hint_type in unit_hints.items():
            if hint_word.lower() in query.lower():
                unit_hint = hint_type
                break

    # Ищем число рядом с ключевыми словами
    sentences = split_into_sentences(combined)
    best_sent = None
    best_score = 0

    for sent in sentences:
        sc = score_sentence(sent, query_words)
        has_num = bool(re.search(r'\d', sent))
        if has_num and sc > best_score:
            best_score = sc
            best_sent = sent

    if not best_sent:
        return ''

    # Извлекаем числа из лучшего предложения
    if unit_hint:
        val = extract_number_with_unit(best_sent, unit_hint)
        if val:
            return val + ' (из: ' + truncate_to_sentence(best_sent, 100) + ')'

    # Общий поиск чисел
    numbers = re.findall(r'\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тыс|million|billion|thousand))?', best_sent)
    if numbers:
        return numbers[0] + ' (из: ' + truncate_to_sentence(best_sent, 100) + ')'

    return truncate_to_sentence(best_sent, MAX_ANSWER_LEN)


# БЛОК 76: Обработчик биографических вопросов
class BiographyExtractor:
    """
    Специализированный извлекатель биографической информации.
    Работает с вопросами типа 'кто такой X'.
    """

    def __init__(self, web_data, query):
        self.web_data = web_data
        self.query = query
        self.combined = web_data.get('combined_text', '')
        self.query_words = build_query_words(query)

    def extract_birth_year(self):
        """Извлекает год рождения"""
        patterns = [
            re.compile(r'родил(?:ся|ась)\s+(?:\d+\s+\w+\s+)?(\d{4})', re.I),
            re.compile(r'\((\d{4})\s*[-–—]\s*(?:\d{4}|н\.в\.|present)', re.I),
            re.compile(r'born\s+(?:\w+\s+\d+,?\s+)?(\d{4})', re.I),
            re.compile(r'\(b\.\s*(\d{4})\)', re.I),
        ]
        for pat in patterns:
            m = pat.search(self.combined)
            if m:
                return m.group(1)
        return ''

    def extract_death_year(self):
        """Извлекает год смерти"""
        patterns = [
            re.compile(r'умер(?:ла)?\s+(?:\d+\s+\w+\s+)?(\d{4})', re.I),
            re.compile(r'скончал(?:ся|ась).{0,30}(\d{4})', re.I),
            re.compile(r'\(\d{4}\s*[-–—]\s*(\d{4})\)', re.I),
            re.compile(r'died\s+(?:\w+\s+\d+,?\s+)?(\d{4})', re.I),
            re.compile(r'\(d\.\s*(\d{4})\)', re.I),
        ]
        for pat in patterns:
            m = pat.search(self.combined)
            if m:
                return m.group(1)
        return ''

    def extract_nationality(self):
        """Извлекает национальность/гражданство"""
        patterns = [
            re.compile(
                r'(?:русский|российский|американский|британский|немецкий|французский|'
                r'итальянский|испанский|китайский|японский)\s+(?:учёный|физик|математик|'
                r'писатель|художник|политик|президент|генерал)', re.I),
            re.compile(
                r'(?:Russian|American|British|German|French|Italian|Spanish|Chinese|Japanese)\s+'
                r'(?:scientist|physicist|mathematician|writer|artist|politician)', re.I),
        ]
        for pat in patterns:
            m = pat.search(self.combined)
            if m:
                return m.group()
        return ''

    def extract_profession(self):
        """Извлекает профессию"""
        prof_words = [
            'физик', 'математик', 'химик', 'биолог', 'астроном', 'инженер',
            'программист', 'писатель', 'поэт', 'художник', 'композитор',
            'режиссёр', 'актёр', 'актриса', 'политик', 'президент', 'учёный',
            'изобретатель', 'предприниматель', 'философ', 'историк',
            'physicist', 'mathematician', 'chemist', 'biologist', 'astronomer',
            'engineer', 'programmer', 'writer', 'poet', 'artist', 'composer',
            'director', 'actor', 'actress', 'politician', 'president',
            'scientist', 'inventor', 'entrepreneur', 'philosopher', 'historian',
        ]
        text_lower = self.combined.lower()
        for prof in prof_words:
            if prof.lower() in text_lower:
                # Ищем предложение с профессией
                for sent in split_into_sentences(self.combined):
                    if prof.lower() in sent.lower():
                        return truncate_to_sentence(sent, 200)
        return ''

    def extract_main_achievement(self):
        """Извлекает главное достижение"""
        achiev_patterns = [
            re.compile(r'(?:известен|известна|прославился|прославилась|знаменит).{0,100}', re.I),
            re.compile(r'(?:открыл|изобрёл|создал|написал|разработал).{0,100}', re.I),
            re.compile(r'(?:known for|famous for|best known|discovered|invented|created).{0,100}', re.I),
        ]
        for pat in achiev_patterns:
            m = pat.search(self.combined)
            if m:
                return truncate_to_sentence(m.group(), 200)
        return ''

    def build_bio_answer(self):
        """Строит биографический ответ"""
        birth = self.extract_birth_year()
        death = self.extract_death_year()
        prof = self.extract_profession()
        achiev = self.extract_main_achievement()

        parts = []
        if prof:
            parts.append(prof[:150])
        if birth:
            span = f"({birth}" + (f"—{death}" if death else '') + ")"
            parts.append(span)
        if achiev and achiev not in ' '.join(parts):
            parts.append(achiev[:150])

        if not parts:
            return AnswerProcessor(self.web_data, self.query, 'who').process()

        return ' '.join(parts)


# БЛОК 77: Обработчик географических вопросов
class GeographyExtractor:
    """
    Специализированный извлекатель географической информации.
    Работает с вопросами о столицах, населении, площади.
    """

    def __init__(self, web_data, query):
        self.web_data = web_data
        self.query = query
        self.combined = web_data.get('combined_text', '')

    def extract_capital(self):
        """Извлекает столицу"""
        patterns = [
            re.compile(r'столица.{0,10}[-—:]\s*([А-ЯЁ][а-яё]+)', re.I),
            re.compile(r'столицей\s+является\s+([А-ЯЁ][а-яё]+)', re.I),
            re.compile(r'capital\s+(?:is|city)\s+([A-Z][a-z]+)', re.I),
            re.compile(r'([A-Z][a-z]+)\s+is\s+the\s+capital', re.I),
        ]
        for pat in patterns:
            m = pat.search(self.combined)
            if m:
                return m.group(1)
        return ''

    def extract_population(self):
        """Извлекает численность населения"""
        pats = [
            re.compile(
                r'население\s*[-:—]?\s*(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тыс))?)', re.I),
            re.compile(
                r'population\s*(?:of\s*)?(?:is\s*)?(\d+(?:[,\.]\d+)?(?:\s*(?:million|billion|thousand))?)', re.I),
            re.compile(
                r'(\d+(?:[,\.]\d+)?(?:\s*(?:млн|млрд|тысяч|million|billion|thousand))?)\s*(?:человек|жителей|inhabitants|people)', re.I),
        ]
        for pat in pats:
            m = pat.search(self.combined)
            if m:
                return m.group(1).strip()
        return ''

    def extract_area(self):
        """Извлекает площадь"""
        pats = [
            re.compile(r'площадь\s*[-:—]?\s*(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:кв\.?\s*км|км²)', re.I),
            re.compile(r'area\s*(?:of\s*)?(?:is\s*)?(\d+(?:[,\.]\d+)?)\s*(?:sq\.?\s*km|km²)', re.I),
        ]
        for pat in pats:
            m = pat.search(self.combined)
            if m:
                return m.group(1).strip() + ' км²'
        return ''

    def build_geo_answer(self):
        """Строит географический ответ"""
        q_lower = self.query.lower()
        if any(w in q_lower for w in ['столица', 'capital']):
            capital = self.extract_capital()
            if capital:
                return capital
        if any(w in q_lower for w in ['население', 'population', 'жителей', 'человек']):
            pop = self.extract_population()
            if pop:
                return pop + ' человек'
        if any(w in q_lower for w in ['площадь', 'area', 'территория']):
            area = self.extract_area()
            if area:
                return area
        return AnswerProcessor(self.web_data, self.query, 'where').process()


# БЛОК 78: Расширенная функция ask() для разных сценариев
def ask_with_category(query, verbose=True):
    """
    ask() с автоматическим определением категории и специализированным извлечением.
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    math_r = calculate_simple(query)
    if math_r:
        init_output_file()
        save_to_file(format_report(query, math_r, [], "math", 0))
        if verbose:
            print(f"[Math] {math_r}")
        return math_r

    cached = _GLOBAL_CACHE.get(query)
    if cached:
        if verbose:
            print(f"[Cache] {cached}")
        return cached

    init_output_file()
    t0 = time.time()

    category = classify_query_category(query)
    q_type = determine_question_type_v2(query)

    if verbose:
        print(f"[AI] Категория: {category} | Тип: {q_type}")

    expanded = expand_query_v2(query)
    web_data = collect_web_texts_robust(expanded, verbose=verbose)

    if not web_data["results"]:
        return "Нет подключения к интернету."

    # Специализированные извлекатели
    answer = ''
    if category == 'biography' or q_type == 'who':
        bio = BiographyExtractor(web_data, query)
        answer = bio.build_bio_answer()

    if not answer and (category == 'geography' or q_type in ('where', 'how_many')):
        geo = GeographyExtractor(web_data, query)
        answer = geo.build_geo_answer()

    if not answer:
        answer = extract_answer_full(web_data, query, q_type)

    answer = postprocess_answer(answer, query)

    if not answer or len(answer) < 15:
        answer = "Не удалось найти точный ответ."

    sources = get_source_links(web_data, max_links=3)
    report = format_report(query, answer, sources, q_type, web_data["sources_count"])
    save_to_file(report)
    _GLOBAL_CACHE.set(query, answer)

    elapsed = time.time() - t0
    if verbose:
        print(f"\n{'='*60}")
        print(f"ОТВЕТ:\n{answer}")
        print(f"{'='*60}")
        print(f"Время: {elapsed:.1f}с | Источников: {web_data['sources_count']}")
        print(f"Сохранено: {OUTPUT_FILE}")

    return answer


# БЛОК 79: Дополнительные паттерны НЕ-ответов
NOT_ANSWER_PATTERNS = [
    re.compile(r'^(?:нет|нету|нельзя|невозможно|неизвестно)$', re.I),
    re.compile(r'^(?:yes|no|maybe|perhaps|possibly)$', re.I),
    re.compile(r'^(?:да|нет|возможно|наверное|вероятно)$', re.I),
    re.compile(r'^\d+$'),
    re.compile(r'^https?://\S+$'),
    re.compile(r'^\W+$'),
    re.compile(r'^.{1,5}$'),
]


def is_valid_answer_text(text):
    """Проверяет, является ли текст валидным ответом"""
    if not text or not text.strip():
        return False
    t = text.strip()
    for pat in NOT_ANSWER_PATTERNS:
        if pat.match(t):
            return False
    words = t.split()
    if len(words) < 3:
        return False
    if len(t) < 20:
        return False
    return True


def filter_invalid_answers(candidates):
    """Фильтрует невалидные ответы из списка кандидатов"""
    return [a for a in candidates if is_valid_answer_text(a)]


# БЛОК 80: Итоговая документация и экспорт
__version__ = "3.0.0"
__author__ = "AI Search System"
__description__ = (
    "Система умного поиска ответов в интернете. "
    "Искал ← в Интернете → обработал → короткий ответ → main.txt"
)

__all__ = [
    # Главные функции
    'ask', 'ask_v2', 'ask_smart_v2', 'ask_cached', 'ask_iterative',
    'ask_batch', 'ask_from_file', 'ask_with_category',
    # Поиск
    'search_links', 'fetch_page', 'collect_web_texts',
    'collect_web_texts_robust', 'multi_search',
    # Извлечение
    'extract_answer_full', 'extract_answer_ultra',
    'extract_with_tfidf', 'extract_with_context_window',
    'extract_with_mmr', 'extract_with_bm25', 'extract_with_stemming',
    'extract_from_best_sources',
    # Классы
    'AnswerProcessor', 'BiographyExtractor', 'GeographyExtractor',
    'FullAnalysisPipeline', 'IterativeSearcher', 'QueryCache',
    'RateLimiter', 'SessionStats', 'AIConfig',
    # Утилиты
    'determine_question_type_v2', 'expand_query_v2',
    'classify_query_category', 'calculate_simple', 'convert_units',
    'get_constant', 'extract_entities', 'extract_fact',
    'extract_all_facts', 'extract_measurements', 'extract_all_numbers',
    'analyze_sentiment', 'estimate_answer_quality', 'validate_answer',
    'postprocess_answer', 'format_report', 'save_to_file',
    # Оценка
    'evaluate_classifier_full', 'run_demo', 'show_help',
    # Конфигурация
    '_CONFIG', '_GLOBAL_CACHE', '_RATE_LIMITER', '_SESSION',
    # Константы
    'OUTPUT_FILE', 'MAX_SITES', 'MAX_ANSWER_LEN', 'PHYSICS_CONSTANTS',
    'ALL_STOP_WORDS', 'PREMIUM_DOMAINS', 'QUESTION_SYNONYMS',
    'FACT_EXTRACTION_PATTERNS', 'STRUCTURED_PATTERNS',
    'SOURCE_QUALITY_RULES', 'TRAINING_EXAMPLES_FULL',
]


def get_version():
    """Возвращает версию AI"""
    return __version__


def get_capabilities():
    """Описывает возможности системы"""
    return {
        "version": __version__,
        "search_engines": ["DuckDuckGo", "Bing"],
        "max_sources": MAX_SITES,
        "question_types": list(QUESTION_SYNONYMS.keys()),
        "extraction_algorithms": [
            "AnswerProcessor (specialized by question type)",
            "TF-IDF sentence scoring",
            "Sliding context window",
            "Maximal Marginal Relevance (MMR)",
            "BM25 ranking",
            "Morphological stemming",
            "Best-source priority extraction",
        ],
        "nlp_features": [
            "Multi-lingual stop words (19 languages)",
            "Named Entity Recognition (8 types)",
            "Fact extraction (100+ fact types)",
            "Sentiment analysis",
            "Deduplication (Jaccard + cosine)",
            "Levenshtein distance fuzzy matching",
            "Russian morphological stemming",
        ],
        "output_formats": ["plain text", "markdown", "json", "csv"],
        "cache": "JSON file with TTL",
        "output_file": OUTPUT_FILE,
        "languages": ["Russian", "English", "Mixed"],
    }




# =================================================================================
# БЛОК 81-90: РАСШИРЕННЫЕ NLP-ФУНКЦИИ И АНАЛИТИКА
# =================================================================================

# БЛОК 81: Окно контекста для поиска ответа
def extract_sentences_around_keyword(text, keyword, window=2):
    """
    Возвращает предложения вокруг ключевого слова (±window предложений).
    Полезно для получения контекста.
    """
    sentences = split_into_sentences(text)
    results = []
    kw_lower = keyword.lower()
    for i, sent in enumerate(sentences):
        if kw_lower in sent.lower():
            start = max(0, i - window)
            end = min(len(sentences), i + window + 1)
            context = ' '.join(sentences[start:end])
            if context not in results:
                results.append(context)
    return results[:3]


def extract_definition_pattern(text, subject):
    """
    Ищет определение субъекта в тексте.
    Паттерны: "X — это Y", "X является Y", "X: Y".
    """
    subj_esc = re.escape(subject)
    patterns = [
        re.compile(subj_esc + r'\s*[-—–:]\s*(.{20,200}?)(?:[.!?]|$)', re.I),
        re.compile(subj_esc + r'\s+(?:является|это|есть|представляет собой)\s+(.{20,200}?)(?:[.!?]|$)', re.I),
        re.compile(subj_esc + r',?\s+(?:which is|is a|is an|is the)\s+(.{20,200}?)(?:[.!?]|$)', re.I),
        re.compile(r'(?:понятие|термин|слово)\s+[«"]?' + subj_esc + r'[»"]?\s+(?:означает|значит)\s+(.{20,200}?)(?:[.!?]|$)', re.I),
    ]
    for pat in patterns:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return ''


def find_first_paragraph(text):
    """Возвращает первый значимый абзац текста (не менее 100 символов)"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    for para in paragraphs:
        if len(para) >= 100:
            return para[:500]
    return text[:500] if text else ''


# БЛОК 82: Нормализация числового ответа
def normalize_number_str(num_str):
    """
    Нормализует строку с числом.
    "1,234,567" → "1234567", "3.14" → "3.14"
    """
    # Убираем пробелы внутри числа
    num_str = re.sub(r'(\d)\s(\d)', r'\1\2', num_str)
    # Убираем запятые как разделители тысяч (1,234 → 1234)
    if re.match(r'^\d{1,3}(,\d{3})+$', num_str):
        num_str = num_str.replace(',', '')
    return num_str.strip()


def format_number_human(num):
    """Форматирует большое число в читаемый вид"""
    try:
        n = float(str(num).replace(',', '.').replace(' ', ''))
        if n >= 1e12:
            return f"{n/1e12:.2g} триллиона"
        if n >= 1e9:
            return f"{n/1e9:.2g} миллиарда"
        if n >= 1e6:
            return f"{n/1e6:.2g} миллиона"
        if n >= 1e3:
            return f"{n/1e3:.2g} тысяч"
        return str(n)
    except Exception:
        return str(num)


# БЛОК 83: Словарь "вопрос → суффикс ответа"
ANSWER_SUFFIXES = {
    'population': 'человек',
    'area': 'км²',
    'height': 'метров',
    'length': 'км',
    'depth': 'метров',
    'speed': 'км/ч',
    'weight': 'кг',
    'temperature': '°C',
    'distance': 'км',
    'age': 'лет',
    'count': 'штук',
    'year': 'год',
    'duration': 'лет',
    'price': 'рублей',
}


def add_answer_suffix(value, suffix_key):
    """Добавляет единицу к числовому ответу"""
    suffix = ANSWER_SUFFIXES.get(suffix_key, '')
    if suffix and not any(s in str(value).lower() for s in ['км', 'м²', 'чел', 'год', 'кг', 'лет']):
        return f"{value} {suffix}"
    return str(value)


# БЛОК 84: Дополнительные методы очистки текста
def remove_urls_from_text(text):
    """Удаляет URL из текста"""
    return re.sub(r'https?://\S+|www\.\S+', '', text)


def remove_emails_from_text(text):
    """Удаляет email-адреса из текста"""
    return re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', '', text)


def remove_phone_numbers(text):
    """Удаляет номера телефонов"""
    return re.sub(r'(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}', '', text)


def remove_special_chars(text, keep='.,!?:-()'):
    """Убирает спецсимволы кроме указанных"""
    pattern = f'[^а-яёА-ЯЁa-zA-Z0-9\\s{re.escape(keep)}]'
    return re.sub(pattern, ' ', text)


def collapse_whitespace(text):
    """Сжимает множественные пробелы в один"""
    return re.sub(r'\s+', ' ', text).strip()


def remove_repeated_words(text):
    """Убирает подряд идущие повторяющиеся слова"""
    return re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.I)


def fix_sentence_case(text):
    """Исправляет заглавные буквы в начале предложений"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return ' '.join(s[0].upper() + s[1:] if s else '' for s in sentences)


def strip_leading_punctuation(text):
    """Убирает начальную пунктуацию"""
    return re.sub(r'^[.,;:!?\-–—\s]+', '', text).strip()


def ensure_sentence_end(text):
    """Убеждается что текст заканчивается на точку"""
    text = text.strip()
    if text and text[-1] not in '.!?…':
        text += '.'
    return text


# БЛОК 85: Извлечение числовых ответов для "сколько" вопросов
_HOW_MANY_CONTEXT_PATTERNS = [
    # население
    re.compile(r'(?:население|population|жителей|inhabitants?)\s*[-:—]?\s*(\d+(?:[,\.]\s*\d+)?(?:\s*(?:млн|млрд|тыс|million|billion|thousand))?)', re.I),
    # площадь
    re.compile(r'(?:площадь|area|territory)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:кв\.?\s*км|km²|sq\.?\s*km)?', re.I),
    # высота
    re.compile(r'(?:высота|height|altitude)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?)\s*(?:метров|м|m\b|feet|ft)?', re.I),
    # глубина
    re.compile(r'(?:глубина|depth)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?)\s*(?:метров|м|m\b)?', re.I),
    # длина
    re.compile(r'(?:длина|протяжённость|length)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?)\s*(?:км|m\b|km\b)?', re.I),
    # скорость
    re.compile(r'(?:скорость|speed|velocity)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?)\s*(?:км/ч|mph|m/s|м/с)?', re.I),
    # температура
    re.compile(r'(?:температура|temperature)\s*[-:—]?\s*([+-]?\d+(?:[,\.]\d+)?)\s*(?:°C|°F|°К|K)?', re.I),
    # расстояние
    re.compile(r'(?:расстояние|distance)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:км|km|световых?\s*лет|light.?years?)?', re.I),
    # количество
    re.compile(r'(?:количество|число|count|number)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?)', re.I),
    # вес
    re.compile(r'(?:вес|масса|weight|mass)\s*[-:—]?\s*(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:кг|т\b|kg|tons?)?', re.I),
]


def extract_numeric_answer_v2(web_data, query):
    """
    Версия 2 извлечения числового ответа — использует контекстные паттерны.
    """
    combined = web_data.get('combined_text', '')
    query_words = build_query_words(query)

    # Пробуем контекстные паттерны
    for pat in _HOW_MANY_CONTEXT_PATTERNS:
        # Ищем во всём тексте
        m = pat.search(combined)
        if m:
            val = m.group(1).strip()
            # Контекст вокруг
            ctx_start = max(0, m.start() - 60)
            ctx_end = min(len(combined), m.end() + 60)
            context = combined[ctx_start:ctx_end].strip()
            return truncate_to_sentence(context, MAX_ANSWER_LEN)

    # Ищем предложение с числом + словами из запроса
    for src in web_data.get('results', []):
        sentences = split_into_sentences(src['text'])
        for sent in sentences:
            if re.search(r'\d', sent):
                sc = score_sentence(sent, query_words)
                if sc > 3:
                    return truncate_to_sentence(sent, MAX_ANSWER_LEN)

    return ''


# БЛОК 86: Кросс-валидация ответов из разных источников
def cross_validate_answers(candidates, query, min_overlap=2):
    """
    Проверяет согласованность ответов из разных источников.
    Возвращает ответ с наибольшим пересечением слов с другими.
    """
    if not candidates:
        return ''
    if len(candidates) == 1:
        return candidates[0]

    query_words = build_query_words(query)
    scored = []

    for i, cand in enumerate(candidates):
        cand_words = set(get_word_tokens(cand))
        # Сходство с запросом
        query_sim = len(cand_words & query_words)
        # Сходство с другими кандидатами
        cross_sim = 0
        for j, other in enumerate(candidates):
            if i == j:
                continue
            other_words = set(get_word_tokens(other))
            cross_sim += len(cand_words & other_words)
        total = query_sim * 2 + cross_sim
        scored.append((total, cand))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else ''


# БЛОК 87: Суммаризация по абзацам
def extractive_summarize(text, n_sentences=3):
    """
    Extractive summarization: выбирает n лучших предложений из текста.
    Не использует нейросети — только статистику.
    """
    sentences = remove_noise_sentences(split_into_sentences(text))
    if not sentences:
        return ''

    # TF по всему тексту
    all_words = get_word_tokens(text)
    tf = Counter(all_words)
    total = max(len(all_words), 1)

    # Оцениваем предложения
    scored = []
    for sent in sentences:
        words = get_word_tokens(sent)
        if not words:
            continue
        score = sum(tf.get(w, 0) / total for w in words) / len(words)
        # Бонус за позицию (начало текста важнее)
        idx = sentences.index(sent)
        position_bonus = 1.0 / (1 + idx * 0.1)
        # Бонус за оптимальную длину
        length_score = min(1.0, len(words) / 20) if len(words) < 50 else max(0.5, 50 / len(words))
        scored.append((score * position_bonus * length_score, sent))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_n = [s for _, s in scored[:n_sentences]]

    # Возвращаем в оригинальном порядке
    ordered = [s for s in sentences if s in top_n]
    return ' '.join(ordered)


def summarize_web_results(web_data, n=3):
    """Суммаризация всех найденных веб-страниц"""
    summaries = []
    for src in rank_sources_by_quality(web_data.get('results', []))[:5]:
        summary = extractive_summarize(src['text'], n_sentences=2)
        if summary and len(summary) > 50:
            summaries.append(summary)

    if not summaries:
        return ''

    combined = ' '.join(summaries[:n])
    return truncate_to_sentence(combined, MAX_ANSWER_LEN)


# БЛОК 88: Детектор неопределённых ответов
UNCERTAINTY_PHRASES = {
    'ru': ['неизвестно', 'неясно', 'нет данных', 'данные отсутствуют',
           'не установлено', 'спорно', 'под вопросом', 'точно неизвестно',
           'сложно сказать', 'трудно определить', 'данные разнятся'],
    'en': ['unknown', 'unclear', 'no data', 'data unavailable',
           'not established', 'disputed', 'questionable', 'uncertain',
           'hard to say', 'difficult to determine', 'data varies'],
}

_UNCERTAINTY_RE = re.compile(
    '|'.join(re.escape(p) for p in
             UNCERTAINTY_PHRASES['ru'] + UNCERTAINTY_PHRASES['en']),
    re.I
)


def contains_uncertainty(text):
    """Проверяет, содержит ли ответ выражения неопределённости"""
    return bool(_UNCERTAINTY_RE.search(text))


def enhance_uncertain_answer(answer, web_data, query):
    """
    Если ответ неопределённый, пытается найти более точный вариант.
    """
    if not contains_uncertainty(answer):
        return answer

    # Пробуем другие методы
    alternatives = [
        extract_with_bm25(web_data, query, top_n=2),
        extract_with_stemming(web_data, query, top_n=2),
        build_summary_from_multiple_sources(web_data, query),
    ]
    alternatives = filter_invalid_answers(alternatives)
    if alternatives:
        best = max(alternatives, key=lambda a: estimate_answer_quality(a, query))
        if not contains_uncertainty(best) and len(best) >= 20:
            return best

    return answer


# БЛОК 89: Обогащение ответа сущностями
def enrich_answer_with_entities(answer, web_data):
    """
    Добавляет найденные даты/числа к ответу, если их нет в исходном тексте.
    """
    combined = web_data.get('combined_text', '')

    # Ищем числа и даты
    dates = extract_entities(combined, 'date')[:2]
    numbers = extract_entities(combined, 'number')[:2]

    # Проверяем что в ответе нет чисел
    has_num = bool(re.search(r'\d', answer))
    if not has_num:
        if dates:
            answer += f" ({', '.join(dates[:1])})"
        elif numbers:
            answer += f" (~{numbers[0]})"

    return answer


# БЛОК 90: Многоязычный поиск
def search_bilingual(query, verbose=False):
    """
    Поиск на двух языках: русском и английском.
    Объединяет результаты для лучшего охвата.
    """
    lang = detect_query_language(query)
    queries_to_run = [query]

    # Упрощённые переводы часто используемых фраз
    RU_TO_EN = {
        'что такое': 'what is',
        'кто такой': 'who is',
        'кто такая': 'who is',
        'когда родился': 'born in',
        'когда умер': 'died in',
        'столица': 'capital of',
        'население': 'population',
        'площадь': 'area',
        'высота': 'height',
        'длина': 'length',
        'глубина': 'depth',
        'скорость': 'speed',
    }

    if lang == 'ru':
        q_lower = query.lower()
        for ru_phrase, en_phrase in RU_TO_EN.items():
            if ru_phrase in q_lower:
                en_query = q_lower.replace(ru_phrase, en_phrase)
                if en_query != q_lower:
                    queries_to_run.append(en_query)
                    break

    all_results = []
    seen_urls = set()

    for q in queries_to_run[:2]:
        if verbose:
            print(f"[BiSearch] {q}")
        data = collect_web_texts(q, verbose=False)
        for src in data.get('results', []):
            if src['url'] not in seen_urls:
                seen_urls.add(src['url'])
                all_results.append(src)

    combined = ' '.join(r['text'] for r in all_results)
    return {
        'query': query,
        'links': list(seen_urls),
        'results': all_results,
        'combined_text': combined,
        'sources_count': len(all_results),
    }


def ask_bilingual(query, verbose=True):
    """
    Двуязычный поиск: даёт лучшие результаты для международных тем.
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    math_r = calculate_simple(query)
    if math_r:
        init_output_file()
        save_to_file(format_report(query, math_r, [], "math", 0))
        if verbose:
            print(f"[Math] {math_r}")
        return math_r

    cached = _GLOBAL_CACHE.get(query)
    if cached:
        if verbose:
            print(f"[Cache] {cached}")
        return cached

    init_output_file()
    web_data = search_bilingual(query, verbose=verbose)

    if not web_data["results"]:
        return "Нет подключения к интернету."

    q_type = determine_question_type_v2(query)
    answer = extract_answer_ultra(web_data, query, q_type)
    answer = postprocess_answer(answer, query)

    if not answer or len(answer) < 15:
        answer = "Не удалось найти точный ответ."

    sources = get_source_links(web_data, max_links=3)
    report = format_report(query, answer, sources, q_type, web_data["sources_count"])
    save_to_file(report)
    _GLOBAL_CACHE.set(query, answer)

    if verbose:
        print(f"\nОТВЕТ:\n{answer}")
        print(f"Сохранено: {OUTPUT_FILE}")

    return answer


# =================================================================================
# БЛОК 91-100: ПРОДВИНУТЫЕ УТИЛИТЫ И ФИНАЛЬНАЯ СБОРКА
# =================================================================================

# БЛОК 91: Система ротации User-Agent
USER_AGENTS_EXTENDED = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) '
    'Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 '
    '(KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 '
    '(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Android 14; Mobile; rv:109.0) '
    'Gecko/121.0 Firefox/121.0',
    'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 '
    '(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) '
    'Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
]

ACCEPT_LANGUAGES_POOL = [
    'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'en-US,en;q=0.9,ru;q=0.8',
    'ru-RU,ru;q=0.8,en;q=0.6',
    'en-GB,en;q=0.9',
    'de-DE,de;q=0.9,en;q=0.8',
    'fr-FR,fr;q=0.9,en;q=0.8',
]


def get_random_headers_extended():
    """Возвращает случайные расширенные HTTP-заголовки"""
    import random as _r
    ua = _r.choice(USER_AGENTS_EXTENDED)
    lang = _r.choice(ACCEPT_LANGUAGES_POOL)
    return {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': lang,
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }


# БЛОК 92: Дополнительная документация

# Руководство по расширению AI (для разработчиков):
# 
# 1. Добавить новый тип вопроса:
#    - Добавить в QUESTION_SYNONYMS['new_type'] = [список фраз]
#    - Добавить в ANSWER_INDICATORS['new_type'] = [индикаторы]
#    - Обновить AnswerProcessor.process()
#
# 2. Добавить новый тип факта:
#    - Добавить в _FACT_TEMPLATES = [..., ('new_fact', ['ключевые слова'])]
#    - FACT_EXTRACTION_PATTERNS обновится автоматически
#
# 3. Добавить новый алгоритм извлечения:
#    - Написать функцию extract_with_new_algo(web_data, query)
#    - Добавить вызов в extract_answer_ultra() или ask_smart_v2()
#
# 4. Добавить новый источник поиска:
#    - В search.py: добавить функцию search_new_engine()
#    - В collect_web_texts(): добавить вызов новой функции
#
# 5. Улучшить оценку качества:
#    - Обновить estimate_answer_quality() — добавить новые критерии
#    - Обновить validate_answer() — добавить новые проверки
#
# 6. Добавить поддержку нового языка:
#    - Добавить стоп-слова в MULTILINGUAL_STOP_WORDS['xx']
#    - Добавить правила стемматизации
#    - Добавить переводы в RU_TO_EN (search_bilingual)


# БЛОК 93: Расширенные настройки по умолчанию
DEFAULT_SETTINGS = {
    'max_sites': 10,
    'request_timeout': 10,
    'sleep_between': 0.3,
    'max_text_len': 50000,
    'min_text_len': 100,
    'max_answer_len': 600,
    'min_sentence_len': 20,
    'max_sentence_len': 600,
    'top_sentences': 7,
    'output_file': 'main.txt',
    'cache_ttl_hours': 24,
    'rate_limit_per_min': 10,
    'retry_count': 2,
    'retry_backoff': 2.0,
    'use_cache': True,
    'use_rate_limit': True,
    'verbose': True,
    'multi_search': False,
    'save_json': False,
    'save_markdown': False,
    'prefer_premium_domains': True,
    'min_answer_quality': 0.2,
    'answer_lang': 'auto',
    'search_lang': 'auto',
    'extraction_algorithms': ['tfidf', 'window', 'mmr', 'bm25', 'stem'],
}


def get_setting(key, default=None):
    """Возвращает значение настройки"""
    return DEFAULT_SETTINGS.get(key, default)


def update_setting(key, value):
    """Обновляет значение настройки"""
    if key in DEFAULT_SETTINGS:
        DEFAULT_SETTINGS[key] = value
        # Обновляем глобальные константы при необходимости
        global MAX_SITES, REQUEST_TIMEOUT, SLEEP_BETWEEN, OUTPUT_FILE
        if key == 'max_sites':
            MAX_SITES = value
        elif key == 'request_timeout':
            REQUEST_TIMEOUT = value
        elif key == 'sleep_between':
            SLEEP_BETWEEN = value
        elif key == 'output_file':
            OUTPUT_FILE = value
        return True
    return False


# БЛОК 94: Хелперы для форматирования ответов
def add_source_hint(answer, sources):
    """Добавляет подсказку об источнике к ответу"""
    if not sources:
        return answer
    domain = urlparse(sources[0]).netloc.replace('www.', '')
    return f"{answer} [Источник: {domain}]"


def format_answer_with_sources(answer, sources, include_urls=False):
    """Форматирует ответ с красивым списком источников"""
    lines = [answer, '']
    if sources:
        lines.append('Источники:')
        for i, src in enumerate(sources[:3], 1):
            domain = urlparse(src).netloc.replace('www.', '')
            if include_urls:
                lines.append(f'  {i}. {domain} ({src})')
            else:
                lines.append(f'  {i}. {domain}')
    return '\n'.join(lines)


def format_batch_report(results):
    """Форматирует отчёт по пакетному запросу"""
    lines = [f"Пакетный запрос: {len(results)} вопросов", '=' * 60]
    for i, r in enumerate(results, 1):
        lines.append(f"\n{i}. {r.get('query', '?')}")
        lines.append(f"   Ответ: {r.get('answer', '?')[:200]}")
        lines.append(f"   Тип: {r.get('q_type', '?')} | "
                     f"Время: {r.get('elapsed', 0):.1f}с")
    lines.append('\n' + '=' * 60)
    return '\n'.join(lines)


# БЛОК 95: Мониторинг производительности
import functools


def timed(func):
    """Декоратор: замеряет время выполнения функции"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        if elapsed > 1.0:
            print(f"[Timing] {func.__name__}: {elapsed:.2f}с")
        return result
    return wrapper


def memoize(func):
    """Декоратор: кэширует результаты вызовов функции"""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper


@memoize
def get_domain_quality_cached(url):
    """Кэшированная версия get_domain_quality"""
    return get_domain_quality(url)


# БЛОК 96: Продвинутая интеграция всех алгоритмов
def ensemble_extract(web_data, query, q_type=None, verbose=False):
    """
    Ансамблевый метод: взвешенное голосование из 7 алгоритмов.
    Каждый алгоритм получает вес в зависимости от надёжности источников.
    """
    if not q_type:
        q_type = determine_question_type_v2(query)

    algorithms = {
        'processor': (AnswerProcessor(web_data, query, q_type).process, 2.0),
        'best_sources': (lambda: extract_from_best_sources(web_data, query, q_type), 2.5),
        'tfidf': (lambda: extract_with_tfidf(web_data, query, top_n=3), 1.5),
        'window': (lambda: extract_with_context_window(web_data, query), 1.0),
        'mmr': (lambda: extract_with_mmr(web_data, query, top_n=3), 1.5),
        'bm25': (lambda: extract_with_bm25(web_data, query, top_n=3), 1.5),
        'stem': (lambda: extract_with_stemming(web_data, query, top_n=3), 1.0),
    }

    # Запускаем все алгоритмы
    results = {}
    for name, (fn, weight) in algorithms.items():
        try:
            result = fn()
            if result and len(result) >= 15:
                quality = estimate_answer_quality(result, query)
                results[name] = {
                    'answer': result,
                    'quality': quality,
                    'weight': weight,
                    'score': quality * weight,
                }
                if verbose:
                    print(f"  [{name}] q={quality:.2f} → {result[:60]}...")
        except Exception as e:
            if verbose:
                print(f"  [{name}] ERROR: {e}")

    if not results:
        return ''

    # Взвешенный выбор
    best = max(results.values(), key=lambda r: r['score'])
    return best['answer']


def ask_ensemble(query, verbose=True):
    """
    Ансамблевый поиск — самый точный метод.
    Запускает все 7 алгоритмов и выбирает лучший результат.
    """
    query = query.strip()
    if not query:
        return "Задайте вопрос!"

    math_r = calculate_simple(query)
    if math_r:
        init_output_file()
        save_to_file(format_report(query, math_r, [], "math", 0))
        if verbose:
            print(f"[Math] {math_r}")
        return math_r

    cached = _GLOBAL_CACHE.get(query)
    if cached:
        if verbose:
            print(f"[Cache] {cached}")
        return cached

    init_output_file()
    t0 = time.time()

    expanded = expand_query_v2(query)
    web_data = collect_web_texts_robust(expanded, verbose=verbose)

    if not web_data["results"]:
        return "Нет подключения к интернету."

    q_type = determine_question_type_v2(query)
    if verbose:
        print(f"[AI] Тип: {q_type} | Запускаю ансамбль 7 алгоритмов...")

    answer = ensemble_extract(web_data, query, q_type, verbose=verbose)
    answer = postprocess_answer(answer, query)

    if not answer or len(answer) < 15:
        answer = "Не удалось найти точный ответ."

    sources = get_source_links(web_data, max_links=3)
    report = format_report(query, answer, sources, q_type, web_data["sources_count"])
    save_to_file(report)
    _GLOBAL_CACHE.set(query, answer)

    elapsed = time.time() - t0
    if verbose:
        print(f"\n{'='*60}")
        print(f"ОТВЕТ:\n{answer}")
        print(f"{'='*60}")
        print(f"Время: {elapsed:.1f}с | Источников: {web_data['sources_count']}")
        print(f"Сохранено: {OUTPUT_FILE}")

    return answer


# БЛОК 97: Обработка ошибок и диагностика
class AIError(Exception):
    """Базовое исключение AI"""
    pass


class NetworkError(AIError):
    """Ошибка сети"""
    pass


class ExtractionError(AIError):
    """Ошибка извлечения ответа"""
    pass


class ValidationError(AIError):
    """Ошибка валидации"""
    pass


def diagnose_system():
    """
    Диагностика системы: проверяет все компоненты.
    Выводит статус каждого компонента.
    """
    print("\n=== Диагностика AI System ===")
    print(f"Версия: {__version__}")
    print(f"Выходной файл: {OUTPUT_FILE}")
    print(f"Кэш: {_GLOBAL_CACHE.size()} записей")
    print(f"Настройки: {len(DEFAULT_SETTINGS)} параметров")

    # Проверка зависимостей
    deps = ['requests', 'bs4', 're', 'math', 'time', 'os', 'sys',
            'collections', 'hashlib', 'json', 'datetime', 'functools']
    print("\nЗависимости:")
    for dep in deps:
        try:
            __import__(dep)
            print(f"  [OK] {dep}")
        except ImportError:
            print(f"  [FAIL] {dep} — не установлен! pip install {dep}")

    # Проверка сети
    print("\nСеть:")
    try:
        test_resp = requests.get('https://duckduckgo.com', timeout=5)
        print(f"  [OK] DuckDuckGo ({test_resp.status_code})")
    except Exception as e:
        print(f"  [FAIL] DuckDuckGo: {e}")

    # Проверка файловой системы
    print("\nФайловая система:")
    try:
        init_output_file()
        print(f"  [OK] {OUTPUT_FILE} доступен")
    except Exception as e:
        print(f"  [FAIL] {OUTPUT_FILE}: {e}")

    print("\n=== Диагностика завершена ===\n")


# БЛОК 98: Быстрые алиасы
search = ask_smart_v2
quick_ask = ask_v2
deep_ask = ask_ensemble
smart_ask = ask_smart_v2
fast_ask = ask_cached


def q(query):
    """Короткий алиас: q("вопрос") → ответ"""
    return ask_smart_v2(query, verbose=True)


def qa(query):
    """Возвращает только строку ответа без вывода"""
    return ask_smart_v2(query, verbose=False)


# БЛОК 99: Интерактивный режим — финальная версия
def interactive_mode_final():
    """
    Финальный интерактивный режим с полным функционалом.
    Команды:
      /help    — справка
      /stats   — статистика сессии
      /cache   — список кэшированных запросов
      /clear   — очистить кэш
      /demo    — запустить демо-вопросы
      /test    — тест классификатора
      /diag    — диагностика системы
      /json Q  — ответ в JSON
      /md Q    — ответ в Markdown
      /facts Q — извлечь факты
      /ent Q   — извлечь сущности
      /math E  — вычислить выражение
      /conv V N— конвертация единиц
      /ver     — версия
      выход    — выход
    """
    print(f"\n{'='*62}")
    print("  AI v{} — Умный поиск в интернете".format(__version__))
    print(f"  Ответы → {OUTPUT_FILE}")
    print("  /help — список команд | выход — завершить")
    print(f"{'='*62}")

    pipeline = FullAnalysisPipeline()

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{_SESSION.report()}")
            print("[AI] До свидания!")
            break

        if not line:
            continue

        if line.lower() in ('выход', 'exit', 'quit', 'q', ':q'):
            print(f"\n{_SESSION.report()}")
            print("[AI] До свидания!")
            break

        if line == '/help':
            show_help()
            continue

        if line == '/stats':
            print(_SESSION.report())
            continue

        if line == '/cache':
            size = _GLOBAL_CACHE.size()
            print(f"Кэш: {size} запросов")
            for q_text in _GLOBAL_CACHE.list_queries()[:10]:
                print(f"  • {q_text}")
            continue

        if line == '/clear':
            _GLOBAL_CACHE.clear_all()
            print("[AI] Кэш очищен.")
            continue

        if line == '/demo':
            run_demo(n=3, verbose=False)
            continue

        if line == '/test':
            evaluate_classifier_full()
            continue

        if line == '/diag':
            diagnose_system()
            continue

        if line == '/ver':
            print(f"AI версия {__version__}")
            continue

        if line.startswith('/json '):
            q_text = line[6:].strip()
            result = pipeline.run(q_text)
            print(format_as_json(q_text, result['answer'],
                                  result['sources'], result['q_type']))
            continue

        if line.startswith('/md '):
            q_text = line[4:].strip()
            result = pipeline.run(q_text)
            print(format_as_markdown(q_text, result['answer'], result['sources']))
            continue

        if line.startswith('/facts '):
            q_text = line[7:].strip()
            web_data = collect_web_texts(q_text, verbose=False)
            facts = extract_all_facts(web_data.get('combined_text', ''))
            if facts:
                print("Найденные факты:")
                for k, v in list(facts.items())[:15]:
                    print(f"  {k}: {v}")
            else:
                print("Факты не найдены.")
            continue

        if line.startswith('/ent '):
            q_text = line[5:].strip()
            web_data = collect_web_texts(q_text, verbose=False)
            ents = extract_all_entities(web_data.get('combined_text', ''))
            print("Именованные сущности:")
            for k, v in ents.items():
                if v:
                    print(f"  {k}: {', '.join(str(x) for x in v[:3])}")
            continue

        if line.startswith('/math '):
            expr = line[6:].strip()
            result = calculate_simple(expr)
            print(result if result else "Не удалось вычислить.")
            continue

        if line.startswith('/conv '):
            parts = line[6:].strip().split(None, 1)
            if len(parts) == 2:
                result = convert_units(parts[0], parts[1])
                print(result if result else f"Конверсия '{parts[1]}' не найдена.")
            else:
                print("Использование: /conv 100 км в мили")
            continue

        # Обычный вопрос — с math-детектором и фильтром мусора
        math_ans = _try_math_extended(line) if '_try_math_extended' in globals() else calculate_simple(line)
        if math_ans:
            math_ans = re.sub(r'(\d+)\.0\b', r'\1', math_ans)
            print(f"\n[Ответ] {math_ans}")
            init_output_file()
            if '_format_clean_answer' in globals():
                save_to_file(_format_clean_answer(line, math_ans, 0))
            else:
                save_to_file(format_report(line, math_ans, [], "math", 0))
        else:
            ask_ensemble(line, verbose=True)


# БЛОК 100: ФИНАЛЬНАЯ ТОЧКА ВХОДА
def main():
    """
    Точка входа программы.
    Принимает аргументы командной строки или запускает интерактивный режим.

    Использование:
      python ai.py                    # интерактивный режим
      python ai.py вопрос             # один вопрос
      python ai.py --help             # справка
      python ai.py --demo             # демо
      python ai.py --test             # тест классификатора
      python ai.py --diag             # диагностика
      python ai.py -b questions.txt   # пакетный режим
    """
    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()

        if arg1 in ('-h', '--help', 'help', 'справка', 'помощь'):
            show_help()
            return

        if arg1 == '--demo':
            run_demo(n=5, verbose=True)
            return

        if arg1 == '--test':
            evaluate_classifier_full()
            return

        if arg1 == '--diag':
            diagnose_system()
            return

        if arg1 in ('-b', '--batch') and len(sys.argv) > 2:
            ask_from_file(sys.argv[2])
            return

        if arg1 == '--version':
            print(f"AI версия {__version__}")
            return

        if arg1 == '--ensemble':
            question = ' '.join(sys.argv[2:])
            ask_ensemble(question, verbose=True)
            return

        if arg1 == '--bilingual':
            question = ' '.join(sys.argv[2:])
            ask_bilingual(question, verbose=True)
            return

        if arg1 == '--smart':
            question = ' '.join(sys.argv[2:])
            ask_smart_v2(question, verbose=True)
            return

        # Обычный вопрос
        question = ' '.join(sys.argv[1:])
        ask_ensemble(question, verbose=True)

    else:
        interactive_mode_final()




# =================================================================================
# БЛОК 101-110: ДОПОЛНИТЕЛЬНЫЕ АЛГОРИТМЫ И ТЕСТЫ
# =================================================================================

# БЛОК 101: Большой тест всех компонентов
def run_all_unit_tests(verbose=True):
    """
    Запускает встроенные тесты всех компонентов.
    Не требует интернета — тестирует только локальные функции.
    """
    results = {}

    def test(name, fn, expected=True):
        try:
            result = fn()
            ok = bool(result) == bool(expected) or result == expected
            results[name] = ('PASS' if ok else 'FAIL', result)
        except Exception as e:
            results[name] = ('ERROR', str(e))

    # Тест стоп-слов
    test('stop_words_ru', lambda: 'и' in ALL_STOP_WORDS)
    test('stop_words_en', lambda: 'the' in ALL_STOP_WORDS)

    # Тест токенизации
    test('tokenize_basic', lambda: get_word_tokens('Привет мир', remove_stops=False) == ['привет', 'мир'])

    # Тест типов вопросов
    test('q_type_who', lambda: determine_question_type_v2('кто такой Ньютон') == 'who')
    test('q_type_what', lambda: determine_question_type_v2('что такое ДНК') == 'what')
    test('q_type_when', lambda: determine_question_type_v2('когда родился Пушкин') == 'when')
    test('q_type_where', lambda: determine_question_type_v2('где Эйфелева башня') == 'where')
    test('q_type_how_many', lambda: determine_question_type_v2('сколько планет') == 'how_many')
    test('q_type_why', lambda: determine_question_type_v2('почему небо синее') == 'why')
    test('q_type_how', lambda: determine_question_type_v2('как работает интернет') == 'how')

    # Тест математики
    test('math_add', lambda: calculate_simple('5 + 3') == '5.0 + 3.0 = 8')
    test('math_sub', lambda: calculate_simple('10 - 4') == '10.0 - 4.0 = 6')
    test('math_mul', lambda: calculate_simple('6 * 7') is not None)
    test('math_div', lambda: calculate_simple('10 / 2') is not None)
    test('math_sqrt', lambda: calculate_simple('корень из 16') is not None)
    test('math_pct', lambda: calculate_simple('10% от 200') is not None)

    # Тест конвертеров
    test('convert_km', lambda: abs(km_to_miles(1) - 0.621371) < 0.001)
    test('convert_kg', lambda: abs(kg_to_pounds(1) - 2.20462) < 0.001)
    test('convert_cel', lambda: celsius_to_fahrenheit(0) == 32.0)
    test('convert_kel', lambda: celsius_to_kelvin(0) == 273.15)

    # Тест очистки текста
    test('normalize', lambda: len(normalize_text('  hello   world  ')) > 0)
    test('clean_noise', lambda: is_noise_sentence('подписывайтесь на канал'))

    # Тест NER
    test('ner_year', lambda: bool(extract_entities('В 2023 году', 'date')))
    test('ner_num', lambda: bool(extract_entities('5 миллионов человек', 'number')))

    # Тест стемматизации
    test('stem_ru', lambda: naive_stem_ru('программирование') != 'программирование')
    test('stem_tokens', lambda: isinstance(stem_tokens(['слово']), list))

    # Тест сходства
    test('cosine_same', lambda: abs(cosine_similarity_bow('кошка кот', 'кот кошка') - 1.0) < 0.01)
    test('cosine_diff', lambda: cosine_similarity_bow('кошка', 'собака') == 0.0)

    # Тест Левенштейна
    test('levenshtein_same', lambda: levenshtein_distance('cat', 'cat') == 0)
    test('levenshtein_diff', lambda: levenshtein_distance('cat', 'bat') == 1)

    # Тест расширения запроса
    test('expand_query', lambda: len(expand_query('когда умер Пушкин')) > 0)
    test('expand_v2', lambda: len(expand_query_v2('столица России')) > 0)

    # Тест категоризатора
    test('category_bio', lambda: classify_query_category('кто такой Ньютон') == 'biography')
    test('category_geo', lambda: classify_query_category('столица Франции') == 'geography')
    test('category_sci', lambda: classify_query_category('теорема Пифагора') == 'science')

    # Тест кэша
    cache = QueryCache.__new__(QueryCache)
    cache._data = {}
    cache.cache_file = '/tmp/test_cache.json'
    cache.ttl = __import__('datetime').timedelta(hours=24)
    cache.set('тест', 'результат теста')
    test('cache_set_get', lambda: cache.get('тест') == 'результат теста')
    cache.clear_all()
    test('cache_clear', lambda: cache.get('тест') is None)

    # Вывод результатов
    passed = sum(1 for status, _ in results.values() if status == 'PASS')
    failed = sum(1 for status, _ in results.values() if status == 'FAIL')
    errors = sum(1 for status, _ in results.values() if status == 'ERROR')

    if verbose:
        print(f"\n=== Результаты тестов ({len(results)} тестов) ===")
        for name, (status, value) in results.items():
            if status != 'PASS' or verbose:
                icon = '✓' if status == 'PASS' else ('✗' if status == 'FAIL' else '!')
                print(f"  [{icon}] {name}: {status}")
        print(f"\nИтого: {passed} OK, {failed} FAIL, {errors} ERROR")

    return passed, failed, errors


# БЛОК 102: Дополнительные полезные паттерны
_EXTRA_YEAR_CONTEXT_PATS = [
    re.compile(r'(?:в|в\s+)\s*(\d{4})\s*(?:году|г\.)', re.I),
    re.compile(r'(?:since|from|in|by)\s+(\d{4})\b', re.I),
    re.compile(r'\b(\d{4})\s*[-–—]\s*(?:по\s+настоящее\s+время|н\.в\.|present)', re.I),
    re.compile(r'\((\d{4})\)', re.I),
]

_EXTRA_DATE_CONTEXT_PATS = [
    re.compile(
        r'\b(\d{1,2})\s+'
        r'(январ|феврал|март|апрел|май|июн|июл|август|сентябр|октябр|ноябр|декабр)\w*'
        r'\s+(\d{4})\b', re.I),
    re.compile(
        r'\b(January|February|March|April|May|June|July|August|'
        r'September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b', re.I),
]


def extract_all_years(text, n=10):
    """Извлекает все года из текста"""
    years = []
    for pat in _EXTRA_YEAR_CONTEXT_PATS:
        for m in pat.finditer(text):
            y = m.group(1)
            if y and y not in years and 1000 <= int(y) <= 2100:
                years.append(y)
    return years[:n]


def extract_all_dates(text, n=5):
    """Извлекает все полные даты из текста"""
    dates = []
    for pat in _EXTRA_DATE_CONTEXT_PATS:
        for m in pat.finditer(text):
            d = m.group()
            if d not in dates:
                dates.append(d)
    return dates[:n]


def get_most_mentioned_year(text):
    """Возвращает наиболее часто упомянутый год"""
    years = extract_all_years(text, n=50)
    if not years:
        return ''
    freq = Counter(years)
    return freq.most_common(1)[0][0]


def get_latest_year(text):
    """Возвращает самый последний год из текста"""
    years = extract_all_years(text, n=50)
    if not years:
        return ''
    valid = [int(y) for y in years if y.isdigit() and 1000 <= int(y) <= 2100]
    return str(max(valid)) if valid else ''


def get_earliest_year(text):
    """Возвращает самый ранний год из текста"""
    years = extract_all_years(text, n=50)
    if not years:
        return ''
    valid = [int(y) for y in years if y.isdigit() and 1000 <= int(y) <= 2100]
    return str(min(valid)) if valid else ''


# БЛОК 103: Расширенный анализ источников
def analyze_sources(web_data):
    """
    Анализирует найденные источники:
    - Количество по типу домена
    - Средняя длина текста
    - Процент премиум-источников
    - Уникальные домены
    """
    results = web_data.get('results', [])
    if not results:
        return {}

    total = len(results)
    premium_count = sum(1 for r in results if is_premium_domain(r['url']))
    avg_len = sum(r.get('length', len(r['text'])) for r in results) / total
    domains = [urlparse(r['url']).netloc.replace('www.', '') for r in results]
    unique_domains = len(set(domains))

    type_counts = Counter(detect_site_type(r['url']) for r in results)

    return {
        'total_sources': total,
        'premium_sources': premium_count,
        'premium_pct': premium_count / total * 100,
        'avg_text_length': avg_len,
        'unique_domains': unique_domains,
        'source_types': dict(type_counts),
        'top_domains': domains[:5],
    }


def print_source_analysis(web_data):
    """Выводит анализ источников"""
    stats = analyze_sources(web_data)
    if not stats:
        print("Источники не найдены.")
        return
    print(f"\n  Источников: {stats['total_sources']}")
    print(f"  Премиум: {stats['premium_sources']} ({stats['premium_pct']:.0f}%)")
    print(f"  Ср. длина текста: {stats['avg_text_length']:.0f} симв.")
    print(f"  Уникальных доменов: {stats['unique_domains']}")
    print(f"  Типы: {stats['source_types']}")


# БЛОК 104: Тематические поисковые подсказки
TOPIC_SEARCH_HINTS = {
    'person': [
        '{subject} биография',
        '{subject} кто такой',
        '{subject} жизнь и деятельность',
        '{subject} biography',
        '{subject} who',
    ],
    'country': [
        '{subject} страна',
        '{subject} столица население площадь',
        '{subject} country facts',
        '{subject} geography',
    ],
    'event': [
        '{subject} когда произошло',
        '{subject} история',
        '{subject} дата',
        '{subject} when history',
    ],
    'concept': [
        '{subject} что такое определение',
        '{subject} объяснение',
        '{subject} what is definition',
        '{subject} explained',
    ],
    'invention': [
        '{subject} кто изобрёл когда',
        '{subject} история изобретения',
        '{subject} who invented when',
        '{subject} invention history',
    ],
    'measurement': [
        '{subject} сколько',
        '{subject} размер',
        '{subject} how many',
        '{subject} size measurement',
    ],
}


def get_topic_hints(query, topic_type):
    """Возвращает подсказки для поиска по теме"""
    hints = TOPIC_SEARCH_HINTS.get(topic_type, [])
    subject = ' '.join(w for w in query.split() if w.lower() not in ALL_STOP_WORDS)
    return [h.format(subject=subject) for h in hints[:2]]


def detect_topic_type(query):
    """Определяет тип темы запроса"""
    q_lower = query.lower()
    q_type = determine_question_type_v2(query)

    if q_type == 'who':
        return 'person'
    if q_type == 'where':
        if any(w in q_lower for w in ['столица', 'страна', 'capital', 'country']):
            return 'country'
    if q_type == 'when':
        return 'event'
    if q_type == 'what':
        if any(w in q_lower for w in ['изобрёл', 'создал', 'invented', 'created']):
            return 'invention'
        return 'concept'
    if q_type == 'how_many':
        return 'measurement'
    return 'concept'


# БЛОК 105: Детектор числовых вопросов с контекстом
_NUMERIC_QUESTION_WORDS = {
    'ru': {
        'population': ['население', 'жителей', 'проживает', 'численность'],
        'area': ['площадь', 'территория', 'занимает'],
        'height': ['высота', 'высок', 'высотой'],
        'depth': ['глубина', 'глубок', 'глубиной'],
        'length': ['длина', 'протяжённость', 'длиной'],
        'distance': ['расстояние', 'далеко', 'расстоянии'],
        'speed': ['скорость', 'быстро', 'скоростью'],
        'weight': ['вес', 'масса', 'весит'],
        'temperature': ['температура', 'градус', 'тепло', 'холодно'],
        'age': ['возраст', 'лет', 'старый'],
        'count': ['сколько', 'количество', 'число', 'численность'],
        'price': ['цена', 'стоимость', 'стоит', 'рублей', 'долларов'],
        'year': ['год', 'когда', 'дата', 'время'],
    },
    'en': {
        'population': ['population', 'inhabitants', 'residents', 'live there'],
        'area': ['area', 'size', 'covers', 'territory'],
        'height': ['height', 'tall', 'altitude'],
        'depth': ['depth', 'deep'],
        'length': ['length', 'long', 'extends'],
        'distance': ['distance', 'far', 'away'],
        'speed': ['speed', 'fast', 'velocity'],
        'weight': ['weight', 'weighs', 'mass'],
        'temperature': ['temperature', 'degrees', 'hot', 'cold'],
        'age': ['age', 'old', 'years old'],
        'count': ['how many', 'number of', 'count of'],
        'price': ['price', 'cost', 'worth', 'dollars', 'euros'],
        'year': ['year', 'when', 'date'],
    },
}


def detect_numeric_subtype(query):
    """Определяет подтип числового вопроса (население, площадь, высота...)"""
    q_lower = query.lower()
    lang = detect_query_language(query)
    words_dict = _NUMERIC_QUESTION_WORDS.get(lang, _NUMERIC_QUESTION_WORDS['ru'])

    for subtype, keywords in words_dict.items():
        if any(kw in q_lower for kw in keywords):
            return subtype
    return 'count'


# БЛОК 106: Расширенные функции постобработки
def postprocess_answer_v2(answer, query, q_type=None):
    """
    Расширенная постобработка ответа:
    1. Базовая очистка
    2. Убирает дубликаты
    3. Исправляет пунктуацию
    4. Убирает URL и email
    5. Убирает мусорные фразы
    6. Проверяет минимальную длину
    7. Форматирует числовые ответы
    8. Убеждается в наличии точки в конце
    """
    if not answer:
        return ''

    # 1. Базовая очистка
    answer = clean_answer_text(answer)

    # 2. Убираем URL и email
    answer = remove_urls_from_text(answer)
    answer = remove_emails_from_text(answer)

    # 3. Убираем мусорные фразы
    if _EXTRA_NOISE_RE.search(answer):
        for marker in EXTRA_NOISE_MARKERS:
            answer = re.sub(re.escape(marker), '', answer, flags=re.I)

    # 4. Убираем скобки с малополезным содержимым
    answer = re.sub(r'\(\s*\)', '', answer)
    answer = re.sub(r'\[\s*\]', '', answer)

    # 5. Убираем дубликаты слов рядом
    answer = remove_repeated_words(answer)

    # 6. Исправляем пробелы
    answer = collapse_whitespace(answer)

    # 7. Убираем начальную пунктуацию
    answer = strip_leading_punctuation(answer)

    # 8. Проверяем длину
    if len(answer) < 15:
        return ''

    # 9. Усекаем до разумного размера
    answer = truncate_to_sentence(answer, MAX_ANSWER_LEN)

    return answer


def rerank_answers(candidates, query, q_type=None):
    """
    Переранжирует кандидатов с учётом:
    1. Качества ответа
    2. Индикаторов типа вопроса
    3. Наличия чисел (для how_many)
    4. Источника
    """
    if not candidates:
        return []

    if not q_type:
        q_type = determine_question_type_v2(query)

    scored = []
    for cand in candidates:
        if not is_valid_answer_text(cand):
            continue

        quality = estimate_answer_quality(cand, query)
        indicator_bonus = score_by_indicators(cand, q_type)

        # Бонус за числа в how_many вопросах
        number_bonus = 0.0
        if q_type == 'how_many' and re.search(r'\d', cand):
            number_bonus = 5.0

        # Штраф за неопределённость
        uncertainty_penalty = -10.0 if contains_uncertainty(cand) else 0.0

        # Бонус за оптимальную длину
        word_count = len(cand.split())
        length_bonus = min(5.0, word_count / 10) if word_count < 50 else max(0, 5 - (word_count - 50) / 20)

        total = quality + indicator_bonus * 2 + number_bonus + uncertainty_penalty + length_bonus
        scored.append((total, cand))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored]


# БЛОК 107: Комплексные тесты на извлечение
EXTRACTION_TEST_CASES = [
    {
        'query': 'сколько планет в Солнечной системе',
        'expected_contains': ['8', 'восемь', 'eight', 'планет'],
        'q_type': 'how_many',
    },
    {
        'query': 'что такое ДНК',
        'expected_contains': ['дезоксирибонуклеин', 'ДНК', 'DNA', 'молекул', 'генетич'],
        'q_type': 'what',
    },
    {
        'query': 'кто изобрёл телефон',
        'expected_contains': ['Белл', 'Bell', '1876', 'Грейам', 'Graham'],
        'q_type': 'who',
    },
    {
        'query': 'столица Франции',
        'expected_contains': ['Париж', 'Paris'],
        'q_type': 'where',
    },
    {
        'query': 'почему небо синее',
        'expected_contains': ['рассеивани', 'Рэлей', 'Rayleigh', 'scattering', 'свет', 'light'],
        'q_type': 'why',
    },
]


def evaluate_extraction(web_data, query, expected_contains, q_type):
    """Оценивает качество извлечения по ожидаемым словам"""
    answer = extract_answer_full(web_data, query, q_type)
    if not answer:
        return 0.0, answer

    found = sum(1 for word in expected_contains
                if word.lower() in answer.lower())
    score = found / len(expected_contains) if expected_contains else 0
    return score, answer


# БЛОК 108: Вспомогательные математические функции
def compute_precision(retrieved, relevant):
    """Точность = (релевантные среди найденных) / (найденных)"""
    if not retrieved:
        return 0.0
    relevant_set = set(relevant)
    retrieved_relevant = sum(1 for r in retrieved if r in relevant_set)
    return retrieved_relevant / len(retrieved)


def compute_recall(retrieved, relevant):
    """Полнота = (релевантных найдено) / (всего релевантных)"""
    if not relevant:
        return 0.0
    relevant_set = set(relevant)
    found = sum(1 for r in retrieved if r in relevant_set)
    return found / len(relevant)


def compute_f1(precision, recall):
    """F1 мера = гармоническое среднее precision и recall"""
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def mean_reciprocal_rank(queries_results):
    """MRR — средний обратный ранг (оценка ранжирования)"""
    if not queries_results:
        return 0.0
    total = 0.0
    for rank, is_correct in enumerate(queries_results, 1):
        if is_correct:
            total += 1.0 / rank
            break
    return total / len(queries_results)


def dcg_at_k(relevances, k):
    """DCG@k — Discounted Cumulative Gain"""
    return sum(
        rel / math.log2(i + 2)
        for i, rel in enumerate(relevances[:k])
    )


def ndcg_at_k(relevances, ideal_relevances, k):
    """NDCG@k — Normalized DCG"""
    dcg = dcg_at_k(relevances, k)
    idcg = dcg_at_k(sorted(ideal_relevances, reverse=True), k)
    return dcg / idcg if idcg > 0 else 0.0


# БЛОК 109: Большой набор тестовых данных для языкового анализа
LINGUISTIC_TEST_DATA = {
    'sentence_splitting': [
        ('Привет мир. Это тест. Работает ли?', 3),
        ('Hello world. This is a test. Does it work?', 3),
        ('Он сказал: "Привет!" — и ушёл.', 1),
        ('1. Первый пункт. 2. Второй пункт. 3. Третий.', 3),
        ('Mr. Smith went to Dr. Jones at 3 p.m. today.', 1),
    ],
    'tokenization': [
        ('Привет мир', ['привет', 'мир']),
        ('Hello World', ['hello', 'world']),
        ('2024 год', ['год']),
        ('', []),
    ],
    'stop_words': [
        ('и это то что и есть', []),
        ('the cat is on the mat', ['cat', 'mat']),
    ],
    'question_type': [
        ('кто создал Python', 'who'),
        ('что такое алгоритм', 'what'),
        ('когда основан Google', 'when'),
        ('где находится Берлин', 'where'),
        ('сколько стран в ЕС', 'how_many'),
        ('почему трава зелёная', 'why'),
        ('как работает двигатель', 'how'),
    ],
    'math': [
        ('5 + 3', '5.0 + 3.0 = 8'),
        ('корень из 9', '√9.0 = 3'),
        ('25% от 100', '25.0% от 100.0 = 25'),
    ],
    'noise_detection': [
        ('подписывайтесь на наш канал', True),
        ('Россия — крупнейшая страна мира', False),
        ('cookie policy privacy terms', True),
        ('ДНК — молекула, хранящая наследственную информацию', False),
    ],
}


def run_linguistic_tests(verbose=True):
    """Запускает тесты лингвистического анализа"""
    total = 0
    passed = 0

    # Тест типов вопросов
    for q, expected in LINGUISTIC_TEST_DATA['question_type']:
        got = determine_question_type_v2(q)
        total += 1
        ok = got == expected
        if ok:
            passed += 1
        if verbose and not ok:
            print(f"  FAIL q_type: {q!r} → {got} (ожид. {expected})")

    # Тест математики
    for expr, expected in LINGUISTIC_TEST_DATA['math']:
        got = calculate_simple(expr)
        total += 1
        ok = got == expected
        if ok:
            passed += 1
        if verbose and not ok:
            print(f"  FAIL math: {expr!r} → {got!r} (ожид. {expected!r})")

    # Тест шума
    for text, expected_is_noise in LINGUISTIC_TEST_DATA['noise_detection']:
        got = is_noise_sentence(text)
        total += 1
        ok = got == expected_is_noise
        if ok:
            passed += 1
        if verbose and not ok:
            print(f"  FAIL noise: {text!r} → {got} (ожид. {expected_is_noise})")

    if verbose:
        print(f"\nЛингвистические тесты: {passed}/{total}")
    return passed, total


# БЛОК 110: Финальный entry point — переопределяем if __name__
def _final_main():
    """
    Финальная точка входа — самая полная.
    Использует ask_ensemble (7 алгоритмов).
    """
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ('-h', '--help', 'help', 'справка'):
            show_help()
            return
        if arg == '--demo':
            run_demo(5, verbose=True)
            return
        if arg == '--test':
            run_all_unit_tests(verbose=True)
            evaluate_classifier_full()
            run_linguistic_tests(verbose=True)
            return
        if arg == '--diag':
            diagnose_system()
            return
        if arg in ('-b', '--batch') and len(sys.argv) > 2:
            ask_from_file(sys.argv[2])
            return
        if arg == '--version':
            print(f"AI v{__version__}")
            return
        question = ' '.join(sys.argv[1:])
        ask_ensemble(question, verbose=True)
    else:
        interactive_mode_final()


# =================================================================================
# БЛОК 111: ФИНАЛЬНАЯ РЕГИСТРАЦИЯ И ТОЧКА ВХОДА
# =================================================================================

# Регистрируем все публичные функции
_PUBLIC_FUNCTIONS = {
    'ask': ask,
    'ask_v2': ask_v2,
    'ask_smart_v2': ask_smart_v2,
    'ask_ensemble': ask_ensemble,
    'ask_bilingual': ask_bilingual,
    'ask_iterative': ask_iterative,
    'ask_cached': ask_cached,
    'ask_with_category': ask_with_category,
    'ask_batch': ask_batch,
    'ask_from_file': ask_from_file,
    'q': q,
    'qa': qa,
    'search': search,
    'quick_ask': quick_ask,
    'deep_ask': deep_ask,
    'smart_ask': smart_ask,
    'fast_ask': fast_ask,
    'calculate_simple': calculate_simple,
    'convert_units': convert_units,
    'get_constant': get_constant,
    'run_demo': run_demo,
    'show_help': show_help,
    'diagnose_system': diagnose_system,
    'evaluate_classifier_full': evaluate_classifier_full,
    'run_all_unit_tests': run_all_unit_tests,
    'run_linguistic_tests': run_linguistic_tests,
    'extract_entities': extract_entities,
    'extract_fact': extract_fact,
    'extract_all_facts': extract_all_facts,
    'analyze_sentiment': analyze_sentiment,
    'get_capabilities': get_capabilities,
    'get_version': get_version,
}


def list_functions():
    """Выводит список всех доступных функций"""
    print(f"\n=== AI v{__version__} — Доступные функции ===")
    for name, fn in sorted(_PUBLIC_FUNCTIONS.items()):
        doc = (fn.__doc__ or '').split('\n')[0].strip()
        print(f"  {name:<25} — {doc[:60]}")
    print(f"\nВсего: {len(_PUBLIC_FUNCTIONS)} функций")




# =================================================================================
# БЛОК 112-120: БОЛЬШИЕ СЛОВАРИ И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =================================================================================

# БЛОК 112: Полный словарь синонимов для вопросных слов (расширенный)
QUESTION_WORD_SYNONYMS_EXTENDED = {
    'who': [
        # Русский
        'кто', 'кому', 'кого', 'кем', 'ком',
        'кто такой', 'кто такая', 'кто такие', 'кто является',
        'какой человек', 'какая личность', 'кем был', 'кем была',
        'кем является', 'кем является', 'кто основал', 'кто создал',
        'кто придумал', 'кто изобрёл', 'кто открыл', 'кто написал',
        'кто снял', 'кто нарисовал', 'кто построил', 'кто разработал',
        'кто руководил', 'кто возглавлял', 'кто управлял',
        'чья', 'чей', 'чьё', 'чьи',
        # Английский
        'who', 'whom', 'whose', 'who is', 'who was', 'who are', 'who were',
        'who founded', 'who created', 'who invented', 'who discovered',
        'who wrote', 'who directed', 'who built', 'who developed',
        'who led', 'who managed', 'who runs', 'who ran',
    ],
    'what': [
        # Русский
        'что', 'чего', 'чему', 'чем', 'чём',
        'что такое', 'что значит', 'что означает', 'что представляет',
        'что есть', 'что является', 'что включает', 'что содержит',
        'какой', 'какая', 'какое', 'какие',
        'что из себя представляет', 'чем является', 'что значит слово',
        'определение', 'смысл', 'суть', 'значение', 'понятие', 'термин',
        'объясни', 'расскажи что', 'что я должен знать',
        # Английский
        'what', 'what is', 'what are', 'what was', 'what were',
        'what does', 'what did', 'what do',
        'define', 'definition', 'meaning', 'what means', 'explain',
        'describe', 'definition of', 'concept of',
    ],
    'when': [
        # Русский
        'когда', 'в какое время', 'в какой год', 'в каком году',
        'в какое время', 'в какой период', 'в какую эпоху',
        'дата', 'год', 'число', 'период',
        'как давно', 'сколько лет назад', 'в каком веке',
        'начало', 'конец', 'окончание', 'создание', 'основание',
        # Английский
        'when', 'when was', 'when did', 'when is',
        'what year', 'what date', 'what time', 'what period',
        'how long ago', 'which year', 'since when',
        'date of', 'year of', 'time of',
    ],
    'where': [
        # Русский
        'где', 'откуда', 'куда',
        'в какой стране', 'в каком городе', 'в каком регионе',
        'в каком месте', 'на каком континенте', 'в каком районе',
        'столица', 'расположение', 'местонахождение', 'местоположение',
        'адрес', 'координаты', 'как добраться', 'как найти',
        # Английский
        'where', 'where is', 'where are', 'where was', 'where were',
        'in what country', 'in which country', 'in what city',
        'location of', 'address of', 'situated', 'located',
        'capital of', 'position of',
    ],
    'how_many': [
        # Русский
        'сколько', 'как много', 'какой размер', 'какая численность',
        'какова численность', 'каково население', 'какова площадь',
        'какова высота', 'какова длина', 'какова глубина',
        'какова скорость', 'каков вес', 'какова масса',
        'какова температура', 'каков возраст', 'каков доход',
        'численность', 'количество', 'число', 'размер', 'величина',
        'мощность', 'производительность',
        # Английский
        'how many', 'how much', 'what size', 'what population',
        'what area', 'what height', 'what length', 'what depth',
        'what speed', 'what weight', 'what mass', 'what temperature',
        'how big', 'how tall', 'how long', 'how deep', 'how fast',
        'how heavy', 'how old', 'how far', 'how large', 'how wide',
    ],
    'why': [
        # Русский
        'почему', 'зачем', 'по какой причине', 'из-за чего',
        'вследствие чего', 'благодаря чему', 'ввиду чего',
        'в связи с чем', 'по каким причинам', 'объясни почему',
        'каковы причины', 'что стало причиной',
        # Английский
        'why', 'why is', 'why are', 'why does', 'why do', 'why did',
        'what causes', 'what caused', 'reason for', 'reason why',
        'explain why', 'for what reason', 'due to what',
    ],
    'how': [
        # Русский
        'как', 'каким образом', 'каким способом', 'каким методом',
        'какова процедура', 'какова последовательность', 'каков алгоритм',
        'как работает', 'как устроен', 'как устроена',
        'как сделать', 'как создать', 'как получить',
        'каков механизм', 'каков принцип', 'каков процесс',
        # Английский
        'how', 'how does', 'how do', 'how did', 'how is', 'how are',
        'how to', 'how can', 'in what way', 'by what means',
        'what is the process', 'what is the method',
        'explain how', 'how works', 'mechanism of',
    ],
}


def determine_question_type_v3(query):
    """
    Самая точная версия определения типа вопроса.
    Использует расширенный словарь с 200+ синонимами.
    """
    q_lower = query.lower().strip()

    for q_type, synonyms in QUESTION_WORD_SYNONYMS_EXTENDED.items():
        for syn in synonyms:
            if q_lower.startswith(syn.lower()) or f' {syn.lower()} ' in f' {q_lower} ':
                return q_type

    # Резервный метод — оригинальная версия
    return determine_question_type_v2(query)


# БЛОК 113: Полный набор паттернов для извлечения структурированных данных
STRUCTURED_DATA_PATTERNS_V2 = {}

_STRUCTURED_TEMPLATES_V2 = [
    # Персоны
    ('born_date', [
        r'родил(?:ся|ась)\s+(?:\d+\s+\w+\s+)?(\d{4})',
        r'born\s+(?:in\s+)?(?:\w+\s+\d+,?\s+)?(\d{4})',
        r'\((\d{4})\s*[-–—]',
    ]),
    ('died_date', [
        r'умер(?:ла)?\s+(?:\d+\s+\w+\s+)?(\d{4})',
        r'died\s+(?:in\s+)?(?:\w+\s+\d+,?\s+)?(\d{4})',
        r'[-–—]\s*(\d{4})\)',
    ]),
    ('nationality_en', [
        r'\b(Russian|American|British|German|French|Italian|Spanish|Chinese|Japanese|'
        r'Polish|Dutch|Swedish|Norwegian|Danish|Finnish|Austrian|Swiss|Portuguese|Greek|Turkish)\b',
    ]),
    ('profession_ru', [
        r'\b(физик|математик|химик|биолог|астроном|инженер|программист|писатель|'
        r'поэт|художник|композитор|режиссёр|актёр|актриса|политик|президент|учёный|'
        r'изобретатель|предприниматель|философ|историк|архитектор|музыкант|певец|певица)\b',
    ]),
    ('profession_en', [
        r'\b(physicist|mathematician|chemist|biologist|astronomer|engineer|programmer|'
        r'writer|poet|artist|composer|director|actor|actress|politician|president|'
        r'scientist|inventor|entrepreneur|philosopher|historian|architect|musician|singer)\b',
    ]),
    ('nationality_ru', [
        r'\b(российский|русский|американский|британский|немецкий|французский|'
        r'итальянский|испанский|китайский|японский|польский|голландский|шведский|'
        r'норвежский|датский|финский|австрийский|швейцарский|португальский|греческий)\b',
    ]),
    # Организации
    ('founded_year', [
        r'основан(?:а|о)?\s+в\s+(\d{4})',
        r'founded\s+in\s+(\d{4})',
        r'established\s+in\s+(\d{4})',
        r'создан(?:а|о)?\s+в\s+(\d{4})',
    ]),
    ('employees', [
        r'(?:сотрудников|работников|employees)\s*[-:]\s*(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн|thousand|million))?)',
        r'(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн|thousand|million))?)\s*(?:сотрудников|работников|employees)',
    ]),
    ('headquarter_city', [
        r'штаб-квартира\s+(?:расположена\s+в\s+)?([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
        r'headquarters\s+(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
    ]),
    # Научные
    ('atomic_number', [
        r'атомный\s+номер\s*(?:=|:)?\s*(\d{1,3})',
        r'atomic\s+number\s*(?:=|:)?\s*(\d{1,3})',
        r'Z\s*=\s*(\d{1,3})',
    ]),
    ('atomic_mass_val', [
        r'атомная\s+масса\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)',
        r'atomic\s+mass\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)',
    ]),
    ('chemical_symbol', [
        r'химический\s+символ\s*[-:]\s*([A-Z][a-z]?)',
        r'chemical\s+symbol\s*[-:]\s*([A-Z][a-z]?)',
        r'\bSym(?:bol)?\s*=\s*([A-Z][a-z]?)',
    ]),
    # Физические объекты
    ('mass_kg', [
        r'масса\s*[-:]\s*(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн|×\s*10\^\d+))?)\s*(?:кг|kg)',
        r'mass\s*[-:]\s*(\d+(?:[,\.]\d+)?(?:\s*(?:thousand|million))?)\s*(?:kg|kilogram)',
    ]),
    ('diameter_km', [
        r'диаметр\s*[-:]\s*(\d+(?:[,\.]\d+)?(?:\s*(?:тыс|млн))?)\s*(?:км|km)',
        r'diameter\s*[-:]\s*(\d+(?:[,\.]\d+)?(?:\s*(?:thousand|million))?)\s*(?:km|kilometer)',
    ]),
    ('orbital_period', [
        r'период\s+обращения\s*[-:]\s*(\d+(?:[,\.]\d+)?)\s*(?:лет|суток|дней|days?|years?)',
        r'orbital\s+period\s*[-:]\s*(\d+(?:[,\.]\d+)?)\s*(?:days?|years?|hours?)',
    ]),
    # Страны
    ('gdp', [
        r'ВВП\s*[-:]\s*(\d+(?:[,\.]\d+)?(?:\s*(?:трлн|млрд|млн|trillion|billion|million))?)',
        r'GDP\s*[-:]\s*(\d+(?:[,\.]\d+)?(?:\s*(?:trillion|billion|million))?)',
    ]),
    ('gini', [
        r'коэффициент\s+Джини\s*[-:]\s*(\d+(?:[,\.]\d+)?)',
        r'Gini\s+(?:coefficient\s+)?[-:]\s*(\d+(?:[,\.]\d+)?)',
    ]),
    ('hdi', [
        r'ИРЧП\s*[-:]\s*(\d+(?:[,\.]\d+)?)',
        r'HDI\s*[-:]\s*(\d+(?:[,\.]\d+)?)',
        r'Human\s+Development\s+Index\s*[-:]\s*(\d+(?:[,\.]\d+)?)',
    ]),
    # Литература
    ('publication_year', [
        r'опубликован(?:а|о)?\s+в\s+(\d{4})',
        r'издан(?:а|о)?\s+в\s+(\d{4})',
        r'published\s+in\s+(\d{4})',
        r'first\s+published\s+(\d{4})',
    ]),
    ('pages_count', [
        r'(\d+)\s+страниц',
        r'(\d+)\s+pages?',
    ]),
    ('isbn', [
        r'ISBN[-:\s]*(\d[\d-]{9,15})',
        r'ISBN[-:\s]*(978[\d-]{10,})',
    ]),
]

for _name, _pats in _STRUCTURED_TEMPLATES_V2:
    STRUCTURED_DATA_PATTERNS_V2[_name] = [re.compile(p, re.I) for p in _pats]


def extract_structured_v2(text, data_type):
    """Извлекает структурированные данные (расширенная версия)"""
    for pat in STRUCTURED_DATA_PATTERNS_V2.get(data_type, []):
        m = pat.search(text)
        if m:
            try:
                return m.group(1).strip()
            except IndexError:
                return m.group().strip()
    return ''


def extract_all_structured_v2(text):
    """Извлекает все структурированные данные"""
    result = {}
    for data_type in STRUCTURED_DATA_PATTERNS_V2:
        val = extract_structured_v2(text, data_type)
        if val:
            result[data_type] = val
    return result


# БЛОК 114: Словарь единиц с конвертацией
UNITS_CONVERSION_TABLE = {
    # Длина (базовая единица = метр)
    'м': 1.0, 'метр': 1.0, 'meter': 1.0, 'm': 1.0,
    'км': 1000.0, 'километр': 1000.0, 'kilometer': 1000.0, 'km': 1000.0,
    'см': 0.01, 'сантиметр': 0.01, 'centimeter': 0.01, 'cm': 0.01,
    'мм': 0.001, 'миллиметр': 0.001, 'millimeter': 0.001, 'mm': 0.001,
    'фут': 0.3048, 'foot': 0.3048, 'ft': 0.3048, 'feet': 0.3048,
    'дюйм': 0.0254, 'inch': 0.0254, 'in': 0.0254,
    'ярд': 0.9144, 'yard': 0.9144, 'yd': 0.9144,
    'миля': 1609.344, 'mile': 1609.344, 'mi': 1609.344,
    'морская миля': 1852.0, 'nautical mile': 1852.0, 'nmi': 1852.0,
    # Масса (базовая = кг)
    'кг': 1.0, 'килограмм': 1.0, 'kilogram': 1.0, 'kg': 1.0,
    'г': 0.001, 'грамм': 0.001, 'gram': 0.001,
    'мг': 1e-6, 'миллиграмм': 1e-6, 'milligram': 1e-6, 'mg': 1e-6,
    'т': 1000.0, 'тонна': 1000.0, 'ton': 1000.0, 'tonne': 1000.0,
    'фунт': 0.453592, 'pound': 0.453592, 'lb': 0.453592,
    'унция': 0.028349, 'ounce': 0.028349, 'oz': 0.028349,
    # Площадь (базовая = м²)
    'м²': 1.0, 'кв.м': 1.0, 'sq m': 1.0,
    'км²': 1e6, 'кв.км': 1e6, 'sq km': 1e6,
    'га': 10000.0, 'гектар': 10000.0, 'hectare': 10000.0, 'ha': 10000.0,
    'акр': 4046.86, 'acre': 4046.86,
    'кв.миля': 2589988.0, 'sq mile': 2589988.0,
    # Объём (базовая = л)
    'л': 1.0, 'литр': 1.0, 'liter': 1.0, 'litre': 1.0, 'L': 1.0,
    'мл': 0.001, 'миллилитр': 0.001, 'milliliter': 0.001, 'ml': 0.001,
    'галлон': 3.78541, 'gallon': 3.78541, 'gal': 3.78541,
    'кварта': 0.946353, 'quart': 0.946353, 'qt': 0.946353,
    'пинта': 0.473176, 'pint': 0.473176, 'pt': 0.473176,
    # Время (базовая = секунда)
    'с': 1.0, 'секунда': 1.0, 'second': 1.0, 'sec': 1.0,
    'мин': 60.0, 'минута': 60.0, 'minute': 60.0, 'min': 60.0,
    'ч': 3600.0, 'час': 3600.0, 'hour': 3600.0, 'hr': 3600.0,
    'сутки': 86400.0, 'день': 86400.0, 'day': 86400.0,
    'неделя': 604800.0, 'week': 604800.0,
    'месяц': 2628000.0, 'month': 2628000.0,
    'год': 31536000.0, 'year': 31536000.0, 'yr': 31536000.0,
}


def convert_measurement(value, from_unit, to_unit):
    """
    Конвертирует значение из одной единицы в другую.
    Работает для единиц одной категории (длина, масса, объём, время).
    """
    try:
        v = float(str(value).replace(',', '.'))
        f = UNITS_CONVERSION_TABLE.get(from_unit.lower())
        t = UNITS_CONVERSION_TABLE.get(to_unit.lower())
        if f is None or t is None:
            return None
        result = v * f / t
        return f"{value} {from_unit} = {result:.6g} {to_unit}"
    except Exception:
        return None


# БЛОК 115: Продвинутый анализатор предложений
def analyze_sentence(sentence):
    """
    Возвращает словарь с характеристиками предложения:
    - words: список слов
    - length: длина в символах
    - word_count: количество слов
    - has_number: содержит число
    - has_date: содержит дату
    - has_name: содержит имя
    - sentiment: тональность
    - q_type_hint: подсказка о типе вопроса
    """
    words = get_word_tokens(sentence)
    return {
        'text': sentence,
        'words': words,
        'word_count': len(words),
        'length': len(sentence),
        'has_number': has_number(sentence),
        'has_date': has_date(sentence),
        'has_name': has_person_name(sentence),
        'has_url': bool(re.search(r'https?://', sentence)),
        'sentiment': analyze_sentiment(sentence),
        'is_noise': is_noise_sentence(sentence),
        'lexical_diversity': len(set(words)) / max(len(words), 1),
        'stop_word_ratio': sum(1 for w in words if w in ALL_STOP_WORDS) / max(len(words), 1),
    }


def rank_sentences_comprehensive(sentences, query_words, q_type='general'):
    """
    Комплексное ранжирование предложений по нескольким критериям:
    1. TF-IDF сходство с запросом (40%)
    2. BM25 (20%)
    3. Наличие индикаторов ответа (20%)
    4. Отсутствие шума (10%)
    5. Оптимальная длина (10%)
    """
    avg_dl = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    query_words_list = list(query_words)

    scored = []
    for sent in sentences:
        analysis = analyze_sentence(sent)

        if analysis['is_noise']:
            continue

        # TF-IDF
        tfidf = score_sentence(sent, query_words)

        # BM25
        bm25 = bm25_score(sent, query_words_list, avg_dl)

        # Индикаторы
        indicators = score_by_indicators(sent, q_type)

        # Длина (оптимум 15-50 слов)
        wc = analysis['word_count']
        length_score = min(1.0, wc / 15) if wc < 15 else (1.0 if wc <= 50 else max(0.5, 50 / wc))

        total = tfidf * 0.4 + bm25 * 0.2 + indicators * 0.2 + length_score * 0.2
        scored.append((total, sent))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored]


def extract_with_comprehensive_ranking(web_data, query, top_n=3):
    """Извлечение через комплексное ранжирование"""
    q_type = determine_question_type_v2(query)
    query_words = build_query_words(query)
    all_sents = []

    for src in web_data.get('results', []):
        sents = split_into_sentences(src['text'])
        all_sents.extend(sents)

    ranked = rank_sentences_comprehensive(all_sents, query_words, q_type)
    unique = deduplicate_sentences(ranked[:top_n * 2])[:top_n]

    if not unique:
        return ''
    return truncate_to_sentence(' '.join(unique), MAX_ANSWER_LEN)


# БЛОК 116: Дополнительные методы АНАЛИЗА ТЕКСТА

def count_question_marks(text):
    """Подсчёт вопросительных знаков"""
    return text.count('?')


def count_exclamation_marks(text):
    """Подсчёт восклицательных знаков"""
    return text.count('!')


def count_digits(text):
    """Подсчёт цифр"""
    return sum(1 for c in text if c.isdigit())


def get_capital_ratio(text):
    """Доля заглавных букв"""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)


def detect_language_mix(text):
    """Определяет смешивание языков"""
    ru = len(re.findall(r'[а-яёА-ЯЁ]', text))
    en = len(re.findall(r'[a-zA-Z]', text))
    total = ru + en
    if total == 0:
        return {'ru': 0.0, 'en': 0.0, 'other': 1.0}
    other = len(text) - total
    return {'ru': ru/total, 'en': en/total, 'other': other/total}


def extract_first_definition_sentence(text):
    """Извлекает первое предложение-определение (с 'это', 'является', 'is a')"""
    sents = split_into_sentences(text)
    def_patterns = [
        re.compile(r'.{5,}\s+[-—–]\s+.{10,}', re.I),
        re.compile(r'.{5,}\s+(?:это|является|есть)\s+.{10,}', re.I),
        re.compile(r'.{5,}\s+(?:is\s+a|is\s+an|is\s+the)\s+.{10,}', re.I),
    ]
    for sent in sents:
        for pat in def_patterns:
            if pat.match(sent):
                return sent
    return sents[0] if sents else ''


def get_summary_sentences(text, n=3):
    """Возвращает n наиболее информативных предложений"""
    sents = remove_noise_sentences(split_into_sentences(text))
    if not sents:
        return []
    summary = extractive_summarize(text, n_sentences=n)
    return split_into_sentences(summary)[:n]


# БЛОК 117: Специализированный обработчик вопросов "что такое"
class DefinitionExtractor:
    """
    Специализированный извлекатель определений.
    Работает с вопросами типа 'что такое X', 'что значит X'.
    """

    DEFINITION_PATTERNS = [
        re.compile(r'([А-ЯЁA-Z].{3,30})\s+[-—–]\s+(.{15,200}?)(?:[.!?]|$)', re.I),
        re.compile(r'(.{3,30})\s+(?:это|есть)\s+(.{15,200}?)(?:[.!?]|$)', re.I),
        re.compile(r'(.{3,30})\s+(?:является|представляет\s+собой)\s+(.{15,200}?)(?:[.!?]|$)', re.I),
        re.compile(r'(.{3,30})\s+(?:is\s+a|is\s+an|is\s+the)\s+(.{15,200}?)(?:[.!?]|$)', re.I),
        re.compile(r'(?:definition|определение)[^:]*:\s*(.{15,200}?)(?:[.!?]|$)', re.I),
    ]

    def __init__(self, web_data, query):
        self.web_data = web_data
        self.query = query
        self.subject = self._extract_subject()
        self.combined = web_data.get('combined_text', '')

    def _extract_subject(self):
        """Извлекает субъект вопроса"""
        q = self.query.lower()
        markers = ['что такое ', 'что значит ', 'что означает ', 'what is ', 'define ']
        for m in markers:
            if q.startswith(m):
                return self.query[len(m):].strip()
        return self.query

    def extract_definition(self):
        """Ищет определение субъекта в тексте"""
        # Сначала ищем прямое определение
        if self.subject:
            direct = extract_definition_pattern(self.combined, self.subject)
            if direct and len(direct) >= 20:
                return direct

        # Потом через паттерны
        for pat in self.DEFINITION_PATTERNS:
            m = pat.search(self.combined)
            if m:
                try:
                    definition = m.group(2).strip()
                    if len(definition) >= 20:
                        return definition
                except IndexError:
                    pass

        # Резервный: TF-IDF
        return extract_with_tfidf(self.web_data, self.query, top_n=2)

    def build_definition_answer(self):
        """Строит полный ответ-определение"""
        defn = self.extract_definition()
        if not defn:
            return ''

        # Форматируем
        if self.subject and not defn.lower().startswith(self.subject.lower()):
            return f"{self.subject} — {defn}"
        return defn


# БЛОК 118: Проверка синтаксиса Python
def validate_python_snippet(code):
    """
    Проверяет синтаксис Python-кода.
    Возвращает (is_valid, error_message).
    """
    import ast
    try:
        ast.parse(code)
        return True, 'OK'
    except SyntaxError as e:
        return False, str(e)


# БЛОК 119: Расширенный help
EXTENDED_HELP_TEXT = """
╔══════════════════════════════════════════════════════════╗
║     AI — Умная система поиска ответов в интернете       ║
║                     Версия {version}                       ║
╚══════════════════════════════════════════════════════════╝

ИСПОЛЬЗОВАНИЕ:
  python ai.py                    → интерактивный режим
  python ai.py "вопрос"           → один вопрос
  python ai.py --demo             → демонстрация
  python ai.py --test             → тест системы
  python ai.py --diag             → диагностика
  python ai.py -b questions.txt   → пакетный режим

В PYTHON:
  from ai import ask, ask_smart_v2, ask_ensemble, q
  
  ask("что такое ДНК")            → поиск в интернете
  ask_smart_v2("кто Ньютон")      → умный поиск (7 алгоритмов)
  ask_ensemble("столица Франции") → ансамблевый поиск
  q("15 + 27")                    → вычисление: 15.0 + 27.0 = 42
  
  ask_batch(["вопрос 1", ...])    → пакетный запрос
  ask_from_file("questions.txt")  → из файла

ИНТЕРАКТИВНЫЕ КОМАНДЫ:
  /help     — эта справка
  /stats    — статистика сессии
  /cache    — список кэшированных запросов
  /clear    — очистить кэш
  /demo     — запустить 3 демо-вопроса
  /test     — тест классификатора
  /diag     — диагностика системы
  /ver      — версия
  /json Q   — ответ в JSON формате
  /md Q     — ответ в Markdown формате
  /facts Q  — извлечь факты из текстов
  /ent Q    — извлечь именованные сущности
  /math E   — вычислить математику
  /conv V N — конвертировать единицы
  выход     — завершить

ПРИМЕРЫ ВОПРОСОВ:
  Что такое нейронная сеть?
  Кто создал Python?
  Когда родился Эйнштейн?
  Где находится Большой Барьерный риф?
  Сколько планет в Солнечной системе?
  Почему небо синее?
  Как работает интернет?
  5 + 3         (математика — без интернета)
  100 км в мили (конвертация — без интернета)

АЛГОРИТМЫ ИЗВЛЕЧЕНИЯ:
  1. AnswerProcessor (специализация по типу вопроса)
  2. TF-IDF (частотный анализ)
  3. Скользящее контекстное окно
  4. MMR (максимальная маргинальная релевантность)
  5. BM25 (взвешенное TF-IDF)
  6. Стемматизация (морфология)
  7. Приоритет лучших источников

ТИПЫ ВОПРОСОВ (автоопределение):
  who      — кто (персоны, организации)
  what     — что (определения, понятия)
  when     — когда (даты, годы)
  where    — где (места, географии)
  how_many — сколько (числа, размеры)
  why      — почему (причины)
  how      — как (методы, процессы)

ВЫВОД:
  Все ответы сохраняются в main.txt
  Каждый ответ содержит: вопрос, ответ, источники

""".format(version=__version__)


def show_extended_help():
    """Выводит расширенную справку"""
    print(EXTENDED_HELP_TEXT)


# БЛОК 120: Финальная точка входа


# =================================================================================
# БЛОК 121: МЕГА-СЛОВАРЬ СИНОНИМОВ ДЛЯ РАСШИРЕНИЯ ПОИСКА (500+ записей)
# =================================================================================

# Расширенный словарь для expand_query
QUERY_EXPAND_MAP_V2 = {
    # Персоны и биографии
    'родился': ['born', 'дата рождения', 'год рождения', 'birth year'],
    'умер': ['died', 'дата смерти', 'год смерти', 'death year', 'скончался'],
    'биография': ['biography', 'жизнеописание', 'жизнь', 'life story'],
    'изобретатель': ['inventor', 'создатель', 'creator', 'разработчик'],
    'первооткрыватель': ['discoverer', 'первый', 'first to discover'],
    'лауреат': ['laureate', 'нобелевский лауреат', 'Nobel laureate', 'winner'],
    'академик': ['academician', 'член академии', 'professor'],
    # Места
    'столица': ['capital', 'capital city', 'главный город', 'административный центр'],
    'страна': ['country', 'state', 'nation', 'государство'],
    'город': ['city', 'town', 'municipality', 'urban area'],
    'регион': ['region', 'province', 'territory', 'область'],
    'континент': ['continent', 'материк', 'часть света'],
    'океан': ['ocean', 'море', 'sea', 'водоём'],
    'гора': ['mountain', 'peak', 'вершина', 'summit'],
    'река': ['river', 'водоём', 'tributaries'],
    'озеро': ['lake', 'водоём', 'reservoir', 'водохранилище'],
    'пустыня': ['desert', 'засушливая территория'],
    # Науки
    'физика': ['physics', 'физическая наука', 'physical science'],
    'химия': ['chemistry', 'chemical science', 'химическая наука'],
    'биология': ['biology', 'life science', 'biological science'],
    'математика': ['mathematics', 'math', 'mathematical science'],
    'астрономия': ['astronomy', 'astrophysics', 'space science'],
    'геология': ['geology', 'earth science'],
    'экология': ['ecology', 'environmental science'],
    'психология': ['psychology', 'behavioral science'],
    'экономика': ['economics', 'economic science', 'financial science'],
    'история': ['history', 'historical science', 'historical study'],
    'лингвистика': ['linguistics', 'language science', 'language study'],
    'социология': ['sociology', 'social science'],
    # Технологии
    'компьютер': ['computer', 'вычислительная машина', 'ЭВМ'],
    'интернет': ['internet', 'web', 'WWW', 'сеть'],
    'искусственный интеллект': ['AI', 'artificial intelligence', 'machine learning', 'ML'],
    'нейросеть': ['neural network', 'deep learning', 'нейронная сеть'],
    'блокчейн': ['blockchain', 'distributed ledger', 'криптовалюта'],
    'программирование': ['programming', 'coding', 'software development'],
    'алгоритм': ['algorithm', 'procedure', 'method', 'technique'],
    # Медицина
    'вирус': ['virus', 'патоген', 'pathogen', 'viral infection'],
    'бактерия': ['bacteria', 'bacterium', 'microorganism'],
    'вакцина': ['vaccine', 'vaccination', 'иммунизация'],
    'антибиотик': ['antibiotic', 'antibacterial', 'antimicrobial'],
    'симптом': ['symptom', 'признак', 'sign', 'manifestation'],
    'диагноз': ['diagnosis', 'постановка диагноза', 'diagnostic'],
    'лечение': ['treatment', 'therapy', 'cure', 'healing', 'терапия'],
    # Физика
    'скорость': ['velocity', 'speed', 'rate', 'pace'],
    'масса': ['mass', 'weight', 'вес', 'gravity'],
    'энергия': ['energy', 'мощность', 'power'],
    'сила': ['force', 'strength', 'мощь'],
    'температура': ['temperature', 'heat', 'тепло', 'coolness', 'холод'],
    'давление': ['pressure', 'напряжение', 'tension'],
    'электричество': ['electricity', 'electrical', 'electric current'],
    'магнетизм': ['magnetism', 'magnetic', 'magnetism'],
    # Химия
    'элемент': ['element', 'chemical element', 'атом', 'atom'],
    'молекула': ['molecule', 'compound', 'вещество'],
    'реакция': ['reaction', 'chemical reaction', 'химическая реакция'],
    'раствор': ['solution', 'растворение', 'dissolve'],
    'кислота': ['acid', 'кислотный', 'acidic'],
    'основание': ['base', 'alkali', 'щёлочь', 'alkaline'],
    # Биология
    'ДНК': ['DNA', 'дезоксирибонуклеиновая кислота', 'deoxynucleic acid', 'генетический материал'],
    'РНК': ['RNA', 'рибонуклеиновая кислота', 'ribonucleic acid'],
    'клетка': ['cell', 'биологическая клетка', 'biological cell'],
    'ген': ['gene', 'генетика', 'genetics', 'heredity', 'наследственность'],
    'эволюция': ['evolution', 'evolve', 'natural selection', 'естественный отбор'],
    'экосистема': ['ecosystem', 'ecology', 'habitat', 'среда обитания'],
    'фотосинтез': ['photosynthesis', 'хлорофилл', 'chlorophyll'],
    # Космос
    'планета': ['planet', 'celestial body', 'небесное тело'],
    'звезда': ['star', 'stellar', 'солнечный'],
    'галактика': ['galaxy', 'galactic', 'Milky Way', 'Млечный путь'],
    'чёрная дыра': ['black hole', 'сингулярность', 'singularity'],
    'астероид': ['asteroid', 'meteor', 'метеор', 'метеорит'],
    'комета': ['comet', 'астероид', 'хвостатая звезда'],
    'квазар': ['quasar', 'квазизвёздный объект', 'quasi-stellar'],
    # Культура
    'фильм': ['film', 'movie', 'кино', 'cinema', 'кинофильм'],
    'книга': ['book', 'novel', 'роман', 'литература', 'произведение'],
    'музыка': ['music', 'song', 'melody', 'musical', 'musical composition'],
    'живопись': ['painting', 'картина', 'изобразительное искусство'],
    'скульптура': ['sculpture', 'statue', 'статуя', 'монумент'],
    'архитектура': ['architecture', 'building', 'здание', 'строительство'],
    'театр': ['theater', 'theatre', 'спектакль', 'пьеса', 'drama'],
    'балет': ['ballet', 'dance', 'танец', 'хореография'],
    # Спорт
    'футбол': ['football', 'soccer', 'association football'],
    'баскетбол': ['basketball', 'NBA', 'FIBA'],
    'теннис': ['tennis', 'wimbledon', 'ATP', 'WTA'],
    'хоккей': ['hockey', 'ice hockey', 'NHL'],
    'лёгкая атлетика': ['athletics', 'track and field', 'sprint', 'marathon'],
    'олимпиада': ['Olympics', 'Olympic Games', 'Олимпийские игры'],
    'чемпионат': ['championship', 'tournament', 'соревнование'],
    'рекорд': ['record', 'world record', 'мировой рекорд', 'achievement'],
    # Еда
    'витамин': ['vitamin', 'питательное вещество', 'nutrient'],
    'белок': ['protein', 'протеин', 'аминокислота', 'amino acid'],
    'углевод': ['carbohydrate', 'сахар', 'sugar', 'starch'],
    'жир': ['fat', 'lipid', 'масло', 'oil'],
    'калория': ['calorie', 'энергетическая ценность', 'kilocalorie', 'kcal'],
    'рецепт': ['recipe', 'как приготовить', 'cooking', 'приготовление'],
    # Право и политика
    'закон': ['law', 'legislation', 'act', 'statute', 'норма права'],
    'конституция': ['constitution', 'основной закон', 'fundamental law'],
    'право': ['right', 'legal right', 'entitlement'],
    'суд': ['court', 'tribunal', 'judiciary', 'судебная система'],
    'демократия': ['democracy', 'democratic', 'народовластие'],
    'монархия': ['monarchy', 'королевство', 'kingdom', 'empire'],
    'республика': ['republic', 'republican', 'government'],
    # Экономика
    'ВВП': ['GDP', 'Gross Domestic Product', 'валовый внутренний продукт'],
    'инфляция': ['inflation', 'рост цен', 'price growth'],
    'банк': ['bank', 'banking', 'финансовое учреждение'],
    'акция': ['stock', 'share', 'equity', 'ценная бумага'],
    'облигация': ['bond', 'debt instrument', 'ценная бумага'],
    'рынок': ['market', 'marketplace', 'биржа'],
}


def expand_query_v3(query):
    """Самая расширенная версия расширения запроса (500+ синонимов)"""
    expanded = expand_query_v2(query)
    q_lower = query.lower()
    extra = []
    for key, syns in QUERY_EXPAND_MAP_V2.items():
        if key.lower() in q_lower:
            extra.extend(syns[:1])
    if extra:
        expanded += ' ' + ' '.join(extra[:3])
    return expanded.strip()


# =================================================================================
# БЛОК 122: ДОПОЛНИТЕЛЬНЫЕ РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ
# =================================================================================

# Паттерны для улучшенного извлечения дат
_DATE_EXTRACTORS = {
    'year_range': re.compile(r'\b(\d{4})\s*[-–—]\s*(\d{4})\b'),
    'year_simple': re.compile(r'\b([12]\d{3})\b'),
    'month_year_ru': re.compile(
        r'\b(январ\w*|феврал\w*|март\w*|апрел\w*|май|маем|июн\w*|июл\w*|'
        r'август\w*|сентябр\w*|октябр\w*|ноябр\w*|декабр\w*)'
        r'\s+(\d{4})\b', re.I),
    'month_year_en': re.compile(
        r'\b(January|February|March|April|May|June|July|August|'
        r'September|October|November|December)\s+(\d{4})\b', re.I),
    'decade': re.compile(r'\b(\d{4})[-е]?е\s*(?:годы|годов)\b', re.I),
    'century_ru': re.compile(r'\b([IVXLCDM]+)\s+(?:век|столетие)', re.I),
    'century_en': re.compile(r'\b(\d+)(?:st|nd|rd|th)\s+century\b', re.I),
    'bc_ad': re.compile(r'\b(\d+)\s*(?:до\s+н\.?\s*э\.?|BC|BCE)\b', re.I),
}


def extract_all_time_data(text):
    """Извлекает все временные данные из текста"""
    result = {}
    for name, pat in _DATE_EXTRACTORS.items():
        found = pat.findall(text)
        if found:
            if isinstance(found[0], tuple):
                result[name] = ['-'.join(f) for f in found[:5]]
            else:
                result[name] = found[:5]
    return result


# =================================================================================
# БЛОК 123: ФИНАЛЬНАЯ ТОЧКА ВХОДА С ВЫБОРОМ ЛУЧШЕГО МЕТОДА
# =================================================================================

def smart_main():
    """
    Умная точка входа. Автоматически выбирает лучший метод.
    Поддерживает все режимы и опции.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='AI — Умный поиск ответов в интернете v' + __version__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python ai.py "кто такой Ньютон"
  python ai.py --ensemble "как работает квантовый компьютер"
  python ai.py --demo
  python ai.py --batch questions.txt
  python ai.py --test
        """
    )
    parser.add_argument('question', nargs='*', help='Вопрос для поиска')
    parser.add_argument('--ensemble', action='store_true', help='Ансамблевый метод (7 алгоритмов)')
    parser.add_argument('--smart', action='store_true', help='Умный метод (по умолчанию)')
    parser.add_argument('--bilingual', action='store_true', help='Двуязычный поиск')
    parser.add_argument('--iterative', action='store_true', help='Итеративный поиск')
    parser.add_argument('--demo', action='store_true', help='Демо-режим')
    parser.add_argument('--test', action='store_true', help='Тестирование системы')
    parser.add_argument('--diag', action='store_true', help='Диагностика')
    parser.add_argument('--batch', '-b', metavar='FILE', help='Пакетный режим из файла')
    parser.add_argument('--version', '-v', action='store_true', help='Версия')
    parser.add_argument('--help-extended', action='store_true', help='Расширенная справка')
    parser.add_argument('--quiet', '-q', action='store_true', help='Тихий режим')

    # Если аргументов нет — интерактивный режим
    if len(sys.argv) == 1:
        interactive_mode_final()
        return

    args = parser.parse_args()
    verbose = not args.quiet

    if args.version:
        print(f"AI v{__version__}")
        return

    if args.help_extended:
        show_extended_help()
        return

    if args.demo:
        run_demo(n=5, verbose=verbose)
        return

    if args.test:
        run_all_unit_tests(verbose=True)
        evaluate_classifier_full()
        run_linguistic_tests(verbose=True)
        return

    if args.diag:
        diagnose_system()
        return

    if args.batch:
        ask_from_file(args.batch)
        return

    if args.question:
        question = ' '.join(args.question)
        if args.ensemble:
            ask_ensemble(question, verbose=verbose)
        elif args.bilingual:
            ask_bilingual(question, verbose=verbose)
        elif args.iterative:
            ask_iterative(question, verbose=verbose)
        else:
            ask_smart_v2(question, verbose=verbose)
    else:
        interactive_mode_final()




# ==============================================================================
# ТОЧКА ВХОДА — ФИНАЛЬНАЯ (единственная настоящая)
# ==============================================================================

def _try_math_extended(query: str):
    """
    Расширенный math-детектор: обрабатывает вопросы вида
    'Сколько будет 10 + 1?', 'Чему равно 5 * 7?', '2 в степени 8' и т.д.
    Возвращает красивый ответ типа '10 + 1 = 11' или None.
    """
    # Убираем вопросительные слова и знаки
    STRIP_PREFIXES = [
        r'сколько\s+будет\s+', r'чему\s+равно\s+', r'посчитай\s+',
        r'вычисли\s+', r'сколько\s+', r'calculate\s+', r'what\s+is\s+',
        r'реши\s+', r'посчитайте\s+', r'сколько\s+получится\s+',
        r'сколько\s+это\s+', r'equals?\s+', r'result\s+of\s+',
    ]
    clean = query.strip().rstrip('?!.').strip()
    for pref in STRIP_PREFIXES:
        clean = re.sub(pref, '', clean, flags=re.I).strip()

    result = calculate_simple(clean)
    if result:
        # Форматируем красиво: "10 + 1 = 11" → убираем .0 если не нужно
        result = re.sub(r'(\d+)\.0\b', r'\1', result)
        return result

    # Попробуем оригинальный запрос
    result = calculate_simple(query)
    if result:
        result = re.sub(r'(\d+)\.0\b', r'\1', result)
        return result

    return None


def _is_garbage_answer(answer: str, query: str) -> bool:
    """
    Проверяет, является ли ответ явным мусором со страниц сайтов.
    Только действительно явный UI-мусор, НЕ фильтрует нормальный текст.
    """
    if not answer or len(answer) < 10:
        return True

    # Очень специфичный мусор (UI элементы, кнопки, куки)
    garbage_patterns = [
        r'^reply\s+\w+',                    # начинается с "reply Алиса"
        r'^назад\s+сколько',                # начинается с "назад Сколько"
        r'осталось\s+до\s+лета',
        r'добавить\s+в\s+корзину',
        r'оформить\s+заказ',
        r'войти\s+в\s+(систему|аккаунт)',
        r'^(все права защищены|all rights reserved)',
        r'^(privacy policy|terms of use|cookie policy)',
        r'^\s*©\s*\d{4}',
    ]
    low = answer.lower().strip()
    for pat in garbage_patterns:
        if re.search(pat, low, re.I):
            return True

    return False


def _format_clean_answer(query: str, answer: str, sources_count: int) -> str:
    """
    Форматирует финальный вывод в стиле 'короткий и по делу',
    как ChatGPT: без лишнего мусора, чисто.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = "=" * 60
    lines = [
        sep,
        f"Запрос:   {query}",
        f"Дата:     {now}",
        f"Источников обработано: {sources_count}",
        "-" * 60,
        "ОТВЕТ:",
        "",
        answer,
        sep,
    ]
    return "\n".join(lines)


def smart_main():
    """
    Умная главная точка входа.
    Обрабатывает аргументы командной строки,
    применяет math-детектор, фильтрует мусор,
    выдаёт чистый короткий ответ.
    """
    if len(sys.argv) > 1:
        raw_arg = sys.argv[1].lower().strip()

        # Служебные флаги
        if raw_arg in ('-h', '--help', 'help', 'справка', 'помощь'):
            show_help()
            return
        if raw_arg == '--demo':
            run_demo(n=5, verbose=True)
            return
        if raw_arg == '--test':
            run_all_unit_tests(verbose=True)
            return
        if raw_arg == '--diag':
            diagnose_system()
            return
        if raw_arg in ('-b', '--batch') and len(sys.argv) > 2:
            ask_from_file(sys.argv[2])
            return
        if raw_arg == '--version':
            print(f"AI v{VERSION}")
            return

        question = ' '.join(sys.argv[1:]).strip()

        # 1. Сначала пробуем математику
        math_ans = _try_math_extended(question)
        if math_ans:
            report = _format_clean_answer(question, math_ans, 0)
            init_output_file()
            save_to_file(report)
            print(report)
            return

        # 2. Ищем в интернете через ask_ensemble
        init_output_file()
        t0 = time.time()
        expanded = expand_query_v2(question)
        web_data = collect_web_texts_robust(expanded, verbose=False)

        answer = ""
        sources_count = web_data.get("sources_count", 0)

        if web_data.get("results"):
            q_type = determine_question_type_v2(question)
            answer = ensemble_extract(web_data, question, q_type, verbose=False)
            answer = postprocess_answer(answer, question)

            # Проверяем на мусор
            if _is_garbage_answer(answer, question):
                # Пробуем postprocess_answer_v2 как запасной вариант
                answer = postprocess_answer_v2(answer, question, q_type)

            if _is_garbage_answer(answer, question):
                answer = ""

        if not answer:
            if not web_data.get("results"):
                answer = "Нет подключения к интернету или не удалось найти информацию."
            else:
                answer = "Не удалось найти точный ответ по данному запросу."

        # Очищаем .0 из чисел
        answer = re.sub(r'(\d+)\.0\b', r'\1', answer)

        report = _format_clean_answer(question, answer, sources_count)
        save_to_file(report)
        print(report)

    else:
        interactive_mode_final()


if __name__ == "__main__":
    smart_main()
