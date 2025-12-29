import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mt5linux import MetaTrader5
import strategy

# ==========================================
# 👇 CONFIGURATION 👇
# ==========================================
BOT_TOKEN = "8550302715:AAFBuYXFZ9vlWJFqauyDvW954dyf-ZoOLSc"
ADMIN_ID = 8509660813  # Your ID for startup message

MT5_ID = 5044173857
MT5_PASS = "BkAnX_E3"
MT5_SERVER = "MetaQuotes-Demo"
SYMBOL = "XAUUSD"

# Trading Settings
TP_PIPS = 8
SL_PIPS = 12
TRADING_ACTIVE = False  # Controlled by /trade and /stop
# ==========================================

mt5 = MetaTrader5()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- STARTUP MESSAGE ---
async def post_init(application: Application):
    """Sends message to Admin ID when bot starts"""
    await application.bot.send_message(chat_id=ADMIN_ID, text="✅ **SYSTEM ONLINE**\nReady for High-Frequency Trading.")

# --- HELP COMMAND ---
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🤖 **COMMAND LIST**\n\n"
        "/trade - Start 1-sec auto trading\n"
        "/stop - Stop opening new trades\n"
        "/status - Show open trades count\n"
        "/bal - Show Account Balance\n"
        "/panic - CLOSE ALL TRADES IMMEDIATELY\n"
        "/help - Show this menu"
    )
    await update.message.reply_text(msg)

# --- COMMAND: /trade (Start Loop) ---
async def trade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    if TRADING_ACTIVE:
        await update.message.reply_text("⚠️ Trading is already ACTIVE!")
        return
    
    TRADING_ACTIVE = True
    await update.message.reply_text("🚀 **High-Frequency Trading STARTED**\nScanning every 1 second...")
    
    # Start the aggressive loop
    asyncio.create_task(run_trading_loop(context))

# --- COMMAND: /stop (Stop Loop) ---
async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    TRADING_ACTIVE = False
    await update.message.reply_text("🛑 **Trading STOPPED**\nNew trades will not be opened.\nExisting trades will hit TP/SL.")

# --- COMMAND: /status ---
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER):
        await update.message.reply_text("❌ MT5 Disconnected")
        return
    
    count = mt5.positions_total()
    await update.message.reply_text(f"📊 **Live Status**\nActive Trades: {count}")

# --- COMMAND: /bal ---
async def bal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER):
        return
    
    info = mt5.account_info()
    await update.message.reply_text(f"💰 **Balance**: ${info.balance}\n📈 **Equity**: ${info.equity}")

# --- COMMAND: /panic (Close All) ---
async def panic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    TRADING_ACTIVE = False # Stop new trades first
    
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER):
        return

    positions = mt5.positions_get(symbol=SYMBOL)
    if positions is None or len(positions) == 0:
        await update.message.reply_text("✅ No trades to close.")
        return

    await update.message.reply_text(f"🚨 **PANIC ACTIVATED**\nClosing {len(positions)} trades...")
    
    for pos in positions:
        # Close logic
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
    
    await update.message.reply_text("💀 All trades liquidated.")

# --- THE AGGRESSIVE TRADING LOOP ---
async def run_trading_loop(context: ContextTypes.DEFAULT_TYPE):
    global TRADING_ACTIVE
    
    # Ensure connection
    if not mt5.initialize(login=int(MT5_ID), password=MT5_PASS, server=MT5_SERVER):
        print("MT5 Init Failed")
        return

    while TRADING_ACTIVE:
        try:
            # 1. Analyze Bias
            signal = strategy.get_smart_bias(SYMBOL)
            
            # 2. Get Point Value for TP/SL Calculation
            # For XAUUSD, usually 1 pip = 10 points or 0.10 price difference
            point = mt5.symbol_info(SYMBOL).point
            tick = mt5.symbol_info_tick(SYMBOL)
            
            # Calculate TP/SL Distance (Approx 8 pips = 80 points)
            tp_dist = TP_PIPS * 10 * point
            sl_dist = SL_PIPS * 10 * point

            if signal == mt5.ORDER_TYPE_BUY:
                sl = tick.ask - sl_dist
                tp = tick.ask + tp_dist
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": SYMBOL,
                    "volume": 0.01,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": tick.ask,
                    "sl": sl,
                    "tp": tp,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                res = mt5.order_send(request)
                if res.retcode == mt5.TRADE_RETCODE_DONE:
                    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🟢 **BUY EXEC**\nPrice: {tick.ask}\nTP: {tp}\nSL: {sl}")

            elif signal == mt5.ORDER_TYPE_SELL:
                sl = tick.bid + sl_dist
                tp = tick.bid - tp_dist
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": SYMBOL,
                    "volume": 0.01,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": tick.bid,
                    "sl": sl,
                    "tp": tp,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                res = mt5.order_send(request)
                if res.retcode == mt5.TRADE_RETCODE_DONE:
                    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔴 **SELL EXEC**\nPrice: {tick.bid}\nTP: {tp}\nSL: {sl}")
            
            # Wait 1 second before next scan
            await asyncio.sleep(1)

        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(1)

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", help_cmd)) # Default to help on start
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("trade", trade_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("bal", bal_cmd))
    app.add_handler(CommandHandler("panic", panic_cmd))
    
    app.run_polling()

if __name__ == '__main__':
    main()
