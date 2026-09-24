# 25/75 RSI Reversal with 1.5% Stop-Loss Strategy

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

# 3. Trade Simulation with 25/75 Thresholds & 1.5% Stop-Loss
position = 0
entry_price = 0.0
stop_loss_pct = 0.015
positions = []

for i in range(len(df)):
    price = df['close'].iloc[i]
    rsi = df['rsi'].iloc[i]
    
    if position == 1:
        # Trigger Stop-Loss
        if price <= entry_price * (1 - stop_loss_pct):
            position = 0
        # Trigger Exit Signal at RSI > 75
        elif rsi > 75:
            position = 0
    elif position == 0:
        # Trigger Entry Signal at RSI < 25
        if rsi < 25:
            position = 1
            entry_price = price
            
    positions.append(position)

df['position'] = positions

# 4. Strategy Returns & 0.1% Taker Fee Adjustment
df['market_return'] = df['close'].pct_change()
df['strategy_return'] = df['position'].shift(1) * df['market_return']

trades = df['position'].diff().fillna(0) != 0
df.loc[trades, 'strategy_return'] -= 0.001

# 5. Performance Metrics
df['cum_return'] = (1 + df['strategy_return']).cumprod()
sharpe_ratio = (df['strategy_return'].mean() / df['strategy_return'].std()) * np.sqrt(24 * 365)

print("\n==========================================================================================")
print("  Signal 6 Variant C: Optimized RSI Reversal Strategy (25/75 + 1.5% Stop-Loss)            ")
print("==========================================================================================")
print(f"Cumulative Return: {(df['cum_return'].iloc[-1] - 1) * 100:.2f}%")
print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Total Trades Triggered: {trades.sum()}")
print("==========================================================================================\n")

# 6. Plot Equity Curve
plt.figure(figsize=(10, 5))
plt.plot(df['cum_return'], label='RSI (25/75) + 1.5% SL PnL', color='tab:green')
plt.title("Signal 6 Variant C: Optimized RSI Reversal Strategy (25/75 + 1.5% Stop-Loss)")
plt.xlabel("Hours")
plt.ylabel("Cumulative Growth")
plt.grid(True)
plt.legend()
plt.show()