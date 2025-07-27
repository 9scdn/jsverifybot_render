
import os
import asyncio
from aiohttp import web
from telegram import Update, BotCommand, ReplyKeyboardMarkup
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
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

config = load_config()

# 命令处理函数
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/list", "/report @示例账号"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🎉 欢迎使用 九色™️ 官方防伪验证机器人！

"
        "请输入要验证的 @账号，我们会告诉你是否为官方认证账号。

"
        "📋 /list 查看所有官方账号
"
        "🚨 /report @账号 举报假冒账号
",
        reply_markup=reply_markup,
    )

async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    public = config["public_accounts"]
    text = "📋 当前公开的官方账号如下：
"
    for acc in public:
        label = "九色官方机器人" if acc == "@jiusebot" else                 "九色官方频道" if acc == "@jiuse9191" else                 "九色官方群组" if acc == "@jiuseX" else "✅ 官方账号"
        text += f"{label} {acc}
"
    await update.message.reply_text(text)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        target = context.args[0].strip()
        if not target.startswith("@"):
            await update.message.reply_text("⚠️ 请输入正确的账号，例如 /report @示例账号")
            return

        if is_official_account(target):
            await update.message.reply_text(f"⚠️ 无需举报：{target} 是我们认证的官方账号。")
            return

        await update.message.reply_text(f"✅ 已记录举报：{target}")
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"📣 收到新举报：{target}
👤 举报人：@{update.effective_user.username or update.effective_user.id}"
        )
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

async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response()

async def main():
    global app
    app = Application.builder().token(BOT_TOKEN).build()

    # 注册命令菜单
    await app.bot.set_my_commands([
        BotCommand("start", "开始验证"),
        BotCommand("list", "查看官方账号列表"),
        BotCommand("report", "举报假冒账号"),
    ])

    # 注册处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 设置 Webhook
    await app.bot.delete_webhook()
    await app.bot.set_webhook(url=WEBHOOK_URL)

    # 启动 AIOHTTP 服务
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
