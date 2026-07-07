import asyncio
import os
from threading import Thread

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from flask import Flask
from openai import AsyncOpenAI

# ======================================
# Загрузка переменных окружения
# ======================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ======================================
# Загрузка системного промпта
# ======================================

def load_system_prompt():
    with open("system_prompt.txt", "r", encoding="utf-8") as file:
        return file.read().strip()

SYSTEM_PROMPT = load_system_prompt()

# ======================================
# Инициализация
# ======================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ======================================
# <<< ДОБАВЛЕНО >>>
# История диалогов пользователей
# Ключ = Telegram ID
# Значение = список сообщений
# ======================================

dialog_histories = {}

# ======================================
# Веб-сервер для Render
# ======================================

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Бот работает!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ======================================
# Команда /start
# ======================================

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Я чат-бот с искусственным интеллектом.\n"
        "Напишите мне любой вопрос."
    )

# ======================================
# Общение с GPT
# ======================================

@dp.message(F.text)
async def chat(message: Message):

    # <<< ДОБАВЛЕНО >>>
    # Получаем ID пользователя

    user_id = message.from_user.id

    # Если пользователь пишет впервые —
    # создаём для него историю

    if user_id not in dialog_histories:
        dialog_histories[user_id] = []

    history = dialog_histories[user_id]

    wait = await message.answer("⏳ Думаю...")

    # <<< ДОБАВЛЕНО >>>
    # Сохраняем сообщение пользователя

    history.append(
        {
            "role": "user",
            "content": message.text
        }
    )

    try:

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                # <<< ДОБАВЛЕНО >>>
                *history
            ]
        )

        answer = response.choices[0].message.content

        # <<< ДОБАВЛЕНО >>>
        # Сохраняем ответ GPT

        history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        await wait.delete()
        await message.answer(answer)

    except Exception as e:
        await wait.edit_text(f"Ошибка:\n{e}")

# ======================================
# Запуск
# ======================================

async def main():
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
