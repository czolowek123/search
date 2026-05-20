#!/usr/bin/env python
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2-vision:11b')
ANSWER_FILE_NAME = os.environ.get('ANSWER_FILE_NAME', 'main.txt')


def ask_ollama(question):
    prompt = (
        "Отвечай по-русски, понятно и кратко.\n"
        "Если точно не знаешь ответ, скажи об этом честно.\n\n"
        f"Вопрос пользователя:\n{question}"
    )

    payload = {
        'model': OLLAMA_MODEL,
        'prompt': prompt,
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


def get_answer_file_path():
    current_dir = Path(__file__).resolve().parent
    answer_file = Path(ANSWER_FILE_NAME)

    if answer_file.is_absolute():
        return answer_file

    return current_dir / answer_file


def write_answer_to_file(question, answer):
    answer_file_path = get_answer_file_path()

    text = (
        "QUESTION:\n"
        f"{question}\n\n"
        "ANSWER:\n"
        f"{answer}\n"
    )

    answer_file_path.write_text(text, encoding='utf-8')

    return answer_file_path


def get_question_from_user():
    if len(sys.argv) > 1:
        return ' '.join(sys.argv[1:]).strip()

    return input('Что хотите задать? ').strip()


def main():
    question = get_question_from_user()

    if not question:
        print('Вопрос пустой. Напишите вопрос и запустите ещё раз.')
        return

    try:
        answer = ask_ollama(question)
    except urllib.error.URLError as exc:
        answer = (
            "Не получилось подключиться к Ollama. "
            "Проверьте, что Ollama запущена командой: ollama serve. "
            f"Ошибка: {exc}"
        )
    except Exception as exc:
        answer = f"Произошла ошибка при запросе к Ollama: {exc}"

    if not answer:
        answer = 'Ollama вернула пустой ответ.'

    answer_file_path = write_answer_to_file(question, answer)

    print('Ответ записан в файл:')
    print(answer_file_path)


if __name__ == '__main__':
    main()