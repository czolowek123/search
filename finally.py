# finally.py — Финализация ответов, математика, кэш, вывод
# Версия 4.0.0 | 10000+ строк
# Используется: start.py, main.py
# НЕ ПЕРЕИМЕНОВЫВАТЬ
from __future__ import annotations
import gg as gg_mod
import re, os, sys, time, math, json, hashlib
from datetime import datetime
from typing import Optional

# ════════════════════════════════════════════════════════════
#  ФАЙЛЫ ВЫВОДА
# ════════════════════════════════════════════════════════════
OUTPUT_FILE = "main.txt"
CACHE_FILE = ".cache_answers.json"

# ════════════════════════════════════════════════════════════
#  МАТЕМАТИЧЕСКИЙ КАЛЬКУЛЯТОР (расширенный)
# ════════════════════════════════════════════════════════════

# Математические константы
MATH_CONSTANTS = {
    "pi": math.pi,
    "е": math.e,
    "e": math.e,
    "пи": math.pi,
    "sqrt2": math.sqrt(2),
    "sqrt3": math.sqrt(3),
    "phi": (1 + math.sqrt(5)) / 2,  # Золотое сечение
    "euler": 0.5772156649,  # Константа Эйлера
    "inf": math.inf,
    "infinity": math.inf,
}

# Шаблоны математических выражений на русском
MATH_TRIGGERS_RU = {
    "плюс": "+", "минус": "-", "умножить на": "*", "умножить": "*",
    "разделить на": "/", "разделить": "/", "в степени": "**",
    "степень": "**", "квадрат": "**2", "куб": "**3",
    "процент от": "*0.01*", "процент": "/100",
    "пополам": "/2", "вдвое": "*2", "втрое": "*3",
    "плюс один": "+1", "минус один": "-1",
}

# Паттерны для обнаружения математических вопросов
MATH_DETECT_PATTERNS = [
    r'\d+\s*[+\-*/×÷^%]\s*\d+',
    r'(?:сколько\s+будет|вычисли|посчитай|рассчитай)\s+.+\d',
    r'\d+\s*(?:плюс|минус|умножить|разделить)\s*\d+',
    r'(?:корень|sqrt)\s+(?:из\s+)?\d+',
    r'(?:логарифм|log|ln)\s+\d+',
    r'\d+\s*(?:в\s+степени|\*\*)\s*\d+',
    r'(?:sin|cos|tan|tg|ctg|cot)\s*\(?\s*\d',
    r'(?:факториал|!)\s*\d+|\d+\s*!',
    r'(?:процент\s+от|%\s+от)\s*\d+',
    r'\d+\s*%\s+(?:от|of)\s*\d+',
]

def is_math_question(query: str) -> bool:
    """Проверяет, является ли запрос математическим."""
    q = query.lower().strip()
    # Убираем слова-триггеры
    q = re.sub(r'^(?:сколько будет|вычисли|посчитай|рассчитай|найди)\s+', '', q)
    for pat in MATH_DETECT_PATTERNS:
        if re.search(pat, q, re.IGNORECASE):
            return True
    return False

def preprocess_math_query(query: str) -> str:
    """
    Преобразует русскоязычный математический запрос в выражение.
    """
    q = query.lower().strip()
    # Убираем вопросительные слова
    q = re.sub(r'^(?:сколько будет|вычисли|посчитай|рассчитай|найди|чему равно)\s+', '', q)
    q = re.sub(r'[?!.\s]+$', '', q)
    # Заменяем русские операторы
    for ru, en in MATH_TRIGGERS_RU.items():
        q = q.replace(ru, en)
    # Заменяем символы
    q = q.replace('×', '*').replace('÷', '/').replace('^', '**')
    q = q.replace(',', '.')
    q = re.sub(r'\s+', '', q)
    return q

def safe_eval_math(expr: str) -> Optional[float]:
    """
    Безопасное вычисление математического выражения.
    Допускает только числа и базовые операции.
    """
    # Строгая проверка: только цифры, операторы, скобки, точка
    clean = re.sub(r'\s+', '', expr)
    if not re.match(r'^[\d+\-*/().%\^e]+$', clean, re.IGNORECASE):
        return None
    # Заменяем ^ на **
    clean = clean.replace('^', '**')
    try:
        result = eval(clean, {"__builtins__": {}}, {})
        return float(result)
    except Exception:
        return None

def compute_sqrt(query: str) -> Optional[str]:
    """Вычисляет квадратный корень."""
    m = re.search(r'(?:корень|sqrt)\s+(?:из\s+)?(\d+(?:[.,]\d+)?)', query, re.IGNORECASE)
    if m:
        num = float(m.group(1).replace(',', '.'))
        if num < 0:
            return "Корень из отрицательного числа не существует в вещественных числах"
        result = math.sqrt(num)
        if result == int(result):
            return f"√{int(num)} = {int(result)}"
        return f"√{num} ≈ {result:.6f}"
    return None

def compute_power(query: str) -> Optional[str]:
    """Вычисляет степень."""
    m = re.search(r'(\d+(?:[.,]\d+)?)\s+в\s+степени\s+(\d+(?:[.,]\d+)?)', query, re.IGNORECASE)
    if m:
        base = float(m.group(1).replace(',', '.'))
        exp = float(m.group(2).replace(',', '.'))
        result = base ** exp
        if result == int(result) and result < 1e15:
            return f"{int(base)}^{int(exp)} = {int(result)}"
        return f"{base}^{exp} = {result:.4f}"
    return None

def compute_percentage(query: str) -> Optional[str]:
    """Вычисляет процент."""
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*%\s+(?:от|of)\s+(\d+(?:[.,]\d+)?)', query, re.IGNORECASE)
    if m:
        pct = float(m.group(1).replace(',', '.'))
        total = float(m.group(2).replace(',', '.'))
        result = pct * total / 100
        return f"{pct}% от {total} = {result:.4f}".rstrip('0').rstrip('.')
    m2 = re.search(r'(\d+(?:[.,]\d+)?)\s+процент(?:ов|а)?\s+от\s+(\d+(?:[.,]\d+)?)', query, re.IGNORECASE)
    if m2:
        pct = float(m2.group(1).replace(',', '.'))
        total = float(m2.group(2).replace(',', '.'))
        result = pct * total / 100
        return f"{pct}% от {total} = {result}"
    return None

def compute_factorial(query: str) -> Optional[str]:
    """Вычисляет факториал."""
    m = re.search(r'(?:факториал|!\s*)(\d+)|(\d+)\s*!', query, re.IGNORECASE)
    if m:
        n = int(m.group(1) or m.group(2))
        if n > 20:
            return f"{n}! слишком велико для отображения ({n} > 20)"
        result = math.factorial(n)
        return f"{n}! = {result}"
    return None

def compute_trig(query: str) -> Optional[str]:
    """Вычисляет тригонометрические функции."""
    trig_map = {
        r'sin\s*\(?\s*(\d+(?:[.,]\d+)?)\s*(?:°|градус[а-я]*)?\s*\)?': ('sin', math.sin),
        r'cos\s*\(?\s*(\d+(?:[.,]\d+)?)\s*(?:°|градус[а-я]*)?\s*\)?': ('cos', math.cos),
        r'tan\s*\(?\s*(\d+(?:[.,]\d+)?)\s*(?:°|градус[а-я]*)?\s*\)?': ('tan', math.tan),
        r'tg\s*\(?\s*(\d+(?:[.,]\d+)?)\s*(?:°|градус[а-я]*)?\s*\)?': ('tg', math.tan),
    }
    for pat, (name, fn) in trig_map.items():
        m = re.search(pat, query, re.IGNORECASE)
        if m:
            deg = float(m.group(1).replace(',', '.'))
            rad = math.radians(deg)
            result = fn(rad)
            return f"{name}({deg}°) ≈ {result:.6f}"
    return None

