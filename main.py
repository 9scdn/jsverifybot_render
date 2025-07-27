import os
import json
import logging
import asyncio
from aiohttp import web
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from utils import is_official_account

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8080))
channel_id_str = os.getenv("CHANNEL_ID")
if not channel_id_str:
    raise RuntimeError("环境变量 CHANNEL_ID 未设置")
CHANNEL_ID = int(channel_id_str)

# 初始化 Application（稍后 initialize）
app = None


# /start 命令处理
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎉 欢迎使用 九色™官方防伪验证机器人！\n\n"
        "你可以通过以下方式快速操作：\n"
        "🔍 发送任何 @用户名 来验证其是否为官方账号\n"
        "🚨 使用 /report 命令举报假冒账号\n"
        "📋 使用 /list 查看官方账号列表\n\n"
        "📢 快捷菜单：\n"
        "✅ [验证机器人](https://t.me/JiuSeBot)\n"
        "📣 [九色官方频道](https://t.me/jiuse9191)\n"
        "💬 [九色官方群组](https://t.me/jiuseX)\n"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


# /report 命令处理
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("请使用格式：/report @username")
        return

    username = context.args[0].strip()
    if not username.startswith("@"):
        await update.message.reply_text("用户名必须以 @ 开头")
        return

    if is_official_account(username):
        await update.message.reply_text("⚠️ 该账号为官方账号，不能举报。")
        return

    reporter = update.effective_user.mention_html()
    message = (
        f"🚨 <b>收到新举报</b>\n\n"
        f"举报人: {reporter}\n"
        f"被举报账号: <code>{username}</code>\n"
        f"消息链接: <a href='https://t.me/{update.effective_user.username}'>用户主页</a>"
    )

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    await update.message.reply_text("✅ 举报已提交，感谢你的反馈！")


# /list 命令处理
async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 当前公开的官方账号如下：\n\n"
        "✅ 九色官方群组：@jiuseX\n"
        "✅ 九色官方频道：@jiuse9191\n"
        "✅ 九色官方机器人：@jiusebot"
    )
    await update.message.reply_text(text)


# 普通消息处理
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    if text.startswith("@"):
        username = text.split()[0]
        if is_official_account(username):
            await update.message.reply_text(f"✅ 账号 {username} 是官方认证账号。")
        else:
            await update.message.reply_text(f"⚠️ 账号 {username} 不是官方认证账号，请注意辨别。")


# 错误处理器
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("发生错误：%s", context.error)


# Webhook 请求处理
async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        logger.exception("Webhook 错误")
        return web.Response(status=500)


# 主程序
async def main():
    global app
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    await app.bot.set_my_commands([
        BotCommand("start", "开始验证"),
        BotCommand("report", "举报假冒账号"),
        BotCommand("list", "查看官方账号列表")
    ])

    await app.initialize()
    await app.start()
    await app.bot.set_webhook(WEBHOOK_URL)

    web_app = web.Application()
    web_app.router.add_post("/", handle_webhook)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"✅ 验证机器人已通过 Webhook 启动在 {WEBHOOK_URL}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
