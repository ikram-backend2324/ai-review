import re
import random
import requests
from django.conf import settings


def ask_ai(messages: list) -> str:
    """Call OpenRouter AI and return the text response."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://quizbot.app",
                "X-Title": "QuizBot Web",
            },
            json={
                "model": settings.AI_MODEL,
                "messages": messages,
            },
            timeout=30,
        )
        data = response.json()
        if "choices" not in data:
            return "⚠️ AI временно недоступен."
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ Ошибка ИИ. Попробуйте позже."


def extract_score(text: str) -> int:
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def generate_question(subject_name: str) -> str:
    random_id = random.randint(1, 100000)
    prompt = f"""
Создай ОДИН вопрос по теме: {subject_name}.

Формат строго:
Вопрос: <текст вопроса>

❗ ЗАПРЕЩЕНО:
- писать ответ
- писать решение
- добавлять объяснения

ID: {random_id}
"""
    return ask_ai([
        {"role": "system", "content": "Отвечай только на русском языке."},
        {"role": "user", "content": prompt},
    ])


def evaluate_answer(question: str, user_answer: str) -> tuple[str, int]:
    prompt = f"""
Вопрос: {question}
Ответ пользователя: {user_answer}

Оцени ответ от 0 до 100%.
Отвечай только на русском языке.

Формат:
Оценка: XX%
Комментарий: ...
"""
    result = ask_ai([
        {"role": "system", "content": "Отвечай только на русском языке."},
        {"role": "user", "content": prompt},
    ])
    score = extract_score(result)
    return result, score
