import asyncio
import unittest

import pytest

from conf.xtb_admin_account import xtb_admin_account_password, xtb_admin_account_id
from trading_client.trading_client import TradingClient, admin_trading_client

@pytest.fixture
@pytest.mark.asyncio
async def login():
    response = await admin_trading_client.login(xtb_admin_account_id, xtb_admin_account_password)
    assert response['status'] == True
    await asyncio.sleep( 1 )

@pytest.mark.asyncio
async def test_get_symbol( login ):
    response = await admin_trading_client.get_symbol( 'BITCOIN')
    print( response )
    assert response['symbol'] == 'BITCOIN'

@pytest.mark.asyncio
async def test_get_all_symbol(login ):
    response = await admin_trading_client.get_all_symbols( )
    assert 'symbol' in response[0].keys()
    for symbol_data in response:
        assert 'symbol' in symbol_data.keys()
        print ( symbol_data['symbol'] )