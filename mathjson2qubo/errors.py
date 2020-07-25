class ParserError(Exception):
    def __init__(self, code: int = 0, message: str = "parser error") -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return "[ERROR: {}]: {}".format(self.code, self.message)


class ParserInitArgumentsError(ParserError):
    def __init__(self, code: int = 1000, message: str = "parser init arguments error."):
        super().__init__(code, message)


class MathJsonFormatError(ParserError):
    def __init__(self, code: int = 2000, message: str = "MathJson format error."):
        super().__init__(code, message)


class VariableAccessError(ParserError):
    def __init__(self, code: int = 3000, message: str = "variable acess error."):
        super().__init__(code, message)


class SumFunctionError(ParserError):
    def __init__(self, code: int = 4000, message: str = "sum function error."):
        super().__init__(code, message)


class CalculationError(ParserError):
    def __init__(self, code: int = 5000, message: str = "calculation error."):
        super().__init__(code, message)


class SubScriptError(ParserError):
    def __init__(self, code: int = 6000, message: str = "sub script error."):
        super().__init__(code, message)


class SuperScriptError(ParserError):
    def __init__(self, code: int = 7000, message: str = "super script error."):
        super().__init__(code, message)
