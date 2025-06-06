import pandas as pd
import os
from colorama import init, Fore, Style

init()

input_folder = "aggTrades_2020_2024"
threshold = 100  # minimum quantity for big trades

for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    print(Fore.YELLOW + f"\nProcessing {filename}..." + Style.RESET_ALL)
    
    try:
        df = pd.read_csv(file_path, header=None)
        df.columns = [
            "agg_id", "price", "quantity", "trade_id_start",
            "trade_id_end", "timestamp", "is_buyer_maker", "flag"
        ]

        # Convert timestamp to datetime and set as index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        df['quantity'] = df['quantity'].astype(float)

        # Filter only big trades
        big_trades = df[df['quantity'] >= threshold].copy()
        if big_trades.empty:
            print("No big trades found")
            continue

        # Determine side
        big_trades['side'] = big_trades['is_buyer_maker'].apply(lambda x: 'sell' if x else 'buy')

        # Find consecutive trades with same side
        big_trades['prev_side'] = big_trades['side'].shift(1)
        big_trades['consecutive'] = big_trades['side'] == big_trades['prev_side']

        # Group consecutive trades
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

        found = False
        for g in groups:
            if len(g) > 1:
                found = True
                print(Fore.LIGHTBLUE_EX + f"Consecutive big trades found ({len(g)}):" + Style.RESET_ALL)
                print(pd.DataFrame(g))
                print("-" * 50)

        if not found:
            print("No consecutive big trades found")

    except Exception as e:
        print(Fore.RED + f"Error processing {filename}: {e}" + Style.RESET_ALL)
