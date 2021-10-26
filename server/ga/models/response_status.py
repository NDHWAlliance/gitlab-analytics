class CodeAndMessage:
    def __init__(self, code, message):
        self.code = code
        self.message = message


class ResponseStatus:
    OK = CodeAndMessage(0, "OK")
    ERROR = CodeAndMessage(1, "Error")
