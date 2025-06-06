import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore, Style
plt.style.use('seaborn-darkgrid')

# --- Cargar datos ---
data = pd.read_csv('aggTrades_aggregated_1h.csv')
data.index = pd.to_datetime(data['timestamp'])
data.drop('timestamp', axis=1, inplace=True)

# --- Parameter sweep setup ---
vwap_windows = [3, 5, 10]
price_rolls = [20, 30, 40]
signal_lags = [0, 1, 2]

results = []

# --- Sweep ---
for vwap_window in vwap_windows:
    for price_roll in price_rolls:
        for signal_lag in signal_lags:

            vwap = (data.price * data.total_volume).rolling(vwap_window).sum() / data.total_volume.rolling(vwap_window).sum()
            num = data.price - vwap

            denom = data.price.rolling(price_roll).apply(np.argmax, raw=True)
            denom = denom.rolling(2).apply(lambda x: np.average(x, weights=np.linspace(0, 1, 2)), raw=True)

            alpha57 = -num / denom
            signal = alpha57.apply(np.sign).shift(signal_lag)

            returns = (signal * data.price.pct_change().shift(-1)).dropna()
            cumprod = (1 + returns).cumprod()
            cumsum = returns.cumsum()
            sharpe = returns.mean() / returns.std() * np.sqrt(24 * 365)

            rolling_max = cumprod.cummax()
            drawdown = cumprod / rolling_max - 1
            max_dd = drawdown.min()

            results.append({
                'vwap_window': vwap_window,
                'price_roll': price_roll,
                'signal_lag': signal_lag,
                'sharpe': sharpe,
                'cumprod': cumprod.iloc[-1],
                'cumsum': cumsum.iloc[-1],
                'max_drawdown': max_dd
            })

# --- Mostrar mejores resultados ---
results_df = pd.DataFrame(results)
best = results_df.sort_values(by='sharpe', ascending=False).head(10)
print(Fore.CYAN + "\nTop 10 parameter combinations by Sharpe Ratio:\n")
print(best.round(4).to_string(index=False) + Style.RESET_ALL)

# --- Plot top 3 combinations ---
fig, ax = plt.subplots(figsize=(15, 7))

for i, row in best.head(3).iterrows():
    vwap = (data.price * data.total_volume).rolling(int(row.vwap_window)).sum() / data.total_volume.rolling(int(row.vwap_window)).sum()
    num = data.price - vwap
    denom = data.price.rolling(int(row.price_roll)).apply(np.argmax, raw=True)
    denom = denom.rolling(2).apply(lambda x: np.average(x, weights=np.linspace(0, 1, 2)), raw=True)
    alpha57 = -num / denom
    signal = alpha57.apply(np.sign).shift(int(row.signal_lag))
    returns = (signal * data.price.pct_change().shift(-1)).dropna()
    cumprod = (1 + returns).cumprod()
    label = f"VWAP={int(row.vwap_window)}, PRoll={int(row.price_roll)}, Lag={int(row.signal_lag)}"
    ax.plot(cumprod, label=label)

ax.set_title('Top 3 Alpha#57 Parameter Combinations - Cumulative Return')
ax.set_xlabel('Time')
ax.set_ylabel('Cumulative Return')
ax.legend()
plt.show()
