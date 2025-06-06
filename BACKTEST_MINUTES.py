import requests
import zipfile
import io
import pandas as pd
import numpy as np
import os
import datetime as dt
from colorama import init, Fore, Style
init()

min_data = pd.read_csv('SIGNALS_THRESHOLD_100.csv')
min_data.index = pd.to_datetime(min_data['timestamp'])
min_data = min_data.drop('timestamp', axis=1)
print(min_data)


def getReturns(position, time, hold, stop_loss, take_profit):
    print('TIME = ', time)

    entry_time = time + dt.timedelta(minutes=1)
    exit_time = time + dt.timedelta(minutes=hold)

    if entry_time not in min_data.index or exit_time not in min_data.index:
        return np.nan, None, None, None, None, None

    entry_time = min_data.loc[entry_time].name
    print("Entry Time = ", entry_time)
    entry_price = min_data['open'].loc[entry_time]
    print("Entry Price = ", entry_price)

    exit_time = min_data.loc[exit_time].name
    print("Exit Time = ", exit_time)
    exit_price = min_data['close'].loc[exit_time]
    print("Exit Price = ", exit_price)

    trade = min_data.loc[entry_time:exit_time]
    #print('POSITION TO OPEN = ', position)
    #print(trade)

    
    spread = 0.0003  # 0.03%
    fee = 0.002  # 0.2% total fee (open + close)
    slipagge = 0.0005 # 0.05%

    if position == -1:  # SHORT
        slippage_cost = entry_price * slipagge   
        print("SLIPPAGE COST = ", slippage_cost)
        entry_price = entry_price - slippage_cost
        entry_price = entry_price * (1 - spread)

        stop_loss_price = entry_price * (1 + stop_loss)
        take_profit_price = entry_price * (1 - take_profit)

        for i in trade.index:
            if trade.loc[i].high >= stop_loss_price:
                returns = pd.Series([stop_loss_price, entry_price]) 
                returns = round(returns.pct_change()[1], 4)
                print(Fore.LIGHTRED_EX +  "Stop Loss Triggered = " +  str(returns)  + Style.RESET_ALL)
                returns = returns - (returns * fee)
                return returns, entry_time, entry_price, i, stop_loss_price, signal

            if trade.loc[i].low <= take_profit_price:
                returns = pd.Series([take_profit_price, entry_price])
                returns = round(returns.pct_change()[1], 4)
                print(Fore.LIGHTGREEN_EX +  "Take Profit Triggered = " +  str(returns)  + Style.RESET_ALL)
                returns = returns - (returns * fee)
                return returns, entry_time, entry_price, i, take_profit_price, signal

        exit_price = exit_price * (1 + spread)
        returns = pd.Series([exit_price, entry_price])
        returns = round(returns.pct_change()[1], 4)
        returns = returns - (returns * fee)

        return returns, entry_time, entry_price, exit_time, exit_price, signal

    elif position == 1:  # LONG
        slippage_cost = entry_price * slipagge
        print("SLIPPAGE COST = ", slippage_cost)
        entry_price = entry_price + slippage_cost
        entry_price = entry_price * (1 + spread)
        

        stop_loss_price = entry_price * (1 - stop_loss)
        take_profit_price = entry_price * (1 + take_profit)

        for i in trade.index:
            if trade.loc[i].low <= stop_loss_price:
                returns = pd.Series([entry_price, stop_loss_price])
                returns = round(returns.pct_change()[1], 4)
                print(Fore.LIGHTRED_EX +  "Stop Loss Triggered = " +  str(returns)  + Style.RESET_ALL)
                returns = returns - (returns * fee)
                return returns, entry_time, entry_price, i, stop_loss_price, signal

            if trade.loc[i].high >= take_profit_price:
                returns = pd.Series([entry_price, take_profit_price])
                returns = round(returns.pct_change()[1], 4)
                print(Fore.LIGHTGREEN_EX +  "Take Profit Triggered = " +  str(returns)  + Style.RESET_ALL)
                returns = returns - (returns * fee)
                return returns, entry_time, entry_price, i, take_profit_price, signal

        exit_price = exit_price * (1 - spread)
        returns = pd.Series([entry_price, exit_price])
        returns = round(returns.pct_change()[1], 4)
        returns = returns - (returns * fee)

        return returns, entry_time, entry_price, exit_time, exit_price, signal
    
    """
    res = input("Continue ? ")
    if res == '':
        return
    """
        
        

    
    
    

strategy_returns  = pd.DataFrame(columns=['entry time', 'exit time', 'entry price', 'exit price', 'position', 'returns'])
exit_time = min_data.index[0]
print("Exit Time = ", exit_time)

hold = 14400 # HORAS - 10 DIAS
stop_loss = 0.01
take_profit = 0.05


