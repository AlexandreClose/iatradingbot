import asyncio

import quart.flask_patch
from unittest.mock import patch

import pytest

from conf.xtb_admin_account import xtb_admin_account_id, xtb_admin_account_password
from manager.strategy_manager import strategy_managers


@pytest.fixture
@pytest.mark.asyncio
async def setup_client( ):
    with patch('quart.current_app'):
        from web.create_app import create_app
        app = create_app()
        quart.current_app = app
        return app

@pytest.mark.asyncio
async def test_balance_manager( setup_client ):
    app = setup_client
    async with app.test_client() as client:
        response = await client.get('/login/?username='+xtb_admin_account_id+'&password='+xtb_admin_account_password)
        assert response.status_code == 200

        response = await client.get('/balance_manager/')
        assert response.status_code == 200

