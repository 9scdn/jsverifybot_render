import os
import asyncio
from aiohttp import web
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from utils import load_config, is_official_account

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PORT = int(os.environ.get("PORT", 10000))
CHANNEL_ID = int(os.environ["CHANNEL_ID"])  # 从环境变量读取频道 ID

config = load_config()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎉 欢迎使用 九色™️ 视频官方防伪验证机器人！\n\n"
        "📌 请输入对方的 @账号，我们会验证是否为官方账号。\n\n"
        "🧩 常用指令：\n"
        "👉 /list 查看官方账号列表\n"
        "👉 /report @账号 举报假冒账号"
    )
    await update.message.reply_text(text)


async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 当前公开的官方账号如下：\n" + "\n".join(f"✅ {a}" for a in config["public_accounts"])
    await update.message.reply_text(text)


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ 用法：/report @账号")
        return

    target = context.args[0]
    user = update.effective_user

    await update.message.reply_text(f"✅ 已记录举报：{target}")

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"📣 用户 @{user.username or user.id} 举报账号：{target}"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    if not q.startswith("@"):
        await update.message.reply_text("⚠️ 请输入 @ 开头的账号，例如 @JiuSeBot")
        return

    if is_official_account(q):
        await update.message.reply_text(f"✅ {q} 是我们认证的官方账号。")
    else:
        await update.message.reply_text(f"❌ {q} 并非官方账号，请谨慎！")


async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response()


async def main():
    global app
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await app.bot.set_my_commands([
        BotCommand("start", "开始验证"),
        BotCommand("list", "查看官方账号"),
        BotCommand("report", "举报假冒账号"),
    ])

    await app.bot.delete_webhook()
    await app.bot.set_webhook(url=WEBHOOK_URL)

    web_app = web.Application()
    web_app.router.add_post("/", handle_webhook)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"✅ 验证机器人已通过 Webhook 启动在 {WEBHOOK_URL}")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
