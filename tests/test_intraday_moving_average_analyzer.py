import asyncio
import unittest

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from analyzer.moving_average_analyzer import MovingAverageAnalyzer
from conf.xtb_admin_account import xtb_admin_account_password, xtb_admin_account_id
from manager.historic_manager import historic_manager
from logging_conf import log
from trading_client.trading_client import admin_trading_client

symbol = 'BITCOIN'
movingAverageAnalyzer= MovingAverageAnalyzer( symbol, 'ema', 3, 20,0.05,0.05,'intraday')

@pytest.fixture
@pytest.mark.asyncio
async def loginAndRegisterSymbol():
    await admin_trading_client.login(xtb_admin_account_id, xtb_admin_account_password, False)
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
    df=await movingAverageAnalyzer.compute_trading_signal_now( )

@pytest.mark.asyncio
async def test_compute_trading_signal(loginAndRegisterSymbol):
    df=await movingAverageAnalyzer.compute_trading_signals()
    log.info( '[TRADING POSITIONS] : %s positions taken', len(df))

@pytest.mark.asyncio
async def test_compute_trading_signal_last(loginAndRegisterSymbol):
    df=await movingAverageAnalyzer.compute_trading_signals( )
    log.info( '[TRADING POSITION] : last ')
    print( df )

@pytest.mark.asyncio
async def test_plot_trading_positions(loginAndRegisterSymbol):
    ema=await movingAverageAnalyzer.compute_exponential_moving_average( )
    trading_positions,df=await movingAverageAnalyzer.compute_trading_signals()
    log.info( '[TRADING POSITIONS] : %s positions taken', len(trading_positions))
    ax = ema.plot(y= 'lma_Close', color="C1")
    ema.plot(y='sma_Close', color='C2',ax=ax)
    trading_positions['color_trading']=np.where(trading_positions['cross_sign_sma_Close_lma_Close']>0, 'green', 'red')
    print( trading_positions )
    plt.scatter(trading_positions.index, trading_positions['sma_Close'],c=trading_positions['color_trading'])
    ax.set_xlim(pd.Timestamp('2021-01-24'), pd.Timestamp('2021-01-25'))
    plt.ylim(30000, 40000)
    plt.show( )

@pytest.mark.asyncio
async def test_optimize (loginAndRegisterSymbol):
    await movingAverageAnalyzer.optimize( )

if __name__ == '__main__':
    unittest.main()
