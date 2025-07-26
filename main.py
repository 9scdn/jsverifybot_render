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

BOT_TOKEN = os.environ["BOT_TOKEN"]
config = load_config()

# 命令处理器
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

# ⛔ 注意：不要在 main() 外使用 asyncio.run()
print("✅ 启动验证机器人...")

app = Application.builder().token(BOT_TOKEN).build()

# 可选：清除 webhook
async def clear_webhook():
    await app.bot.delete_webhook(drop_pending_updates=True)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_accounts))
app.add_handler(CommandHandler("report", report))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# run_polling 是阻塞调用，会自己处理事件循环
if __name__ == "__main__":
    app.run_polling(
        on_startup=[clear_webhook],  # 注意这里用的是 list of coroutine
    )
