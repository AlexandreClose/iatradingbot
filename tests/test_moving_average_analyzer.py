import asyncio
import unittest

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from conf.xtb_admin_account import xtb_admin_account_password
from conf.xtb_admin_account import xtb_admin_account_id
from manager.historic_manager import historic_manager
from logging_conf import log
from trading_client.trading_client import admin_trading_client
import matplotlib.dates as mdates

symbol = 'BITCOIN'
movingAverageAnalyzer= MovingAverageAnalyzer( symbol, 'ema', 3, 20 ,3.0, 0.01)

@pytest.fixture
@pytest.mark.asyncio
async def loginAndRegisterSymbol():
    await admin_trading_client.login(xtb_admin_account_id,  xtb_admin_account_password, False)
    await historic_manager.register_symbol( symbol)

@pytest.mark.asyncio
async def test_plot_history_dataframe(loginAndRegisterSymbol):
    ema=await movingAverageAnalyzer.compute_exponential_moving_average( )
    ax = ema.plot(y= 'lma_Close', color="C1")
    ema.plot(y='sma_Close', color='C2', ax = ax)
    plt.show()

@pytest.mark.asyncio
async def test_compute_exponential_moving_average_last(loginAndRegisterSymbol):
    df=await movingAverageAnalyzer.compute_exponential_moving_average( )
    log.info( '[EMA] : Last computation')
    print ( df )
    log.info( '[EMA] : Size last computation : %s', len(df))

@pytest.mark.asyncio
async def test_compute_trading_signal_now(loginAndRegisterSymbol):
    signal =await movingAverageAnalyzer.compute_trading_signal_now( )
    print( signal )

@pytest.mark.asyncio
async def test_compute_trading_signal(loginAndRegisterSymbol):
    df=await movingAverageAnalyzer.compute_trading_signals()
    log.info( '[TRADING POSITIONS] : %s positions taken', len(df))
    print(df)

@pytest.mark.asyncio
async def test_plot_trading_positions(loginAndRegisterSymbol):
    ema=await movingAverageAnalyzer.compute_exponential_moving_average( )
    trading_positions,df=await movingAverageAnalyzer.compute_trading_signals()
    log.info( '[TRADING POSITIONS] : %s positions taken', len(trading_positions))
    ax=ema.plot(y='Close', color='C1')
    trading_positions['color_trading']=np.where(trading_positions['cross_sign_sma_Close_lma_Close']>0, 'green', 'red')
    plt.scatter(trading_positions.index, trading_positions['sma_Close'],c=trading_positions['color_trading'])
    ax.set_xlim(pd.Timestamp('2017-01-01'), pd.Timestamp('2019-01-01'))
    plt.tight_layout()
    plt.show( )

@pytest.mark.asyncio
async def test_plot_trading_positions_doc(loginAndRegisterSymbol):
    start_date = '2015-01-01'
    end_date = '2016-12-31'
    my_year_month_fmt = mdates.DateFormatter('%m/%y')
    ema=await movingAverageAnalyzer.compute_exponential_moving_average( )
    trading_positions,df=await movingAverageAnalyzer.compute_trading_signals()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16,9))

    ax1.plot(ema.loc[start_date:end_date, :].index, ema.loc[start_date:end_date, 'Close'], label = 'EMA')

    ax1.set_ylabel('$')
    ax1.legend(loc='best')
    # ax1.xaxis.set_major_formatter(my_year_month_fmt)

    ax2.plot(df.loc[start_date:end_date, :].index, df.loc[start_date:end_date, 'trading_positions'],
             label='Trading position')

    ax2.set_ylabel('Trading position')
    ax2.xaxis.set_major_formatter(my_year_month_fmt)
    plt.show()

@pytest.mark.asyncio
async def test_compute_profit(loginAndRegisterSymbol ):
    df,profit, df_signals = await movingAverageAnalyzer.compute_profit()

@pytest.mark.asyncio
async def test_compute_profit_doc(loginAndRegisterSymbol ):
    my_year_month_fmt = mdates.DateFormatter('%m/%y')

    df_profit,profit,trading_signals =  await movingAverageAnalyzer.compute_profit()
    cum_strategy_asset_relative_returns=df_profit['cumsum_relative_log_return']
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16,9))

    ax1.plot(df_profit.index, cum_strategy_asset_relative_returns, label='MSFT')

    ax1.set_ylabel('Cumulative log-returns')
    ax1.legend(loc='best')
    ax1.xaxis.set_major_formatter(my_year_month_fmt)
    plt.show()

@pytest.mark.asyncio
async def test_optimize (loginAndRegisterSymbol):
    await movingAverageAnalyzer.optimize( )

if __name__ == '__main__':
    unittest.main()
