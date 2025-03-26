import asyncio
import telegram

async def get_chat_id():
    TELEGRAM_TOKEN = '6377969316:AAEKc2q_6u60iFM3idaw0VEihIeC9vXKpTY'  # Replace with your actual Telegram token
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    updates = await bot.get_updates()

    if updates:
        chat_id = updates[0].message.chat_id
        print(f"Chat ID: {chat_id}")
    else:
        print("No updates found. Send a message to the bot to get an update.")

if __name__ == "__main__":
    asyncio.run(get_chat_id())