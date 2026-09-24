# z_window = 20, z_buy = -2.0

import pandas as pd
import numpy as np
import os

# 1. Load market data (Binance raw CSV without header)
data_path = 'data/BTCUSDT-1h-2026-08.csv'
if not os.path.exists(data_path):
    data_path = '../../data/BTCUSDT-1h-2026-08.csv'

# Define standard Binance K-line column headers
column_names = [
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_volume', 'count', 'taker_buy_volume',
    'taker_buy_quote_volume', 'ignore'
]

# Read CSV explicitly setting header=None
df = pd.read_csv(data_path, header=None, names=column_names)

# Convert open_time from timestamp (ms/us) to datetime
df['open_time'] = pd.to_datetime(df['open_time'], unit='us')
df = df.sort_values('open_time').reset_index(drop=True)

# 2. Strategy parameters (Baseline)
return_period = 1       # Period for return calculation (1h)
z_window = 20           # Rolling window for Z-Score calculation (20h)
z_buy = -2.0            # Oversold buy threshold
z_exit = 0.0            # Mean reversion exit threshold
stop_loss_pct = 0.015   # 1.5% Stop Loss
fee_rate = 0.001        # 0.1% Taker fee per trade

# 3. Indicator calculation: Return & Z-Score
df['returns'] = df['close'].pct_change(return_period)
df['ret_mean'] = df['returns'].rolling(window=z_window).mean()
df['ret_std'] = df['returns'].rolling(window=z_window).std()
df['z_score'] = (df['returns'] - df['ret_mean']) / df['ret_std']

# 4. Backtesting engine logic
initial_balance = 100000.0
balance = initial_balance
position = 0          # 0: Out of market, 1: Long position
entry_price = 0.0
trades = []

for i in range(z_window + 1, len(df)):
    current_price = df.loc[i, 'close']
    current_time = df.loc[i, 'open_time']
    current_z = df.loc[i, 'z_score']
    
    # Entry logic
    if position == 0:
        if current_z < z_buy:
            position = 1
            entry_price = current_price
            balance *= (1 - fee_rate)
            trades.append({
                'type': 'BUY',
                'time': current_time,
                'price': entry_price,
                'z_score': current_z,
                'balance': balance
            })
            
    # Exit logic
    elif position == 1:
        price_change = (current_price - entry_price) / entry_price
        
        # Stop loss trigger (1.5%)
        if price_change <= -stop_loss_pct:
            position = 0
            exit_price = entry_price * (1 - stop_loss_pct)
            balance *= (1 - stop_loss_pct) * (1 - fee_rate)
            trades.append({
                'type': 'SELL_SL',
                'time': current_time,
                'price': exit_price,
                'z_score': current_z,
                'reason': 'Stop Loss 1.5%',
                'balance': balance
            })
            
        # Z-Score mean reversion trigger
        elif current_z >= z_exit:
            position = 0
            exit_price = current_price
            balance *= (1 + price_change) * (1 - fee_rate)
            trades.append({
                'type': 'SELL_SIGNAL',
                'time': current_time,
                'price': exit_price,
                'z_score': current_z,
                'reason': 'Z-Score Reversion',
                'balance': balance
            })

# 5. Performance summary
total_return = (balance - initial_balance) / initial_balance * 100
total_trades = len([t for t in trades if t['type'].startswith('SELL')])

print("=" * 55)
print("Signal 4: Extreme Return Reversal - Baseline Results")
print("=" * 55)
print(f"Initial Balance : ${initial_balance:,.2f}")
print(f"Final Balance   : ${balance:,.2f}")
print(f"Total Return    : {total_return:+.2f}%")
print(f"Total Trades    : {total_trades}")
print("=" * 55)