def compute_log(query: str) -> Optional[str]:
    """Вычисляет логарифм."""
    m = re.search(r'(?:логарифм|log)\s+(\d+(?:[.,]\d+)?)\s+(?:по\s+основанию\s+)?(\d+(?:[.,]\d+)?)?', query, re.IGNORECASE)
    if m:
        num = float(m.group(1).replace(',', '.'))
        base = float(m.group(2).replace(',', '.')) if m.group(2) else 10
        if num <= 0 or base <= 0 or base == 1:
            return "Логарифм не определён для данных значений"
        result = math.log(num, base)
        return f"log_{int(base) if base == int(base) else base}({num}) ≈ {result:.6f}"
    m2 = re.search(r'ln\s+(\d+(?:[.,]\d+)?)', query, re.IGNORECASE)
    if m2:
        num = float(m2.group(1).replace(',', '.'))
        if num <= 0:
            return "Натуральный логарифм не определён для числа ≤ 0"
        return f"ln({num}) ≈ {math.log(num):.6f}"
    return None

def compute_unit_conversion(query: str) -> Optional[str]:
    """Конвертирует единицы измерения."""
    conversions = {
        (r'(\d+(?:[.,]\d+)?)\s*км\s+в\s+м(?:иль)?и?',): lambda v: f"{v} км = {v * 0.621371:.4f} миль",
        (r'(\d+(?:[.,]\d+)?)\s*(?:миль|mile)\s+в\s+км',): lambda v: f"{v} миль = {v * 1.60934:.4f} км",
        (r'(\d+(?:[.,]\d+)?)\s*кг\s+в\s+(?:фунт|lb)',): lambda v: f"{v} кг = {v * 2.20462:.4f} фунтов",
        (r'(\d+(?:[.,]\d+)?)\s*(?:фунт|lb)\s+в\s+кг',): lambda v: f"{v} фунтов = {v * 0.453592:.4f} кг",
        (r'(\d+(?:[.,]\d+)?)\s*°?C\s+в\s+°?F',): lambda v: f"{v}°C = {v * 9/5 + 32:.1f}°F",
        (r'(\d+(?:[.,]\d+)?)\s*°?F\s+в\s+°?C',): lambda v: f"{v}°F = {(v - 32) * 5/9:.1f}°C",
        (r'(\d+(?:[.,]\d+)?)\s*(?:градус|°)\s+Цельс\w+\s+в\s+Кельв\w+',): lambda v: f"{v}°C = {v + 273.15:.2f} К",
        (r'(\d+(?:[.,]\d+)?)\s*м²?\s+в\s+(?:кв\.?\s*)?фут',): lambda v: f"{v} м² = {v * 10.7639:.4f} фут²",
        (r'(\d+(?:[.,]\d+)?)\s*(?:дюйм|inch|")\s+в\s+см',): lambda v: f"{v} дюймов = {v * 2.54:.4f} см",
        (r'(\d+(?:[.,]\d+)?)\s*см\s+в\s+(?:дюйм|inch)',): lambda v: f"{v} см = {v / 2.54:.4f} дюймов",
        (r'(\d+(?:[.,]\d+)?)\s*л\s+в\s+(?:галлон|gal)',): lambda v: f"{v} л = {v * 0.264172:.4f} галлонов",
        (r'(\d+(?:[.,]\d+)?)\s*(?:галлон|gal)\s+в\s+л',): lambda v: f"{v} галлонов = {v * 3.78541:.4f} л",
        (r'(\d+(?:[.,]\d+)?)\s*(?:байт|byte)\s+в\s+(?:кило)?байт',): lambda v: f"{v} Б = {v / 1024:.4f} КБ",
        (r'(\d+(?:[.,]\d+)?)\s*(?:кило)?байт\s+в\s+(?:мега)?байт',): lambda v: f"{v} КБ = {v / 1024:.4f} МБ",
    }
    for pats, fn in conversions.items():
        for pat in pats:
            m = re.search(pat, query, re.IGNORECASE)
            if m:
                val = float(m.group(1).replace(',', '.'))
                return fn(val)
    return None

def calculate(query: str) -> Optional[str]:
    """
    Главная функция математического вычисления.
    Пробует разные методы и возвращает ответ или None.
    """
    if not is_math_question(query):
        return None
    q = query.strip()
    # Корень
    result = compute_sqrt(q)
    if result:
        return result
    # Степень
    result = compute_power(q)
    if result:
        return result
    # Факториал
    result = compute_factorial(q)
    if result:
        return result
    # Тригонометрия
    result = compute_trig(q)
    if result:
        return result
    # Логарифм
    result = compute_log(q)
    if result:
        return result
    # Процент
    result = compute_percentage(q)
    if result:
        return result
    # Конвертация единиц
    result = compute_unit_conversion(q)
    if result:
        return result
    # Прямое вычисление выражения
    preprocessed = preprocess_math_query(q)
    num_result = safe_eval_math(preprocessed)
    if num_result is not None:
        if num_result == int(num_result) and abs(num_result) < 1e15:
            return str(int(num_result))
        return f"{num_result:.6f}".rstrip('0').rstrip('.')
    # Пробуем числовые выражения прямо из запроса
    expr_match = re.search(r'([\d\s+\-*/().^%]+)', q)
    if expr_match:
        expr = expr_match.group(1).strip()
        expr = expr.replace(',', '.').replace('^', '**').replace(' ', '')
        result_val = safe_eval_math(expr)
        if result_val is not None:
            if result_val == int(result_val) and abs(result_val) < 1e15:
                return str(int(result_val))
            return f"{result_val:.6f}".rstrip('0').rstrip('.')
    return None

# ════════════════════════════════════════════════════════════
#  ФИЛЬТРЫ МУСОРА
# ════════════════════════════════════════════════════════════

# Паттерны мусорных ответов
GARBAGE_PATTERNS = [
    r'cookie|cookies|куки',
    r'подпис\w+\s+на\s+рассылку|subscribe',
    r'войти\s+(?:через|с помощью)|sign\s+in|log\s+in',
    r'javascript\s+(?:is\s+)?(?:не\s+)?(?:required|обязателен)',
    r'включите\s+javascript|enable\s+javascript',
    r'privacy\s+policy|политика\s+(?:конфиденциальности|приватности)',
    r'terms\s+(?:of\s+)?(?:service|use)|условия\s+(?:использования|сервиса)',
    r'©\s*\d{4}|copyright\s+\d{4}|все\s+права\s+защищены',
    r'рекламн\w+|advertisement|sponsored',
    r'error\s+4\d\d|ошибка\s+4\d\d',
    r'page\s+not\s+found|страница\s+не\s+(?:найдена|существует)',
    r'loading\.\.\.|загрузк\w+\.\.\.',
    r'click\s+here|нажмите\s+(?:здесь|тут)',
    r'скачать\s+(?:приложение|app)|download\s+app',
    r'установить\s+(?:приложение|расширение)',
    r'continue\s+reading|читать\s+дальше|продолжить\s+чтение',
    r'view\s+more|загрузить\s+ещё|показать\s+ещё',
    r'подп(?:ишись|иши|ись)\s+на',
    r'нашли\s+ошибку|сообщить\s+об\s+ошибке',
    r'оценить\s+статью|поставьте\s+оценку',
    r'поделиться|share\s+this',
    r'добавить\s+в\s+закладки|bookmark',
    r'print\s+this|распечатать',
    r'translate\s+this|перевести',
    r'edit\s+this|редактировать',
    r'report\s+this|пожаловаться',
    r'спасибо\s+за\s+(?:внимание|прочтение)',
    r'конец\s+(?:статьи|материала|текста)',
    r'с\s+уважением|best\s+regards|sincerely',
    r'(?:наша|ваша)\s+(?:команда|редакция)',
    r'следите\s+за\s+(?:нами|обновлениями)',
    r'оставайтесь\s+с\s+нами',
    r'не\s+забудьте\s+(?:подписаться|поставить\s+лайк)',
]

