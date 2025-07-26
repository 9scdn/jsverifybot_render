import os
import asyncio
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
bot = Bot(token=BOT_TOKEN)

async def reset():
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook 已清除，旧轮询会话已终止。")

if __name__ == "__main__":
    asyncio.run(reset())
