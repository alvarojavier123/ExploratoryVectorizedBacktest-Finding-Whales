import requests
import zipfile
import io
import pandas as pd
import os
from datetime import datetime, timedelta

symbol = "BTCUSDT"
start_date = datetime(2021, 1, 1)  
end_date = datetime(2025, 6, 1)  
output_folder = f"{symbol}_aggTrades_2021-2025"
os.makedirs(output_folder, exist_ok=True)

date = start_date
while date <= end_date:
    date_str = date.strftime("%Y-%m-%d")
    zip_name = f"{symbol}-aggTrades-{date_str}.zip"
    url = f"https://data.binance.vision/data/spot/daily/aggTrades/{symbol}/{zip_name}"

    print(f"⏳ {date_str} ...", end=" ")

    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            print("❌ No disponible")
            date += timedelta(days=1)
            continue

        z = zipfile.ZipFile(io.BytesIO(resp.content))
        csv_name = z.namelist()[0]
        extracted_path = os.path.join(output_folder, csv_name)
        z.extract(csv_name, path=output_folder)

        df = pd.read_csv(extracted_path, header=None)
        if df.shape[1] == 8:
            df.columns = ['agg_trade_id', 'price', 'qty',
                          'first_trade_id', 'last_trade_id',
                          'timestamp', 'is_buyer_maker', 'ignore']
            df = df.drop(columns=['ignore'])
        else:
            df.columns = ['agg_trade_id', 'price', 'qty',
                          'first_trade_id', 'last_trade_id',
                          'timestamp', 'is_buyer_maker']

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        # Guardar CSV limpio (sin la columna ignore)
        csv_clean_name = f"{symbol}_aggTrades_{date_str}.csv"
        csv_clean_path = os.path.join(output_folder, csv_clean_name)
        df.to_csv(csv_clean_path, index=False)

        # Opcional: eliminar CSV extraído original si quieres (comentado)
        # os.remove(extracted_path)

        print("✅ Guardado")

    except Exception as e:
        print(f"⚠️ Error: {e}")

    date += timedelta(days=1)

print(f"\n📁 Archivos guardados en carpeta: {output_folder}")
