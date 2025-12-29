import logging
import asyncio
import os
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mt5linux import MetaTrader5
import strategy

# ==========================================
# 👇 CREDENTIALS & CONFIG 👇
# ==========================================
BOT_TOKEN = "8550302715:AAFBuYXFZ9vlWJFqauyDvW954dyf-ZoOLSc"
ADMIN_ID = 8509660813
MT5_ID = 5044173857
MT5_PASS = "BkAnX_E3"
MT5_SERVER = "MetaQuotes-Demo"
SYMBOL = "XAUUSD"

# Trading Settings
TP_PIPS = 8
SL_PIPS = 12
TRADING_ACTIVE = False
# ==========================================

mt5 = MetaTrader5()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- DUMMY WEB SERVER (FOR UPTIMEROBOT) ---
async def health_check(request):
    return web.Response(text="META BOT IS LIVE AND SPYING")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌍 Web Server running on Port 8080")

# --- STARTUP MESSAGE ---
async def post_init(application: Application):
    await application.bot.send_message(chat_id=ADMIN_ID, text="😈 **META BOT IS LIVE AND SPYING**\nTarget: XAUUSD\nStatus: Hunting...")

# --- COMMANDS ---
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "💀 **META BOT COMMANDS**\n"
        "/trade - Start Auto-Trading (1s Scan)\n"
        "/stop - Stop Trading\n"
        "/status - Show Active Trades\n"
        "/bal - Show Balance\n"
        "/panic - CLOSE ALL TRADES NOW\n"
        "/help - Show Menu"
    )
    await update.message.reply_text(msg)

async def trade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    if TRADING_ACTIVE:
        await update.message.reply_text("⚠️ Already hunting!")
        return
    TRADING_ACTIVE = True
    await update.message.reply_text("🚀 **HFT STARTED**\nScanning market every 1 second...")
    asyncio.create_task(run_trading_loop(context))

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    TRADING_ACTIVE = False
    await update.message.reply_text("🛑 **HFT STOPPED**")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER):
        await update.message.reply_text("❌ MT5 Disconnected")
        return
    count = mt5.positions_total()
    await update.message.reply_text(f"📊 **Live Status**\nActive Trades: {count}")

async def bal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER): return
    info = mt5.account_info()
    await update.message.reply_text(f"💰 Balance: ${info.balance}\n📈 Equity: ${info.equity}")

async def panic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    TRADING_ACTIVE = False
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER): return
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        await update.message.reply_text("✅ No trades to close.")
        return
    await update.message.reply_text(f"🚨 **PANIC: Closing {len(positions)} trades!**")
    for pos in positions:
        type_close = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(SYMBOL).bid if type_close == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(SYMBOL).ask
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": pos.volume,
            "type": type_close,
            "position": pos.ticket,
            "price": price,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(req)
    await update.message.reply_text("💀 **LIQUIDATION COMPLETE**")

# --- TRADING LOOP ---
async def run_trading_loop(context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER): return
    while TRADING_ACTIVE:
        try:
            signal = strategy.get_smart_bias(SYMBOL)
            point = mt5.symbol_info(SYMBOL).point
            tick = mt5.symbol_info_tick(SYMBOL)
            tp_dist = TP_PIPS * 10 * point
            sl_dist = SL_PIPS * 10 * point

            if signal == mt5.ORDER_TYPE_BUY:
                req = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": SYMBOL,
                    "volume": 0.01,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": tick.ask,
                    "sl": tick.ask - sl_dist,
                    "tp": tick.ask + tp_dist,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                res = mt5.order_send(req)
                if res.retcode == mt5.TRADE_RETCODE_DONE:
                    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🟢 **BUY** @ {tick.ask}")

            elif signal == mt5.ORDER_TYPE_SELL:
                req = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": SYMBOL,
                    "volume": 0.01,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": tick.bid,
                    "sl": tick.bid + sl_dist,
                    "tp": tick.bid - tp_dist,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                res = mt5.order_send(req)
                if res.retcode == mt5.TRADE_RETCODE_DONE:
                    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔴 **SELL** @ {tick.bid}")
            
            await asyncio.sleep(1)
        except Exception:
            await asyncio.sleep(1)

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_web_server()) # Start Web Server
    
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", help_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("trade", trade_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("bal", bal_cmd))
    app.add_handler(CommandHandler("panic", panic_cmd))
    
    app.run_polling()

if __name__ == '__main__':
    main()
