# No imports needed here. We use the 'mt5' object passed from bot.py

def get_smart_bias(mt5, symbol):
    # 1. Get 50 candles
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
    if rates is None or len(rates) < 30: 
        return "WAIT"
    
    # 2. Simple List extraction
    close_prices = [x[4] for x in rates]

    # 3. Calculate EMA 9 manually
    k9 = 2 / (9 + 1)
    ema9 = close_prices[0]
    for p in close_prices: 
        ema9 = (p - ema9) * k9 + ema9

    # 4. Calculate EMA 21 manually
    k21 = 2 / (21 + 1)
    ema21 = close_prices[0]
    for p in close_prices: 
        ema21 = (p - ema21) * k21 + ema21

    # 5. Signal Logic (Using constants from the mt5 object)
    if ema9 > ema21:
        return mt5.ORDER_TYPE_BUY
    elif ema9 < ema21:
        return mt5.ORDER_TYPE_SELL
    
    return "WAIT"
