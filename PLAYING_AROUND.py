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

data = data.loc[data.index < '2024-01-01']
test = data.loc[data.index >= '2024-01-01']

lookback = 24
holding_period = 10 # HOURS
corr_coefficient = 0.3

data['returns'] = data['price'].pct_change()

data['direction'] = np.where(data['returns'].rolling(lookback).mean() > 0, 'up', 'down')

data['correlation'] = data['returns'].rolling(lookback).corr(data['returns'].shift(1))

strong_corr = data[data['correlation'] > corr_coefficient]
pd.set_option("display.max_rows", None)

data['signal'] = np.where(
    (data['correlation'] > corr_coefficient) & (data['direction'] == 'up'), 1,
    np.where((data['correlation'] > corr_coefficient) & (data['direction'] == 'down'), -1, 0))


signals = data[data['signal'].isin([1, -1])]


data['pnl'] = 0.0
data['future holding returns'] = data['price'].pct_change(holding_period)
last_trade_end = -np.inf

for i in range(len(data) - holding_period):
    if i > last_trade_end and data['signal'].iloc[i] != 0:
        cost_per_trade = 0.003
        ret = data['price'].pct_change(holding_period).iloc[i + holding_period] - cost_per_trade * abs(data['signal'].iloc[i])
        data.loc[data.index[i + holding_period], 'pnl'] = data['signal'].iloc[i] * ret
        last_trade_end = i + holding_period

print(data.tail(300))

pnl = data['pnl']

pnl.cumsum().plot(label='data', figsize=(15, 7))

returns = pnl.dropna()
cumprod = (1 + returns).cumprod()
cumsum = returns.cumsum()
sharpe = returns.mean() / returns.std() * np.sqrt(24 * 365)

rolling_max = cumprod.cummax()
drawdown = cumprod / rolling_max - 1
max_dd = drawdown.min()

trade_count = (data['signal'].diff().fillna(0) != 0).sum()
print(Fore.YELLOW + f"Trade count: {int(trade_count)}" + Style.RESET_ALL)


# Print metrics
print(Fore.CYAN + f"\nSharpe Ratio: {sharpe:.2f}")
print(f"Cumulative Return (final): {cumprod.iloc[-1]:.2f}")
print(f"Cumulative PnL (final): {cumsum.iloc[-1]:.2f}")
print(f"Max Drawdown: {max_dd:.2%}" + Style.RESET_ALL)

# Set the title and axis labels
plt.title('PnL', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Cumulative Returns', fontsize=14)
plt.legend()
plt.show()


"""
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

# Split train/test
train = data.loc[data.index < '2024-01-01']
test = data.loc[data.index >= '2024-01-01']

# Parameters to sweep
lookbacks = [12, 24, 36]
holding_periods = [5, 10, 15, 20]
corr_coeffs = [0.2, 0.3, 0.4]

plt.figure(figsize=(15, 8))

for lookback in lookbacks:
    for holding_period in holding_periods:
        for corr_coefficient in corr_coeffs:
            df = train.copy()
            df['returns'] = df['price'].pct_change(fill_method=None)

            df['direction'] = np.where(df['returns'].rolling(lookback).mean() > 0, 'up', 'down')
            df['correlation'] = df['returns'].rolling(lookback).corr(df['returns'].shift(1))

            df['signal'] = np.where(
                (df['correlation'] > corr_coefficient) & (df['direction'] == 'up'), 1,
                np.where((df['correlation'] > corr_coefficient) & (df['direction'] == 'down'), -1, 0)
            )

            df['pnl'] = 0.0
            last_trade_end = -np.inf

            for i in range(len(df) - holding_period):
                if i > last_trade_end and df['signal'].iloc[i] != 0:
                    cost_per_trade = 0.003
                    ret = df['price'].pct_change(holding_period, fill_method=None).iloc[i + holding_period] - cost_per_trade * abs(df['signal'].iloc[i])

                    df.loc[df.index[i + holding_period], 'pnl'] = df['signal'].iloc[i] * ret
                    last_trade_end = i + holding_period

            pnl = df['pnl'].dropna()
            cumret = (1 + pnl).cumprod()

            sharpe = pnl.mean() / pnl.std() * np.sqrt(24 * 365) if pnl.std() != 0 else 0
            max_dd = (cumret / cumret.cummax() - 1).min()

            label = f"LB{lookback} HP{holding_period} CC{corr_coefficient}"
            plt.plot(cumret, label=label)

            print(Fore.YELLOW + f"\n{label}")
            print(Fore.CYAN + f"Sharpe Ratio: {sharpe:.2f}")
            print(f"Cumulative Return: {cumret.iloc[-1]:.2f}")
            print(f"Max Drawdown: {max_dd:.2%}" + Style.RESET_ALL)

plt.title('PnL Curves Parameter Sweep (Train Data)', fontsize=16)
plt.xlabel('Time', fontsize=14)
plt.ylabel('Cumulative Returns', fontsize=14)
plt.legend(fontsize='small')
plt.show()
"""


