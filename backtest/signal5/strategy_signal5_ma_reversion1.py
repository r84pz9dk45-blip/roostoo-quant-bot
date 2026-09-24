# ma_window = 20, bias_buy = -0.02, exit_bias = 0.0

import os
import pandas as pd
import numpy as np

def run_signal5_baseline():
    csv_filename = 'BTCUSDT-1h-2026-08.csv'
    possible_paths = [
        os.path.join('data', csv_filename),
        os.path.join('..', 'data', csv_filename),
        os.path.join('..', '..', 'data', csv_filename),
        os.path.join(os.path.dirname(__file__), 'data', csv_filename),
        os.path.join(os.path.dirname(__file__), '..', 'data', csv_filename),
        os.path.join(os.path.dirname(__file__), '..', '..', 'data', csv_filename)
    ]
    
    csv_path = None
    for p in possible_paths:
        if os.path.exists(p):
            csv_path = p
            break
            
    if not csv_path:
        raise FileNotFoundError(f"File {csv_filename} not found.")

    # 1. Load data with proper columns for raw Binance K-line CSV
    columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_base_vol',
        'taker_quote_vol', 'ignore'
    ]
    df = pd.read_csv(csv_path, header=None, names=columns)

    # Numeric conversion
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fix: Use 'us' (microseconds) instead of 'ms' to prevent OutOfBoundsDatetime error
    df['open_time'] = pd.to_datetime(df['open_time'], unit='us', errors='coerce')
    df = df.sort_values('open_time').reset_index(drop=True)

    # 2. Strategy parameters
    ma_window = 20
    bias_buy = -0.02
    stop_loss = 0.015
    taker_fee = 0.001
    initial_balance = 100000.0

    # 3. Calculate indicators
    df['ma'] = df['close'].rolling(window=ma_window).mean()
    df['bias'] = (df['close'] - df['ma']) / df['ma']

    # 4. Backtest execution
    balance = initial_balance
    position = 0.0
    entry_price = 0.0
    trades = []

    for i in range(ma_window, len(df)):
        current_close = df.loc[i, 'close']
        current_bias = df.loc[i, 'bias']
        current_ma = df.loc[i, 'ma']

        # Check exit if in position
        if position > 0:
            # Stop Loss
            if current_close <= entry_price * (1 - stop_loss):
                exit_price = current_close
                trade_pnl = (exit_price - entry_price) / entry_price - (2 * taker_fee)
                balance *= (1 + trade_pnl)
                trades.append({'type': 'SL', 'pnl': trade_pnl})
                position = 0.0
                entry_price = 0.0

            # Exit Condition: Close >= MA
            elif current_close >= current_ma:
                exit_price = current_close
                trade_pnl = (exit_price - entry_price) / entry_price - (2 * taker_fee)
                balance *= (1 + trade_pnl)
                trades.append({'type': 'TP_MA', 'pnl': trade_pnl})
                position = 0.0
                entry_price = 0.0

        # Check entry if flat
        elif position == 0:
            if current_bias <= bias_buy:
                position = 1.0
                entry_price = current_close

    # 5. Output results
    total_return = (balance - initial_balance) / initial_balance * 100
    print("==================================================")
    print("Signal 5: MA Reversion - Baseline")
    print("==================================================")
    print(f"Initial Balance : ${initial_balance:,.2f}")
    print(f"Final Balance   : ${balance:,.2f}")
    print(f"Total Return    : {total_return:.2f}%")
    print(f"Total Trades    : {len(trades)}")
    print("==================================================")

if __name__ == "__main__":
    run_signal5_baseline()