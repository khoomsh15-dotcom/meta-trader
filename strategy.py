import pandas as pd
import pandas_ta as ta

def calculate_bias(df):
    """
    Returns: 'BUY', 'SELL', or 'WAIT'
    Logic: EMA 9 crosses EMA 21 + RSI filter
    """
    if len(df) < 30: return "WAIT"

    df['ema_fast'] = ta.ema(df['close'], length=9)
    df['ema_slow'] = ta.ema(df['close'], length=21)
    df['rsi'] = ta.rsi(df['close'], length=14)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Bullish Cross + RSI above 50
    if prev['ema_fast'] <= prev['ema_slow'] and last['ema_fast'] > last['ema_slow'] and last['rsi'] > 50:
        return "BUY"
    
    # Bearish Cross + RSI below 50
    if prev['ema_fast'] >= prev['ema_slow'] and last['ema_fast'] < last['ema_slow'] and last['rsi'] < 50:
        return "SELL"

    return "WAIT"