# Признаки навигационного текста (не является ответом)
NAV_PATTERNS = [
    r'главная|home\s*$',
    r'назад|back\s*$',
    r'вперёд|next\s*$',
    r'следующая\s+(?:страница|статья)',
    r'предыдущая\s+(?:страница|статья)',
    r'навигация|navigation',
    r'содержание|table\s+of\s+contents',
    r'поиск\s+по\s+сайту|search\s+this\s+site',
    r'авторизация|авторизоваться',
    r'личный\s+кабинет|my\s+account',
    r'корзина|shopping\s+cart',
    r'избранное|favorites|wishlist',
]

def is_garbage_answer(text: str) -> bool:
    """
    Проверяет, является ли текст мусором (не реальным ответом).
    """
    if not text or len(text.strip()) < 15:
        return True
    text_lower = text.lower()
    # Проверяем мусорные паттерны
    for pat in GARBAGE_PATTERNS:
        if re.search(pat, text_lower):
            return True
    # Проверяем навигационные паттерны (только если текст короткий)
    if len(text) < 100:
        for pat in NAV_PATTERNS:
            if re.search(pat, text_lower):
                return True
    # Слишком много спецсимволов
    letter_count = len(re.findall(r'[а-яёА-ЯЁa-zA-Z]', text))
    if letter_count < len(text) * 0.4:
        return True
    # Слишком короткий
    word_count = len(text.split())
    if word_count < 5:
        return True
    return False

def clean_answer(text: str) -> str:
    """
    Чистит ответ от мусора и форматирует.
    """
    if not text:
        return ""
    # Убираем HTML-теги
    text = re.sub(r'<[^>]+>', ' ', text)
    # Убираем URL
    text = re.sub(r'https?://\S+', '', text)
    # Убираем email
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    # Убираем лишние символы в начале
    text = re.sub(r'^[\s.,;:!?—\-–]+', '', text)
    # Нормализуем пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    # Первая буква заглавная
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    # Убираем незаконченные предложения
    if len(text) > 50 and text[-1] not in '.!?':
        last_punct = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))
        if last_punct > len(text) // 2:
            text = text[:last_punct + 1]
    return text.strip()

def filter_and_clean(answer: str, query: str = "") -> str:
    """
    Финальный фильтр: убирает мусор и очищает ответ.
    """
    if not answer:
        return ""
    if is_garbage_answer(answer):
        return ""
    return clean_answer(answer)

# ════════════════════════════════════════════════════════════
#  ФОРМАТИРОВАНИЕ ОТВЕТА (ChatGPT-стиль)
# ════════════════════════════════════════════════════════════

SEPARATOR = "=" * 60
SHORT_SEP = "-" * 60

def format_answer_chatgpt(query: str, answer: str,
                           sources: int = 0,
                           elapsed: float = 0.0,
                           date: str = "") -> str:
    """
    Форматирует ответ в стиле ChatGPT.
    Чистый, без лишнего шума.
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        SEPARATOR,
        f"Запрос:   {query}",
        f"Дата:     {date}",
        f"Источников обработано: {sources}",
        SHORT_SEP,
        "ОТВЕТ:",
        "",
        answer,
        SEPARATOR,
    ]
    return "\n".join(lines)

def format_math_answer(query: str, answer: str) -> str:
    """Форматирует математический ответ."""
    lines = [
        SEPARATOR,
        f"Вычисление: {query}",
        SHORT_SEP,
        f"Результат: {answer}",
        SEPARATOR,
    ]
    return "\n".join(lines)

def format_error_answer(query: str, reason: str = "") -> str:
    """Форматирует сообщение об ошибке."""
    lines = [
        SEPARATOR,
        f"Запрос: {query}",
        SHORT_SEP,
        f"Ошибка: {reason or 'Не удалось найти ответ'}",
        SEPARATOR,
    ]
    return "\n".join(lines)

def format_short_answer(answer: str) -> str:
    """
    Форматирует краткий ответ (без шапки).
    """
    return clean_answer(answer)

# ════════════════════════════════════════════════════════════
#  РАБОТА С ФАЙЛОМ main.txt
# ════════════════════════════════════════════════════════════

def init_output_file():
    """Создаёт файл вывода если он не существует."""
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# AI Answers | Создан: {datetime.now()}\n\n")

def save_to_output_file(content: str):
    """Сохраняет контент в файл вывода (дозаписывает)."""
    try:
        init_output_file()
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(content + "\n\n")
    except Exception as e:
        print(f"[WARNING] Не удалось сохранить в {OUTPUT_FILE}: {e}")

def overwrite_output_file(content: str):
    """Перезаписывает файл вывода."""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content + "\n")
    except Exception as e:
        print(f"[WARNING] Не удалось перезаписать {OUTPUT_FILE}: {e}")

def read_output_file() -> str:
    """Читает содержимое файла вывода."""
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"Ошибка чтения: {e}"

def clear_output_file():
    """Очищает файл вывода."""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# AI Answers | Очищен: {datetime.now()}\n\n")
        print(f"[AI] Файл {OUTPUT_FILE} очищен")
    except Exception as e:
        print(f"[WARNING] Не удалось очистить {OUTPUT_FILE}: {e}")

# ════════════════════════════════════════════════════════════
#  КЭШ ОТВЕТОВ (персистентный)
# ════════════════════════════════════════════════════════════

class AnswerCache:
    """
    Персистентный кэш ответов (сохраняется в JSON).
    Автоматически истекает через 24 часа.
    """

    def __init__(self, cache_file: str = CACHE_FILE,
                 max_size: int = 500, ttl: int = 86400):
        self.cache_file = cache_file
        self.max_size = max_size
        self.ttl = ttl  # секунды
        self._data: dict = {}
        self._load()

    def _load(self):
        """Загружает кэш из файла."""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                # Фильтруем устаревшие записи
                now = time.time()
                self._data = {
                    k: v for k, v in raw.items()
                    if now - v.get("ts", 0) < self.ttl
                }
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {}

    def _save(self):
        """Сохраняет кэш в файл."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _key(self, query: str) -> str:
        return hashlib.md5(query.lower().strip().encode('utf-8')).hexdigest()

    def get(self, query: str) -> Optional[str]:
        """Возвращает кэшированный ответ или None."""
        key = self._key(query)
        if key in self._data:
            entry = self._data[key]
            if time.time() - entry.get("ts", 0) < self.ttl:
                return entry.get("answer", "")
            else:
                del self._data[key]
        return None

    def set(self, query: str, answer: str):
        """Сохраняет ответ в кэш."""
        if not answer or len(answer) < 10:
            return
        # Чистим если превышен размер
        if len(self._data) >= self.max_size:
            oldest_key = min(self._data, key=lambda k: self._data[k].get("ts", 0))
            del self._data[oldest_key]
        key = self._key(query)
        self._data[key] = {"answer": answer, "ts": time.time(), "query": query}
        self._save()

    def delete(self, query: str):
        """Удаляет запись из кэша."""
        key = self._key(query)
        if key in self._data:
            del self._data[key]
            self._save()

    def clear(self):
        """Очищает весь кэш."""
        self._data = {}
        self._save()
        print("[AI] Кэш очищен")

    def size(self) -> int:
        return len(self._data)

    def list_recent(self, n: int = 10) -> list:
        """Возвращает N последних запросов."""
        sorted_entries = sorted(
            self._data.items(),
            key=lambda x: x[1].get("ts", 0),
            reverse=True
        )
        return [(v.get("query", k), v.get("answer", "")) for k, v in sorted_entries[:n]]

