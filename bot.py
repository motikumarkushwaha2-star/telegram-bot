import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Я чат-бот с искусственным интеллектом.\n"
        "Напишите мне любой вопрос."
    )

@dp.message(F.text)
async def chat(message: Message):
    wait = await message.answer("⏳ Думаю...")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Ты полезный русскоязычный помощник."
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )
        answer = response.choices[0].message.content
        await wait.delete()
        await message.answer(answer)
    except Exception as e:
        await wait.edit_text(f"Ошибка:\n{e}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":  
    asyncio.run(main())
