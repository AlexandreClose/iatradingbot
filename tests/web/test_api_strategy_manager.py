import json

import quart.flask_patch
from unittest.mock import patch

import pytest

from conf.xtb_admin_account import xtb_admin_account_id, xtb_admin_account_password
from manager.strategy_manager import strategy_managers


@pytest.fixture
@pytest.mark.asyncio
async def setup_client( ):
    from web.create_app import create_app
    app = create_app()
    quart.current_app = app
    return app

@pytest.mark.asyncio
async def test_register_strategy( setup_client ):
    app = setup_client
    async with app.test_client() as client:
        response = await client.get('/login/?username='+xtb_admin_account_id+'&password='+xtb_admin_account_password)
        assert response.status_code == 200

        response = await client.get('/strategy_manager/register/?symbol=BITCOIN&strategy_type=moving_average&n_currencies=4000')
        assert response.status_code == 200
        assert len(strategy_managers) == 1

@pytest.mark.asyncio
async def test_get_all_strategies( setup_client ):
    app = setup_client
    async with app.test_client() as client:
        response = await client.get('/login/?username='+xtb_admin_account_id+'&password='+xtb_admin_account_password)
        assert response.status_code == 200

        response = await client.get('/strategy_manager/register/?symbol=BITCOIN&strategy_type=moving_average&n_currencies=4000')
        assert response.status_code == 200
        assert len(strategy_managers) == 1

        response = await client.get('/strategy_manager/')
        assert response.status_code == 200
        result = await response.get_json()
        print( result)
        assert len(result) == 1

