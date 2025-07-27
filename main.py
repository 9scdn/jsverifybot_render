import os
import asyncio
import logging
from aiohttp import web
from telegram.ext import ApplicationBuilder
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # 例如 https://jsverifybot-apio.onrender.com
PORT = int(os.environ.get("PORT", 10000))

# 日志设置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 示例命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("你好，我是九色机器人。")

# aiohttp Webhook handler
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

# 初始化 Application 和 aiohttp Web Server
async def main():
    global app
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # 必须 initialize 再设置 webhook
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    logging.info(f"✅ 已设置 webhook: {WEBHOOK_URL}/webhook")

    # aiohttp server
    web_app = web.Application()
    web_app.add_routes([web.post("/webhook", handle_webhook)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"✅ 验证机器人已通过 Webhook 启动在 {WEBHOOK_URL}")

    # 保持运行
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
