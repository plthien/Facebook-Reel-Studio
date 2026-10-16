import os

import pytest

from app.config import Settings
from app.integrations.meta.adapter import MetaAdapter
from app.integrations.meta.client import MetaClient


@pytest.mark.live_meta
def test_live_authorized_page_discovery():
    if os.environ.get("RUN_META_READ_TESTS") != "1":
        pytest.skip("Live Meta read testing requires explicit opt-in")
    config = Settings.from_env()
    if not config.user_token:
        pytest.skip("No user token")
    client = MetaClient(config.graph_version)
    try:
        pages = MetaAdapter(client).pages(config.user_token)
        assert isinstance(pages, list)
    finally:
        client.close()

