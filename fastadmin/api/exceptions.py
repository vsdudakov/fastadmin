class AdminApiException(Exception):
    """API exception with HTTP status code and detail message."""

    def __init__(self, status_code: int, detail: str | None = None):
        super().__init__(detail or "")
        self.status_code = status_code
        self.detail = detail
