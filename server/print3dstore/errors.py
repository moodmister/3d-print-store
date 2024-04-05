from flask import make_response

class RequestException(Exception):
    def __init__(self, message, http_code) -> None:
        super().__init__(message)
        self.http_code = http_code
