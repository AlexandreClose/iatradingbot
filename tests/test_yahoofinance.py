import asyncio
import unittest

import pytest

from logging_conf import log
from historicprovider.yahoo_historic_provider import YahooHistoricProvider, yahoo_historic_provider

@pytest.mark.asyncio
async def test_send_max_history( ):
    yahoo_finance = yahoo_historic_provider
    datas = await yahoo_finance.fetch_max_history( 'DASH')
    log.info( '[YAHOO] : Fetch %s historic data',len(datas))
    assert len(datas) > 0