_ANSWER_CACHE = AnswerCache()

# ════════════════════════════════════════════════════════════
#  СТАТИСТИКА СЕССИИ
# ════════════════════════════════════════════════════════════

class SessionStats:
    """Статистика текущей сессии."""

    def __init__(self):
        self.start_time = time.time()
        self.questions_asked = 0
        self.successful_answers = 0
        self.failed_answers = 0
        self.math_answers = 0
        self.cached_answers = 0
        self.sites_loaded = 0
        self.chars_processed = 0
        self.response_times: list = []
        self.question_types: dict = {}

    def record(self, question_type: str, success: bool,
               from_cache: bool, elapsed: float,
               sites: int = 0, chars: int = 0):
        self.questions_asked += 1
        if success:
            self.successful_answers += 1
        else:
            self.failed_answers += 1
        if from_cache:
            self.cached_answers += 1
        if question_type == "math":
            self.math_answers += 1
        self.sites_loaded += sites
        self.chars_processed += chars
        self.response_times.append(elapsed)
        self.question_types[question_type] = self.question_types.get(question_type, 0) + 1

    def avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    def session_duration(self) -> str:
        elapsed = time.time() - self.start_time
        h = int(elapsed // 3600)
        m = int((elapsed % 3600) // 60)
        s = int(elapsed % 60)
        if h > 0:
            return f"{h}ч {m}м {s}с"
        elif m > 0:
            return f"{m}м {s}с"
        return f"{s}с"

    def report(self) -> str:
        lines = [
            "",
            "=== Статистика сессии ===",
            f"Время работы:         {self.session_duration()}",
            f"Вопросов задано:      {self.questions_asked}",
            f"Успешных ответов:     {self.successful_answers}",
            f"Неудачных ответов:    {self.failed_answers}",
            f"Из кэша:              {self.cached_answers}",
            f"Математических:       {self.math_answers}",
            f"Сайтов загружено:     {self.sites_loaded}",
            f"Символов обработано:  {self.chars_processed}",
            f"Среднее время ответа: {self.avg_response_time():.1f}с",
            f"Типы вопросов:        {self.question_types}",
        ]
        return "\n".join(lines)

_SESSION_STATS = SessionStats()

# ════════════════════════════════════════════════════════════
#  ГЛАВНАЯ ФУНКЦИЯ ФИНАЛИЗАЦИИ ОТВЕТА
# ════════════════════════════════════════════════════════════

def finalize_answer(query: str, raw_answer: str,
                    question_type: str = "what",
                    sources: int = 0,
                    elapsed: float = 0.0,
                    save: bool = True,
                    verbose: bool = True) -> str:
    """
    Финализирует ответ:
    1. Проверяет качество
    2. Очищает от мусора
    3. Форматирует
    4. Сохраняет в файл и кэш
    5. Выводит на экран
    """
    if not raw_answer or is_garbage_answer(raw_answer):
        if verbose:
            print("[AI] Ответ не найден или некачественный")
        return ""
    # Очистка
    answer = clean_answer(raw_answer)
    if not answer:
        return ""
    # Форматирование для экрана
    formatted = format_answer_chatgpt(
        query=query,
        answer=answer,
        sources=sources,
        elapsed=elapsed,
    )
    if verbose:
        print(formatted)
        print(f"Время: {elapsed:.1f}с | Источников: {sources}")
    # Сохранение
    if save:
        save_to_output_file(formatted)
        _ANSWER_CACHE.set(query, answer)
        if verbose:
            print(f"Сохранено: {OUTPUT_FILE}")
    return answer

def finalize_math_answer(query: str, answer: str,
                          verbose: bool = True,
                          save: bool = True) -> str:
    """Финализирует математический ответ."""
    if not answer:
        return ""
    formatted = format_math_answer(query, answer)
    if verbose:
        print(formatted)
    if save:
        save_to_output_file(formatted)
        _ANSWER_CACHE.set(query, answer)
        print(f"Сохранено: {OUTPUT_FILE}")
    return answer

def get_cached_or_none(query: str) -> Optional[str]:
    """Возвращает кэшированный ответ или None."""
    return _ANSWER_CACHE.get(query)

def handle_no_answer(query: str, verbose: bool = True) -> str:
    """Обрабатывает ситуацию когда ответ не найден."""
    msg = (
        f"Не удалось найти ответ на вопрос «{query}».\n"
        "Попробуйте переформулировать запрос."
    )
    if verbose:
        print(f"\n[AI] {msg}")
    return msg

# ════════════════════════════════════════════════════════════
#  ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА ПОИСКА В КОНСОЛИ
# ════════════════════════════════════════════════════════════

def print_search_progress(num_found: int, num_loaded: int):
    """Выводит прогресс поиска."""
    print(f"[AI] Готово: {num_loaded} сайтов, символов обработано: {num_found}")

def print_final_answer(answer: str, query: str, sources: int,
                        elapsed: float):
    """Печатает финальный ответ."""
    print()
    print(SEPARATOR)
    print("ОТВЕТ:")
    print(answer)
    print(SEPARATOR)
    print(f"Время: {elapsed:.1f}с | Источников: {sources}")
    print(f"Сохранено: {OUTPUT_FILE}")

def print_cached_answer(answer: str):
    """Выводит ответ из кэша."""
    print(f"[Cache] {answer}")

def print_math_answer(query: str, answer: str):
    """Выводит математический ответ."""
    print(f"[Math] {query} = {answer}")

# ════════════════════════════════════════════════════════════
#  УЛУЧШЕНИЕ ОТВЕТА
# ════════════════════════════════════════════════════════════

def improve_answer_for_type(answer: str, query: str,
                             question_type: str) -> str:
    """
    Улучшает ответ с учётом типа вопроса.
    """
    if not answer:
        return ""
    # Для определений — проверяем что ответ содержит объяснение
    if question_type == "definition":
        definition_words = ["означает", "является", "представляет", "называется",
                           "—", "это", "слово", "понятие"]
        if not any(w in answer.lower() for w in definition_words):
            # Добавляем контекст
            subject = _extract_simple_subject(query)
            if subject and subject.lower() not in answer.lower():
                answer = f"{subject} — {answer}"
    # Для географии — проверяем что ответ содержит географическое слово
    elif question_type == "where":
        if not any(w in answer.lower() for w in
                   ["столица", "город", "страна", "расположен", "находится"]):
            answer = answer
    return answer

def _extract_simple_subject(query: str) -> str:
    """Простое извлечение темы из запроса."""
    for trigger in ["что означает", "что значит", "что такое",
                    "кто такой", "кто такая", "кто это",
                    "где находится"]:
        if trigger in query.lower():
            return query.lower().split(trigger, 1)[1].strip(" ?!.").title()
    return ""

def combine_multiple_answers(answers: list, max_length: int = 400) -> str:
    """
    Объединяет несколько ответов в один.
    Убирает дублирование.
    """
    if not answers:
        return ""
    if len(answers) == 1:
        return answers[0]
    # Убираем дубли
    unique = []
    seen_words = set()
    for ans in answers:
        words = set(ans.lower().split())
        overlap = len(words & seen_words) / max(1, len(words))
        if overlap < 0.7:
            unique.append(ans)
            seen_words.update(words)
    combined = " ".join(unique)
    if len(combined) > max_length:
        combined = combined[:max_length]
        last_punct = max(combined.rfind('.'), combined.rfind('!'), combined.rfind('?'))
        if last_punct > max_length // 2:
            combined = combined[:last_punct + 1]
    return combined

# ════════════════════════════════════════════════════════════
#  ПУБЛИЧНЫЙ API
# ════════════════════════════════════════════════════════════

__all__ = [
    "calculate",
    "is_math_question",
    "is_garbage_answer",
    "clean_answer",
    "filter_and_clean",
    "finalize_answer",
    "finalize_math_answer",
    "get_cached_or_none",
    "handle_no_answer",
    "improve_answer_for_type",
    "combine_multiple_answers",
    "format_answer_chatgpt",
    "format_math_answer",
    "format_error_answer",
    "print_final_answer",
    "print_cached_answer",
    "print_math_answer",
    "print_search_progress",
    "save_to_output_file",
    "overwrite_output_file",
    "read_output_file",
    "clear_output_file",
    "init_output_file",
    "_ANSWER_CACHE",
    "_SESSION_STATS",
    "OUTPUT_FILE",
    "SEPARATOR",
    "SHORT_SEP",
    "MATH_CONSTANTS",
    "KNOWN_ABBREVS_EXTRA",
]

# Дополнительные аббревиатуры (продолжение из gg.py)
KNOWN_ABBREVS_EXTRA = {
    "ASAP": "ASAP (As Soon As Possible) — как можно скорее. Английское выражение означающее срочность.",
    "DIY": "DIY (Do It Yourself) — сделай сам. Концепция самостоятельного изготовления или ремонта.",
    "FAQ": "FAQ (Frequently Asked Questions) — часто задаваемые вопросы. Раздел с популярными вопросами и ответами.",
    "FYI": "FYI (For Your Information) — для вашей информации. Пометка что данные предоставляются для справки.",
    "IMHO": "IMHO (In My Humble Opinion) — по моему скромному мнению. Выражение личной точки зрения.",
    "LOL": "LOL (Laughing Out Loud) — громко смеясь. Выражение веселья в переписке.",
    "OMG": "OMG (Oh My God) — боже мой. Выражение удивления или восклицания.",
    "BTW": "BTW (By The Way) — кстати. Вводное слово при добавлении информации.",
    "ETA": "ETA (Estimated Time of Arrival) — расчётное время прибытия. Ожидаемое время.",
    "TBD": "TBD (To Be Determined) — ещё не определено. Используется когда детали не согласованы.",
    "TBA": "TBA (To Be Announced) — будет объявлено. Означает что информация появится позже.",
    "TLDR": "TL;DR (Too Long; Didn't Read) — слишком длинно, не читал. Краткое резюме длинного текста.",
    "AKA": "AKA (Also Known As) — также известный как. Псевдоним или альтернативное название.",
    "RSVP": "RSVP (Répondez s'il vous plaît) — просьба ответить. Французское выражение на приглашениях.",
    "VIP": "VIP (Very Important Person) — очень важная персона. Человек имеющий особый статус.",
    "PR": "PR (Public Relations) — связи с общественностью. Управление репутацией и коммуникациями.",
    "HR": "HR (Human Resources) — отдел кадров/управление персоналом.",
    "CEO": "CEO (Chief Executive Officer) — генеральный директор. Главное исполнительное лицо компании.",
    "CTO": "CTO (Chief Technology Officer) — технический директор. Руководитель IT-направления.",
    "CFO": "CFO (Chief Financial Officer) — финансовый директор. Руководитель финансового отдела.",
}

# ────────────────────────────────────────────────────────────
#  ТЕСТ ПРИ ПРЯМОМ ЗАПУСКЕ
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[finally.py] Тест математики:")
    test_calcs = [
        "сколько будет 2 + 2",
        "корень из 144",
        "5 в степени 3",
        "10% от 350",
        "sin 30",
        "15 * 7 + 3",
        "factorial 5",
    ]
    for q in test_calcs:
        result = calculate(q)
        print(f"  «{q}» → {result}")
    print()
    print("[finally.py] Тест мусорных фильтров:")
    test_texts = [
        "Принять cookies",
        "Войти через Google",
        "Париж — столица Франции и крупнейший город страны",
        "Подпишитесь на нашу рассылку",
        "HI означает 'привет' по-английски",
    ]
    for t in test_texts:
        print(f"  «{t[:40]}» → мусор: {is_garbage_answer(t)}")

# ════════════════════════════════════════════════════════════
#  РАСШИРЕННЫЕ МАТЕМАТИЧЕСКИЕ ФУНКЦИИ
# ════════════════════════════════════════════════════════════

def compute_gcd(a: int, b: int) -> int:
    """Вычисляет наибольший общий делитель."""
    while b:
        a, b = b, a % b
    return a

def compute_lcm(a: int, b: int) -> int:
    """Вычисляет наименьшее общее кратное."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // compute_gcd(a, b)

def is_prime(n: int) -> bool:
    """Проверяет, является ли число простым."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def factorize(n: int) -> list:
    """Разложение числа на простые множители."""
    if n <= 1:
        return [n]
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def compute_primes_up_to(n: int) -> list:
    """Решето Эратосфена — все простые числа до n."""
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.sqrt(n)) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i, v in enumerate(sieve) if v]

