from functools import reduce
from typing import Callable, Dict, List, Union

from pyqubo import Array, Express

from mathjson2qubo.errors import (
    InvalidMathJsonFormatError,
    InvalidSubScriptError,
    InvalidSuperScriptError,
    NotFoundVariableError,
    VariableIndexOutOfRangeError,
)

ComputableTerm = Union[float, Express]
Term = Union[float, List[int], Express]


class Parser:
    @property
    def funcs(self) -> Dict[str, Callable]:
        return dict(
            add=self._fn_add,
            multiply=self._fn_multiply,
            negate=self._fn_negate,
            list=self._fn_list,
        )

    def _fn_add(self, args: List[ComputableTerm]) -> ComputableTerm:
        return reduce(lambda x, y: x + y, args)

    def _fn_multiply(self, args: List[ComputableTerm]) -> ComputableTerm:
        return reduce(lambda x, y: x * y, args)

    def _fn_negate(self, args: List[ComputableTerm]) -> ComputableTerm:
        return reduce(lambda x, y: x + y, map(lambda x: -x, args))

    def _fn_list(self, args: List[ComputableTerm]) -> List[int]:
        return list(map(int, args))

    def _sup(self, base: Term, arg: dict) -> ComputableTerm:
        if isinstance(base, list):
            raise InvalidSuperScriptError()
        superscript = self.parse_mathjson(arg["sup"])
        if isinstance(superscript, (Express, list)):
            raise InvalidSuperScriptError()
        return pow(base, superscript)

    def _sub(self, arg: dict) -> ComputableTerm:
        subscript = self.parse_mathjson(arg["sub"])
        if isinstance(subscript, list):
            subscript = tuple(map(lambda x: x - 1, subscript))
        elif isinstance(subscript, float):
            subscript = int(subscript) - 1
        else:
            raise InvalidSubScriptError()
        try:
            return eval("self.{}[{}]".format(arg["sym"], subscript))
        except AttributeError:
            raise NotFoundVariableError()
        except (TypeError, IndexError):
            raise VariableIndexOutOfRangeError()

    def __init__(self, variable, constants=[]):
        self.x = None
        self.q = None
        variable_array = Array.create(
            variable["label"], variable["size"], variable["type"].upper()
        )
        exec("self.{} = variable_array".format(variable["label"]))

    # def tex2pyqubo(self, objective_terms: List[Dict], constraint_terms: List[Dict]):
    #     objectives = sum(list(map(lambda obj: self.parse_mathjson(obj), objective_terms)))
    #     constraints = sum(
    #         list(map(lambda const: self.parse_mathjson(const), constraint_terms))
    #     )
    #     Q = cast(Express, objectives + constraints)
    #     model = Q.compile()
    #     qubo, offset = model.to_qubo()
    #     return qubo

    def parse_mathjson(self, arg: dict) -> Term:
        result = None
        if "sym" in arg:
            if "sub" in arg:
                result = self._sub(arg)
            else:
                result = eval("self.{}".format(arg["sym"]))
        elif "num" in arg:
            result = float(arg["num"])
        elif "fn" in arg:
            parsed_args = list(map(lambda a: self.parse_mathjson(a), arg["arg"]))
            result = self.funcs[arg["fn"]](parsed_args)

        if "sup" in arg:
            result = self._sup(result, arg)

        if result is None:
            raise InvalidMathJsonFormatError()

        return result
