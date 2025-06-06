import os
import pandas as pd

input_folder = "aggTrades_2020_2025"
output_folder = "aggTrades_2020_2025_1S"

os.makedirs(output_folder, exist_ok=True)

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
    data['price'] = data['price'].astype(float)
    data['quantity'] = data['quantity'].astype(float)
    
    # Note: timestamp is in microseconds, convert accordingly
    data["timestamp"] = pd.to_datetime(data["timestamp"], unit="ms")
    data.set_index("timestamp", inplace=True)
    
    resampled = data.resample('1S').agg({
        'price': 'last',
        'quantity': 'sum',
        'agg_id': 'count'
    })
    
    resampled['buy_volume'] = data[data['aggressor'] == 'buy'].resample('1S')['quantity'].sum()
    resampled['sell_volume'] = data[data['aggressor'] == 'sell'].resample('1S')['quantity'].sum()
    
    resampled[['buy_volume', 'sell_volume']] = resampled[['buy_volume', 'sell_volume']].fillna(0)
    resampled.rename(columns={'agg_id': 'trade_count'}, inplace=True)
    
    # Save aggregated CSV
    output_path = os.path.join(output_folder, filename)
    resampled.to_csv(output_path)
    print(f"Saved aggregated data to {output_path}")

