import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mt5linux import MetaTrader5
import strategy

# Load Token from Render Environment
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==========================================
# 👇 YOUR HARDCODED CREDENTIALS 👇
# ==========================================
MT5_ID = 5044173857           
MT5_PASS = "BkAnX_E3"     
MT5_SERVER = "MetaQuotes-Demo"     
# ==========================================

mt5 = MetaTrader5()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Bot Connected to {MT5_SERVER}!")

async def trade_loop(context: ContextTypes.DEFAULT_TYPE):
    symbol = "XAUUSD" # Gold
    
    # 1. Connect using Hardcoded Details
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER):
        print(f"❌ Connection Failed: {mt5.last_error()}")
        return

    # 2. Get Signal from Lite Strategy
    signal = strategy.get_smart_bias(symbol)
    print(f"🔍 {symbol}: {signal}")

    # 3. Execute Trade
    if signal in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL]:
        price = mt5.symbol_info_tick(symbol).ask if signal == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 0.01,
            "type": signal,
            "price": price,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        print(f"🚀 Trade Executed: {result}")

def main():
    if not BOT_TOKEN:
        print("CRITICAL: BOT_TOKEN not found in env!")
        return
        
    print("🤖 Starting Bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.job_queue.run_repeating(trade_loop, interval=60, first=10)
    app.run_polling()

if __name__ == '__main__':
    main()
