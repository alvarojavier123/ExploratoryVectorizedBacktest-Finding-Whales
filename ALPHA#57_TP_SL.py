import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore, Style
plt.style.use('seaborn-darkgrid')

# --- Load data ---
data = pd.read_csv('aggTrades_aggregated_1h.csv')
data.index = pd.to_datetime(data['timestamp'])
data.drop('timestamp', axis=1, inplace=True)

# --- Parameters ---
vwap_window = 5
price_roll = 30
signal_lag = 1
stop_loss = 0.01
take_profit = 0.02

# --- Alpha#57 signal ---
vwap = (data.price * data.total_volume).rolling(vwap_window).sum() / data.total_volume.rolling(vwap_window).sum()
num = data.price - vwap
denom = data.price.rolling(price_roll).apply(np.argmax, raw=True)
denom = denom.rolling(2).apply(lambda x: np.average(x, weights=np.linspace(0, 1, 2)), raw=True)
alpha57 = -num / denom

# Signal: based on past, act on next bar
signal = alpha57.shift(signal_lag).apply(np.sign)
signal = signal.replace([np.inf, -np.inf], 0).fillna(0)

# Simulate trade entry at next bar
entry_price = data.price.shift(1)  # simulate buying at next open
exit_price = data.price.shift(2)   # simulate exit after 1 bar (you can replace with better data later)

# Calculate raw return per trade
raw_return = (exit_price - entry_price) / entry_price
raw_return = raw_return.fillna(0)

# SL/TP capped returns
long_return = np.clip(raw_return, -stop_loss, take_profit)
short_return = np.clip(-raw_return, -stop_loss, take_profit)

returns = np.where(signal > 0, long_return,
            np.where(signal < 0, short_return, 0))
returns = pd.Series(returns, index=data.index)

# --- Metrics ---
returns = returns.replace([np.inf, -np.inf], 0).fillna(0)
cumprod = (1 + returns).cumprod()
cumsum = returns.cumsum()
sharpe = returns.mean() / returns.std() * np.sqrt(24 * 365)
rolling_max = cumprod.cummax()
drawdown = cumprod / rolling_max - 1
max_dd = drawdown.min()

# --- Print ---
print(Fore.CYAN + f"\nSharpe Ratio: {sharpe:.2f}")
print(f"Cumulative Return (final): {cumprod.iloc[-1]:.2f}")
print(f"Cumulative PnL (final): {cumsum.iloc[-1]:.2f}")
print(f"Max Drawdown: {max_dd:.2%}" + Style.RESET_ALL)

# --- Plot ---
plt.figure(figsize=(15, 7))
plt.plot(cumprod, label="Cumulative Return (No Lookahead, 1-Bar SL/TP)")
plt.title("Alpha#57 with Proper SL/TP (No Lookahead)")
plt.xlabel("Time")
plt.ylabel("Cumulative Return")
plt.legend()
plt.show()
