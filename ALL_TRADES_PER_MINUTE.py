import os
import pandas as pd

input_folder = "aggTrades_2020_2025"
output_file = "aggTrades_aggregated_1min.csv"

# Remove output file if it already exists
if os.path.exists(output_file):
    os.remove(output_file)

first_chunk = True  # To write header only once

for filename in os.listdir(input_folder):
    if not filename.endswith(".csv"):
        continue

    file_path = os.path.join(input_folder, filename)
    print(f"Processing {filename}...")

    data = pd.read_csv(file_path, header=None)

    data.columns = [
        "agg_id",
        "price",
        "quantity",
        "trade_id_start",
        "trade_id_end",
        "timestamp",
        "is_buyer_maker",
        "flag"
    ]

    data.drop(columns=["flag"], inplace=True)
    data["aggressor"] = data["is_buyer_maker"].map({True: "sell", False: "buy"})
    data["price"] = data["price"].astype(float)
    data["quantity"] = data["quantity"].astype(float)

    # Convert timestamp from milliseconds to datetime
    
    data["timestamp"] = pd.to_datetime(data["timestamp"], unit="ms")
    data.set_index("timestamp", inplace=True)

    # 1-minute resampling
    resampled = data.resample('1min').agg({
        'price': 'last',
        'quantity': 'sum',
        'agg_id': 'count'
    })

    resampled['buy_volume'] = data[data['aggressor'] == 'buy'].resample('1min')['quantity'].sum()
    resampled['sell_volume'] = data[data['aggressor'] == 'sell'].resample('1min')['quantity'].sum()

    resampled[['buy_volume', 'sell_volume']] = resampled[['buy_volume', 'sell_volume']].fillna(0)
    resampled.rename(columns={'agg_id': 'trade_count'}, inplace=True)

    # Append to CSV
    resampled.to_csv(output_file, mode='a', header=first_chunk)
    first_chunk = False

    print(f"Appended aggregated 1-min data from {filename} to {output_file}")
