from mt5linux import MetaTrader5
mt5 = MetaTrader5()

def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period  # Simple MA as starting point
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_smart_bias(symbol):
    # Connect if not connected
    if not mt5.initialize(): return "WAIT"

    # Get 50 candles (Enough for EMA 21)
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
    if rates is None or len(rates) < 30: return "WAIT"
    
    # Extract closing prices (Simple Python List)
    close_prices = [x[4] for x in rates]

    # Calculate Indicators Manually
    ema_fast = calculate_ema(close_prices, 9)
    ema_slow = calculate_ema(close_prices, 21)
    rsi = calculate_rsi(close_prices, 14)

    if ema_fast is None or ema_slow is None: return "WAIT"

    # Strategy Logic (Same as before)
    if ema_fast > ema_slow and rsi > 50:
        return mt5.ORDER_TYPE_BUY
    elif ema_fast < ema_slow and rsi < 50:
        return mt5.ORDER_TYPE_SELL
    
    return "WAIT"
