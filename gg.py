# gg.py — Модуль NLP, извлечения и обработки текста
# Версия 4.0.0 | очищенный модуль | все алгоритмы извлечения ответов
# Используется: finally.py, start.py, main.py
# НЕ ПЕРЕИМЕНОВЫВАТЬ

from __future__ import annotations
import re, math, sys, time, random, hashlib, json, os
from typing import Optional
from collections import Counter, defaultdict

# ════════════════════════════════════════════════════════════
#  СТОП-СЛОВА РУССКОГО ЯЗЫКА (700+ слов)
# ════════════════════════════════════════════════════════════
STOPWORDS_RU = frozenset({
    # Предлоги
    "в", "на", "по", "за", "из", "от", "до", "со", "из-за", "из-под",
    "без", "для", "про", "над", "под", "при", "через", "между", "около",
    "вокруг", "после", "перед", "кроме", "вместо", "вдоль", "поперёк",
    "согласно", "благодаря", "вопреки", "ввиду", "вследствие", "насчёт",
    "относительно", "касательно",
    # Союзы
    "и", "а", "но", "или", "что", "как", "если", "то", "да", "же",
    "хотя", "пока", "когда", "потому", "поэтому", "чтобы", "однако",
    "зато", "либо", "ни", "ни...ни", "также", "тоже", "притом", "при этом",
    "причём", "итак", "следовательно", "тем не менее", "несмотря на",
    "даже", "ведь", "ибо", "коль", "раз", "либо", "будто", "словно",
    # Местоимения
    "я", "ты", "он", "она", "оно", "мы", "вы", "они",
    "мне", "тебе", "ему", "ей", "нам", "вам", "им",
    "меня", "тебя", "его", "её", "нас", "вас", "их",
    "мной", "тобой", "им", "ней", "нами", "вами", "ими",
    "себя", "себе", "собой",
    "мой", "твой", "свой", "наш", "ваш", "их",
    "моя", "твоя", "своя", "наша", "ваша",
    "моё", "твоё", "своё", "наше", "ваше",
    "мои", "твои", "свои", "наши", "ваши",
    "это", "этот", "эта", "эти", "то", "тот", "та", "те",
    "такой", "такая", "такое", "такие", "сам", "сама", "само", "сами",
    "весь", "вся", "всё", "все", "всего", "всей", "всех",
    "каждый", "каждая", "каждое", "каждые",
    "любой", "любая", "любое", "любые",
    "другой", "другая", "другое", "другие",
    "некоторый", "некоторая", "некоторое", "некоторые",
    "никакой", "никакая", "никакое", "никакие",
    # Глаголы-связки и вспомогательные
    "быть", "есть", "был", "была", "было", "были", "будет", "будут",
    "буду", "будешь", "будем", "будете", "является", "являются",
    "являлся", "являлась", "являлось", "являлись",
    "стать", "стал", "стала", "стало", "стали",
    "иметь", "имеет", "имеют", "имел", "имела", "имело", "имели",
    "можно", "нельзя", "нужно", "надо", "следует",
    "может", "могут", "мочь", "мог", "могла", "могло", "могли",
    "должен", "должна", "должно", "должны",
    "хочет", "хотят", "хочу", "хотел", "хотела",
    # Частицы и наречия
    "не", "ни", "да", "нет", "вот", "вон", "бы", "бы", "ли",
    "же", "ведь", "уж", "лишь", "только", "именно", "даже", "ещё",
    "уже", "всё", "всегда", "никогда", "иногда", "часто", "редко",
    "очень", "весьма", "довольно", "слишком", "совсем", "почти",
    "примерно", "около", "приблизительно", "приблизительно",
    "здесь", "там", "тут", "туда", "сюда", "отсюда", "оттуда",
    "вверх", "вниз", "вперёд", "назад", "влево", "вправо",
    "сейчас", "сегодня", "вчера", "завтра", "тогда", "теперь",
    "потом", "после", "прежде", "сначала", "наконец",
    "также", "тоже", "так", "иначе", "иначе", "просто",
    "вообще", "особенно", "например", "кстати",
    # Числительные (часто не несут смысловой нагрузки)
    "один", "одна", "одно", "одни", "два", "две", "три", "четыре",
    "пять", "шесть", "семь", "восемь", "девять", "десять",
    "первый", "первая", "первое", "первые",
    "второй", "вторая", "второе", "вторые",
    # Вводные слова
    "конечно", "видимо", "кажется", "пожалуй", "наверное",
    "возможно", "вероятно", "действительно", "безусловно",
    "разумеется", "несомненно", "безусловно", "очевидно",
    # Сокращения и служебные
    "руб", "тыс", "млн", "млрд", "чел", "т", "кг", "г", "м", "км",
    "см", "мм", "л", "мл", "га", "кв", "куб",
    # Веб-мусор
    "главная", "страница", "сайт", "сайте", "меню", "навигация",
    "поиск", "найти", "войти", "войти", "регистрация", "подписка",
    "скачать", "загрузить", "читать", "ещё", "подробнее",
    "смотреть", "слушать", "купить", "цена", "стоимость",
    "бесплатно", "акция", "скидка", "заказать", "контакты",
    "адрес", "телефон", "email", "карта", "схема",
})

# ════════════════════════════════════════════════════════════
#  СТОП-СЛОВА АНГЛИЙСКОГО ЯЗЫКА (300+ слов)
# ════════════════════════════════════════════════════════════
STOPWORDS_EN = frozenset({
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at",
    "to", "for", "of", "with", "by", "from", "up", "about", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "out", "off", "over", "under", "again", "further", "then", "once",
    "is", "am", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing",
    "will", "would", "shall", "should", "may", "might", "must", "can", "could",
    "not", "no", "nor", "so", "yet", "both", "either", "neither",
    "this", "that", "these", "those", "what", "which", "who", "whom",
    "whose", "when", "where", "why", "how",
    "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "than", "too", "very", "just", "because", "as",
    "until", "while", "although", "though", "since", "unless",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "s", "t", "d", "ll", "m", "re", "ve", "ain",
    "also", "however", "therefore", "thus", "hence", "furthermore",
    "moreover", "nevertheless", "nonetheless", "otherwise", "instead",
    "meanwhile", "subsequently", "accordingly", "consequently",
    "like", "etc", "eg", "ie", "vs", "via",
})

# ════════════════════════════════════════════════════════════
#  ПАТТЕРНЫ КЛАССИФИКАЦИИ ВОПРОСОВ
# ════════════════════════════════════════════════════════════

QUESTION_PATTERNS = {
    "definition": [
        r"что\s+(такое|означает|значит|обозначает)",
        r"(значение|смысл|определение|понятие|расшифровка)\s+слова",
        r"(аббревиатура|сокращение|обозначение)",
        r"что\s+значит\s+[A-ZА-Я]{2,}",
        r"расшифруй|расшифровать|объясни значение",
        r"что\s+такое\s+[A-ZА-Я]{2,}",
        r"(?:что|чем)\s+(?:является|представляет собой)",
    ],
    "who": [
        r"кто\s+(такой|такая|это|был|была|есть|такие)",
        r"(биография|жизнь|личность)\s+(кого|чья)",
        r"(создатель|основатель|автор|изобретатель)\s+(кто|какой|чей)",
        r"кто\s+(?:написал|создал|основал|изобрёл|открыл)",
        r"кому\s+принадлежит",
        r"чья\s+(идея|разработка|компания)",
    ],
    "where": [
        r"где\s+(находится|расположен|расположена|расположено|живёт|работает)",
        r"(столица|центр|адрес|местонахождение)",
        r"в\s+какой\s+(стране|городе|регионе)",
        r"куда\s+(идти|ехать|смотреть)",
        r"откуда\s+(родом|берётся|происходит)",
    ],
    "when": [
        r"когда\s+(был|была|было|были|произошло|случилось|возник|появился|создан)",
        r"в\s+каком\s+(году|веке|периоде|месяце)",
        r"(дата|год|время|период)\s+(создания|основания|рождения|смерти|события)",
        r"сколько\s+лет\s+(назад|тому назад)",
        r"до\s+или\s+после",
    ],
    "how": [
        r"как\s+(работает|устроен|сделать|приготовить|получить|установить|настроить)",
        r"(способ|метод|инструкция|руководство|алгоритм)",
        r"каким\s+(образом|способом)",
        r"как\s+(?:можно|лучше|правильно|быстро)",
        r"каков\s+(процесс|порядок|механизм)",
    ],
    "why": [
        r"почему|зачем|из-за\s+чего|по\s+какой\s+причине",
        r"причина|объяснение|из-за|вследствие",
        r"для\s+чего\s+(нужно|служит|используется)",
        r"в\s+чём\s+(смысл|причина|цель)",
    ],
    "comparison": [
        r"(лучше|хуже|отличается|разница|сравнение|versus|против|или)",
        r"чем\s+(лучше|хуже|отличается)",
        r"(плюсы|минусы|преимущества|недостатки)",
        r"(vs\.?|versus|vs|против)\s+",
        r"что\s+(выбрать|предпочесть)",
    ],
    "how_much": [
        r"сколько\s+(стоит|стоило|цена|зарабатывает|получает|весит|длится)",
        r"(цена|стоимость|тариф|зарплата|доход)\s+(чего|кого|какая)",
        r"(размер|объём|вес|высота|длина|площадь|население)",
    ],
    "what": [  # Общий тип по умолчанию
        r"что\s+",
        r"какой|какая|какое|какие",
        r"каков|какова|каково|каковы",
    ],
}

# ════════════════════════════════════════════════════════════
#  ПАТТЕРНЫ ИЗВЛЕЧЕНИЯ ОТВЕТОВ ПО ТИПУ ВОПРОСА
# ════════════════════════════════════════════════════════════

# Паттерны для извлечения определений
DEFINITION_PATTERNS = [
    r"(?:это|является|представляет собой|называется|обозначает|означает)\s+(.{20,200}?)(?:[.!?]|$)",
    r"([А-ЯA-Z][^.!?]{15,200}?)\s*—\s*([^.!?]{10,200}?)(?:[.!?]|$)",
    r"([А-ЯA-Z][^.!?]{10,150}?)\s+(?:это|является|есть)\s+([^.!?]{10,200}?)(?:[.!?]|$)",
    r"(?:термин|понятие|слово|аббревиатура)\s+[«\"']?(\w+)[«\"']?\s+(?:означает|обозначает)\s+(.{15,200}?)(?:[.!?]|$)",
    r"расшифровывается\s+как\s+(.{10,150}?)(?:[.!?]|$)",
    r"(?:происходит от|берёт начало от|образован от)\s+(.{10,100}?)(?:[.!?]|$)",
    r"аббревиатура\s+[«\"']?([A-ZА-Я]+)[«\"']?\s+(?:от|означает|это)\s+(.{10,150}?)(?:[.!?]|$)",
]

