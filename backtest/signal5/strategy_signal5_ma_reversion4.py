# ma_window = 20, bias_buy = -0.01, exit_bias = -0.002

import os
import pandas as pd
import numpy as np

def run_signal5_variant_c():
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

    # 1. Load data
    columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_base_vol',
        'taker_quote_vol', 'ignore'
    ]
    df = pd.read_csv(csv_path, header=None, names=columns)
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['open_time'] = pd.to_datetime(df['open_time'], unit='us', errors='coerce')
    df = df.sort_values('open_time').reset_index(drop=True)

    # 2. Strategy parameters (Variant C: Quick Exit -0.2%)
    ma_window = 20
    bias_buy = -0.01
    exit_bias = -0.002
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

        if position > 0:
            # Stop Loss
            if current_close <= entry_price * (1 - stop_loss):
                exit_price = current_close
                trade_pnl = (exit_price - entry_price) / entry_price - (2 * taker_fee)
                balance *= (1 + trade_pnl)
                trades.append({'type': 'SL', 'pnl': trade_pnl})
                position = 0.0
                entry_price = 0.0

            # Exit Condition: Bias >= exit_bias
            elif current_bias >= exit_bias:
                exit_price = current_close
                trade_pnl = (exit_price - entry_price) / entry_price - (2 * taker_fee)
                balance *= (1 + trade_pnl)
                trades.append({'type': 'TP', 'pnl': trade_pnl})
                position = 0.0
                entry_price = 0.0

        elif position == 0:
            if current_bias <= bias_buy:
                position = 1.0
                entry_price = current_close

    # 5. Output results
    total_return = (balance - initial_balance) / initial_balance * 100
    win_trades = [t for t in trades if t['pnl'] > 0]
    win_rate = (len(win_trades) / len(trades) * 100) if len(trades) > 0 else 0.0

    print("==================================================")
    print("Signal 5: MA Reversion - Variant C (Quick Exit -0.2%)")
    print("==================================================")
    print(f"Initial Balance : ${initial_balance:,.2f}")
    print(f"Final Balance   : ${balance:,.2f}")
    print(f"Total Return    : {total_return:.2f}%")
    print(f"Total Trades    : {len(trades)}")
    print(f"Win Rate        : {win_rate:.1f}%")
    print("==================================================")

if __name__ == "__main__":
    run_signal5_variant_c()