from functools import reduce
from typing import Dict, List, cast

from pyqubo import Array, Express

from mathjson2qubo.parser_exeptions import (
    NotFoundVariableError,
    VariableIndexOutOfRangeError,
)


class Parser:
    @property
    def funcs(self):
        return dict(
            add=self._fn_add,
            multiply=self._fn_multiply,
            negate=self._fn_negate,
            list=self._fn_list,
        )

    def _fn_add(self, args: list) -> float:
        return reduce(lambda x, y: x + y, args)

    def _fn_multiply(self, args: list) -> float:
        return reduce(lambda x, y: x * y, args)

    def _fn_negate(self, args: list) -> float:
        return reduce(lambda x, y: x + y, map(lambda x: -x, args))

    def _fn_list(self, args: list) -> list:
        return list(map(int, args))

    def _sub_access(self, arg: dict) -> Express:
        """Access the indexed variables.

        Args:
            arg (dict): The example of `x_{1,2}` is {"sym":"x","sub":{"fn":"list","arg":[{"num":"1"},{"num":"2"}]}}

        Returns:
            Express: The evaluation result as pyqubo.core.Express
        """
        try:
            index = self.parse(arg["sub"])
            if isinstance(index, list):
                index = tuple(map(lambda x: x - 1, index))
            else:
                index = int(index) - 1
            return eval("self.{}[{}]".format(arg["sym"], index))
        except AttributeError:
            raise NotFoundVariableError()
        except (TypeError, IndexError):
            raise VariableIndexOutOfRangeError()

    def __init__(self, variable, constants=[]):
        self.x = None
        self.q = None
        self._generateVariables(variable)

    def _generateVariables(self, variable: dict):
        variable_array = Array.create(
            variable["label"], variable["size"], variable["type"].upper()
        )
        exec("self.{} = variable_array".format(variable["label"]))

    def tex2pyqubo(self, objective_terms: List[Dict], constraint_terms: List[Dict]):
        objectives = sum(list(map(lambda obj: self.parse(obj), objective_terms)))
        constraints = sum(list(map(lambda const: self.parse(const), constraint_terms)))
        Q = cast(Express, objectives + constraints)
        model = Q.compile()
        qubo, offset = model.to_qubo()
        return qubo

    def parse(self, arg: dict):
        if "sym" in arg:
            if "sub" in arg:
                return eval("self.{}[{}]".format(arg["sym"], self.parse(arg["sub"])))
            else:
                return eval("self.{}".format(arg["sym"]))
        elif "num" in arg:
            return float(arg["num"])
        elif "fn" in arg:
            parsed_args = list(map(lambda a: self.parse(a), arg["arg"]))
            return self.funcs[arg["fn"]](parsed_args)
