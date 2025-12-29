from mt5linux import MetaTrader5
import strategy

# Linux Bridge connect kar raha hai
mt5 = MetaTrader5()

def run_martingale_cycle(user_data):
    # Connection logic
    if not mt5.initialize(login=int(user_data['mt5_id']), password=user_data['mt5_pass'], server=user_data['mt5_server']):
        return "Conn Error"

    symbol = user_data['active_asset']
    
    # Check agar pehle se trade open hai
    if len(mt5.positions_get(symbol=symbol) or []) > 0:
        return "Position Busy"

    # Martingale Logic (Loss hua to 3x lot)
    history = mt5.history_deals_get(group=f"*{symbol}*")
    current_lot = user_data['base_lot']
    if history and history[-1].profit < 0:
        current_lot = round(user_data['base_lot'] * 3, 2)
    
    bias = strategy.get_smart_bias(symbol)
    if bias == "WAIT": return "Scanning..."

    # Trade Execution
    price = mt5.symbol_info_tick(symbol).ask if bias == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": current_lot,
        "type": bias,
        "price": price,
        "magic": 999,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    return f"🚀 {symbol} Trade: {current_lot} lots"
