import os
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from aiohttp import web
from utils import load_config, is_official_account

# 环境变量
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
PORT = int(os.environ.get("PORT", 10000))

# 加载配置
config = load_config()

# 日志
logging.basicConfig(level=logging.INFO)

# 命令处理器：start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 欢迎使用 九色™官方防伪验证机器人！\n\n"
        "请发送你要验证的 @账号，例如 @jiusebot。\n\n"
        "📋 快捷指令：\n"
        "👉 /list - 查看官方账号\n"
        "🚨 /report @账号 - 举报假冒账号"
    )

# 命令处理器：list
async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 当前公开的官方账号如下：\n\n"
        "✅ 九色官方群组 @jiuseX\n"
        "✅ 九色官方频道 @jiuse9191\n"
        "✅ 九色官方机器人 @jiusebot"
    )
    await update.message.reply_text(text)

# 命令处理器：report
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ 用法：/report @账号")
        return

    reported_account = context.args[0].strip()
    user = update.effective_user

    if not reported_account.startswith("@"):
        await update.message.reply_text("⚠️ 请输入以 @ 开头的账号，例如 /report @fakebot")
        return

    if is_official_account(reported_account):
        await update.message.reply_text("⚠️ 无需举报官方账号。")
        return

    msg = (
        f"🚨 举报通知：\n\n"
        f"举报人：@{user.username or user.first_name}\n"
        f"被举报账号：{reported_account}"
    )

    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    await update.message.reply_text(f"✅ 感谢举报，我们将尽快处理：{reported_account}")

# 文本处理器
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text.strip()
    if not q.startswith("@"):
        await update.message.reply_text("⚠️ 请输入 @ 开头的账号，例如 @JiuSeBot")
        return

    if is_official_account(q):
        await update.message.reply_text(f"✅ {q} 是我们认证的官方账号。")
    else:
        await update.message.reply_text(f"❌ {q} 并非官方账号，请谨慎！")

# webhook handler
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response()

# 主入口
async def main():
    global app
    app = Application.builder().token(BOT_TOKEN).build()

    # 设置菜单命令
    await app.bot.set_my_commands([
        BotCommand("start", "开始使用验证机器人"),
        BotCommand("list", "查看官方账号"),
        BotCommand("report", "举报假冒账号")
    ])

    # 添加 handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 设置 webhook
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(url=WEBHOOK_URL)

    # 启动 aiohttp web 服务
    web_app = web.Application()
    web_app.router.add_post("/", handle_webhook)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"✅ 验证机器人已通过 Webhook 启动在 {WEBHOOK_URL}")

    # 保持运行
    import asyncio
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
