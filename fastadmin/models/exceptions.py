class AdminModelException(Exception):
    detail: str | None

    def __init__(self, detail: str | None = None):
        self.detail = detail
