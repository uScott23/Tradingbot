import MetaTrader5 as mt5
import pandas as pd
import numpy as np

# Set up MT5 connection
if not mt5.initialize():
    print("MT5 connection failed")
    exit()

# Define the symbol (XAUUSD) and timeframe (1 minute)
symbol = 'XAUUSD'
timeframe = mt5.TIMEFRAME_M1

# Get the latest 1000 bars
bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)

# Check if bars is not empty
if not bars:
    print("No data received")
    mt5.shutdown()
    exit()

# Convert the bars to a Pandas DataFrame
df = pd.DataFrame(bars)

# Define a simple moving average strategy
def strategy(df):
    df_strategy = df.copy()
    df_strategy['SMA_50'] = df_strategy['close'].rolling(window=50).mean()
    df_strategy['SMA_200'] = df_strategy['close'].rolling(window=200).mean()
    
    df_strategy['signal'] = (df_strategy['SMA_50'] > df_strategy['SMA_200']).astype(int)
    
    return df_strategy

# Apply the strategy to the DataFrame
df_strategy = strategy(df)

# Open a buy position when the signal is 1
if df_strategy['signal'].iloc[-1] == 1:
    request = {
        "action": mt5.TRADE_REQUEST_ACTIONS_DEAL,
        "symbol": symbol,
        "volume": 0.1,
        "type": mt5.TRADE_REQUEST_TYPE_BUY,
        "price": df_strategy['close'].iloc[-1],
        "deviation": 0,
        "magic": 234000,
        "comment": "Python script open",
        "type_time": mt5.TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Order send failed: {}".format(result.comment))

# Shut down the MT5 connection
mt5.shutdown()