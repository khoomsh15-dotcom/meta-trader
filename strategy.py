import pandas as pd
import pandas_ta as ta
from mt5linux import MetaTrader5
mt5 = MetaTrader5()

def get_smart_bias(symbol):
    if not mt5.initialize(): return "WAIT"

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
    if rates is None: return "WAIT"
    
    df = pd.DataFrame(rates)
    df['ema_fast'] = ta.ema(df['close'], length=9)
    df['ema_slow'] = ta.ema(df['close'], length=21)
    df['rsi'] = ta.rsi(df['close'], length=14)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Logic: EMA Crossover + RSI
    if prev['ema_fast'] <= prev['ema_slow'] and last['ema_fast'] > last['ema_slow'] and last['rsi'] > 50:
        return mt5.ORDER_TYPE_BUY
    elif prev['ema_fast'] >= prev['ema_slow'] and last['ema_fast'] < last['ema_slow'] and last['rsi'] < 50:
        return mt5.ORDER_TYPE_SELL
    
    return "WAIT"
