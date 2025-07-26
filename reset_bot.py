import os
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
bot = Bot(token=BOT_TOKEN)

bot.delete_webhook(drop_pending_updates=True)
print("✅ Webhook 已清除，旧轮询会话已终止。")
