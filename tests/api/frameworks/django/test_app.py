from datetime import datetime, timezone
from uuid import uuid4

from fastadmin.api.frameworks.django.app.api import JsonEncoder


async def test_json_provider():
    today = datetime.now(timezone.utc).date()
    now = datetime.now(timezone.utc)
    uuid = uuid4()
    assert JsonEncoder().default(today) == today.isoformat()
    assert JsonEncoder().default(now) == now.isoformat()
    assert JsonEncoder().default(uuid) == str(uuid)
