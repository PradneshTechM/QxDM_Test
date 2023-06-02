from enum import IntEnum

class QConnectException(Exception):
    class Codes(IntEnum):
        QUTS = 101
        QCAT = 102

    def __init__(self, code: Codes, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{repr(self.code)} {self.message}"