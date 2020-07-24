class ParserError(Exception):
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
