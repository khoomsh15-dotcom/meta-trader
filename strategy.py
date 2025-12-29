from mt5linux import MetaTrader5
mt5 = MetaTrader5()

def get_smart_bias(symbol):
    # Ensure connection
    if not mt5.initialize(): return "WAIT"

    # Get 50 candles (Lightweight)
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
    if rates is None or len(rates) < 30: return "WAIT"
    
    # Simple Python List (No Pandas)
    close_prices = [x[4] for x in rates]

    # Calculate EMA 9 manually
    k9 = 2 / (9 + 1)
    ema9 = close_prices[0]
    for p in close_prices: ema9 = (p - ema9) * k9 + ema9

    # Calculate EMA 21 manually
    k21 = 2 / (21 + 1)
    ema21 = close_prices[0]
    for p in close_prices: ema21 = (p - ema21) * k21 + ema21

    # Signal Logic
    if ema9 > ema21:
        return mt5.ORDER_TYPE_BUY
    elif ema9 < ema21:
        return mt5.ORDER_TYPE_SELL
    
    return "WAIT"
