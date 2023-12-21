import asyncio
import telegram

async def main():
    TELEGRAM_TOKEN = '6377969316:AAEKc2q_6u60iFM3idaw0VEihIeC9vXKpTY'
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    updates = await bot.get_updates()
    for update in updates:
        print(update.message)

if __name__ == "__main__":
    asyncio.run(main())