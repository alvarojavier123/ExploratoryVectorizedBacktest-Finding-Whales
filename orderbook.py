import asyncio
import websockets
import json
from datetime import datetime, timedelta

symbol = 'btcusdt'

# Globals to store order book and trades info
order_book = {
    "bids": [],
    "asks": []
}
buy_volume = 0.0
sell_volume = 0.0

# Keep track of current 1-min candle period
current_minute = None

# Lock for safe concurrent updates
lock = asyncio.Lock()

async def depth_handler():
    global order_book
    url = f"wss://stream.binance.com:9443/ws/{symbol}@depth@100ms"
    async with websockets.connect(url) as ws:
        async for message in ws:
            data = json.loads(message)
            async with lock:
                # Update top bids and asks from depth update
                # 'b' and 'a' are lists of [price, qty]
                order_book['bids'] = data.get('b', order_book['bids'])[:10]
                order_book['asks'] = data.get('a', order_book['asks'])[:10]

async def trades_handler():
    global buy_volume, sell_volume, current_minute
    url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    async with websockets.connect(url) as ws:
        async for message in ws:
            data = json.loads(message)
            async with lock:
                trade_time = datetime.utcfromtimestamp(data['T'] / 1000)
                trade_minute = trade_time.replace(second=0, microsecond=0)
                if current_minute is None:
                    current_minute = trade_minute

                # Reset volumes if new minute
                if trade_minute != current_minute:
                    current_minute = trade_minute
                    buy_volume = 0.0
                    sell_volume = 0.0

                qty = float(data['q'])
                if data['m']:  # seller is maker => aggressive sell
                    sell_volume += qty
                else:          # buyer is maker => aggressive buy
                    buy_volume += qty

async def snapshot_saver():
    global buy_volume, sell_volume, current_minute, order_book
    while True:
        await asyncio.sleep(60)  # wait for 1 minute

        async with lock:
            if current_minute is None:
                continue

            snapshot = {
                "timestamp": current_minute.strftime('%Y-%m-%d %H:%M:%S'),
                "order_book": {
                    "bids": order_book['bids'],
                    "asks": order_book['asks']
                },
                "buy_volume": buy_volume,
                "sell_volume": sell_volume
            }

            filename = f"{symbol}_1min_snapshots.jsonl"
            with open(filename, "a") as f:
                f.write(json.dumps(snapshot) + "\n")

            # Reset volumes for next minute
            buy_volume = 0.0
            sell_volume = 0.0

async def main():
    await asyncio.gather(
        depth_handler(),
        trades_handler(),
        snapshot_saver()
    )

if __name__ == "__main__":
    asyncio.run(main())
