from datetime import date, datetime
from uuid import uuid4

from fastadmin.api.frameworks.django.app.api import JsonEncoder


async def test_json_provider():
    today = date.today()
    now = datetime.now()
    uuid = uuid4()
    assert JsonEncoder().default(today) == today.isoformat()
    assert JsonEncoder().default(now) == now.isoformat()
    assert JsonEncoder().default(uuid) == str(uuid)
