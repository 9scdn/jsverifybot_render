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

# 从环境变量获取敏感配置
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PORT = int(os.environ.get("PORT", 10000))
CHANNEL_ID = int(os.environ["CHANNEL_ID"])  # 频道 ID

config = load_config()

# /start 命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 欢迎使用 九色™️ 视频官方防伪验证机器人！\n\n"
        "您可以使用以下功能快速开始：\n\n"
        "🔹 /list - 查看所有认证账号\n"
        "🔹 /report @账号 - 举报疑似假冒账号\n\n"
        "或者直接发送 @账号 查询是否为官方认证。"
    )

# /list 命令
async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 当前公开的官方账号如下：\n" + "\n".join(f"✅ {a}" for a in config["public_accounts"])
    await update.message.reply_text(text)

# /report 命令
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        account = context.args[0]
        await update.message.reply_text(f"✅ 已记录举报：{account}")
        msg = (
            f"🚨 用户 @{update.effective_user.username or update.effective_user.id} 举报了账号：{account}"
        )
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    else:
        await update.message.reply_text("⚠️ 用法：/report @账号")

# 文本消息处理
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    if not q.startswith("@"):
        await update.message.reply_text("⚠️ 请输入 @ 开头的账号，例如 @JiuSeBot")
        return

    if is_official_account(q):
        await update.message.reply_text(f"✅ {q} 是我们认证的官方账号。")
    else:
        await update.message.reply_text(f"❌ {q} 并非官方账号，请谨慎！")

# webhook 处理函数
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response()

# 主入口
async def main():
    global app
    app = Application.builder().token(BOT_TOKEN).build()

    # 注册命令和文本处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 设置机器人菜单命令
    await app.bot.set_my_commands([
        BotCommand("start", "开始验证"),
        BotCommand("list", "查看官方账号"),
        BotCommand("report", "举报假冒账号"),
    ])

    # 初始化并启动 bot
    await app.initialize()
    await app.bot.delete_webhook()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()

    # aiohttp webhook 接收服务
    web_app = web.Application()
    web_app.router.add_post("/", handle_webhook)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"✅ 验证机器人已通过 Webhook 启动在 {WEBHOOK_URL}")

    # 持续运行
    await app.updater.start_polling()
    await app.updater.wait()

if __name__ == "__main__":
    asyncio.run(main())
