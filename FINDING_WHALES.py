import requests
import zipfile
import io
import pandas as pd
import os
from datetime import datetime, timedelta
from colorama import init, Fore, Style
init()

min_data = pd.read_csv('BTC_USDT_1min_since_2020.csv')
min_data.index = pd.to_datetime(min_data['timestamp'])
min_data = min_data.drop('timestamp', axis=1)
min_data['signals'] = 0
print(min_data)

input_folder = "aggTrades_2020_2024"
whale_trades = []

threshold = 100

for filename in os.listdir(input_folder):

    file_path = os.path.join(input_folder, filename)
    print(Fore.YELLOW + f"Processing {filename}..." + Style.RESET_ALL)
    df = pd.read_csv(file_path, header=None)
    df.columns = [
        "agg_id", "price", "quantity", "trade_id_start",
        "trade_id_end", "timestamp", "is_buyer_maker", "flag"
    ]

    df.index = pd.to_datetime(df["timestamp"] // 1000, unit="s")
    
    """
    df["timestamp"] = df["timestamp"].astype("int64")
    df.index = pd.to_datetime(df["timestamp"], unit="us", errors="coerce")
    df = df[df.index.notna()]
    """
    df = df.drop('timestamp', axis=1)

    print(df)


    df['quantity'] = df['quantity'].astype(float)

    buyers = df[(df['quantity'] > threshold) & (df['is_buyer_maker'] == False)]
    sellers = df[(df['quantity'] > threshold) & (df['is_buyer_maker'] == True)]

    if not buyers.empty:
        print(Fore.LIGHTGREEN_EX + f"AGGRESSIVE BUYERS (Trades : {len(buyers)})" + Style.RESET_ALL)
        print(buyers)
        signal = 1
        entry_time_signal = buyers.index[0]
        entry_time_signal = entry_time_signal.replace(second=0)
        print(entry_time_signal)
        min_data.loc[entry_time_signal, 'signals'] = 1 
        row = min_data.loc[entry_time_signal]
        print(row)

        #print("--------------------------------------------------")
        
        res = input("Continue ? ")
        if res == '':
            print("--------------------------------------------------")
            continue
        

    if not sellers.empty:
        print(Fore.LIGHTRED_EX + f"AGGRESSIVE SELLERS (Trades : {len(sellers)})" + Style.RESET_ALL)
        print(sellers)
        signal = -1
        entry_time_signal = sellers.index[0]
        entry_time_signal = entry_time_signal.replace(second=0)
        print(entry_time_signal)
        min_data.loc[entry_time_signal, 'signals'] = -1 
        row = min_data.loc[entry_time_signal]
        print(row)
        #print("--------------------------------------------------")
        
        res = input("Continue ? ")
        if res == '':
            print("--------------------------------------------------")
            continue
        

    if buyers.empty and sellers.empty:
        print("No Whale Transactions")

       

#min_data.to_csv(f"SIGNALS_THRESHOLD_{threshold}_2025.csv")