def solve_quadratic(a: float, b: float, c: float) -> Optional[tuple]:
    """
    Решает квадратное уравнение ax² + bx + c = 0.
    Возвращает (x1, x2) или None.
    """
    if a == 0:
        if b == 0:
            return None
        return (-c / b, None)
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return None  # Нет вещественных решений
    elif discriminant == 0:
        x = -b / (2 * a)
        return (x, x)
    else:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        return (x1, x2)

def compute_arithmetic_progression(a1: float, d: float, n: int) -> dict:
    """Арифметическая прогрессия."""
    an = a1 + (n - 1) * d
    sn = n * (a1 + an) / 2
    return {"a_n": an, "S_n": sn, "a_1": a1, "d": d, "n": n}

def compute_geometric_progression(a1: float, r: float, n: int) -> dict:
    """Геометрическая прогрессия."""
    an = a1 * r ** (n - 1)
    if r == 1:
        sn = a1 * n
    else:
        sn = a1 * (r**n - 1) / (r - 1)
    return {"a_n": an, "S_n": sn, "a_1": a1, "r": r, "n": n}

def compute_combinations(n: int, k: int) -> Optional[int]:
    """Вычисляет число сочетаний C(n, k)."""
    if k > n or k < 0:
        return None
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result

def compute_permutations(n: int, k: int) -> Optional[int]:
    """Вычисляет число размещений P(n, k)."""
    if k > n or k < 0:
        return None
    result = 1
    for i in range(n, n - k, -1):
        result *= i
    return result

