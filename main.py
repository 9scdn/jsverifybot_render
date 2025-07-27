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

# 加载配置
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # 如：https://your-app-name.onrender.com
PORT = int(os.environ.get("PORT", "10000"))  # Render 默认 PORT=10000

config = load_config()

# 处理 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 欢迎使用 九色™️ 视频官方防伪验证机器人！\n\n"
        "输入对方的 @账号，我们会验证是否为官方账号。"
    )

# 处理 /list
async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 当前公开的官方账号如下：\n" + "\n".join(f"✅ {a}" for a in config["public_accounts"])
    await update.message.reply_text(text)

# 处理 /report
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(f"✅ 已记录举报：{context.args[0]}")
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

# aiohttp 的 webhook 接收处理
async def webhook_handler(request: web.Request):
    data = await request.json()
    await application.update_queue.put(Update.de_json(data, application.bot))
    return web.Response(text="ok")

# 创建 Telegram 应用
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("list", list_accounts))
application.add_handler(CommandHandler("report", report))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# aiohttp 应用绑定
app = web.Application()
app.router.add_post("/webhook", webhook_handler)

async def on_startup(app: web.Application):
    # 设置 webhook
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    print("✅ 已设置 webhook:", f"{WEBHOOK_URL}/webhook")

if __name__ == "__main__":
    app.on_startup.append(on_startup)
    print("✅ 启动验证机器人（Webhook 模式）")
    web.run_app(app, host="0.0.0.0", port=PORT)
