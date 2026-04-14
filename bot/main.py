import asyncio
import datetime
import subprocess

import config
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile

bot = Bot(token=config.TOKEN)
dp = Dispatcher()


def save_log(user_id, user_name, command, result: str) -> None:
    with open("bot_logs.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = result or ""
        preview = text[:100]
        suffix = "..." if len(text) > 100 else ""
        f.write(f"[{timestamp}] ID: {user_id} ({user_name}) | CMD: {command}\n")
        f.write(f"RESULT: {preview}{suffix}\n")
        f.write("-" * 30 + "\n")


@dp.message()
async def execute_command(message: types.Message):
    if message.from_user.id not in config.ALLOWED_IDS:
        await message.reply("What are you doing here? You're not on the list!")
        return

    if message.text == "/log":
        if message.from_user.id == config.ROOT_ID:
            try:
                await message.answer_document(FSInputFile("bot_logs.txt"), caption="Log file")
            except Exception:
                await message.answer("File not found")
        else:
            await message.answer("Access denied")
        return

    command = message.text
    if not command:
        await message.answer("Send a text command.")
        return

    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = process.stdout if process.stdout else process.stderr
        if not output:
            output = "Done"

        user = message.from_user
        save_log(
            user.id,
            user.full_name or user.username or "unknown",
            command,
            output,
        )

        await message.answer(f"<code>{output[:4000]}</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Error: {e}")


async def main():
    bot_info = await bot.get_me()
    print("--- Bot launched ---")
    print(f"user bot: {bot_info.first_name}")
    print(f"Username: @{bot_info.username}")
    print(f"Allowed IDs: {config.ALLOWED_IDS}")
    print("-------------------")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
