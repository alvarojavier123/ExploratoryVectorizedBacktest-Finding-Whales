import pandas as pd

# Load the CSV data
df = pd.read_csv('aggTrades_aggregated_1min.csv')
df.index = pd.to_datetime(df['timestamp'])
df = df.drop('timestamp', axis=1)

# Aggregate volumes hourly by summing buy_volume and sell_volume, get last price in hour
hourly = df.resample('1H').agg({
    'price': 'last',         # closing price of last minute in the hour
    'buy_volume': 'sum',
    'sell_volume': 'sum'
})

# Calculate volume difference and total volume
hourly['volume_diff'] = hourly['buy_volume'] - hourly['sell_volume']
hourly['total_volume'] = hourly['buy_volume'] + hourly['sell_volume']

# Calculate buy_ratio and sell_ratio
hourly['buy_ratio'] = hourly['buy_volume'] / hourly['total_volume']
hourly['sell_ratio'] = hourly['sell_volume'] / hourly['total_volume']

# Determine aggressor column: "Buy" if buy_ratio > sell_ratio else "Sell"
hourly['aggressor'] = hourly.apply(
    lambda row: 'Buy' if row['buy_ratio'] > row['sell_ratio'] else 'Sell', axis=1
)

# Reorder columns to put price first, then the rest
hourly = hourly[['price', 'buy_volume', 'sell_volume', 'volume_diff', 'total_volume', 'aggressor']]

# Save to CSV
hourly.to_csv('aggTrades_aggregated_1h.csv')

print("Hourly aggregated data saved to 'aggTrades_aggregated_1h.csv'.")
print(hourly.head())
