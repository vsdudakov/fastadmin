class AdminApiException(Exception):
    status_code: int
    detail: str | None

    def __init__(self, status_code: int, detail: str | None = None):
        self.status_code = status_code
        self.detail = detail
