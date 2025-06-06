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

# Calculate VWAP for the 12 stocks
vwap = (data.price * data.total_volume).rolling(10).sum()/data.total_volume.rolling(10).sum()

# Calculate numerator of alpha #57
num = data.price - vwap

# Calculate denominator of alpha #57
denom = data.price.rolling(30).apply(np.argmax).rolling(2).apply(
    lambda x: np.average(x, weights=np.linspace(0, 1, 2))
    )

alpha57 = -num/denom

pnl = (alpha57.apply(np.sign).shift(1) * data.price.pct_change())
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

# Display the chart
plt.show()

"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from colorama import init, Fore, Style
import plotly.io as pio
pio.renderers.default = "browser"

init()
pd.set_option("display.max_rows", None)

# --- Cargar y preparar los datos ---
data = pd.read_csv('aggTrades_aggregated_1h.csv')
data.index = pd.to_datetime(data['timestamp'])
data = data.drop('timestamp', axis=1)

# --- Calcular Alpha y PnL ---
alpha = data['price'].rolling(10).corr(data['buy_volume'])
pnl = alpha.apply(np.sign).shift(1) * data['price'].pct_change()
pnl = pnl.dropna()

# --- Crear DataFrame de estrategia ---
strategy_returns = pd.DataFrame()
strategy_returns['returns'] = pnl
strategy_returns['entry time'] = pnl.index
strategy_returns['exit time'] = pnl.index  # PnL es por barra, así que mismo timestamp

# --- Métricas ---
strategy_returns['cumsum returns'] = strategy_returns['returns'].cumsum()
strategy_returns['cumulative returns'] = (1 + strategy_returns['returns']).cumprod()
compounded_returns = (1 + strategy_returns['returns']).prod() - 1
simple_returns = strategy_returns['returns'].sum()
cumulative_compounded = (1 + strategy_returns['returns']).cumprod()
cumulative_simple = strategy_returns['returns'].cumsum()

running_max = cumulative_compounded.cummax()
drawdown = (cumulative_compounded - running_max) / running_max
max_drawdown = drawdown.min()

avg_trade_days = 1  # datos por hora, se asume un día por trade
daily_returns = strategy_returns['returns']
annualized_return = (1 + compounded_returns) ** (252) - 1
annualized_volatility = daily_returns.std() * np.sqrt(252 * 24)
sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else np.nan

win_rate = (strategy_returns['returns'] > 0).mean()
gross_profit = strategy_returns.loc[strategy_returns['returns'] > 0, 'returns'].sum()
gross_loss = abs(strategy_returns.loc[strategy_returns['returns'] <= 0, 'returns'].sum())
profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.nan
cumulative_compounded -= 1  # empieza desde 0

# --- Gráfico interactivo Plotly ---
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=strategy_returns['exit time'],
    y=cumulative_compounded,
    mode='lines',
    name='Compounded Returns ($)',
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=strategy_returns['exit time'],
    y=cumulative_simple,
    mode='lines',
    name='Simple Returns (Cumsum)',
    line=dict(color='green', dash='dash')
))

fig.add_trace(go.Scatter(
    x=strategy_returns['exit time'],
    y=drawdown,
    mode='lines',
    fill='tozeroy',
    name='Drawdown',
    line=dict(color='red'),
    fillcolor='rgba(255, 0, 0, 0.3)',
    yaxis='y2'
))

fig.update_layout(
    title=f"Alpha PnL Strategy from {strategy_returns['entry time'].min().date()} to {strategy_returns['exit time'].max().date()}",
    xaxis_title='Date',
    yaxis=dict(title='Returns', side='left'),
    yaxis2=dict(
        title='Drawdown',
        overlaying='y',
        side='right',
        showgrid=False,
        tickformat=".0%",
        range=[np.min(drawdown) * 1.1, 0]
    ),
    legend=dict(x=0.01, y=0.99),
    hovermode='x unified',
    margin=dict(l=60, r=60, t=60, b=60),
    height=600
)

metrics_text = (
    f"Compounded Returns: {compounded_returns:.2%}\n"
    f"Simple Returns: {simple_returns:.2%}\n"
    f"Max Drawdown: {max_drawdown:.2%}\n"
    f"Sharpe Ratio: {sharpe_ratio:.2f}\n"
    f"Win Rate: {win_rate:.2%}\n"
    f"Profit Factor: {profit_factor:.2f}"
)

fig.add_annotation(
    xref='paper', yref='paper',
    x=0.5, y=0.98,
    xanchor='center',
    showarrow=False,
    align='left',
    bgcolor='white',
    bordercolor='black',
    borderwidth=1,
    borderpad=4,
    text=metrics_text.replace('\n', '<br>'),
    font=dict(size=12, color='black', family='Arial Black')
)

fig.show()

# --- Métricas en consola ---
print(Fore.CYAN + "====== Strategy Performance Metrics ======")
print(Fore.YELLOW + metrics_text)
print(Fore.CYAN + "==========================================")
"""

"""
pnl = alpha.apply(np.sign)

pd.set_option("display.max_rows", None)
print((data.price).rolling(10).corr(data.buy_volume).head(50))
print(alpha.head(50))
print(pnl.head(50))
"""

"""
data['returns'] = data['price'].pct_change()

mean_diff = data['volume_diff'].mean()
std_diff = data['volume_diff'].std()
threshold = mean_diff + 3 * std_diff

data['signal'] = 0
data.loc[data['volume_diff'] > threshold, 'signal'] = 1
data.loc[data['volume_diff'] < -threshold, 'signal'] = -1


pd.set_option("display.max_rows", None)
print(data.head(1000))
"""



