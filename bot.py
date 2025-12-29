import logging
import asyncio
import os
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mt5linux import MetaTrader5
import strategy

# ==========================================
# 👇 CREDENTIALS 👇
# ==========================================
BOT_TOKEN = "8550302715:AAFBuYXFZ9vlWJFqauyDvW954dyf-ZoOLSc"
ADMIN_ID = 8509660813
MT5_ID = 5044173857
MT5_PASS = "BkAnX_E3"
MT5_SERVER = "MetaQuotes-Demo"
SYMBOL = "XAUUSD"

TP_PIPS = 8
SL_PIPS = 12
TRADING_ACTIVE = False
# ==========================================

# ⚠️ GLOBAL VARIABLE: Starts as None (Disconnected)
mt5_connection = None 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- DUMMY WEB SERVER ---
async def health_check(request):
    return web.Response(text="META BOT IS ALIVE")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌍 Web Server running on Port 8080")

# --- SAFE CONNECTION FUNCTION ---
def ensure_mt5_connection():
    global mt5_connection
    try:
        if mt5_connection is None:
            # Try to connect
            temp_mt5 = MetaTrader5()
            if temp_mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER):
                mt5_connection = temp_mt5
                print("✅ MT5 Connected Successfully!")
                return True
        else:
            # Check if still connected
            if not mt5_connection.terminal_info():
                mt5_connection = None
                return False
            return True
    except Exception as e:
        print(f"⏳ Waiting for MT5 App to start... ({e})")
        return False

# --- COMMANDS ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😈 **META BOT IS LIVE**\nUse /trade to start hunting.")

async def trade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    TRADING_ACTIVE = True
    await update.message.reply_text("🚀 **HFT STARTED**\nScanning every 1 second...")
    asyncio.create_task(run_trading_loop(context))

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    TRADING_ACTIVE = False
    await update.message.reply_text("🛑 **HFT STOPPED**")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ensure_mt5_connection():
        count = mt5_connection.positions_total()
        await update.message.reply_text(f"📊 **Active Trades:** {count}")
    else:
        await update.message.reply_text("⏳ MT5 is still loading...")

async def panic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    TRADING_ACTIVE = False
    if not ensure_mt5_connection(): return
    
    positions = mt5_connection.positions_get(symbol=SYMBOL)
    if not positions:
        await update.message.reply_text("✅ No trades to close.")
        return
        
    await update.message.reply_text(f"🚨 **PANIC: Closing {len(positions)} trades!**")
    for pos in positions:
        type_close = mt5_connection.ORDER_TYPE_SELL if pos.type == mt5_connection.ORDER_TYPE_BUY else mt5_connection.ORDER_TYPE_BUY
        price = mt5_connection.symbol_info_tick(SYMBOL).bid if type_close == mt5_connection.ORDER_TYPE_SELL else mt5_connection.symbol_info_tick(SYMBOL).ask
        req = {
            "action": mt5_connection.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": pos.volume,
            "type": type_close,
            "position": pos.ticket,
            "price": price,
            "type_filling": mt5_connection.ORDER_FILLING_IOC,
        }
        mt5_connection.order_send(req)
    await update.message.reply_text("💀 **LIQUIDATED**")

# --- TRADING LOOP ---
async def run_trading_loop(context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    while TRADING_ACTIVE:
        # 1. Check Connection safely
        if not ensure_mt5_connection():
            await asyncio.sleep(5) # Wait 5s before retrying
            continue

        try:
            # 2. Use the SAFE 'mt5_connection' object
            signal = strategy.get_smart_bias(mt5_connection, SYMBOL)
            
            if signal != "WAIT":
                tick = mt5_connection.symbol_info_tick(SYMBOL)
                point = mt5_connection.symbol_info(SYMBOL).point
                tp_dist = TP_PIPS * 10 * point
                sl_dist = SL_PIPS * 10 * point
                
                if signal == mt5_connection.ORDER_TYPE_BUY:
                    sl = tick.ask - sl_dist
                    tp = tick.ask + tp_dist
                    req = {"action": mt5_connection.TRADE_ACTION_DEAL, "symbol": SYMBOL, "volume": 0.01, "type": mt5_connection.ORDER_TYPE_BUY, "price": tick.ask, "sl": sl, "tp": tp, "type_filling": mt5_connection.ORDER_FILLING_IOC}
                    res = mt5_connection.order_send(req)
                    if res.retcode == mt5_connection.TRADE_RETCODE_DONE:
                        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🟢 **BUY** @ {tick.ask}")

                elif signal == mt5_connection.ORDER_TYPE_SELL:
                    sl = tick.bid + sl_dist
                    tp = tick.bid - tp_dist
                    req = {"action": mt5_connection.TRADE_ACTION_DEAL, "symbol": SYMBOL, "volume": 0.01, "type": mt5_connection.ORDER_TYPE_SELL, "price": tick.bid, "sl": sl, "tp": tp, "type_filling": mt5_connection.ORDER_FILLING_IOC}
                    res = mt5_connection.order_send(req)
                    if res.retcode == mt5_connection.TRADE_RETCODE_DONE:
                        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔴 **SELL** @ {tick.bid}")

            await asyncio.sleep(1)
        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(1)

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_web_server())
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("trade", trade_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("panic", panic_cmd))
    
    print("🤖 Bot Started! Waiting for MT5...")
    app.run_polling()

if __name__ == '__main__':
    main()
