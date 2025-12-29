import os
import MetaTrader5 as mt5
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import database as db
import engine

# States
ID, PASS, SERVER, ASSET, LOT, STREAK = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😈 **Trading Bot OS Live**\n/setup - Link MT5\n/scalp - Start Engine\n/status - Check Trade\n/newsetup - Reset Account")

async def setup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠 Setup Mode: Enter your MT5 Login ID:")
    return ID

async def save_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['id'] = update.message.text
    await update.message.reply_text("Enter MT5 Password:")
    return PASS

async def save_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['pass'] = update.message.text
    await update.message.reply_text("Enter MT5 Server Name:")
    return SERVER

async def save_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.save_creds(user_id, context.user_data['id'], context.user_data['pass'], update.message.text)
    await update.message.reply_text("✅ Credentials Saved! Now use /scalp to configure your trade.")
    return ConversationHandler.END

async def scalp_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💹 Enter Asset Name (e.g., XAUUSD):")
    return ASSET

async def set_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['asset'] = update.message.text.upper()
    await update.message.reply_text(f"Targeting {context.user_data['asset']}. Enter Starting Lot:")
    return LOT

async def set_lot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.update_trade_settings(user_id, context.user_data['asset'], float(update.message.text), 0)
    
    # Run the Engine immediately for this user
    user_data = db.get_user(user_id)
    result = engine.run_martingale_cycle(user_data)
    await update.message.reply_text(f"🔥 Engine Active: {result}")
    return ConversationHandler.END

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(token).build()

    # Conversation Handlers
    setup_conv = ConversationHandler(
        entry_points=[CommandHandler("setup", setup_start)],
        states={
            ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_id)],
            PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_pass)],
            SERVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_server)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )

    scalp_conv = ConversationHandler(
        entry_points=[CommandHandler("scalp", scalp_start)],
        states={
            ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_asset)],
            LOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_lot)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(setup_conv)
    app.add_handler(scalp_conv)
    app.run_polling()

if __name__ == "__main__":
    main()
