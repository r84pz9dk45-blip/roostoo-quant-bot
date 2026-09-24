# 25/75 RSI Reversal Strategy 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load Binance Vision OHLCV Data
df = pd.read_csv('data/BTCUSDT-1h-2026-08.csv', header=None)
df = df.iloc[:, :6]
df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
df['close'] = df['close'].astype(float)

# 2. Calculate 14-period RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# 3. Generate Signals with Stricter Thresholds (25 Buy / 75 Sell)
df['signal'] = 0
df.loc[df['rsi'] < 25, 'signal'] = 1
df.loc[df['rsi'] > 75, 'signal'] = 0
df['position'] = df['signal'].ffill().fillna(0)

# 4. Strategy Returns & 0.1% Taker Fee Adjustment
df['market_return'] = df['close'].pct_change()
df['strategy_return'] = df['position'].shift(1) * df['market_return']

trades = df['position'].diff().fillna(0) != 0
df.loc[trades, 'strategy_return'] -= 0.001

# 5. Performance Metrics
df['cum_return'] = (1 + df['strategy_return']).cumprod()
sharpe_ratio = (df['strategy_return'].mean() / df['strategy_return'].std()) * np.sqrt(24 * 365)

print("\n==================================================================")
print("  Signal 6 Variant A: Stricter Threshold RSI Reversal (25/75)     ")
print("==================================================================")
print(f"Cumulative Return: {(df['cum_return'].iloc[-1] - 1) * 100:.2f}%")
print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Total Trades Triggered: {trades.sum()}")
print("==================================================================\n")

# 6. Plot Equity Curve
plt.figure(figsize=(10, 5))
plt.plot(df['cum_return'], label='RSI (25/75) Strategy PnL', color='tab:blue')
plt.title("Signal 6 Variant A: Stricter Threshold RSI Reversal (25/75)")
plt.xlabel("Hours")
plt.ylabel("Cumulative Growth")
plt.grid(True)
plt.legend()
plt.show()