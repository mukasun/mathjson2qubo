from functools import reduce
from typing import Callable, Dict, List, TypedDict, Union, cast

import numpy as np
import pyqubo
from pyqubo import Array, Constraint, Express, Placeholder, Sum, solve_ising, solve_qubo
from pyqubo.core.express import Binary, Spin

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
    ParserInitArgumentsError,
    UndefinedVariableTypeError,
    VariableIndexOutOfRangeError,
)

from .model import Model

ComputableTerm = Union[float, Express]
Term = Union[float, List[int], Express]


class Variable(TypedDict):
    symbol: str
    dimension: int
    size: Union[int, tuple]


class Constant(TypedDict):
    symbol: str
    values: Union[int, float, list]


class ObjectiveTerm(TypedDict):
    label: str
    tex: dict
    weight: float


class ConstraintTerm(TypedDict):
    label: str
    tex: dict
    weight: float


class Parser:
    def __init__(
        self, vartype: str, variables: List[Variable], constants: List[Constant] = []
    ):
        # set variable type
        self.vartype: str = vartype.upper()
        self.x = np.array([[]])  # for test
        if self.vartype not in ["SPIN", "BINARY"]:
            raise ParserInitArgumentsError(
                code=1001, message="vartype must be 'spin' or 'binary'."
            )

        # set variables
        for variable in variables:
            if len(variable["symbol"]) != 1:
                raise ParserInitArgumentsError(
                    code=1002, message="variable symbol must be one character."
                )

            if variable["dimension"] > 0:
                var = Array.create(variable["symbol"], variable["size"], self.vartype)
            elif variable["dimension"] == 0:
                if self.vartype == "SPIN":
                    var = Spin(variable["symbol"])
                else:
                    var = Binary(variable["symbol"])
            else:
                raise ParserInitArgumentsError(
                    code=1003, message="variable dimension must be positive integer."
                )
            exec("self.{} = var".format(variable["symbol"]))

        # set constants
        for constant in constants:
            if isinstance(constant["values"], (int, float)):
                const = float(constant["values"])
            elif isinstance(constant["values"], list):
                const = np.array(constant["values"])
            exec("self.{} = const".format(constant["symbol"]))

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
        return base ** int(superscript)

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

    def parse_to_pyqubo_model(
        self,
        objectives: List[ObjectiveTerm] = [],
        constraints: List[ConstraintTerm] = [],
    ) -> pyqubo.Model:
        parsed_objectives = [
            Placeholder(o["label"]) * self.parse_mathjson(o["tex"]) for o in objectives
        ]
        parsed_constraints = [
            Placeholder(c["label"])
            * Constraint(self.parse_mathjson(c["tex"]), label=c["label"])
            for c in constraints
        ]
        H = cast(Express, sum(parsed_objectives) + sum(parsed_constraints))
        pyqubo_model = H.compile()
        return pyqubo_model

    def solve(
        self,
        objectives: List[ObjectiveTerm] = [],
        constraints: List[ConstraintTerm] = [],
        num_reads=10,
        sweeps=1000,
        beta_range=(1, 50),
    ):
        pyqubo_model = self.parse_to_pyqubo_model(objectives, constraints)
        feed_dict = {}
        feed_dict.update({o["label"]: o["weight"] for o in objectives})
        feed_dict.update({c["label"]: c["weight"] for c in constraints})

        if self.vartype == "SPIN":
            linear, quad, offset = pyqubo_model.to_ising(feed_dict=feed_dict)
            solution = solve_ising(
                linear, quad, num_reads=num_reads, sweeps=sweeps, beta_range=beta_range
            )
        elif self.vartype == "BINARY":
            model, offset = pyqubo_model.to_qubo(feed_dict=feed_dict)
            solution = solve_qubo(
                model, num_reads=num_reads, sweeps=sweeps, beta_range=beta_range
            )
        else:
            raise UndefinedVariableTypeError()

        return pyqubo_model.decode_solution(
            solution, vartype=self.vartype, feed_dict=feed_dict
        )

    def to_matrix(
        self,
        objectives: List[ObjectiveTerm] = [],
        constraints: List[ConstraintTerm] = [],
    ):
        pyqubo_model = self.parse_to_pyqubo_model(objectives, constraints)
        feed_dict = {}
        feed_dict.update({o["label"]: o["weight"] for o in objectives})
        feed_dict.update({c["label"]: c["weight"] for c in constraints})

        if self.vartype == "SPIN":
            model = pyqubo_model.to_ising(feed_dict=feed_dict)
        elif self.vartype == "BINARY":
            model = pyqubo_model.to_qubo(feed_dict=feed_dict)
        else:
            raise UndefinedVariableTypeError()

        return Model.make_model_from_tuple(model)
