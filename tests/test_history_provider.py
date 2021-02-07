import asyncio
import os
import json
import unittest

import pandas as pd
import pytest

from conf.xtb_admin_account import xtb_admin_account_password, xtb_admin_account_id
from manager.symbol_manager import symbol_manager
from manager.tick_manager import TickManager
from trading_client.trading_client import admin_trading_client
from manager.historic_manager import HistoricManager
import matplotlib.pyplot as plt

@pytest.fixture
@pytest.mark.asyncio
async def loginAndRegisterSymbol():
    await admin_trading_client.login(xtb_admin_account_id, xtb_admin_account_password,False)
    await symbol_manager.register_symbol( 'ETHEREUM')

@pytest.mark.asyncio
async def test_plot_history( loginAndRegisterSymbol ):
    await HistoricManager.instance().plot_history( 'ETHEREUM')

@pytest.mark.asyncio
async def test_compare_history_tick_price( loginAndRegisterSymbol ):

    if not os.path.isfile('last_minutes_tick_history_comparison/last_minutes_history.json') or not os.path.isfile('last_minutes_tick_history_comparison/last_minutes_tick_prices.json'):
        await  asyncio.sleep( 650 )
        last_minutes_history = await HistoricManager.instance().fetch_time_delta_history( 'BITCOIN', 10)
        last_minutes_tick_prices = await TickManager.instance().get_tick_prices_time_delta( 'BITCOIN', 10 )

        with open('last_minutes_tick_history_comparison/last_minutes_history.json', 'w') as fp:
            json.dump(last_minutes_history, fp)

        with open('last_minutes_tick_history_comparison/last_minutes_tick_prices.json', 'w') as fp:
            json.dump(last_minutes_tick_prices, fp)

    else:
        with open('last_minutes_tick_history_comparison/last_minutes_history.json') as f:
            last_minutes_history = json.load(f)
        with open('last_minutes_tick_history_comparison/last_minutes_tick_prices.json') as f:
            last_minutes_tick_prices = json.load(f)

    last_minutes_history = pd.DataFrame(last_minutes_history)
    last_minutes_history.set_index('Date', inplace = True)


    last_minutes_tick_prices = pd.DataFrame(list(last_minutes_tick_prices.values()))
    last_minutes_tick_prices.set_index('timestamp', inplace = True)

    ax = last_minutes_history.plot( y='Open')
    last_minutes_tick_prices.plot( y='bid', ax=ax)
    plt.show()
