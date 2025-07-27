import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from utils import load_config, is_official_account
from aiohttp import web

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # eg. https://jiusebot.onrender.com
PORT = int(os.environ.get("PORT", 8080))  # Render 会传递 PORT 环境变量

config = load_config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 欢迎使用 九色™️ 视频官方防伪验证机器人！\n\n"
        "输入对方的 @账号，我们会验证是否为官方账号。"
    )

async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 当前公开的官方账号如下：\n" + "\n".join(f"✅ {a}" for a in config["public_accounts"])
    await update.message.reply_text(text)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(f"✅ 已记录举报：{context.args[0]}")
    else:
        await update.message.reply_text("⚠️ 用法：/report @账号")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    if not q.startswith("@"):
        await update.message.reply_text("⚠️ 请输入 @ 开头的账号，例如 @JiuSeBot")
        return

    if is_official_account(q):
        await update.message.reply_text(f"✅ {q} 是我们认证的官方账号。")
    else:
        await update.message.reply_text(f"❌ {q} 并非官方账号，请谨慎！")

async def main():
    print("✅ 启动验证机器人（Webhook 模式）...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 取消旧 webhook，设置新 webhook
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(url=WEBHOOK_URL)

    # 创建 aiohttp 应用以处理 Webhook 请求
    web_app = web.Application()
    web_app.add_routes([web.post("/", app.webhook_handler())])

    # aiohttp 监听 Render 提供的端口
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"✅ Webhook 设置完成，监听端口 {PORT}")
    # 保持程序运行
    await app.updater.start_polling()  # 如果你需要 fallback 保留，可以启用，否则用 `await asyncio.Event().wait()` 持续挂起

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
