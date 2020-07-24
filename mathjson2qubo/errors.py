class ParserError(Exception):
    def __init__(self, code: int = 0, message: str = "") -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return "[ERROR: {}]: {}".format(self.code, self.message)


class ParserInitArgumentsError(ParserError):
    pass


class NotFoundVariableError(ParserError):
    pass


class VariableIndexOutOfRangeError(ParserError):
    pass


class InvalidMathJsonFormatError(ParserError):
    pass


class InvalidSubScriptError(ParserError):
    pass


class InvalidSuperScriptError(ParserError):
    pass


class InvalidSumFuncError(ParserError):
    pass


class NotFoundIndexVariableOfSumError(ParserError):
    pass


class InvalidStartIndexOfSumError(ParserError):
    pass


class InvalidEndIndexOfSumError(ParserError):
    pass


class InvalidSubtractionArgumentsError(ParserError):
    pass


class InvalidDivisionArgumentsError(ParserError):
    pass


class UndefinedVariableTypeError(ParserError):
    pass