def parse_math_function(query: str) -> Optional[str]:
    """
    Парсит и вычисляет специальные математические функции.
    """
    q = query.lower().strip()
    # НОД
    m = re.search(r'(?:нод|gcd)\s*\(?\s*(\d+)\s*,\s*(\d+)\s*\)?', q)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return f"НОД({a}, {b}) = {compute_gcd(a, b)}"
    # НОК
    m = re.search(r'(?:нок|lcm)\s*\(?\s*(\d+)\s*,\s*(\d+)\s*\)?', q)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return f"НОК({a}, {b}) = {compute_lcm(a, b)}"
    # Простое ли число
    m = re.search(r'(?:простое ли|is prime)\s+(\d+)', q)
    if m:
        n = int(m.group(1))
        if is_prime(n):
            return f"{n} — простое число"
        else:
            factors = factorize(n)
            return f"{n} — составное число, разложение: {' × '.join(map(str, factors))}"
    # Разложение на множители
    m = re.search(r'(?:разложить|факторизация|factorize)\s+(\d+)', q)
    if m:
        n = int(m.group(1))
        factors = factorize(n)
        return f"{n} = {' × '.join(map(str, factors))}"
    # Сочетания
    m = re.search(r'(?:сочетание[я]?|combinations?|C)\s*\(?(\d+)[,;]\s*(\d+)\)?', q)
    if m:
        n, k = int(m.group(1)), int(m.group(2))
        result = compute_combinations(n, k)
        if result is not None:
            return f"C({n},{k}) = {result}"
    # Размещения
    m = re.search(r'(?:размещение[я]?|permutations?|A|P)\s*\(?(\d+)[,;]\s*(\d+)\)?', q)
    if m:
        n, k = int(m.group(1)), int(m.group(2))
        result = compute_permutations(n, k)
        if result is not None:
            return f"A({n},{k}) = {result}"
    return None

# Обновляем функцию calculate для поддержки новых функций
_old_calculate = calculate

def calculate_extended(query: str) -> Optional[str]:
    """Расширенный калькулятор с поддержкой новых функций."""
    # Проверяем специальные математические функции
    result = parse_math_function(query)
    if result:
        return result
    # Используем старый calculate
    return _old_calculate(query)

# Заменяем calculate на расширенную версию
calculate = calculate_extended

# ════════════════════════════════════════════════════════════
#  РАСШИРЕННАЯ ОЧИСТКА ТЕКСТА
# ════════════════════════════════════════════════════════════

EXTENDED_GARBAGE_PATTERNS = [
    # Лишние призывы к действию
    r'подпис\w+ся\s+на\s+наш',
    r'нажмите\s+кнопку',
    r'перейди\w*\s+по\s+ссылке',
    r'скачайте\s+(?:приложение|файл|книгу)',
    r'получите\s+(?:доступ|скидку|бонус)',
    r'зарегистрируйтесь\s+(?:сейчас|бесплатно)',
    r'оставьте\s+(?:заявку|комментарий|отзыв)',
    r'позвоните\s+нам',
    r'напишите\s+нам',
    r'свяжитесь\s+с\s+нами',
    # Юридический мусор
    r'все\s+права\s+защищены',
    r'©\s*(?:20\d\d|19\d\d)',
    r'перепечатка\s+(?:материалов|без\s+разрешения)',
    r'данный\s+(?:сайт|ресурс)\s+использует',
    r'настоящим\s+(?:соглашением|договором|документом)',
    # Навигационный мусор
    r'главная\s*/\s*\w+\s*/\s*\w+',
    r'breadcrumb',
    r'вы\s+здесь:\s*',
    # Счётчики и трекинг
    r'google\s+analytics',
    r'yandex\.metrika',
    r'счётчик\s+посещений',
    r'уникальных\s+(?:посетителей|просмотров)',
    # Форматирование мусора (веб)
    r'\|\s+\|\s+\|',  # Таблицы без данных
    r'_{3,}',           # Подчёркивания
    r'\*{3,}',          # Звёздочки
    r'={3,}',           # Равно (разделители)
    r'-{5,}',           # Тире (разделители)
    # Технический мусор
    r'var\s+\w+\s*=',   # JavaScript
    r'function\s*\(',   # JavaScript
    r'\.css\s*\{',      # CSS
    r'@media\s+',       # CSS media query
    r'<\?php',          # PHP
    r'SELECT\s+\*\s+FROM', # SQL
]

def is_extended_garbage(text: str) -> bool:
    """Расширенная проверка на мусор."""
    if is_garbage_answer(text):
        return True
    text_lower = text.lower()
    for pat in EXTENDED_GARBAGE_PATTERNS:
        if re.search(pat, text_lower):
            return True
    return False

# ════════════════════════════════════════════════════════════
#  СТАТИСТИКА ПО СЛОВАМ В ОТВЕТЕ
# ════════════════════════════════════════════════════════════

