
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
data['returns'] = data['price'].pct_change()

data = data.loc[data.index < '2024-01-01']
test = data.loc[data.index >= '2024-01-01']

print(data)
mean_diff = data['volume_diff'].mean()
std_diff = data['volume_diff'].std()
threshold = mean_diff + 3 * std_diff

lookback = 24
holding_period = 10 # HOURS

print(data.loc[data['volume_diff'] > threshold])
print(data.loc[data['volume_diff'] < -threshold])

data['direction'] = np.where(data['returns'].rolling(lookback).mean() > 0, 'up', 'down')

data['signal'] = np.where(
    (data['volume_diff'] > threshold) & (data['direction'] == 'up'), 1,
    np.where((data['volume_diff'] < -threshold) & (data['direction'] == 'down'), -1, 0)
)

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
data['returns'] = data['price'].pct_change()

data = data.loc[data.index < '2024-01-01']
test = data.loc[data.index >= '2024-01-01']

mean_diff = data['volume_diff'].mean()
std_diff = data['volume_diff'].std()
threshold = mean_diff + 3 * std_diff
lookback = 24

data['direction'] = np.where(data['returns'].rolling(lookback).mean() > 0, 'up', 'down')
data['signal'] = np.where(
    (data['volume_diff'] > threshold) & (data['direction'] == 'up'), 1,
    np.where((data['volume_diff'] < -threshold) & (data['direction'] == 'down'), -1, 0)
)

# Plot PnL curves for multiple holding periods
plt.figure(figsize=(15, 7))

for holding_period in [5, 10, 15, 20, 25, 30]:
    data['pnl'] = 0.0
    last_trade_end = -np.inf

    for i in range(len(data) - holding_period):
        if i > last_trade_end and data['signal'].iloc[i] != 0:
            cost_per_trade = 0.003
            ret = data['price'].pct_change(holding_period).iloc[i + holding_period] - cost_per_trade * abs(data['signal'].iloc[i])
            data.loc[data.index[i + holding_period], 'pnl'] = data['signal'].iloc[i] * ret
            last_trade_end = i + holding_period

    pnl = data['pnl'].dropna()
    cumret = (1 + pnl).cumprod()
    plt.plot(cumret, label=f'Holding {holding_period}h')

    # Print performance for each
    sharpe = pnl.mean() / pnl.std() * np.sqrt(24 * 365)
    print(Fore.YELLOW + f"\nHolding Period {holding_period}h" + Style.RESET_ALL)
    print(Fore.CYAN + f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Cumulative Return: {cumret.iloc[-1]:.2f}")
    print(f"Max Drawdown: {(cumret / cumret.cummax() - 1).min():.2%}" + Style.RESET_ALL)

# Final plot setup
plt.title('PnL by Holding Period', fontsize=16)
plt.xlabel('Time', fontsize=14)
plt.ylabel('Cumulative Returns', fontsize=14)
plt.legend()
plt.show()
"""

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
init()
plt.style.use('seaborn-darkgrid')

data = pd.read_csv('aggTrades_aggregated_1h.csv')
data.index = pd.to_datetime(data['timestamp'])
data = data.drop('timestamp', axis=1)
data['returns'] = data['price'].pct_change()

data = data.loc[data.index < '2024-01-01']
test = data.loc[data.index >= '2024-01-01']

mean_diff = data['volume_diff'].mean()
std_diff = data['volume_diff'].std()
threshold = mean_diff + 3 * std_diff

lookback_range = [12, 24, 36]
holding_range = [5, 10, 15, 20]

plt.figure(figsize=(15, 7))

for lookback in lookback_range:
    data['direction'] = np.where(
        data['returns'].rolling(lookback).mean() > 0, 'up', 'down'
    )

    data['signal'] = np.where(
        (data['volume_diff'] > threshold) & (data['direction'] == 'up'), 1,
        np.where((data['volume_diff'] < -threshold) & (data['direction'] == 'down'), -1, 0)
    )

    for holding_period in holding_range:
        data['pnl'] = 0.0
        last_trade_end = -np.inf

        for i in range(len(data) - holding_period):
            if i > last_trade_end and data['signal'].iloc[i] != 0:
                cost = 0.003
                ret = data['price'].pct_change(holding_period).iloc[i + holding_period] - cost * abs(data['signal'].iloc[i])
                data.loc[data.index[i + holding_period], 'pnl'] = data['signal'].iloc[i] * ret
                last_trade_end = i + holding_period

        pnl = data['pnl'].dropna()
        cumret = (1 + pnl).cumprod()

        label = f'LB:{lookback}, H:{holding_period}'
        plt.plot(cumret, label=label)

        # Print metrics
        sharpe = pnl.mean() / pnl.std() * np.sqrt(24 * 365)
        max_dd = (cumret / cumret.cummax() - 1).min()
        print(Fore.YELLOW + f"\nLookback {lookback}h, Holding {holding_period}h" + Style.RESET_ALL)
        print(Fore.CYAN + f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Cumulative Return: {cumret.iloc[-1]:.2f}")
        print(f"Max Drawdown: {max_dd:.2%}" + Style.RESET_ALL)

# Final plot
plt.title('PnL Curves for Lookback x Holding Period')
plt.xlabel('Time')
plt.ylabel('Cumulative Returns')
plt.legend()
plt.show()
"""