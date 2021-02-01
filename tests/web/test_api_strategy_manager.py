import asyncio
import pytest
from hypercorn import Config
from hypercorn.asyncio import serve
from quart import Quart

from manager.historic_manager import historic_manager
from manager.strategy_manager import strategy_managers
from strategies.moving_average_strategy import MovingAverageStrategy
from trading_client.trading_client import admin_trading_client
from web.api_strategy_manager import api_strategy_manager
from web.api_trading_client import api_trading_client
from logging_conf import log


@pytest.fixture
@pytest.mark.asyncio
async def setup_client():
    app = Quart(__name__)
    app.register_blueprint(api_trading_client)
    app.register_blueprint(api_strategy_manager)
    app.secret_key = "secret"
    return app.test_client()

@pytest.mark.asyncio
async def test_login( setup_client ):
    client = setup_client
    response = await client.get('/login/?username=11769869&password=TestTest123123')
    assert response.status_code == 200

    response = await client.get('/strategy_manager/register/?symbol=BITCOIN&strategy_type=moving_average')
    assert response.status_code == 200
    assert len(strategy_managers) == 1