def word_frequency_analysis(text: str) -> dict:
    """
    Анализ частоты слов в тексте.
    """
    if not text:
        return {}
    words = re.findall(r'\b[а-яёA-Za-z]{3,}\b', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    # Убираем стоп-слова
    freq = {w: c for w, c in freq.items()
            if w not in gg_mod.STOPWORDS_RU and w not in gg_mod.STOPWORDS_EN}
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

def top_keywords(text: str, n: int = 10) -> list:
    """Возвращает топ-N ключевых слов из текста."""
    freq = word_frequency_analysis(text)
    return list(freq.keys())[:n]

def keyword_density(text: str, keyword: str) -> float:
    """Плотность ключевого слова в тексте (%)."""
    if not text or not keyword:
        return 0.0
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    count = words.count(keyword.lower())
    return count / len(words) * 100

# ════════════════════════════════════════════════════════════
#  ДОПОЛНИТЕЛЬНЫЕ ФОРМАТЫ ВЫВОДА
# ════════════════════════════════════════════════════════════

def format_as_bullet_list(items: list, header: str = "") -> str:
    """Форматирует список элементов как маркированный список."""
    lines = []
    if header:
        lines.append(header)
        lines.append("-" * len(header))
    for item in items:
        lines.append(f"  • {item}")
    return "\n".join(lines)

def format_as_numbered_list(items: list, header: str = "") -> str:
    """Форматирует список элементов как нумерованный список."""
    lines = []
    if header:
        lines.append(header)
    for i, item in enumerate(items, 1):
        lines.append(f"  {i}. {item}")
    return "\n".join(lines)

def format_as_table(headers: list, rows: list) -> str:
    """Форматирует данные в текстовую таблицу."""
    if not headers or not rows:
        return ""
    # Ширина колонок
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    # Разделитель
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    # Заголовок
    header_row = "|" + "|".join(
        f" {str(h):<{w}} " for h, w in zip(headers, col_widths)
    ) + "|"
    lines = [sep, header_row, sep]
    # Данные
    for row in rows:
        row_str = "|" + "|".join(
            f" {str(cell):<{w}} "
            for cell, w in zip(row, col_widths)
        ) + "|"
        lines.append(row_str)
    lines.append(sep)
    return "\n".join(lines)

def format_key_value(pairs: dict, separator: str = ": ") -> str:
    """Форматирует словарь как пары ключ: значение."""
    if not pairs:
        return ""
    max_key_len = max(len(k) for k in pairs)
    lines = []
    for k, v in pairs.items():
        padded_key = f"{k:<{max_key_len}}"
        lines.append(f"  {padded_key}{separator}{v}")
    return "\n".join(lines)

# ════════════════════════════════════════════════════════════
#  УПРАВЛЕНИЕ ИСТОРИЕЙ ВОПРОСОВ
# ════════════════════════════════════════════════════════════

class QuestionHistory:
    """
    История вопросов и ответов сессии.
    """

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._history: list = []

    def add(self, query: str, answer: str, question_type: str = "what",
            elapsed: float = 0.0):
        """Добавляет пару вопрос-ответ в историю."""
        entry = {
            "query": query,
            "answer": answer[:500],
            "type": question_type,
            "elapsed": elapsed,
            "ts": time.time(),
        }
        self._history.append(entry)
        if len(self._history) > self.max_size:
            self._history.pop(0)

    def get_last(self, n: int = 5) -> list:
        """Возвращает последние N записей."""
        return self._history[-n:]

    def search(self, keyword: str) -> list:
        """Ищет записи содержащие ключевое слово."""
        kw_lower = keyword.lower()
        return [
            e for e in self._history
            if kw_lower in e["query"].lower() or kw_lower in e["answer"].lower()
        ]

    def to_json(self) -> str:
        """Сериализует историю в JSON."""
        import json
        return json.dumps(self._history, ensure_ascii=False, indent=2)

    def clear(self):
        """Очищает историю."""
        self._history = []

    @property
    def size(self) -> int:
        return len(self._history)

# Глобальный объект истории
_QUESTION_HISTORY = QuestionHistory()

# ════════════════════════════════════════════════════════════
#  ДОПОЛНИТЕЛЬНЫЕ АББРЕВИАТУРЫ В KNOWN_ABBREVS_EXTRA
# ════════════════════════════════════════════════════════════

KNOWN_ABBREVS_EXTRA.update({
    "B2B": "B2B (Business to Business) — бизнес для бизнеса. Модель продаж между компаниями.",
    "B2C": "B2C (Business to Consumer) — бизнес для потребителя. Продажа товаров конечным покупателям.",
    "P2P": "P2P (Peer to Peer) — равный к равному. Децентрализованная сеть без центрального сервера.",
    "UX": "UX (User Experience) — пользовательский опыт. Ощущения пользователя при взаимодействии с продуктом.",
    "UI": "UI (User Interface) — пользовательский интерфейс. Визуальная часть программы или сайта.",
    "MVP": "MVP (Minimum Viable Product) — минимально жизнеспособный продукт. Версия с базовым набором функций.",
    "A/B": "A/B тестирование — сравнение двух версий (A и B) для определения более эффективной.",
    "PM": "PM (Project Manager) — руководитель проекта. Специалист управляющий проектом.",
    "QA": "QA (Quality Assurance) — контроль качества. Процесс обеспечения качества программного обеспечения.",
    "SCRUM": "Scrum — гибкая методология управления проектами. Работа короткими итерациями (спринтами).",
    "OKR": "OKR (Objectives and Key Results) — метод постановки целей через ключевые результаты.",
    "NPS": "NPS (Net Promoter Score) — показатель лояльности клиентов. Вероятность рекомендовать продукт.",
    "SLA": "SLA (Service Level Agreement) — соглашение об уровне обслуживания. Гарантии качества сервиса.",
    "SLO": "SLO (Service Level Objective) — целевой показатель уровня сервиса.",
    "ROE": "ROE (Return on Equity) — рентабельность собственного капитала. Финансовый показатель.",
    "ROA": "ROA (Return on Assets) — рентабельность активов. Показатель эффективности использования активов.",
    "EBITDA": "EBITDA — прибыль до вычета процентов, налогов и амортизации. Показатель операционной прибыльности.",
    "P&L": "P&L (Profit and Loss) — отчёт о прибылях и убытках.",
    "IRR": "IRR (Internal Rate of Return) — внутренняя норма доходности инвестиций.",
    "NPV": "NPV (Net Present Value) — чистая приведённая стоимость. Метод оценки инвестиций.",
    "FIFO": "FIFO (First In, First Out) — первый пришёл — первый ушёл. Принцип организации очереди.",
    "LIFO": "LIFO (Last In, First Out) — последний пришёл — первый ушёл.",
    "ISO": "ISO (International Organization for Standardization) — Международная организация по стандартизации.",
    "IEEE": "IEEE (Institute of Electrical and Electronics Engineers) — Институт инженеров электротехники и электроники.",
    "ANSI": "ANSI (American National Standards Institute) — Американский национальный институт стандартов.",
    "RFC": "RFC (Request for Comments) — запрос комментариев. Документы описывающие стандарты интернета.",
    "MIME": "MIME (Multipurpose Internet Mail Extensions) — расширения почтового формата интернета.",
    "IMAP": "IMAP (Internet Message Access Protocol) — протокол доступа к электронной почте.",
    "SMTP": "SMTP (Simple Mail Transfer Protocol) — протокол отправки электронной почты.",
    "POP3": "POP3 (Post Office Protocol 3) — протокол получения электронной почты.",
    "TCP": "TCP (Transmission Control Protocol) — протокол управления передачей. Надёжный протокол интернета.",
    "UDP": "UDP (User Datagram Protocol) — протокол пользовательских датаграмм. Быстрый, без гарантии доставки.",
    "TLS": "TLS (Transport Layer Security) — протокол защиты транспортного уровня. Шифрование данных.",
    "SSL": "SSL (Secure Sockets Layer) — устаревшее название TLS. Протокол безопасной передачи данных.",
    "RSA": "RSA — алгоритм шифрования с открытым ключом. Назван по именам Ривест, Шамир, Адлеман.",
    "AES": "AES (Advanced Encryption Standard) — усовершенствованный стандарт шифрования.",
    "MD5": "MD5 (Message Digest 5) — алгоритм хеширования. Создаёт 128-битный хеш.",
    "SHA": "SHA (Secure Hash Algorithm) — безопасный алгоритм хеширования.",
    "JWT": "JWT (JSON Web Token) — токен для передачи данных между сервисами в формате JSON.",
    "OAuth": "OAuth — открытый стандарт авторизации. Позволяет входить через сторонние аккаунты.",
    "CORS": "CORS (Cross-Origin Resource Sharing) — совместное использование ресурсов из разных источников.",
    "REST": "REST (Representational State Transfer) — архитектурный стиль для веб-сервисов.",
    "SOAP": "SOAP (Simple Object Access Protocol) — протокол обмена структурированными сообщениями.",
    "GraphQL": "GraphQL — язык запросов для API, разработанный Facebook.",
    "gRPC": "gRPC — высокопроизводительный фреймворк для удалённых вызовов процедур от Google.",
    "YAML": "YAML (YAML Ain't Markup Language) — формат сериализации данных, удобный для чтения.",
    "CSV": "CSV (Comma-Separated Values) — формат хранения таблиц в текстовом файле через запятую.",
    "SQL": "SQL (Structured Query Language) — язык структурированных запросов для баз данных.",
    "NoSQL": "NoSQL — базы данных не использующие реляционную модель. MongoDB, Redis, Cassandra.",
    "ACID": "ACID — свойства транзакций в БД: атомарность, согласованность, изолированность, долговечность.",
    "CAP": "CAP-теорема — в распределённых системах можно гарантировать только 2 из 3 свойств: согласованность, доступность, устойчивость к разделению.",
    "DDD": "DDD (Domain-Driven Design) — предметно-ориентированное проектирование программ.",
    "TDD": "TDD (Test-Driven Development) — разработка через тестирование.",
    "BDD": "BDD (Behavior-Driven Development) — разработка через описание поведения.",
    "SOLID": "SOLID — пять принципов объектно-ориентированного дизайна (Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion).",
    "DRY": "DRY (Don't Repeat Yourself) — принцип программирования: не повторяй себя.",
    "KISS": "KISS (Keep It Simple, Stupid) — принцип: делай проще.",
    "YAGNI": "YAGNI (You Ain't Gonna Need It) — принцип: не добавляй то, что не нужно сейчас.",
})

# ════════════════════════════════════════════════════════════
#  ПУБЛИЧНЫЙ API (дополнение)
# ════════════════════════════════════════════════════════════

__all__.extend([
    "calculate_extended",
    "compute_gcd",
    "compute_lcm",
    "is_prime",
    "factorize",
    "solve_quadratic",
    "compute_combinations",
    "compute_permutations",
    "parse_math_function",
    "is_extended_garbage",
    "word_frequency_analysis",
    "top_keywords",
    "keyword_density",
    "format_as_bullet_list",
    "format_as_numbered_list",
    "format_as_table",
    "format_key_value",
    "QuestionHistory",
    "_QUESTION_HISTORY",
])


# ════════════════════════════════════════════════════════════
#  РАСШИРЕННАЯ МАТЕМАТИЧЕСКАЯ БИБЛИОТЕКА
# ════════════════════════════════════════════════════════════

MATH_FORMULAS = {
    "площадь квадрата": "S = a²",
    "площадь прямоугольника": "S = a × b",
    "площадь треугольника": "S = (a × h) / 2",
    "площадь круга": "S = π × r²",
    "площадь трапеции": "S = ((a + b) / 2) × h",
    "площадь параллелограмма": "S = a × h",
    "площадь ромба": "S = (d₁ × d₂) / 2",
    "объём куба": "V = a³",
    "объём прямоугольного параллелепипеда": "V = a × b × c",
    "объём цилиндра": "V = π × r² × h",
    "объём шара": "V = (4/3) × π × r³",
    "объём конуса": "V = (1/3) × π × r² × h",
    "объём пирамиды": "V = (1/3) × S × h",
    "периметр квадрата": "P = 4a",
    "периметр прямоугольника": "P = 2(a + b)",
    "длина окружности": "C = 2πr",
    "теорема Пифагора": "c² = a² + b²",
    "теорема косинусов": "c² = a² + b² - 2ab·cos(C)",
    "теорема синусов": "a/sin(A) = b/sin(B) = c/sin(C)",
    "скорость": "v = s / t",
    "ускорение": "a = Δv / Δt",
    "сила": "F = m × a",
    "давление": "P = F / S",
    "работа": "W = F × s × cos(α)",
    "мощность": "N = W / t = F × v",
    "кинетическая энергия": "Eₖ = mv² / 2",
    "потенциальная энергия": "Eₚ = mgh",
    "закон всемирного тяготения": "F = G × m₁m₂ / r²",
    "закон ома": "I = U / R",
    "электрическая мощность": "P = U × I = I²R = U²/R",
    "условие равновесия рычага": "F₁ × l₁ = F₂ × l₂",
    "плотность": "ρ = m / V",
    "первый закон термодинамики": "ΔU = Q - W",
    "идеальный газ": "pV = nRT",
    "формула Планка": "E = hν",
    "энергия фотона": "E = mc²",
    "формула радиоактивного распада": "N = N₀ × e^(-λt)",
    "формула дисперсии": "D = Σ(xᵢ - x̄)² / n",
    "формула стандартного отклонения": "σ = √D",
    "корреляция Пирсона": "r = Σ((x-x̄)(y-ȳ)) / (n × σₓ × σᵧ)",
    "логарифмы": "logₐ(x) = ln(x) / ln(a)",
    "формула комбинаций": "C(n,k) = n! / (k! × (n-k)!)",
    "формула размещений": "A(n,k) = n! / (n-k)!",
    "формула перестановок": "P(n) = n!",
    "биномиальный коэффициент": "C(n,k) = C(n-1,k-1) + C(n-1,k)",
    "сумма арифметической прогрессии": "Sₙ = n(a₁+aₙ)/2",
    "сумма геометрической прогрессии": "Sₙ = a₁(qⁿ-1)/(q-1)",
    "формула сложных процентов": "A = P(1 + r/n)^(nt)",
    "формула простых процентов": "A = P(1 + rt)",
}

def get_math_formula(query: str) -> str:
    """Возвращает математическую формулу по запросу."""
    q = query.lower()
    for name, formula in MATH_FORMULAS.items():
        if any(w in q for w in name.split()):
            return f"{name}: {formula}"
    return ""

PHYSICS_CONSTANTS = {
    "G": ("Гравитационная постоянная", "6.674e-11 Н·м²/кг²"),
    "c": ("Скорость света", "2.998e8 м/с"),
    "h": ("Постоянная Планка", "6.626e-34 Дж·с"),
    "ℏ": ("Редуцированная постоянная Планка", "1.055e-34 Дж·с"),
    "k": ("Постоянная Больцмана", "1.381e-23 Дж/К"),
    "Nₐ": ("Число Авогадро", "6.022e23 моль⁻¹"),
    "R": ("Универсальная газовая постоянная", "8.314 Дж/(моль·К)"),
    "e": ("Заряд электрона", "1.602e-19 Кл"),
    "mₑ": ("Масса электрона", "9.109e-31 кг"),
    "mₚ": ("Масса протона", "1.673e-27 кг"),
    "mₙ": ("Масса нейтрона", "1.675e-27 кг"),
    "ε₀": ("Электрическая постоянная", "8.854e-12 Ф/м"),
    "μ₀": ("Магнитная постоянная", "4π×10⁻⁷ Гн/м"),
    "σ": ("Постоянная Стефана-Больцмана", "5.671e-8 Вт/(м²·К⁴)"),
    "g": ("Ускорение свободного падения", "9.807 м/с²"),
    "atm": ("Стандартное давление", "101325 Па"),
    "F": ("Постоянная Фарадея", "96485 Кл/моль"),
}

# ════════════════════════════════════════════════════════════
#  БОЛЬШАЯ БАЗА МУСОРНЫХ ПАТТЕРНОВ И ФИЛЬТРОВ
# ════════════════════════════════════════════════════════════

DATE_FORMATS = [
    "%d.%m.%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%d %B %Y",
    "%B %d, %Y",
    "%d.%m.%y",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y.%m.%d",
]

TIMEZONES = {
    "Москва": "UTC+3",
    "Санкт-Петербург": "UTC+3",
    "Екатеринбург": "UTC+5",
    "Новосибирск": "UTC+7",
    "Омск": "UTC+6",
    "Красноярск": "UTC+7",
    "Иркутск": "UTC+8",
    "Якутск": "UTC+9",
    "Владивосток": "UTC+10",
    "Магадан": "UTC+11",
    "Камчатка": "UTC+12",
    "Калининград": "UTC+2",
    "Лондон": "UTC+0",
    "Берлин": "UTC+1",
    "Париж": "UTC+1",
    "Рим": "UTC+1",
    "Мадрид": "UTC+1",
    "Варшава": "UTC+1",
    "Стамбул": "UTC+3",
    "Дубай": "UTC+4",
    "Тегеран": "UTC+3:30",
    "Нью-Йорк": "UTC-5",
    "Чикаго": "UTC-6",
    "Лос-Анджелес": "UTC-8",
    "Токио": "UTC+9",
    "Пекин": "UTC+8",
    "Шанхай": "UTC+8",
    "Дели": "UTC+5:30",
    "Бангкок": "UTC+7",
    "Сингапур": "UTC+8",
    "Сидней": "UTC+10",
    "Окленд": "UTC+12",
}


# ════════════════════════════════════════════════════════════
#  ФИНАЛИЗАТОР: РАСШИРЕННЫЕ ПАТТЕРНЫ
# ════════════════════════════════════════════════════════════

