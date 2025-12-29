import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import database as db
import engine
import MetaTrader5 as mt5

# State constants
ID, PASS, SERVER, ASSET, LOT, STREAK = range(6)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.get_user(update.effective_user.id)
    if not user or not mt5.initialize(login=int(user['mt5_id']), password=user['mt5_pass'], server=user['mt5_server']):
        return await update.message.reply_text("❌ Setup your account first.")
    
    acc = mt5.account_info()
    await update.message.reply_text(f"💰 Balance: ${acc.balance}\n📈 Equity: ${acc.equity}\n📊 Active Asset: {user.get('active_asset', 'None')}")

async def newsetup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.users_col.delete_one({"user_id": update.effective_user.id})
    await update.message.reply_text("🗑 Data cleared. Use /setup to add a new account.")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    # Add your command handlers here (setup, scalp, panic, status, newsetup)
    app.run_polling()

if __name__ == "__main__":
    main()
