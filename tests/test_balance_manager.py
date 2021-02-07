import asyncio
import pytest

from conf.xtb_admin_account import xtb_admin_account_id, xtb_admin_account_password
from manager.balance_manager import admin_balance_manager
from trading_client.trading_client import admin_trading_client


@pytest.fixture
@pytest.mark.asyncio
async def login():
    await admin_trading_client.login(xtb_admin_account_id, xtb_admin_account_password)
    await asyncio.sleep( 1 )


@pytest.mark.asyncio
async def test_get_last_balance(login):
    last_balance = await admin_balance_manager.get_last_balance()
    assert 'balance' in last_balance