for min in min_data.index:
    time = min_data.loc[min].name
    print("Time = ", time)
    signal = min_data['signals'].loc[min]
    print("Signal = ", signal)
    price = min_data['close'].loc[min]
    print("Price at the time = ", price)
    print('---------------------------------------')

    if pd.to_datetime(time) == dt.datetime(2023, 12 ,1): # STOP ITERATING AT THIS DATE
          break
    
    if exit_time is None:
            continue
    
    if pd.to_datetime(time) >= pd.to_datetime(exit_time):
          
        if signal == 1:
            returns, entry_time, entry_price, exit_time, exit_price, signal = getReturns(signal, time, hold, stop_loss, take_profit)
        
            print("EXIT TIME = ", exit_time)
            print("RETURNS = ", returns)
            strategy_returns.loc[len(strategy_returns)] = {
                "entry time": entry_time,
                "exit time": exit_time,
                "entry price": entry_price,
                "exit price" : exit_price,
                "position": signal,
                "returns": returns
            }
            print(strategy_returns)
            
            """
            res = input("Continue ?")
            if res == "":
                continue
            """
        
        if signal == -1:
            returns, entry_time, entry_price, exit_time, exit_price, signal = getReturns(signal, time, hold, stop_loss, take_profit)
        
            print("EXIT TIME = ", exit_time)
            print("RETURNS = ", returns)
            strategy_returns.loc[len(strategy_returns)] = {
                "entry time": entry_time,
                "exit time": exit_time,
                "entry price": entry_price,
                "exit price" : exit_price,
                "position": signal,
                "returns": returns
            }
            print(strategy_returns)

            """
            res = input("Continue ?")
            if res == "":
                continue
            """

import plotly.graph_objects as go

pd.set_option("display.max_rows", None)

strategy_returns['cumsum returns'] = strategy_returns['returns'].cumsum()
strategy_returns['cumulative returns'] = (1 + strategy_returns['returns']).cumprod()
print(strategy_returns)

strategy_returns['entry time'] = pd.to_datetime(strategy_returns['entry time'])
strategy_returns['exit time'] = pd.to_datetime(strategy_returns['exit time'])
strategy_returns = strategy_returns.sort_values('entry time').reset_index(drop=True)

compounded_returns = (1 + strategy_returns['returns']).prod() - 1
simple_returns = strategy_returns['returns'].sum()
cumulative_compounded = (1 + strategy_returns['returns']).cumprod()
cumulative_simple = strategy_returns['returns'].cumsum()

running_max = cumulative_compounded.cummax()
drawdown = (cumulative_compounded - running_max) / running_max
max_drawdown = drawdown.min()

avg_trade_days = (strategy_returns['exit time'] - strategy_returns['entry time']).dt.days.mean()
avg_trade_days = avg_trade_days if avg_trade_days > 0 else 1
daily_returns = strategy_returns['returns'] / avg_trade_days
annualized_return = (1 + compounded_returns) ** (252 / (avg_trade_days * len(strategy_returns))) - 1
annualized_volatility = daily_returns.std() * np.sqrt(252)
sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else np.nan

win_rate = (strategy_returns['returns'] > 0).mean()
gross_profit = strategy_returns.loc[strategy_returns['returns'] > 0, 'returns'].sum()
gross_loss = abs(strategy_returns.loc[strategy_returns['returns'] <= 0, 'returns'].sum())
profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.nan

cumulative_compounded = (1 + strategy_returns['returns']).cumprod() - 1 # MAKE SURE IT FITS THE PLOT FROM 0 RETURNS

# --- Crear figura interactiva ---

fig = go.Figure()

# Línea de Retornos Compuestos
fig.add_trace(go.Scatter(
    x=strategy_returns['exit time'],
    y=cumulative_compounded,
    mode='lines',
    name='Compounded Returns ($)',
    line=dict(color='blue')
))

# Línea de Retornos Simples acumulados
fig.add_trace(go.Scatter(
    x=strategy_returns['exit time'],
    y=cumulative_simple,
    mode='lines',
    name='Simple Returns (Cumsum)',
    line=dict(color='green', dash='dash')
))

# Área de Drawdown
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

# Layout con doble eje Y
fig.update_layout(
    title=f"Strategy Performance from {strategy_returns['entry time'].min().date()} to {strategy_returns['exit time'].max().date()}",
    xaxis_title='Date',
    yaxis=dict(
        title='Returns',
        side='left'
    ),
    yaxis2=dict(
        title='Drawdown',
        overlaying='y',
        side='right',
        showgrid=False,
        tickformat=".0%",
        range=[np.min(drawdown)*1.1, 0]

    ),
    legend=dict(x=0.01, y=0.99),
    hovermode='x unified',
    margin=dict(l=60, r=60, t=60, b=60),
    height=600
)

# Añadir cuadro con métricas como anotación en la gráfica
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
    x=0.5, y=0.98,  # Top center
    xanchor='center',
    showarrow=False,
    align='left',
    bgcolor='white',
    bordercolor='black',
    borderwidth=1,
    borderpad=4,
    text=metrics_text.replace('\n', '<br>'),  # Use <br> for line breaks in HTML
    font=dict(size=12, color='black', family='Arial Black')  # Strong black font
)



import plotly.io as pio
pio.renderers.default = "browser"



fig.show()

print("====== Strategy Performance Metrics ======")
print(metrics_text)
print("==========================================")