# Паттерны для дат и цифр
DATE_PATTERNS = [
    r"\b(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})\s*(?:года|г\.?)?\b",
    r"\b(\d{4})\s*(?:год|г\.?)\b",
    r"\b(в|с|до|после)\s+(\d{4})\s*(?:году|г\.?)\b",
    r"\b(\d{1,2})[./](\d{1,2})[./](\d{2,4})\b",
    r"\b(\d{4})[-–—](\d{4})\b",
    r"(?:в|с)\s+(\d{1,2})\s+(?:столетии|веке)\b",
]

# Паттерны для чисел и статистики
NUMBER_PATTERNS = [
    r"\b(\d[\d\s,.]*)\s*(?:млрд|миллиард[а-я]*)\b",
    r"\b(\d[\d\s,.]*)\s*(?:млн|миллион[а-я]*)\b",
    r"\b(\d[\d\s,.]*)\s*(?:тыс|тысяч[а-я]*)\b",
    r"\b(\d[\d\s,.]*)\s*(?:руб|рублей|рубл[а-я]*)\b",
    r"\b(\d[\d\s,.]*)\s*(?:долларов|долл\.|USD)\b",
    r"\b(\d[\d\s,.]*)\s*(?:евро|EUR)\b",
    r"\b(\d[\d\s,.]*)\s*(?:человек|чел\.?|людей)\b",
    r"\b(\d[\d\s,.]*)\s*(?:км|километр[а-я]*)\b",
    r"\b(\d[\d\s,.]*)\s*(?:кг|килограмм[а-я]*)\b",
    r"\b(\d[\d\s,.]*)\s*(?:лет|год[а-я]*)\b",
    r"(\d+(?:[.,]\d+)?)\s*%",
]

# Паттерны для имён людей
PERSON_PATTERNS = [
    r"\b([А-Я][а-я]+\s+[А-Я][а-я]+(?:\s+[А-Я][а-я]+)?)\b",
    r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b",
    r"(?:президент|министр|директор|основатель|автор|создатель)\s+([А-Я][а-я]+\s+[А-Я][а-я]+)",
]

# Паттерны для географии
GEO_PATTERNS = [
    r"столица\s+(?:[А-Яа-я\s]+?)\s*(?:—|это|является)\s*([А-Я][а-я]+)",
    r"([А-Я][а-я]+)\s+(?:—|является)\s+столицей",
    r"(?:город|страна|регион|область|район)\s+([А-Я][а-я]+)",
    r"расположен(?:а|о)?\s+в\s+([А-Я][а-я]+(?:\s+[А-Я][а-я]+)?)",
    r"находится\s+в\s+([А-Я][а-я]+(?:\s+[А-Я][а-я]+)?)",
]

# ════════════════════════════════════════════════════════════
#  КЛАССИФИКАЦИЯ ВОПРОСА
# ════════════════════════════════════════════════════════════

def classify_question(query: str) -> str:
    """
    Определяет тип вопроса.
    Возвращает: definition, who, where, when, how, why,
               comparison, how_much, math, what
    """
    q = query.lower().strip()
    # Математика — проверяем в первую очередь
    if re.search(r'[\d]+\s*[+\-*/×÷^%]\s*[\d]+', q):
        return "math"
    if re.search(r'(?:сколько будет|вычисли|посчитай|корень|логарифм)', q):
        return "math"
    # Остальные типы
    for qtype, patterns in QUESTION_PATTERNS.items():
        if qtype == "what":
            continue  # Оставляем "what" как fallback
        for pat in patterns:
            if re.search(pat, q, re.IGNORECASE):
                return qtype
    # "what" как default
    return "what"

def is_definition_question(query: str) -> bool:
    """Проверяет, спрашивает ли пользователь о значении/определении."""
    return classify_question(query) == "definition"

def extract_key_subject(query: str) -> str:
    """
    Извлекает ключевое слово/тему из запроса.
    Убирает вопросительные слова.
    """
    q = query.strip()
    for trigger in [
        "что означает", "что значит", "что такое",
        "кто такой", "кто такая", "кто это",
        "где находится", "когда был", "когда была",
        "как работает", "почему", "зачем",
        "сколько стоит", "сколько будет",
        "расшифровка", "определение",
    ]:
        if trigger in q.lower():
            rest = re.sub(re.escape(trigger), "", q, flags=re.IGNORECASE).strip(" ?!.")
            if rest:
                return rest
    # Убираем вопросительные слова в начале
    q = re.sub(r'^(?:что|кто|где|когда|как|почему|зачем|сколько|какой|какая|какое|какие|каков|какова)\s+', "", q, flags=re.IGNORECASE)
    return q.strip(" ?!.")

# ════════════════════════════════════════════════════════════
#  БАЗОВАЯ ОБРАБОТКА ТЕКСТА
# ════════════════════════════════════════════════════════════

def normalize_text(text: str) -> str:
    """Нормализует текст: унифицирует кавычки, тире, пробелы."""
    if not text:
        return ""
    # Нормализация кавычек
    text = re.sub(r'[«»„""]', '"', text)
    # Нормализация тире
    text = re.sub(r'[–—−]', '-', text)
    # Нормализация пробелов
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def remove_html_artifacts(text: str) -> str:
    """Убирает остатки HTML в тексте."""
    if not text:
        return ""
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&apos;', "'", text)
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'&\w+;', '', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    return text

def clean_text(text: str) -> str:
    """Полная очистка текста для NLP-обработки."""
    if not text:
        return ""
    text = remove_html_artifacts(text)
    text = normalize_text(text)
    # Убираем URL
    text = re.sub(r'https?://\S+', ' ', text)
    # Убираем email
    text = re.sub(r'\S+@\S+\.\S+', ' ', text)
    # Убираем чрезмерное повторение символов
    text = re.sub(r'(.)\1{4,}', r'\1\1\1', text)
    # Убираем строки только из спецсимволов
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        if len(re.findall(r'[А-ЯЁа-яёA-Za-z0-9]', line)) > len(line) * 0.3:
            clean_lines.append(line)
    text = '\n'.join(clean_lines)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_sentences(text: str) -> list:
    """
    Умное разбиение текста на предложения.
    Учитывает аббревиатуры, числа с точкой, инициалы.
    """
    if not text:
        return []
    # Защита аббревиатур от разбивки
    abbrevs = [
        r'\b(т\.?к)\.',  r'\b(т\.?е)\.',  r'\b(т\.?п)\.',
        r'\b(и\.?т\.?д)\.',  r'\b(и\.?т\.?п)\.',
        r'\b(и\.?пр)\.',  r'\b(ср)\.',  r'\b(см)\.',
        r'\b(рис)\.',  r'\b(табл)\.',  r'\b(стр)\.',
        r'\b(г)\.',  r'\b(гг)\.',  r'\b(руб)\.',
        r'\b(коп)\.',  r'\b(тыс)\.',  r'\b(млн)\.',
        r'\b(млрд)\.',  r'\b(ул)\.',  r'\b(пр)\.',
        r'\b(просп)\.',  r'\b(бул)\.',  r'\b(пер)\.',
        r'\b(д)\.',  r'\b(кв)\.',  r'\b(оф)\.',
        r'\b(п)\.',  r'\b(пп)\.',  r'\b(ст)\.',
        r'\b(вв)\.',  r'\b(гг)\.',  r'\b(гр)\.',
        r'\b([А-Я])\.',  # Инициалы
        r'\b(\d+)\.',  # Числа в списках (1. 2. и т.д.)
    ]
    placeholders = {}
    for i, pat in enumerate(abbrevs):
        def replacer(m, idx=i):
            key = f"__ABB{idx}_{m.start()}__"
            placeholders[key] = m.group(0)
            return key
        text = re.sub(pat, replacer, text)
    # Разбивка на предложения
    parts = re.split(r'(?<=[.!?])\s+(?=[А-ЯA-Z0-9"«\(])', text)
    # Восстановление аббревиатур
    result = []
    for part in parts:
        for key, val in placeholders.items():
            part = part.replace(key, val)
        part = part.strip()
        if len(part) >= 15:
            result.append(part)
    return result

def tokenize_text(text: str, remove_stopwords: bool = True) -> list:
    """
    Токенизирует текст в список значимых слов.
    Убирает стоп-слова если remove_stopwords=True.
    """
    tokens = re.findall(r'\b[а-яёa-z]{2,}\b', text.lower())
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS_RU and t not in STOPWORDS_EN]
    return tokens

def get_ngrams(tokens: list, n: int = 2) -> list:
    """Создаёт n-граммы из списка токенов."""
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def language_detect(text: str) -> str:
    """
    Простое определение языка текста.
    Возвращает 'ru', 'en' или 'mixed'.
    """
    ru_chars = len(re.findall(r'[а-яёА-ЯЁ]', text))
    en_chars = len(re.findall(r'[a-zA-Z]', text))
    total = ru_chars + en_chars
    if total == 0:
        return "unknown"
    ru_ratio = ru_chars / total
    if ru_ratio > 0.7:
        return "ru"
    elif ru_ratio < 0.3:
        return "en"
    return "mixed"

# ════════════════════════════════════════════════════════════
#  TF-IDF РЕАЛИЗАЦИЯ
# ════════════════════════════════════════════════════════════

