import quart.flask_patch
from unittest.mock import patch

import pytest

from conf.xtb_admin_account import xtb_admin_account_id, xtb_admin_account_password
from logging_conf import log


@pytest.fixture
@pytest.mark.asyncio
async def setup_client( ):
    from web.create_app import create_app
    app = create_app()
    return app

@pytest.mark.asyncio
async def test_login( setup_client ):
    app = setup_client
    async with app.test_client() as client:
        response = await client.get('/login/?username='+xtb_admin_account_id+'&password='+xtb_admin_account_password)
        assert response.status_code == 200