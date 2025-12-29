import MetaTrader5 as mt5
import strategy

def run_martingale_cycle(user_data):
    if not mt5.initialize(login=int(user_data['mt5_id']), password=user_data['mt5_pass'], server=user_data['mt5_server']):
        return "Conn Error"

    symbol = user_data['active_asset']
    if len(mt5.positions_get(symbol=symbol)) > 0:
        return "Position already open"

    # 3x Martingale scaling based on history
    history = mt5.history_deals_get(group=f"*{symbol}*")
    current_lot = user_data['base_lot']
    if history and history[-1].profit < 0:
        current_lot = round(user_data['base_lot'] * 3, 2)
    
    bias = strategy.get_smart_bias(symbol)
    if bias == "WAIT": return "Searching for Bias..."

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
    return f"🚀 Trade Placed: {current_lot} lot on {symbol}"