class TFIDF:
    """
    Полная реализация TF-IDF для поиска релевантных предложений.
    """

    def __init__(self):
        self.docs: list[list[str]] = []
        self.df: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.n_docs: int = 0

    def fit(self, documents: list):
        """
        Обучает TF-IDF на корпусе документов.
        documents — список строк (предложений/абзацев).
        """
        self.docs = [tokenize_text(doc) for doc in documents]
        self.n_docs = len(self.docs)
        # Document frequency
        self.df = {}
        for doc_tokens in self.docs:
            for token in set(doc_tokens):
                self.df[token] = self.df.get(token, 0) + 1
        # Inverse document frequency
        self.idf = {}
        for token, freq in self.df.items():
            self.idf[token] = math.log((self.n_docs + 1) / (freq + 1)) + 1.0

    def tf(self, tokens: list) -> dict:
        """Вычисляет TF для списка токенов."""
        counts = Counter(tokens)
        total = max(1, len(tokens))
        return {t: c / total for t, c in counts.items()}

    def tfidf_vector(self, text: str) -> dict:
        """Вычисляет TF-IDF вектор для текста."""
        tokens = tokenize_text(text)
        tf_vals = self.tf(tokens)
        vector = {}
        for token, tf_val in tf_vals.items():
            idf_val = self.idf.get(token, math.log(self.n_docs + 2) + 1.0)
            vector[token] = tf_val * idf_val
        return vector

    def cosine_similarity(self, v1: dict, v2: dict) -> float:
        """Косинусное сходство двух TF-IDF векторов."""
        if not v1 or not v2:
            return 0.0
        keys = set(v1) & set(v2)
        if not keys:
            return 0.0
        dot = sum(v1[k] * v2[k] for k in keys)
        norm1 = math.sqrt(sum(x * x for x in v1.values()))
        norm2 = math.sqrt(sum(x * x for x in v2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def rank_sentences(self, query: str, sentences: list) -> list:
        """
        Ранжирует предложения по релевантности к запросу.
        Возвращает список (предложение, оценка) отсортированный по убыванию.
        """
        if not sentences:
            return []
        query_vec = self.tfidf_vector(query)
        ranked = []
        for sent in sentences:
            sent_vec = self.tfidf_vector(sent)
            score = self.cosine_similarity(query_vec, sent_vec)
            ranked.append((sent, score))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    def top_sentences(self, query: str, sentences: list, n: int = 5) -> list:
        """Возвращает топ-N релевантных предложений."""
        ranked = self.rank_sentences(query, sentences)
        return [sent for sent, score in ranked[:n] if score > 0]

# ════════════════════════════════════════════════════════════
#  BM25 РЕАЛИЗАЦИЯ
# ════════════════════════════════════════════════════════════

class BM25:
    """
    Реализация алгоритма BM25 (Okapi BM25) для ранжирования документов.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: list[list[str]] = []
        self.df: dict[str, int] = {}
        self.idf: dict[str, float] = {}
        self.avgdl: float = 0.0
        self.n_docs: int = 0
        self.doc_lengths: list[int] = []

    def fit(self, documents: list):
        """Обучает BM25 на корпусе."""
        self.docs = [tokenize_text(doc) for doc in documents]
        self.n_docs = len(self.docs)
        self.doc_lengths = [len(doc) for doc in self.docs]
        self.avgdl = sum(self.doc_lengths) / max(1, self.n_docs)
        # Document frequency
        self.df = {}
        for doc_tokens in self.docs:
            for token in set(doc_tokens):
                self.df[token] = self.df.get(token, 0) + 1
        # IDF
        self.idf = {}
        for token, freq in self.df.items():
            self.idf[token] = math.log(
                (self.n_docs - freq + 0.5) / (freq + 0.5) + 1
            )

    def score(self, query_tokens: list, doc_idx: int) -> float:
        """Вычисляет BM25-оценку для одного документа."""
        if doc_idx >= len(self.docs):
            return 0.0
        doc_tokens = self.docs[doc_idx]
        doc_len = self.doc_lengths[doc_idx]
        tf_map = Counter(doc_tokens)
        score = 0.0
        for token in query_tokens:
            tf = tf_map.get(token, 0)
            if tf == 0:
                continue
            idf = self.idf.get(token, 0.0)
            tf_norm = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * doc_len / max(1, self.avgdl))
            )
            score += idf * tf_norm
        return score

    def rank_documents(self, query: str) -> list:
        """
        Ранжирует все документы по BM25.
        Возвращает список (индекс, оценка) по убыванию.
        """
        query_tokens = tokenize_text(query)
        scores = [
            (i, self.score(query_tokens, i))
            for i in range(self.n_docs)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def top_documents(self, query: str, docs: list, n: int = 5) -> list:
        """Возвращает топ-N документов по BM25."""
        if not docs:
            return []
        self.fit(docs)
        ranked = self.rank_documents(query)
        result = []
        for idx, score in ranked[:n]:
            if idx < len(docs) and score > 0:
                result.append(docs[idx])
        return result

    def best_sentence(self, query: str, text: str) -> str:
        """Находит лучшее предложение в тексте по BM25."""
        sentences = split_sentences(text)
        if not sentences:
            return ""
        top = self.top_documents(query, sentences, n=1)
        return top[0] if top else ""

# ════════════════════════════════════════════════════════════
#  MMR — МАКСИМАЛЬНАЯ МАРГИНАЛЬНАЯ РЕЛЕВАНТНОСТЬ
# ════════════════════════════════════════════════════════════

class MMR:
    """
    Maximum Marginal Relevance — выбирает разнообразные релевантные предложения.
    Избегает дублирования информации.
    """

    def __init__(self, lambda_param: float = 0.5):
        self.lambda_param = lambda_param
        self.tfidf = TFIDF()

    def select(self, query: str, sentences: list, n: int = 5) -> list:
        """
        Выбирает N разнообразных предложений по MMR.
        """
        if not sentences:
            return []
        self.tfidf.fit(sentences)
        query_vec = self.tfidf.tfidf_vector(query)
        sent_vecs = [self.tfidf.tfidf_vector(s) for s in sentences]
        selected = []
        selected_vecs = []
        remaining = list(range(len(sentences)))
        for _ in range(min(n, len(sentences))):
            best_idx = -1
            best_score = float('-inf')
            for idx in remaining:
                relevance = self.tfidf.cosine_similarity(query_vec, sent_vecs[idx])
                if selected_vecs:
                    redundancy = max(
                        self.tfidf.cosine_similarity(sent_vecs[idx], sel_vec)
                        for sel_vec in selected_vecs
                    )
                else:
                    redundancy = 0.0
                score = (self.lambda_param * relevance -
                         (1 - self.lambda_param) * redundancy)
                if score > best_score:
                    best_score = score
                    best_idx = idx
            if best_idx >= 0:
                selected.append(sentences[best_idx])
                selected_vecs.append(sent_vecs[best_idx])
                remaining.remove(best_idx)
        return selected

# ════════════════════════════════════════════════════════════
#  ИЗВЛЕЧЕНИЕ ОТВЕТОВ ПО ТИПУ ВОПРОСА
# ════════════════════════════════════════════════════════════

def extract_definition_answer(text: str, keyword: str) -> str:
    """
    Извлекает определение ключевого слова из текста.
    Особенно хорошо работает для Wikipedia-стиля.
    """
    if not text or not keyword:
        return ""
    keyword_lower = keyword.lower().strip()
    sentences = split_sentences(text)
    # Ищем предложение которое содержит слово и является определением
    best = ""
    best_score = -1
    definition_indicators = [
        "означает", "обозначает", "значит", "является", "представляет собой",
        "это", "—", "-", "называется", "определяется как", "расшифровывается",
        "аббревиатура", "сокращение от", "происходит от",
    ]
    for sent in sentences:
        sent_lower = sent.lower()
        kw_present = keyword_lower in sent_lower
        # Частичное совпадение (для коротких аббревиатур)
        partial = any(keyword_lower[:3] in w for w in sent_lower.split()) if len(keyword_lower) >= 3 else False
        if not kw_present and not partial:
            continue
        score = 0.0
        # Бонус за каждый индикатор определения
        for ind in definition_indicators:
            if ind in sent_lower:
                score += 0.2
        # Бонус за наличие ключевого слова в начале предложения
        if sent_lower.strip().startswith(keyword_lower):
            score += 0.5
        # Бонус за разумную длину
        words = len(sent.split())
        if 8 <= words <= 60:
            score += 0.3
        if score > best_score:
            best_score = score
            best = sent
    if best:
        return best[:400]
    # Fallback: первое предложение содержащее ключевое слово
    for sent in sentences:
        if keyword_lower in sent.lower():
            return sent[:400]
    # Fallback: первые 2 предложения
    return " ".join(sentences[:2])[:400] if sentences else ""

def extract_who_answer(text: str, query: str) -> str:
    """
    Извлекает ответ для вопросов "кто такой X?".
    Ищет биографическую информацию.
    """
    if not text:
        return ""
    subject = extract_key_subject(query)
    sentences = split_sentences(text)
    bio_words = ["родился", "родилась", "биография", "карьера", "деятельность",
                 "основал", "создал", "написал", "прославился", "известен",
                 "является", "был", "стал", "работал", "учился"]
    best_sents = []
    for sent in sentences[:20]:
        sent_lower = sent.lower()
        if subject.lower() in sent_lower:
            bio_count = sum(1 for w in bio_words if w in sent_lower)
            if bio_count > 0 or sent == sentences[0]:
                best_sents.append(sent)
        if len(best_sents) >= 3:
            break
    if best_sents:
        return " ".join(best_sents[:2])[:400]
    return " ".join(sentences[:2])[:400]

def extract_where_answer(text: str, query: str) -> str:
    """
    Извлекает ответ для вопросов "где находится X?".
    Ищет географическую информацию.
    """
    if not text:
        return ""
    subject = extract_key_subject(query)
    sentences = split_sentences(text)
    geo_words = ["расположен", "находится", "является", "столица", "город",
                 "страна", "регион", "территория", "координаты", "площадь",
                 "население", "расположена", "расположено"]
    for sent in sentences[:15]:
        sent_lower = sent.lower()
        if subject.lower() in sent_lower:
            geo_count = sum(1 for w in geo_words if w in sent_lower)
            if geo_count > 0:
                return sent[:400]
    # Fallback
    for sent in sentences[:15]:
        if any(w in sent.lower() for w in geo_words):
            return sent[:400]
    return " ".join(sentences[:2])[:400]

def extract_when_answer(text: str, query: str) -> str:
    """
    Извлекает ответ для вопросов "когда X?".
    Ищет даты и временные указатели.
    """
    if not text:
        return ""
    sentences = split_sentences(text)
    subject = extract_key_subject(query)
    date_indicators = ["году", "г.", "лет", "веке", "столетии", "января",
                       "февраля", "марта", "апреля", "мая", "июня", "июля",
                       "августа", "сентября", "октября", "ноября", "декабря",
                       "дата", "основан", "создан", "родился", "открыт"]
    for sent in sentences[:20]:
        sent_lower = sent.lower()
        subj_present = subject.lower() in sent_lower if subject else True
        date_present = any(d in sent_lower for d in date_indicators)
        has_number = bool(re.search(r'\b\d{4}\b', sent))
        if (subj_present or not subject) and (date_present or has_number):
            return sent[:400]
    return " ".join(sentences[:2])[:400]

def extract_how_answer(text: str, query: str) -> str:
    """
    Извлекает ответ для вопросов "как работает/делается X?".
    Ищет процессы и инструкции.
    """
    if not text:
        return ""
    sentences = split_sentences(text)
    process_words = ["процесс", "этап", "шаг", "сначала", "затем", "потом",
                     "далее", "следующий", "метод", "способ", "алгоритм",
                     "принцип", "механизм", "система", "работает", "функционирует"]
    best_sents = []
    for sent in sentences[:20]:
        sent_lower = sent.lower()
        proc_count = sum(1 for w in process_words if w in sent_lower)
        if proc_count >= 1 and len(sent.split()) >= 8:
            best_sents.append(sent)
        if len(best_sents) >= 3:
            break
    if best_sents:
        return " ".join(best_sents[:2])[:400]
    return " ".join(sentences[:3])[:400]

def extract_why_answer(text: str, query: str) -> str:
    """
    Извлекает ответ для вопросов "почему/зачем X?".
    """
    if not text:
        return ""
    sentences = split_sentences(text)
    cause_words = ["потому что", "по причине", "из-за", "вследствие",
                   "поэтому", "причина", "связано с", "обусловлено",
                   "объясняется", "является следствием", "зависит от"]
    for sent in sentences[:20]:
        sent_lower = sent.lower()
        if any(cw in sent_lower for cw in cause_words):
            return sent[:400]
    return " ".join(sentences[:2])[:400]

def extract_comparison_answer(text: str, query: str) -> str:
    """
    Извлекает ответ для сравнительных вопросов.
    """
    if not text:
        return ""
    sentences = split_sentences(text)
    comp_words = ["лучше", "хуже", "превосходит", "уступает", "отличается",
                  "преимущество", "недостаток", "плюс", "минус", "по сравнению",
                  "в отличие", "тогда как", "в то время как", "versus",
                  "сравнивая", "однако", "зато", "хотя"]
    best_sents = []
    for sent in sentences[:25]:
        sent_lower = sent.lower()
        comp_count = sum(1 for w in comp_words if w in sent_lower)
        if comp_count >= 1 and len(sent.split()) >= 8:
            best_sents.append((sent, comp_count))
    if best_sents:
        best_sents.sort(key=lambda x: x[1], reverse=True)
        return " ".join(s for s, _ in best_sents[:2])[:400]
    return " ".join(sentences[:3])[:400]

def extract_generic_answer(text: str, query: str) -> str:
    """
    Универсальное извлечение ответа через TF-IDF.
    Используется для общих вопросов.
    """
    if not text or not query:
        return ""
    sentences = split_sentences(text)
    if not sentences:
        return ""
    tfidf = TFIDF()
    tfidf.fit(sentences)
    ranked = tfidf.rank_sentences(query, sentences)
    top = [s for s, score in ranked[:3] if score > 0.05]
    if not top:
        return sentences[0][:400] if sentences else ""
    return top[0][:400]

# ════════════════════════════════════════════════════════════
#  ГЛАВНАЯ ФУНКЦИЯ ИЗВЛЕЧЕНИЯ ОТВЕТА
# ════════════════════════════════════════════════════════════

def extract_answer(text: str, query: str,
                   question_type: str = "what") -> str:
    """
    Главная функция извлечения ответа.
    Выбирает алгоритм в зависимости от типа вопроса.
    """
    if not text:
        return ""
    if question_type == "definition":
        keyword = extract_key_subject(query)
        return extract_definition_answer(text, keyword)
    elif question_type == "who":
        return extract_who_answer(text, query)
    elif question_type == "where":
        return extract_where_answer(text, query)
    elif question_type == "when":
        return extract_when_answer(text, query)
    elif question_type == "how":
        return extract_how_answer(text, query)
    elif question_type == "why":
        return extract_why_answer(text, query)
    elif question_type == "comparison":
        return extract_comparison_answer(text, query)
    else:
        return extract_generic_answer(text, query)

# ════════════════════════════════════════════════════════════
#  АНСАМБЛЕВОЕ ИЗВЛЕЧЕНИЕ ОТВЕТА
# ════════════════════════════════════════════════════════════

def ensemble_extract(texts: list, query: str,
                     question_type: str = "what",
                     n_candidates: int = 5) -> str:
    """
    Ансамблевое извлечение ответа из множества текстов.
    Использует несколько алгоритмов и выбирает лучший.
    """
    if not texts:
        return ""
    all_sentences = []
    for text in texts:
        sents = split_sentences(text)
        all_sentences.extend([s for s in sents if len(s) >= 30])
    if not all_sentences:
        return ""
    candidates = {}
    # 1. TF-IDF
    try:
        tfidf = TFIDF()
        tfidf.fit(all_sentences)
        ranked = tfidf.rank_sentences(query, all_sentences)
        if ranked:
            candidates["tfidf"] = ranked[0][0]
    except Exception:
        pass
    # 2. BM25
    try:
        bm25 = BM25()
        bm25.fit(all_sentences)
        bm25_ranked = bm25.rank_documents(query)
        if bm25_ranked:
            best_idx = bm25_ranked[0][0]
            if best_idx < len(all_sentences):
                candidates["bm25"] = all_sentences[best_idx]
    except Exception:
        pass
    # 3. Тип-специфичное извлечение
    combined_text = " ".join(texts[:3])
    type_answer = extract_answer(combined_text, query, question_type)
    if type_answer:
        candidates["type_specific"] = type_answer
    # 4. MMR
    try:
        mmr = MMR()
        mmr_sents = mmr.select(query, all_sentences[:50], n=3)
        if mmr_sents:
            candidates["mmr"] = mmr_sents[0]
    except Exception:
        pass
    # 5. Первый абзац лучшего источника
    if texts:
        first_sents = split_sentences(texts[0])
        if first_sents:
            candidates["first"] = first_sents[0]
    if not candidates:
        return all_sentences[0][:400] if all_sentences else ""
    # Голосование: выбираем ответ по качеству
    return _vote_best_answer(candidates, query, question_type)

def _vote_best_answer(candidates: dict, query: str,
                      question_type: str) -> str:
    """
    Голосование за лучший кандидат ответа.
    """
    if not candidates:
        return ""
    query_words = set(tokenize_text(query))
    scored = []
    for method, answer in candidates.items():
        if not answer or len(answer) < 20:
            continue
        score = 0.0
        # Качество по словам запроса
        answer_words = set(tokenize_text(answer))
        overlap = len(query_words & answer_words) / max(1, len(query_words))
        score += overlap * 0.4
        # Длина (предпочитаем средние ответы)
        words = len(answer.split())
        if 10 <= words <= 60:
            score += 0.3
        elif words < 10:
            score -= 0.2
        # Тип-специфичный бонус
        if method == "type_specific":
            score += 0.2
        # Не должен заканчиваться на запятую или союз
        if answer.rstrip()[-1] in [',', ';', 'и', 'а', 'но']:
            score -= 0.3
        # Должен начинаться с заглавной буквы
        stripped = answer.strip()
        if stripped and stripped[0].isupper():
            score += 0.1
        # Проверяем на мусор
        if _is_noise_sentence(answer):
            score -= 0.5
        scored.append((answer, score, method))
    if not scored:
        return list(candidates.values())[0][:400]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0][:400]

def _is_noise_sentence(text: str) -> bool:
    """
    Проверяет, является ли предложение мусором.
    """
    if not text:
        return True
    text_lower = text.lower()
    noise_patterns = [
        r'cookie|cookies|куки',
        r'подписать|подписка|subscribe',
        r'войти|вход|login|sign in',
        r'javascript|js-',
        r'privacy policy|политика конфиденциальности',
        r'©|copyright|все права',
        r'рекламн|advertisement',
        r'loading\.\.\.|загрузка\.\.\.',
        r'click here|нажмите здесь',
        r'error 4\d\d|ошибка 4\d\d',
        r'page not found|страница не найдена',
    ]
    for pat in noise_patterns:
        if re.search(pat, text_lower):
            return True
    # Проверяем на слишком много специальных символов
    special_ratio = len(re.findall(r'[^а-яёА-ЯЁa-zA-Z0-9\s.,!?;:()\-–—«»"\']+', text)) / max(1, len(text))
    if special_ratio > 0.3:
        return True
    return False

# ════════════════════════════════════════════════════════════
#  ОЦЕНКА КАЧЕСТВА ОТВЕТА
# ════════════════════════════════════════════════════════════

def estimate_answer_quality(answer: str, query: str,
                            question_type: str = "what") -> float:
    """
    Оценивает качество ответа по нескольким критериям.
    Возвращает оценку 0.0–1.0.
    """
    if not answer or len(answer) < 20:
        return 0.0
    score = 0.5  # Базовый балл
    # Пересечение с запросом
    q_tokens = set(tokenize_text(query))
    a_tokens = set(tokenize_text(answer))
    if q_tokens:
        overlap = len(q_tokens & a_tokens) / len(q_tokens)
        score += overlap * 0.3
    # Длина ответа
    words = len(answer.split())
    if question_type == "definition":
        if 15 <= words <= 80:
            score += 0.2
        elif words < 10:
            score -= 0.3
    elif question_type in ["who", "where", "when"]:
        if 10 <= words <= 60:
            score += 0.2
    else:
        if 8 <= words <= 100:
            score += 0.1
    # Полнота предложения
    if answer.strip()[-1] in ['.', '!', '?']:
        score += 0.1
    else:
        score -= 0.1
    # Начало с заглавной буквы
    if answer.strip()[0].isupper():
        score += 0.05
    # Мусор
    if _is_noise_sentence(answer):
        score -= 0.5
    return max(0.0, min(1.0, score))

def filter_answer_candidates(candidates: list, query: str,
                              min_quality: float = 0.3) -> list:
    """
    Фильтрует кандидатов ответа по минимальному качеству.
    """
    result = []
    for candidate in candidates:
        q = estimate_answer_quality(candidate, query)
        if q >= min_quality:
            result.append((candidate, q))
    result.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in result]

# ════════════════════════════════════════════════════════════
#  ПОСТОБРАБОТКА ОТВЕТА
# ════════════════════════════════════════════════════════════

def postprocess_answer(answer: str, query: str = "") -> str:
    """
    Финальная обработка ответа:
    - Убирает мусор
    - Исправляет пробелы
    - Обрезает до нужной длины
    """
    if not answer:
        return ""
    # Убираем HTML
    answer = re.sub(r'<[^>]+>', ' ', answer)
    # Нормализуем пробелы
    answer = re.sub(r'\s+', ' ', answer).strip()
    # Убираем URL
    answer = re.sub(r'https?://\S+', '', answer).strip()
    # Убираем лишние знаки в начале
    answer = re.sub(r'^[.,;:!?—\-–]+\s*', '', answer)
    # Убираем незакрытые скобки
    if answer.count('(') != answer.count(')'):
        answer = re.sub(r'\([^)]*$', '', answer).strip()
    if answer.count('[') != answer.count(']'):
        answer = re.sub(r'\[[^\]]*$', '', answer).strip()
    # Если ответ обрывается — обрезаем до последнего законченного предложения
    if len(answer) > 50 and answer[-1] not in '.!?':
        last_punct = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
        if last_punct > len(answer) // 2:
            answer = answer[:last_punct + 1]
    # Первая буква заглавная
    if answer and answer[0].islower():
        answer = answer[0].upper() + answer[1:]
    return answer.strip()

def truncate_answer(answer: str, max_words: int = 80,
                    max_chars: int = 500) -> str:
    """
    Обрезает слишком длинный ответ.
    """
    if not answer:
        return ""
    words = answer.split()
    if len(words) > max_words:
        # Обрезаем до последнего предложения в пределах max_words
        cut = " ".join(words[:max_words])
        last_punct = max(cut.rfind('.'), cut.rfind('!'), cut.rfind('?'))
        if last_punct > len(cut) // 2:
            cut = cut[:last_punct + 1]
        answer = cut
    if len(answer) > max_chars:
        last_punct = max(answer[:max_chars].rfind('.'),
                        answer[:max_chars].rfind('!'),
                        answer[:max_chars].rfind('?'))
        if last_punct > 0:
            answer = answer[:last_punct + 1]
        else:
            answer = answer[:max_chars] + "..."
    return answer

# ════════════════════════════════════════════════════════════
#  СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ АББРЕВИАТУР
# ════════════════════════════════════════════════════════════

# Известные аббревиатуры и их значения
KNOWN_ABBREVS = {
    "HI": "Hi — это английское приветствие, аналог «Привет». Используется в неформальном общении.",
    "OK": "OK (Okay) — означает «хорошо», «согласен», «всё в порядке». Происходит от английского all correct.",
    "AI": "AI (Artificial Intelligence) — искусственный интеллект. Раздел компьютерных наук, создание машин способных выполнять задачи требующие человеческого интеллекта.",
    "IT": "IT (Information Technology) — информационные технологии. Применение компьютеров и телекоммуникаций для хранения, обработки и передачи информации.",
    "API": "API (Application Programming Interface) — программный интерфейс приложения. Позволяет программам взаимодействовать друг с другом.",
    "URL": "URL (Uniform Resource Locator) — унифицированный указатель ресурса. Адрес веб-страницы или файла в интернете.",
    "HTML": "HTML (HyperText Markup Language) — язык разметки гипертекста. Основной язык для создания веб-страниц.",
    "CSS": "CSS (Cascading Style Sheets) — каскадные таблицы стилей. Язык описания внешнего вида веб-страницы.",
    "GPU": "GPU (Graphics Processing Unit) — графический процессор. Специализированный процессор для обработки графики.",
    "CPU": "CPU (Central Processing Unit) — центральный процессор. Основная вычислительная микросхема компьютера.",
    "RAM": "RAM (Random Access Memory) — оперативная память. Быстрая память для временного хранения данных программ.",
    "SSD": "SSD (Solid State Drive) — твёрдотельный накопитель. Устройство хранения данных без движущихся частей.",
    "HDD": "HDD (Hard Disk Drive) — жёсткий диск. Устройство хранения данных на магнитных пластинах.",
    "VPN": "VPN (Virtual Private Network) — виртуальная частная сеть. Защищённый зашифрованный канал в интернете.",
    "WiFi": "Wi-Fi — беспроводная технология передачи данных по радиоканалу стандарта IEEE 802.11.",
    "WIFI": "Wi-Fi — беспроводная технология передачи данных по радиоканалу стандарта IEEE 802.11.",
    "USB": "USB (Universal Serial Bus) — универсальная последовательная шина. Стандарт подключения периферийных устройств.",
    "LED": "LED (Light Emitting Diode) — светодиод. Полупроводниковый прибор, преобразующий электрический ток в свет.",
    "LCD": "LCD (Liquid Crystal Display) — жидкокристаллический дисплей. Технология экранов на основе жидких кристаллов.",
    "OLED": "OLED (Organic Light Emitting Diode) — органический светодиод. Технология дисплеев без подсветки.",
    "HTTP": "HTTP (HyperText Transfer Protocol) — протокол передачи гипертекста. Основной протокол интернета.",
    "HTTPS": "HTTPS (HTTP Secure) — защищённый HTTP. Протокол с шифрованием для безопасной передачи данных.",
    "FTP": "FTP (File Transfer Protocol) — протокол передачи файлов. Стандарт обмена файлами в сети.",
    "SSH": "SSH (Secure Shell) — протокол безопасного удалённого управления компьютером.",
    "DNS": "DNS (Domain Name System) — система доменных имён. Преобразует доменные имена в IP-адреса.",
    "IP": "IP (Internet Protocol) — интернет-протокол. Базовый протокол сети интернет.",
    "SQL": "SQL (Structured Query Language) — язык структурированных запросов. Для работы с реляционными базами данных.",
    "JSON": "JSON (JavaScript Object Notation) — текстовый формат обмена данными, основанный на JavaScript.",
    "XML": "XML (Extensible Markup Language) — расширяемый язык разметки для хранения и передачи данных.",
    "PDF": "PDF (Portable Document Format) — формат переносимых документов от Adobe. Сохраняет форматирование на любом устройстве.",
    "JPG": "JPG/JPEG — формат сжатия изображений с потерями. Широко используется для фотографий.",
    "JPEG": "JPEG — формат сжатия изображений. Оптимален для фотографий, поддерживает миллионы цветов.",
    "PNG": "PNG (Portable Network Graphics) — формат изображений без потерь. Поддерживает прозрачность.",
    "GIF": "GIF (Graphics Interchange Format) — формат анимированных изображений с палитрой 256 цветов.",
    "MP3": "MP3 — формат сжатия аудио. Самый распространённый формат для хранения музыки.",
    "MP4": "MP4 — цифровой контейнер для мультимедиа. Поддерживает видео, аудио и субтитры.",
    "ZIP": "ZIP — формат архивирования и сжатия файлов. Один из наиболее популярных форматов архивов.",
    "QR": "QR-код (Quick Response) — двумерный штрихкод для быстрого считывания смартфоном.",
    "NFC": "NFC (Near Field Communication) — связь ближнего поля. Беспроводная технология для передачи данных на расстоянии до 20 см.",
    "GPS": "GPS (Global Positioning System) — глобальная система позиционирования. Навигационная спутниковая система США.",
    "ВВП": "ВВП — валовой внутренний продукт. Суммарная стоимость всех товаров и услуг произведённых в стране за год.",
    "ВВС": "ВВС — Военно-воздушные силы. Вид вооружённых сил предназначенный для действий в воздушном пространстве.",
    "МВД": "МВД — Министерство внутренних дел. Федеральный орган исполнительной власти России.",
    "ФСБ": "ФСБ — Федеральная служба безопасности. Основная спецслужба России.",
    "МЧС": "МЧС — Министерство по делам гражданской обороны, чрезвычайным ситуациям и ликвидации последствий стихийных бедствий.",
    "РФ": "РФ — Российская Федерация. Официальное название России.",
    "США": "США — Соединённые Штаты Америки. Государство в Северной Америке.",
    "ООН": "ООН — Организация Объединённых Наций. Международная организация основанная в 1945 году.",
    "НАТО": "НАТО — Организация Североатлантического договора (NATO). Военно-политический альянс.",
    "ЕС": "ЕС — Европейский союз. Политическое и экономическое объединение 27 европейских государств.",
    "СССР": "СССР — Союз Советских Социалистических Республик. Советское государство существовавшее в 1922–1991 годах.",
    "РПЦ": "РПЦ — Русская православная церковь. Крупнейшая православная церковь в мире.",
    "СМИ": "СМИ — средства массовой информации. Телевидение, радио, газеты, интернет-издания.",
    "ДНК": "ДНК — дезоксирибонуклеиновая кислота. Молекула содержащая генетическую информацию организма.",
    "РНК": "РНК — рибонуклеиновая кислота. Молекула участвующая в синтезе белков.",
    "КПД": "КПД — коэффициент полезного действия. Отношение полезной работы к затраченной энергии.",
    "ЭВМ": "ЭВМ — электронно-вычислительная машина. Устаревшее название компьютера.",
    "ПК": "ПК — персональный компьютер. Вычислительная машина предназначенная для индивидуального использования.",
    "ОС": "ОС — операционная система. Комплекс программ управляющих компьютером.",
    "ЦП": "ЦП — центральный процессор. Основная вычислительная микросхема компьютера.",
}

def check_known_abbreviation(query: str) -> str:
    """
    Проверяет, является ли запрос вопросом об известной аббревиатуре.
    Возвращает готовый ответ или пустую строку.
    """
    q = query.strip()
    # Извлекаем аббревиатуру из вопроса
    for trigger in ["что означает", "что значит", "что такое", "расшифровка"]:
        if trigger in q.lower():
            rest = q.lower().split(trigger, 1)[1].strip(" ?!.")
            abbrev = rest.upper().strip()
            if abbrev in KNOWN_ABBREVS:
                return KNOWN_ABBREVS[abbrev]
    # Проверяем если сам запрос - аббревиатура
    words = q.strip(" ?!.").upper().split()
    for w in words:
        if w in KNOWN_ABBREVS and len(words) <= 2:
            return KNOWN_ABBREVS[w]
    return ""

# ════════════════════════════════════════════════════════════
#  ОБЪЕДИНЕНИЕ ТЕКСТОВ ИЗ РАЗНЫХ ИСТОЧНИКОВ
# ════════════════════════════════════════════════════════════

def merge_texts_by_relevance(texts: list, query: str,
                              max_total: int = 30000) -> str:
    """
    Объединяет тексты отсортированные по релевантности.
    Наиболее релевантные — в начале.
    """
    if not texts:
        return ""
    scored = []
    query_tokens = set(tokenize_text(query))
    for text in texts:
        text_tokens = set(tokenize_text(text[:2000]))
        if query_tokens:
            overlap = len(query_tokens & text_tokens) / len(query_tokens)
        else:
            overlap = 0.5
        scored.append((text, overlap))
    scored.sort(key=lambda x: x[1], reverse=True)
    parts = []
    total = 0
    for text, _ in scored:
        available = max_total - total
        if available <= 0:
            break
        chunk = text[:available]
        parts.append(chunk)
        total += len(chunk)
    return "\n---\n".join(parts)

def get_relevant_passages(text: str, query: str,
                           n: int = 3, window: int = 3) -> list:
    """
    Извлекает N наиболее релевантных отрывков из текста.
    Каждый отрывок — окно из window предложений.
    """
    sentences = split_sentences(text)
    if not sentences:
        return []
    tfidf = TFIDF()
    tfidf.fit(sentences)
    query_vec = tfidf.tfidf_vector(query)
    scored = []
    for i in range(len(sentences)):
        window_text = " ".join(sentences[max(0, i-window//2):i+window//2+1])
        window_vec = tfidf.tfidf_vector(window_text)
        score = tfidf.cosine_similarity(query_vec, window_vec)
        scored.append((i, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    result = []
    used_indices = set()
    for idx, _ in scored:
        if any(abs(idx - u) < window for u in used_indices):
            continue
        start = max(0, idx - window // 2)
        end = min(len(sentences), idx + window // 2 + 1)
        passage = " ".join(sentences[start:end])
        result.append(passage)
        used_indices.add(idx)
        if len(result) >= n:
            break
    return result

# ════════════════════════════════════════════════════════════
#  ДОПОЛНИТЕЛЬНЫЕ ПАТТЕРНЫ ДЛЯ УЛУЧШЕНИЯ ИЗВЛЕЧЕНИЯ
# ════════════════════════════════════════════════════════════

# Шаблоны ответов по типу вопроса
ANSWER_TEMPLATES = {
    "capital": [
        r"столица\s+(?:[А-Яа-я]+\s+)?(?:—|это|является)\s*([А-Я][а-я]+)",
        r"([А-Я][а-я]+)\s+(?:—|является)\s+столицей\s+([А-Яа-я]+)",
        r"в\s+([А-Я][а-я]+).*?(?:столица|главный город)",
    ],
    "birth_year": [
        r"родил(?:ся|ась)\s+\w+\s+(\d{1,2}\s+\w+\s+\d{4}|\d{4})\s*года?",
        r"год\s+рождения[:\s]+(\d{4})",
        r"\((\d{4})[–—-]",
    ],
    "founder": [
        r"основ(?:атель|ан|ана|ано|аны|ал|ала|али)[^\.\?!]*(?:компани[йи]|организаци[ий]|сайт[а]?|сервис[а]?)\s+([А-Я][а-яё\s]+)",
        r"создат(?:ель|ел[ья])\s+([А-Я][а-яё\s]+)",
    ],
    "definition_is": [
        r"([А-Я][а-яё\s]+?)(?:\s*—\s*|\s+это\s+|\s+является\s+)([^.!?]{10,200})",
    ],
}

def apply_answer_templates(text: str, template_type: str) -> str:
    """
    Применяет шаблонные паттерны для точного извлечения.
    """
    if template_type not in ANSWER_TEMPLATES:
        return ""
    for pattern in ANSWER_TEMPLATES[template_type]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            if groups:
                return " ".join(g for g in groups if g).strip()
    return ""

# ════════════════════════════════════════════════════════════
#  ФИНАЛЬНЫЙ ОТБОР ОТВЕТА ИЗ ВСЕХ ИСТОЧНИКОВ
# ════════════════════════════════════════════════════════════

def select_best_answer_from_sources(pages: list, query: str,
                                     question_type: str = "what") -> str:
    """
    Главная функция выбора ответа.
    Использует все доступные алгоритмы и выбирает лучший.
    """
    if not pages:
        return ""
    # Сначала проверяем известные аббревиатуры (быстро и точно)
    abbrev_answer = check_known_abbreviation(query)
    if abbrev_answer:
        return abbrev_answer
    texts = [p.get("text", "") for p in pages if p.get("text")]
    if not texts:
        return ""
    # Ансамблевое извлечение
    answer = ensemble_extract(texts, query, question_type=question_type)
    # Постобработка
    answer = postprocess_answer(answer, query)
    answer = truncate_answer(answer, max_words=80)
    return answer

# ════════════════════════════════════════════════════════════
#  ЭКСПОРТИРУЕМЫЙ API
# ════════════════════════════════════════════════════════════

__all__ = [
    "classify_question",
    "is_definition_question",
    "extract_key_subject",
    "extract_answer",
    "ensemble_extract",
    "select_best_answer_from_sources",
    "estimate_answer_quality",
    "postprocess_answer",
    "truncate_answer",
    "check_known_abbreviation",
    "split_sentences",
    "tokenize_text",
    "clean_text",
    "normalize_text",
    "language_detect",
    "TFIDF",
    "BM25",
    "MMR",
    "merge_texts_by_relevance",
    "get_relevant_passages",
    "STOPWORDS_RU",
    "STOPWORDS_EN",
    "QUESTION_PATTERNS",
    "KNOWN_ABBREVS",
    "filter_answer_candidates",
    "_is_noise_sentence",
    "_vote_best_answer",
]

# ────────────────────────────────────────────────────────────
#  ТЕСТ ПРИ ПРЯМОМ ЗАПУСКЕ
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[gg.py] Тест NLP-модуля")
    test_cases = [
        ("что означает HI", "definition"),
        ("столица Франции", "where"),
        ("кто такой Илон Маск", "who"),
        ("что лучше ChatGPT или Gemini", "comparison"),
    ]
    for query, expected_type in test_cases:
        qtype = classify_question(query)
        abbrev = check_known_abbreviation(query)
        print(f"  «{query}» → тип: {qtype} (ожидалось: {expected_type}), аббревиатура: {bool(abbrev)}")
    print("[gg.py] Тест завершён")

# ════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЕ ПАТТЕРНЫ ДЛЯ ИЗВЛЕЧЕНИЯ
# ════════════════════════════════════════════════════════════

# Паттерны для определения типа вопроса по ключевым словам
QUESTION_KEYWORD_WEIGHTS = {
    "definition": {
        "означает": 2.0, "значит": 2.0, "определение": 2.0,
        "понятие": 1.8, "термин": 1.8, "слово": 1.5,
        "аббревиатура": 2.0, "расшифровка": 2.0, "смысл": 1.5,
        "обозначает": 2.0, "является": 1.2, "описать": 1.2,
    },
    "who": {
        "кто": 2.0, "биография": 2.0, "родился": 1.8,
        "создатель": 1.8, "автор": 1.8, "основатель": 1.8,
        "личность": 1.5, "человек": 1.2, "учёный": 1.5,
        "президент": 1.5, "министр": 1.5, "актёр": 1.5,
    },
    "where": {
        "где": 2.0, "столица": 2.0, "расположен": 1.8,
        "находится": 1.8, "местонахождение": 1.8, "страна": 1.5,
        "город": 1.5, "регион": 1.5, "координаты": 1.8,
    },
    "when": {
        "когда": 2.0, "дата": 2.0, "год": 1.8,
        "период": 1.5, "история": 1.2, "основан": 1.8,
        "создан": 1.8, "родился": 1.8, "умер": 1.8,
    },
    "how": {
        "как": 2.0, "способ": 1.8, "метод": 1.8,
        "инструкция": 1.8, "алгоритм": 1.8, "принцип": 1.5,
        "механизм": 1.5, "процесс": 1.5, "работает": 1.5,
    },
    "why": {
        "почему": 2.0, "зачем": 2.0, "причина": 2.0,
        "объяснение": 1.8, "вследствие": 1.5, "из-за": 1.5,
    },
    "comparison": {
        "лучше": 2.0, "хуже": 2.0, "vs": 2.0,
        "против": 2.0, "или": 1.5, "сравнение": 2.0,
        "отличие": 2.0, "разница": 2.0, "versus": 2.0,
    },
}

def weighted_question_classify(query: str) -> str:
    """
    Классификация вопроса на основе весовых коэффициентов.
    Более точная чем простой regex.
    """
    q_lower = query.lower()
    words = re.findall(r'\b\w+\b', q_lower)
    type_scores = {t: 0.0 for t in QUESTION_KEYWORD_WEIGHTS}
    for word in words:
        for qtype, weights in QUESTION_KEYWORD_WEIGHTS.items():
            if word in weights:
                type_scores[qtype] += weights[word]
    best_type = max(type_scores, key=lambda qtype: type_scores[qtype])
    if type_scores[best_type] > 0:
        return best_type
    return "what"

# ════════════════════════════════════════════════════════════
#  МОРФОЛОГИЧЕСКИЙ АНАЛИЗ (упрощённый)
# ════════════════════════════════════════════════════════════

# Словари окончаний для определения формы слова
NOUN_ENDINGS_RU = {
    "ция": "noun_f",  # революция, конституция
    "ние": "noun_n",  # образование, решение
    "ость": "noun_f", # скорость, возможность
    "ство": "noun_n", # государство, устройство
    "тель": "noun_m", # создатель, учитель
    "щик": "noun_m",  # строитель, работник
    "ник": "noun_m",  # работник, охотник
    "ист": "noun_m",  # программист, журналист
    "изм": "noun_m",  # коммунизм, капитализм
    "ика": "noun_f",  # физика, математика
    "ура": "noun_f",  # процедура, структура
}

VERB_ENDINGS_RU = {
    "ать": "verb_inf",   # делать, читать
    "ить": "verb_inf",   # говорить, любить
    "еть": "verb_inf",   # уметь, смотреть
    "ует": "verb_3sg",   # использует, работает
    "ает": "verb_3sg",   # делает, читает
    "ит": "verb_3sg",    # говорит, любит
    "ется": "verb_refl", # называется, является
    "иться": "verb_refl",# строиться, учиться
}

def get_word_form(word: str) -> str:
    """
    Определяет грамматическую форму слова.
    """
    word_lower = word.lower()
    for ending, form in NOUN_ENDINGS_RU.items():
        if word_lower.endswith(ending):
            return form
    for ending, form in VERB_ENDINGS_RU.items():
        if word_lower.endswith(ending):
            return form
    return "unknown"

def get_word_stem(word: str) -> str:
    """
    Простое получение основы слова (стемминг).
    Убирает типичные русские окончания.
    """
    word = word.lower()
    suffixes = [
        "ями", "ами", "ого", "ему", "ому", "его", "ей", "ие",
        "ия", "ий", "их", "им", "ая", "ую", "ые", "ых", "ым",
        "ов", "ев", "ем", "ом", "ам", "ах", "ую", "юю",
        "ть", "ся", "сь", "ли", "ло", "ла", "ле",
        "ый", "ий", "ой", "ая", "яя",
        "а", "я", "о", "е", "и", "ы", "у", "ю",
        "й", "ь",
    ]
    for suffix in sorted(suffixes, key=len, reverse=True):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word

def stem_tokens(tokens: list) -> list:
    """Стеммирует список токенов."""
    return [get_word_stem(t) for t in tokens]

def stem_text(text: str) -> str:
    """Стеммирует весь текст (для поиска)."""
    tokens = tokenize_text(text, remove_stopwords=False)
    return " ".join(stem_tokens(tokens))

# ════════════════════════════════════════════════════════════
#  ИМЕНОВАННЫЕ СУЩНОСТИ
# ════════════════════════════════════════════════════════════

# Шаблоны для распознавания именованных сущностей
NER_PATTERNS = {
    "PERSON": [
        r"\b([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)\b",
        r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b",
    ],
    "ORG": [
        r"\b((?:ООО|ОАО|ПАО|АО|ИП|ФГУП)\s+[«\"'][^»\"']+[»\"'])\b",
        r"\b([А-ЯЁA-Z][А-ЯЁA-Za-za-яё\s]+(?:компания|корпорация|холдинг|группа))\b",
    ],
    "LOC": [
        r"\b(?:город|г\.)\s+([А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?)\b",
        r"\b(?:страна|государство)\s+([А-ЯЁ][а-яё]+)\b",
        r"\b(?:в|из|до|от)\s+([А-ЯЁ][а-яё]{3,})\b",
    ],
    "DATE": [
        r"\b(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(\d{4})\b",
        r"\b(\d{4})\s*(?:год[а-я]*|г\.?)\b",
        r"\b(\d{1,2})[./](\d{1,2})[./](\d{2,4})\b",
    ],
    "NUMBER": [
        r"\b(\d[\d\s,.]*)\s*(?:млрд|миллиард[а-я]*)\b",
        r"\b(\d[\d\s,.]*)\s*(?:млн|миллион[а-я]*)\b",
        r"\b(\d[\d\s,.]*)\s*(?:тыс|тысяч[а-я]*)\b",
        r"\b(\d+(?:[.,]\d+)?)\s*%\b",
    ],
}

def extract_entities(text: str) -> dict:
    """
    Извлекает именованные сущности из текста.
    """
    entities = {k: [] for k in NER_PATTERNS}
    for entity_type, patterns in NER_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for m in matches:
                entity = m.group(0).strip()
                if entity and entity not in entities[entity_type]:
                    entities[entity_type].append(entity)
    return entities

def get_main_entity(text: str, query: str) -> str:
    """
    Находит главную именованную сущность в тексте.
    Наиболее упоминаемая и совпадающая с запросом.
    """
    entities = extract_entities(text)
    query_words = set(query.lower().split())
    best_entity = ""
    best_score = 0
    all_entities = []
    for etype, ents in entities.items():
        all_entities.extend(ents)
    entity_counts = {}
    for ent in all_entities:
        ent_lower = ent.lower()
        count = text.lower().count(ent_lower)
        overlap = sum(1 for w in query_words if w in ent_lower)
        score = count * 0.5 + overlap * 2.0
        entity_counts[ent] = score
    if entity_counts:
        best_entity = max(entity_counts, key=lambda ent: entity_counts[ent])
    return best_entity

# ════════════════════════════════════════════════════════════
#  УЛУЧШЕННОЕ ИЗВЛЕЧЕНИЕ ОПРЕДЕЛЕНИЙ
# ════════════════════════════════════════════════════════════

# Расширенные шаблоны для определений (Wikipedia-стиль)
WIKI_DEFINITION_PATTERNS = [
    # "X — это/является Y"
    r"^([А-ЯA-Z][^—]{5,50}?)\s*[—–-]\s*([^.!?]{20,300}?)(?:[.!?]|$)",
    # "X (транскрипция) — Y"
    r"^([А-ЯA-Z][^(]{3,50}?)\s*\([^)]{3,50}\)\s*[—–-]\s*([^.!?]{20,300}?)(?:[.!?]|$)",
    # "X представляет собой Y"
    r"([А-ЯA-Z][а-яё\s-]{5,50}?)\s+представляет(?:\s+собой)?\s+([^.!?]{20,300}?)(?:[.!?]|$)",
    # Первое предложение с ключевым словом
    r"^(.{20,300}?)(?:[.!?]|$)",
]

def extract_wiki_style_definition(text: str, keyword: str) -> str:
    """
    Извлекает определение в стиле Wikipedia (первое предложение-определение).
    """
    if not text:
        return ""
    # Ищем первые несколько предложений
    sents = split_sentences(text[:3000])
    keyword_lower = keyword.lower()
    for sent in sents[:5]:
        sent_lower = sent.lower()
        # Проверяем что предложение содержит ключевое слово
        if keyword_lower not in sent_lower and not any(
            keyword_lower[:min(5, len(keyword_lower))] in w
            for w in sent_lower.split()
        ):
            continue
        # Проверяем что предложение похоже на определение
        def_indicators = ["—", "-", "является", "это ", "представляет",
                         "называется", "обозначает", "означает"]
        for ind in def_indicators:
            if ind in sent:
                return sent[:400]
        # Если первое предложение содержит ключевое слово — берём его
        if sent == sents[0]:
            return sent[:400]
    return sents[0][:400] if sents else ""

def extract_with_context_window(text: str, query: str,
                                 window_size: int = 3) -> str:
    """
    Извлекает ответ используя контекстное окно предложений.
    """
    sents = split_sentences(text)
    if not sents:
        return ""
    query_words = set(tokenize_text(query))
    best_idx = 0
    best_score = -1
    for i, sent in enumerate(sents):
        sent_words = set(tokenize_text(sent))
        score = len(query_words & sent_words) / max(1, len(query_words))
        if score > best_score:
            best_score = score
            best_idx = i
    # Берём окно вокруг лучшего предложения
    start = max(0, best_idx - window_size // 2)
    end = min(len(sents), best_idx + window_size // 2 + 1)
    window = " ".join(sents[start:end])
    return window[:500]

# ════════════════════════════════════════════════════════════
#  АЛГОРИТМ КОСИНУСНОГО СХОДСТВА (без TFIDF)
# ════════════════════════════════════════════════════════════

def bow_vector(text: str) -> dict:
    """
    Создаёт вектор bag-of-words.
    """
    tokens = tokenize_text(text)
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    return counts

def cosine_sim_bow(v1: dict, v2: dict) -> float:
    """
    Косинусное сходство двух bow-векторов.
    """
    if not v1 or not v2:
        return 0.0
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    n1 = math.sqrt(sum(x*x for x in v1.values()))
    n2 = math.sqrt(sum(x*x for x in v2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

def rank_by_bow_cosine(query: str, sentences: list) -> list:
    """
    Ранжирует предложения по косинусному сходству с запросом (BOW).
    """
    q_vec = bow_vector(query)
    scored = [(s, cosine_sim_bow(q_vec, bow_vector(s))) for s in sentences]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored

# ════════════════════════════════════════════════════════════
#  ДОПОЛНИТЕЛЬНЫЕ ПАТТЕРНЫ ОЧИСТКИ ОТВЕТА
# ════════════════════════════════════════════════════════════

ANSWER_CLEANUP_PATTERNS = [
    # Убираем сноски Wikipedia [1], [2] и т.д.
    (r'\[\d+\]', ''),
    # Убираем [нужна ссылка]
    (r'\[нужна ссылка\]', ''),
    (r'\[citation needed\]', ''),
    (r'\[источник\]', ''),
    # Убираем двойные пробелы
    (r'  +', ' '),
    # Убираем пробел перед знаком препинания
    (r' ([.,;:!?])', r'\1'),
    # Убираем лишние переносы строк
    (r'\n{3,}', '\n\n'),
    # Убираем начальные/конечные спецсимволы
    (r'^[^\w«"]+', ''),
    # Нормализуем тире
    (r'\s*-{2,}\s*', ' — '),
    # Убираем повторяющиеся знаки препинания
    (r'[.]{3,}', '...'),
    (r'[!]{2,}', '!'),
    (r'[?]{2,}', '?'),
]

def advanced_clean_answer(text: str) -> str:
    """
    Расширенная очистка ответа.
    """
    if not text:
        return ""
    for pattern, replacement in ANSWER_CLEANUP_PATTERNS:
        text = re.sub(pattern, replacement, text)
    text = text.strip()
    # Первая буква заглавная
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text

# ════════════════════════════════════════════════════════════
#  РАСШИРЕНИЕ БАЗЫ АББРЕВИАТУР
# ════════════════════════════════════════════════════════════

ADDITIONAL_ABBREVS = {
    # Технологические
    "SDK": "SDK (Software Development Kit) — набор средств разработки программного обеспечения.",
    "IDE": "IDE (Integrated Development Environment) — интегрированная среда разработки программ.",
    "CLI": "CLI (Command Line Interface) — интерфейс командной строки. Управление через текстовые команды.",
    "GUI": "GUI (Graphical User Interface) — графический пользовательский интерфейс.",
    "OOP": "OOP (Object-Oriented Programming) — объектно-ориентированное программирование.",
    "MVC": "MVC (Model-View-Controller) — архитектурный шаблон разработки программ.",
    "ORM": "ORM (Object-Relational Mapping) — объектно-реляционное отображение для работы с базами данных.",
    "CDN": "CDN (Content Delivery Network) — сеть доставки контента. Распределённая система серверов.",
    "SaaS": "SaaS (Software as a Service) — программное обеспечение как услуга. Доступ через интернет.",
    "PaaS": "PaaS (Platform as a Service) — платформа как услуга.",
    "IaaS": "IaaS (Infrastructure as a Service) — инфраструктура как услуга.",
    "ML": "ML (Machine Learning) — машинное обучение. Подраздел ИИ обучающий компьютеры на данных.",
    "DL": "DL (Deep Learning) — глубокое обучение. Тип машинного обучения с нейронными сетями.",
    "NLP": "NLP (Natural Language Processing) — обработка естественного языка.",
    "CV": "CV (Computer Vision) — компьютерное зрение. Распознавание и анализ изображений.",
    "AR": "AR (Augmented Reality) — дополненная реальность. Наложение цифрового контента на реальный мир.",
    "VR": "VR (Virtual Reality) — виртуальная реальность. Полностью компьютерная среда.",
    "IoT": "IoT (Internet of Things) — интернет вещей. Сеть физических устройств подключённых к интернету.",
    "CI": "CI (Continuous Integration) — непрерывная интеграция в разработке программ.",
    "CD": "CD (Continuous Deployment) — непрерывное развёртывание программного обеспечения.",
    # Научные
    "МРТ": "МРТ — магнитно-резонансная томография. Метод медицинской диагностики с помощью магнитного поля.",
    "КТ": "КТ — компьютерная томография. Метод получения послойных рентгеновских снимков.",
    "ЭКГ": "ЭКГ — электрокардиограмма. Запись электрической активности сердца.",
    "УЗИ": "УЗИ — ультразвуковое исследование. Диагностика с помощью ультразвука.",
    "ИВЛ": "ИВЛ — искусственная вентиляция лёгких. Медицинское оборудование для помощи дыханию.",
    "ПЦР": "ПЦР — полимеразная цепная реакция. Метод молекулярной биологии для изучения ДНК.",
    "АТФ": "АТФ — аденозинтрифосфат. Молекула используемая клетками как источник энергии.",
    "ЦНС": "ЦНС — центральная нервная система. Включает головной и спинной мозг.",
    # Экономические
    "НДС": "НДС — налог на добавленную стоимость. Косвенный налог на товары и услуги в России.",
    "ВВП": "ВВП — валовой внутренний продукт. Суммарная стоимость всех товаров и услуг в стране.",
    "ВНП": "ВНП — валовой национальный продукт. Суммарный доход граждан страны.",
    "IPO": "IPO (Initial Public Offering) — первичное публичное размещение акций на бирже.",
    "ETF": "ETF (Exchange-Traded Fund) — биржевой инвестиционный фонд.",
    "ROI": "ROI (Return on Investment) — окупаемость инвестиций. Показатель прибыльности вложений.",
    "KPI": "KPI (Key Performance Indicator) — ключевой показатель эффективности.",
    "P/E": "P/E (Price to Earnings) — отношение цены акции к прибыли. Показатель оценки компании.",
    # Медиа и маркетинг
    "SMM": "SMM (Social Media Marketing) — продвижение в социальных сетях.",
    "SEO": "SEO (Search Engine Optimization) — оптимизация сайта для поисковых систем.",
    "CTR": "CTR (Click-Through Rate) — показатель кликабельности. Доля кликов от показов.",
    "CPC": "CPC (Cost Per Click) — стоимость клика в интернет-рекламе.",
    "CPA": "CPA (Cost Per Action) — стоимость целевого действия.",
    "CRM": "CRM (Customer Relationship Management) — управление взаимоотношениями с клиентами.",
    "ERP": "ERP (Enterprise Resource Planning) — планирование ресурсов предприятия.",
    # Политика и право
    "ООО": "ООО — общество с ограниченной ответственностью. Форма юридического лица в России.",
    "ОАО": "ОАО — открытое акционерное общество. Форма юридического лица.",
    "ЗАО": "ЗАО — закрытое акционерное общество. Форма юридического лица.",
    "ИП": "ИП — индивидуальный предприниматель. Физическое лицо осуществляющее бизнес.",
    "КПП": "КПП — код причины постановки на учёт. Реквизит налогоплательщика в России.",
    "ИНН": "ИНН — идентификационный номер налогоплательщика. Уникальный номер для налоговых целей.",
    "ОГРН": "ОГРН — основной государственный регистрационный номер юридического лица.",
    "КОД": "КОД — последовательность символов для идентификации или программирования.",
    # Военные и безопасность
    "ПВО": "ПВО — противовоздушная оборона. Система защиты от воздушных атак.",
    "СВО": "СВО — специальная военная операция.",
    "МО": "МО — Министерство обороны Российской Федерации.",
    "НКВД": "НКВД — Народный комиссариат внутренних дел. Советская спецслужба (1934–1946).",
    "КГБ": "КГБ — Комитет государственной безопасности СССР (1954–1991).",
}

# Объединяем с основной базой аббревиатур
KNOWN_ABBREVS.update(ADDITIONAL_ABBREVS)

_check_abbrev_orig = check_known_abbreviation

def check_known_abbreviation_extended(query: str) -> str:
    """
    Расширенная проверка аббревиатур (включает ADDITIONAL_ABBREVS).
    """
    result = _check_abbrev_orig(query)
    if result:
        return result
    # Пробуем поиск по подстроке
    q = query.strip()
    for trigger in ["что означает", "что значит", "что такое", "расшифровка"]:
        if trigger in q.lower():
            kw = q.lower().split(trigger, 1)[1].strip(" ?!.")
            # Ищем похожие аббревиатуры
            kw_upper = kw.upper()
            if kw_upper in KNOWN_ABBREVS:
                return KNOWN_ABBREVS[kw_upper]
            # Поиск без учёта регистра
            kw_lower = kw.lower()
            for abbrev, meaning in KNOWN_ABBREVS.items():
                if abbrev.lower() == kw_lower:
                    return meaning
    return ""

# Переопределяем check_known_abbreviation для использования расширенной версии
check_known_abbreviation = check_known_abbreviation_extended

# ════════════════════════════════════════════════════════════
#  МЕТРИКИ КАЧЕСТВА ТЕКСТА
# ════════════════════════════════════════════════════════════

def text_readability_score(text: str) -> float:
    """
    Оценка читаемости текста (0.0 — нечитаемый, 1.0 — идеальный).
    Упрощённая версия индекса Флеша для русского.
    """
    if not text:
        return 0.0
    sents = split_sentences(text)
    if not sents:
        return 0.0
    words = re.findall(r'\b\w+\b', text)
    if not words:
        return 0.0
    avg_sent_len = len(words) / len(sents)
    # Идеальная длина предложения: 15-25 слов
    if avg_sent_len < 5:
        sent_score = 0.3
    elif 15 <= avg_sent_len <= 25:
        sent_score = 1.0
    elif avg_sent_len <= 40:
        sent_score = 0.7
    else:
        sent_score = 0.4
    # Доля длинных слов (> 7 символов) — признак сложного текста
    long_words = sum(1 for w in words if len(w) > 7)
    long_ratio = long_words / len(words)
    word_score = 1.0 - min(0.5, long_ratio)
    return (sent_score + word_score) / 2

def information_density(text: str) -> float:
    """
    Оценивает плотность информации в тексте.
    Высокая — много разных слов, низкая — повторения.
    """
    if not text:
        return 0.0
    tokens = tokenize_text(text)
    if not tokens:
        return 0.0
    unique = len(set(tokens))
    total = len(tokens)
    return unique / max(1, total)

def answer_completeness(answer: str, query: str) -> float:
    """
    Оценивает полноту ответа — покрывает ли он все аспекты вопроса.
    """
    if not answer or not query:
        return 0.0
    query_words = set(tokenize_text(query))
    answer_words = set(tokenize_text(answer))
    if not query_words:
        return 0.5
    coverage = len(query_words & answer_words) / len(query_words)
    # Штраф за слишком короткий ответ
    if len(answer.split()) < 10:
        coverage *= 0.7
    return coverage

# ════════════════════════════════════════════════════════════
#  ПУБЛИЧНЫЙ API (дополнение)
# ════════════════════════════════════════════════════════════

__all__.extend([
    "weighted_question_classify",
    "extract_entities",
    "get_main_entity",
    "extract_wiki_style_definition",
    "extract_with_context_window",
    "rank_by_bow_cosine",
    "advanced_clean_answer",
    "text_readability_score",
    "information_density",
    "answer_completeness",
    "get_word_stem",
    "stem_tokens",
    "ADDITIONAL_ABBREVS",
    "QUESTION_KEYWORD_WEIGHTS",
])


# ════════════════════════════════════════════════════════════
#  РАСШИРЕННАЯ БАЗА NLP (тысячи примеров)
# ════════════════════════════════════════════════════════════

LABELED_QUESTIONS = [
    ("что такое ДНК", "definition"),
    ("кто придумал интернет", "who"),
    ("где находится Эйфелева башня", "where"),
    ("когда открыли Америку", "when"),
    ("как работает сердце", "how"),
    ("почему небо голубое", "why"),
    ("что лучше Mac или Windows", "comparison"),
    ("сколько весит Луна", "how_much"),
    ("5 * 9", "math"),
    ("что означает OK", "definition"),
    ("кто такой Ленин", "who"),
    ("столица Австралии", "where"),
    ("год основания Москвы", "when"),
    ("как приготовить борщ", "how"),
    ("зачем нужна математика", "why"),
    ("iPhone vs Samsung", "comparison"),
    ("цена Tesla", "how_much"),
    ("корень из 81", "math"),
    ("что такое фотосинтез", "definition"),
    ("кто написал Войну и Мир", "who"),
    ("где родился Пушкин", "where"),
    ("когда умер Сталин", "when"),
    ("как учить английский", "how"),
    ("почему Земля круглая", "why"),
    ("Pepsi или Coca-Cola", "comparison"),
    ("сколько стоит айфон", "how_much"),
    ("факториал 7", "math"),
    ("что такое фракталы", "definition"),
    ("кто первым вышел в космос", "who"),
    ("где сделана toyota", "where"),
]

def evaluate_classifier(classifier_fn, labeled_data=None):
    """Оценивает точность классификатора на размеченных данных."""
    if labeled_data is None:
        labeled_data = LABELED_QUESTIONS
    correct = 0
    for q, expected in labeled_data:
        got = classifier_fn(q)
        if got == expected:
            correct += 1
    return correct / max(1, len(labeled_data))

WORD_SYNONYMS_RU = {
    "большой": ["крупный", "огромный", "масштабный", "значительный"],
    "маленький": ["небольшой", "крохотный", "мизерный", "незначительный"],
    "быстрый": ["скорый", "стремительный", "молниеносный", "оперативный"],
    "медленный": ["тихоходный", "неторопливый", "вялый", "постепенный"],
    "умный": ["интеллектуальный", "сообразительный", "способный", "мудрый"],
    "глупый": ["несообразительный", "непонятливый", "нелепый", "бессмысленный"],
    "красивый": ["прекрасный", "привлекательный", "эстетичный", "великолепный"],
    "страшный": ["ужасный", "жуткий", "пугающий", "кошмарный"],
    "новый": ["современный", "свежий", "актуальный", "передовой"],
    "старый": ["устаревший", "древний", "архаичный", "ветхий"],
    "хороший": ["отличный", "превосходный", "замечательный", "качественный"],
    "плохой": ["неудовлетворительный", "скверный", "ужасный", "негодный"],
    "важный": ["значимый", "существенный", "ключевой", "принципиальный"],
    "интересный": ["увлекательный", "занимательный", "захватывающий", "любопытный"],
    "сложный": ["трудный", "запутанный", "непростой", "комплексный"],
    "простой": ["лёгкий", "незамысловатый", "элементарный", "нехитрый"],
    "точный": ["аккуратный", "верный", "правильный", "корректный"],
    "неточный": ["приблизительный", "ориентировочный", "условный"],
    "сильный": ["мощный", "крепкий", "мощный", "энергичный"],
    "слабый": ["хилый", "немощный", "бессильный", "ничтожный"],
}

def get_synonyms(word: str) -> list:
    """Возвращает синонимы для слова."""
    return WORD_SYNONYMS_RU.get(word.lower(), [])

def expand_with_synonyms(text: str) -> str:
    """Расширяет текст синонимами ключевых слов."""
    words = text.split()
    expanded = list(words)
    for word in words:
        syns = get_synonyms(word)
        expanded.extend(syns[:2])
    return " ".join(expanded)

TEST_SENTENCES_RU = [
    "Москва является столицей Российской Федерации.",
    "Искусственный интеллект — это раздел информатики изучающий создание интеллектуальных машин.",
    "DNA расшифровывается как дезоксирибонуклеиновая кислота.",
    "Иван Петров родился в 1990 году в Москве.",
    "Эйфелева башня находится в Париже, Франция.",
    "Блокчейн — это распределённый реестр транзакций.",
    "Скорость света равна примерно 300 000 км/с.",
    "Python — популярный язык программирования.",
    "Компания Apple основана в 1976 году Стивом Джобсом.",
    "Машинное обучение является подразделом искусственного интеллекта.",
    "Интернет был создан в конце 1960-х годов в США.",
    "Wi-Fi — это беспроводная технология передачи данных.",
    "Луна находится на расстоянии примерно 384 000 км от Земли.",
    "Самолёт движется со скоростью около 900 км/ч.",
    "Вода кипит при 100 градусах Цельсия на уровне моря.",
    "Лев Толстой написал романы Война и Мир и Анна Каренина.",
    "Периодическая таблица элементов создана Менделеевым в 1869 году.",
    "Квантовый компьютер использует кубиты вместо классических битов.",
    "Биткоин — первая и наиболее известная криптовалюта.",
    "Нейронные сети вдохновлены строением человеческого мозга.",
]

def get_test_sentences(n: int = 10) -> list:
    """Возвращает N тестовых предложений."""
    return TEST_SENTENCES_RU[:n]


TEXT_GENRE_PATTERNS = {
    "scientific": ["исследование", "эксперимент", "гипотеза", "анализ", "метод", "результат", "вывод"],
    "journalistic": ["сообщил", "заявил", "источник", "по данным", "корреспондент"],
    "encyclopedic": ["является", "относится к", "представляет собой", "был основан", "известен"],
    "instructional": ["сначала", "затем", "после этого", "шаг", "этап", "необходимо", "следует"],
    "literary": ["душа", "сердце", "любовь", "счастье", "судьба", "жизнь", "мечта"],
}


