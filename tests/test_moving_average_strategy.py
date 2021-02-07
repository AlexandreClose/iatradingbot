import asyncio
import pytest
from quart import Quart

from conf.xtb_admin_account import xtb_admin_account_id, xtb_admin_account_password
from manager.historic_manager import historic_manager
from strategies.moving_average_strategy import MovingAverageStrategy
from trading_client.trading_client import admin_trading_client

@pytest.fixture
@pytest.mark.asyncio
async def setup_session():
    app = Quart(__name__)
    app.secret_key = "secret"
    test_client = app.test_client()
    async with test_client.session_transaction() as local_session:
        local_session['trading_client']='admin'


@pytest.mark.asyncio
async def test_get_last_signal( setup_session ):

    symbol = 'BITCOIN'
    movingAverageStrategy= MovingAverageStrategy( symbol, 200, optimized=True)

    await admin_trading_client.login(xtb_admin_account_id, xtb_admin_account_password)
    await  historic_manager.register_symbol( symbol)
    await asyncio.sleep( 3 )
    signal = await movingAverageStrategy.compute_signal()
