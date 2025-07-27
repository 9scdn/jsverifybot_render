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
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
PORT = int(os.environ.get("PORT", 10000))

config = load_config()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/list", "/report @假冒账号"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🎉 欢迎使用 九色™️ 视频官方防伪验证机器人！\n\n"
        "您可以通过以下命令快速验证账号：\n\n"
        "✅ /list 查看官方账号\n"
        "🚨 /report @假冒账号 进行举报",
        reply_markup=reply_markup
    )


async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 当前公开的官方账号如下：\n\n" +
        "✅ 九色官方群组 @jiuseX\n"
        "✅ 九色官方频道 @jiuse9191\n"
        "✅ 九色官方机器人 @jiusebot"
    )
    await update.message.reply_text(text)


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        target = context.args[0].strip()
        if not target.startswith("@"):
            await update.message.reply_text("⚠️ 请输入正确的账号，例如 /report @示例账号")
            return

        # 拦截举报官方账号
        if is_official_account(target):
            await update.message.reply_text(f"⚠️ 无需举报：{target} 是我们认证的官方账号。")
            return

        # 发送举报信息到频道
        await update.message.reply_text(f"✅ 已记录举报：{target}")
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=(
                f"🚨 收到新举报\n"
                f"👤 举报人：@{update.effective_user.username or update.effective_user.id}\n"
                f"🎯 举报对象：{target}"
            )
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

    # 设置 Bot 命令菜单
    await app.bot.set_my_commands([
        BotCommand("start", "开始使用"),
        BotCommand("list", "查看官方账号"),
        BotCommand("report", "举报假冒账号"),
    ])

    # 注册指令和消息处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 设置 Webhook
    await app.bot.delete_webhook()
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)

    # 启动 aiohttp Web 服务
    web_app = web.Application()
    web_app.router.add_post("/", handle_webhook)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print(f"✅ 验证机器人已通过 Webhook 启动在 {WEBHOOK_URL}")

    await app.start()
    await app.updater.start_polling()  # 保证处理状态
    await app.updater.wait()


if __name__ == "__main__":
    asyncio.run(main())
