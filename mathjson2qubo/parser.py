from functools import reduce
from typing import Callable, Dict, List, Union

from pyqubo import Array, Express, Sum

from mathjson2qubo.errors import (
    InvalidDivisionArgumentsError,
    InvalidEndIndexOfSumError,
    InvalidMathJsonFormatError,
    InvalidStartIndexOfSumError,
    InvalidSubScriptError,
    InvalidSubtractionArgumentsError,
    InvalidSumFuncError,
    InvalidSuperScriptError,
    NotFoundIndexVariableOfSumError,
    NotFoundVariableError,
    VariableIndexOutOfRangeError,
)

ComputableTerm = Union[float, Express]
Term = Union[float, List[int], Express]


class Parser:
    def __init__(self, variable, constants=[]):
        self.x = None
        variable_array = Array.create(
            variable["label"], variable["size"], variable["type"].upper()
        )
        exec("self.{} = variable_array".format(variable["label"]))
        for c in constants:
            exec("self.{} = c['values']".format(c["label"]))

    @property
    def funcs(self) -> Dict[str, Callable]:
        return dict(
            add=self._fn_add,
            multiply=self._fn_multiply,
            subtract=self._fn_subtract,
            divide=self._fn_divide,
            negate=self._fn_negate,
            list=self._fn_list,
        )

    def _fn_add(self, args: List[ComputableTerm]) -> ComputableTerm:
        return reduce(lambda x, y: x + y, args)

    def _fn_multiply(self, args: List[ComputableTerm]) -> ComputableTerm:
        return reduce(lambda x, y: x * y, args)

    def _fn_subtract(self, args: List[ComputableTerm]) -> ComputableTerm:
        if len(args) != 2:
            raise InvalidSubtractionArgumentsError()
        return args[0] - args[1]

    def _fn_divide(self, args: List[ComputableTerm]) -> ComputableTerm:
        if len(args) != 2:
            raise InvalidDivisionArgumentsError()
        try:
            return args[0] / args[1]
        except ZeroDivisionError:
            raise InvalidDivisionArgumentsError()

    def _fn_negate(self, args: List[ComputableTerm]) -> ComputableTerm:
        return reduce(lambda x, y: x + y, map(lambda x: -x, args))

    def _fn_list(self, args: List[ComputableTerm]) -> List[int]:
        return list(map(int, args))

    def _fn_sum(self, arg: dict, index: Dict[str, int] = None) -> Express:
        if "sub" not in arg or "sup" not in arg:
            raise InvalidSumFuncError()

        sub = arg["sub"]
        sup = arg["sup"]

        if sub["fn"] != "equal":
            raise InvalidStartIndexOfSumError()

        if "sym" not in sub["arg"][0]:
            raise NotFoundIndexVariableOfSumError()

        if len(sub["arg"]) != 2:
            raise InvalidStartIndexOfSumError()

        idx_sym: str = sub["arg"][0]["sym"]
        start_index = self.parse_mathjson(sub["arg"][1])
        end_index = self.parse_mathjson(sup)

        if not isinstance(start_index, float) or not float.is_integer(start_index):
            raise InvalidStartIndexOfSumError()

        if not isinstance(end_index, float) or not float.is_integer(end_index):
            raise InvalidEndIndexOfSumError()

        start_index = int(start_index) - 1
        end_index = int(end_index)

        return Sum(
            start_index,
            end_index,
            lambda i: self.parse_mathjson(
                arg["arg"][0],
                dict({idx_sym: i + 1}, **({} if index is None else index)),
            ),
        )

    def _sup(
        self, base: Term, arg: dict, index: Dict[str, int] = None
    ) -> ComputableTerm:
        if isinstance(base, list):
            raise InvalidSuperScriptError()
        superscript = self.parse_mathjson(arg["sup"], index)
        if isinstance(superscript, (Express, list)):
            raise InvalidSuperScriptError()
        return base ** superscript

    def _sub(self, arg: dict, index: Dict[str, int] = None) -> ComputableTerm:
        subscript = self.parse_mathjson(arg["sub"], index)
        if isinstance(subscript, list):
            subscript = tuple(map(lambda x: x - 1, subscript))
        elif isinstance(subscript, float):
            if not float.is_integer(subscript):
                raise InvalidSubScriptError()
            subscript = int(subscript) - 1
        else:
            raise InvalidSubScriptError()
        try:
            return eval("self.{}[{}]".format(arg["sym"], subscript))
        except AttributeError:
            raise NotFoundVariableError()
        except (TypeError, IndexError):
            raise VariableIndexOutOfRangeError()

    def parse_mathjson(self, arg: dict, index: Dict[str, int] = None) -> Term:
        result = None
        if "sym" in arg:
            if index is not None and arg["sym"] in index.keys():
                result = float(index[arg["sym"]])
            else:
                if "sub" in arg:
                    result = self._sub(arg, index)
                else:
                    result = eval("float(self.{})".format(arg["sym"]))
        elif "num" in arg:
            result = float(arg["num"])
        elif "fn" in arg:
            if arg["fn"] == "sum":
                return self._fn_sum(arg, index)
            else:
                parsed_args = list(
                    map(lambda a: self.parse_mathjson(a, index), arg["arg"])
                )
                result = self.funcs[arg["fn"]](parsed_args)

        if "sup" in arg:
            result = self._sup(result, arg)

        if result is None:
            raise InvalidMathJsonFormatError()

        return result
