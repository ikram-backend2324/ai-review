import re
import random
import requests
from django.conf import settings

LANG_CONFIGS = {
    "en": {
        "system": "You must respond only in English.",
        "question_prompt": lambda subject, rid: f"""
Create ONE question on the topic: {subject}.

Strict format:
Question: <question text>

❗ FORBIDDEN:
- writing the answer
- writing the solution
- adding explanations

ID: {rid}
""",
        "eval_prompt": lambda question, answer: f"""
Question: {question}
User's answer: {answer}

Evaluate the answer from 0 to 100%.
Respond only in English.

Format:
Score: XX%
Comment: ...
""",
        "eval_system": "You must respond only in English.",
        "unavailable": "⚠️ AI is temporarily unavailable.",
        "error": "⚠️ AI error. Please try again later.",
    },
    "ru": {
        "system": "Отвечай только на русском языке.",
        "question_prompt": lambda subject, rid: f"""
Создай ОДИН вопрос по теме: {subject}.

Формат строго:
Вопрос: <текст вопроса>

❗ ЗАПРЕЩЕНО:
- писать ответ
- писать решение
- добавлять объяснения

ID: {rid}
""",
        "eval_prompt": lambda question, answer: f"""
Вопрос: {question}
Ответ пользователя: {answer}

Оцени ответ от 0 до 100%.
Отвечай только на русском языке.

Формат:
Оценка: XX%
Комментарий: ...
""",
        "eval_system": "Отвечай только на русском языке.",
        "unavailable": "⚠️ AI временно недоступен.",
        "error": "⚠️ Ошибка ИИ. Попробуйте позже.",
    },
    "uz": {
        "system": "Faqat o'zbek tilida javob ber.",
        "question_prompt": lambda subject, rid: f"""
Mavzu bo'yicha BITTA savol tuzing: {subject}.

Qat'iy format:
Savol: <savol matni>

❗ TAQIQLANADI:
- javob yozish
- yechim yozish
- tushuntirish qo'shish

ID: {rid}
""",
        "eval_prompt": lambda question, answer: f"""
Savol: {question}
Foydalanuvchi javobi: {answer}

Javobni 0 dan 100% gacha baholang.
Faqat o'zbek tilida javob bering.

Format:
Baho: XX%
Izoh: ...
""",
        "eval_system": "Faqat o'zbek tilida javob ber.",
        "unavailable": "⚠️ AI vaqtincha mavjud emas.",
        "error": "⚠️ AI xatosi. Keyinroq urinib ko'ring.",
    },
}


def get_lang_config(lang: str) -> dict:
    return LANG_CONFIGS.get(lang, LANG_CONFIGS["en"])


def ask_ai(messages: list, lang: str = "en") -> str:
    cfg = get_lang_config(lang)
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
            return cfg["unavailable"]
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("AI ERROR:", e)
        return cfg["error"]


def extract_score(text: str) -> int:
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def generate_question(subject_name: str, lang: str = "en") -> str:
    cfg = get_lang_config(lang)
    random_id = random.randint(1, 100000)
    prompt = cfg["question_prompt"](subject_name, random_id)
    return ask_ai([
        {"role": "system", "content": cfg["system"]},
        {"role": "user", "content": prompt},
    ], lang=lang)


def evaluate_answer(question: str, user_answer: str, lang: str = "en") -> tuple[str, int]:
    cfg = get_lang_config(lang)
    prompt = cfg["eval_prompt"](question, user_answer)
    result = ask_ai([
        {"role": "system", "content": cfg["eval_system"]},
        {"role": "user", "content": prompt},
    ], lang=lang)
    score = extract_score(result)
    return result, score