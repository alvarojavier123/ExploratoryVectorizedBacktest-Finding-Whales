import requests
import zipfile
import io
import pandas as pd
import numpy as np
import os
import datetime as dt
import matplotlib.pyplot as plt
plt.style.use('seaborn-darkgrid')
from colorama import init, Fore, Style
init()

data = pd.read_csv('aggTrades_aggregated_1h.csv')
data.index = pd.to_datetime(data['timestamp'])
data = data.drop('timestamp', axis=1)
print(data)

def ts_delta(df, period=1):
    return df.diff(period)

def alpha012(v, c):
    return (np.sign(ts_delta(v, 1)).mul(-ts_delta(c, 1)))

alpha12 = alpha012(data.buy_volume, data.price)

pnl = alpha12.apply(np.sign) * data.price.pct_change().shift(-1)

pnl.cumsum().plot(label='data', figsize=(15, 7))

returns = pnl.dropna()
cumprod = (1 + returns).cumprod()
cumsum = returns.cumsum()
sharpe = returns.mean() / returns.std() * np.sqrt(24 * 365)

rolling_max = cumprod.cummax()
drawdown = cumprod / rolling_max - 1
max_dd = drawdown.min()

# Print metrics
print(Fore.CYAN + f"\nSharpe Ratio: {sharpe:.2f}")
print(f"Cumulative Return (final): {cumprod.iloc[-1]:.2f}")
print(f"Cumulative PnL (final): {cumsum.iloc[-1]:.2f}")
print(f"Max Drawdown: {max_dd:.2%}" + Style.RESET_ALL)

# Set the title and axis labels
plt.title('PnL of Alpha #3', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Cumulative Returns', fontsize=14)
plt.legend()
plt.show()