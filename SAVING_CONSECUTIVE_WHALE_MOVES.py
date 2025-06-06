import pandas as pd
import os
from colorama import init, Fore, Style

init()

input_folder = "aggTrades_2025"
threshold = 50  # minimum quantity for big trades

all_signals = []

for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    print(Fore.YELLOW + f"\nProcessing {filename}..." + Style.RESET_ALL)
    
    try:
        df = pd.read_csv(file_path, header=None)
        df.columns = [
            "agg_id", "price", "quantity", "trade_id_start",
            "trade_id_end", "timestamp", "is_buyer_maker", "flag"
        ]

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
        """
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['quantity'] = df['quantity'].astype(float)
        """

        big_trades = df[df['quantity'] >= threshold].copy()
        if big_trades.empty:
            print("No big trades found")
            continue

        big_trades['side'] = big_trades['is_buyer_maker'].apply(lambda x: 'sell' if x else 'buy')
        big_trades['prev_side'] = big_trades['side'].shift(1)
        big_trades['consecutive'] = big_trades['side'] == big_trades['prev_side']

        groups = []
        group = []

        for idx, row in big_trades.iterrows():
            if row['consecutive']:
                group.append(row)
            else:
                if group:
                    groups.append(group)
                group = [row]
        if group:
            groups.append(group)

        if not any(len(g) > 1 for g in groups):
            print("No consecutive big trades found")
            continue

        hourly_records = []

        for g in groups:
            if len(g) > 1:
                trade1 = g[0]
                trade2 = g[1]

                second_trade_hour = trade2.name.floor('H')
                signal = 1 if trade2['side'] == 'buy' else -1

                # Dates of both trades as strings
                trade1_date = trade1.name.strftime('%Y-%m-%d %H:%M:%S')
                trade2_date = trade2.name.strftime('%Y-%m-%d %H:%M:%S')

                # Quantities of both trades separately
                qty1 = trade1['quantity']
                qty2 = trade2['quantity']

                print(Fore.LIGHTBLUE_EX + f"Consecutive big trades found ({len(g)}):" + Style.RESET_ALL)
                print(f"First trade time: {trade1_date}, side: {trade1['side']}, qty: {qty1}")
                print(f"Second trade time: {trade2_date}, side: {trade2['side']}, qty: {qty2}")
                print(f"Hourly signal timestamp: {second_trade_hour}, signal: {signal}, qty sum: {qty1 + qty2}")
                print("-" * 50)

                hourly_records.append({
                    'timestamp': second_trade_hour,
                    'signal': signal,
                    'quantity_sum': qty1 + qty2,
                    'quantity_trade1': qty1,
                    'quantity_trade2': qty2,
                    'trade1_date': trade1_date,
                    'trade2_date': trade2_date,
                    'filename': filename
                })

        hourly_df = pd.DataFrame(hourly_records)
        hourly_df.set_index('timestamp', inplace=True)
        all_signals.append(hourly_df)

    except Exception as e:
        print(Fore.RED + f"Error processing {filename}: {e}" + Style.RESET_ALL)

if all_signals:
    combined_signals = pd.concat(all_signals)
    combined_signals = combined_signals.groupby(['timestamp', 'filename']).agg({
        'signal': 'last',
        'quantity_sum': 'sum',
        'quantity_trade1': 'sum',
        'quantity_trade2': 'sum',
        'trade1_date': 'first',
        'trade2_date': 'first'
    }).reset_index()

    combined_signals.to_csv('hourly_consecutive_big_trades_signals_2025.csv', index=False)
    print(Fore.GREEN + "\nSaved hourly signals CSV: hourly_consecutive_big_trades_signals.csv" + Style.RESET_ALL)
else:
    print("No signals to save.")
