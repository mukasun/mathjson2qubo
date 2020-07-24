import random

import numpy as np
from expects import expect, raise_error
from expects.matchers.built_in.equal import equal
from mamba import before, context, description, it
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
from mathjson2qubo.parser import Parser
from pyqubo import Sum

with description("Parser") as self:
    with before.each:
        self.parser = Parser(
            {"type": "binary", "dimension": 1, "size": 4, "label": "x"}
        )

    with description("_fn_add()"):
        with it("return convorutional sum"):
            args = [1.0, 2.0, 3.0]
            expect(self.parser._fn_add(args)).to(equal(1.0 + 2.0 + 3.0))

    with description("_fn_subtract"):
        with context("call w/ not 2 elements argument"):
            with it("raise InvalidSubtractionArgumentsError"):
                args = [1.0]
                expect(lambda: self.parser._fn_subtract(args)).to(
                    raise_error(InvalidSubtractionArgumentsError)
                )
                args = [1.0, 2.0, 3.0]
                expect(lambda: self.parser._fn_subtract(args)).to(
                    raise_error(InvalidSubtractionArgumentsError)
                )

        with context("call w/ 2 elements argument"):
            with it("return subtract the second from the first"):
                args = [1.0, 2.0]
                expect(self.parser._fn_subtract(args)).to(equal(1.0 - 2.0))

    with description("_fn_multiply()"):
        with it("return convorutional product"):
            args = [4.0, 5.0, 6.0]
            expect(self.parser._fn_multiply(args)).to(equal(4.0 * 5.0 * 6.0))

    with description("_fn_divide"):
        with context("call w/ not 2 elements argument"):
            with it("raise InvalidDivisionArgumentsError"):
                args = [1.0]
                expect(lambda: self.parser._fn_divide(args)).to(
                    raise_error(InvalidDivisionArgumentsError)
                )
                args = [1.0, 2.0, 3.0]
                expect(lambda: self.parser._fn_divide(args)).to(
                    raise_error(InvalidDivisionArgumentsError)
                )

        with context("call w/ 2 elements argument"):
            with it("return the firstr divided by the second"):
                args = [1.0, 2.0]
                expect(self.parser._fn_divide(args)).to(equal(1.0 / 2.0))

        with context("call w/ zero division"):
            with it("raise InvalidDivisionArgumentsError"):
                args = [1.0, 0]
                expect(lambda: self.parser._fn_divide(args)).to(
                    raise_error(InvalidDivisionArgumentsError)
                )

    with description("_fn_negate()"):
        with it("return negated value"):
            args = [1.0]
            expect(self.parser._fn_negate(args)).to(equal(-args[0]))

    with description("_fn_list()"):
        with it("return int list"):
            args = [1.0, 2.0, 3.0]
            expect(self.parser._fn_list(args)).to(equal(list(map(int, args))))

    with description("_fn_sum()"):
        with before.each:
            self.size = 4
            self.constant_values = [1, 2, 3, 4]
            self.parser = Parser(
                {"type": "binary", "dimension": 1, "size": self.size, "label": "x",},
                [
                    {"label": "N", "values": self.size},
                    {"label": "n", "values": self.constant_values},
                ],
            )

        with context("call w/o sub or sup"):
            with it("raise InvalidSumFuncError"):
                sum_arg_wo_sub = {
                    "fn": "sum",
                    "sup": {"sym": "N"},
                }
                sum_arg_wo_sup = {
                    "fn": "sum",
                    "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                }
                expect(lambda: self.parser._fn_sum(sum_arg_wo_sub)).to(
                    raise_error(InvalidSumFuncError)
                )
                expect(lambda: self.parser._fn_sum(sum_arg_wo_sup)).to(
                    raise_error(InvalidSumFuncError)
                )

        with context("call w/o index variable"):
            with it("raise NotFoundIndexVariableOfSumError"):
                sum_arg = {
                    "fn": "sum",
                    "sup": {"sym": "N"},
                    "sub": {"fn": "equal", "arg": [{"num": 1}]},
                }
                expect(lambda: self.parser._fn_sum(sum_arg)).to(
                    raise_error(NotFoundIndexVariableOfSumError)
                )

        with context("call w/ invalid start index"):
            with context("subscript is not equal"):
                with it("raise InvalidStartIndexOfSumError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"sym": "N"},
                        "sub": {"fn": "elementof", "arg": [{"sym": "i"}, {"num": "G"}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(InvalidStartIndexOfSumError)
                    )

            with context("equal of subscript is invalid"):
                with it("raise InvalidStartIndexOfSumError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"sym": "N"},
                        "sub": {
                            "fn": "equal",
                            "arg": [{"sym": "i"}, {"sym": "j"}, {"num": 1}],
                        },
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(InvalidStartIndexOfSumError)
                    )

            with context("start index is float"):
                with it("raise InvalidStartIndexOfSumError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"num": 5},
                        "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1.5}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(InvalidStartIndexOfSumError)
                    )

            with context("start index is Express"):
                with it("raise InvalidStartIndexOfSumError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"num": 5},
                        "sub": {
                            "fn": "equal",
                            "arg": [{"sym": "i"}, {"sym": "x", "sub": {"num": 1}}],
                        },
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(InvalidStartIndexOfSumError)
                    )

        with context("call w/ invalid end index"):
            with context("end index is float"):
                with it("raise InvalidEndIndexOfSumError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"num": 1.5},
                        "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(InvalidEndIndexOfSumError)
                    )

            with context("end index is Express"):
                with it("raise InvalidEndIndexOfSumError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"sym": "x", "sub": {"num": 1}},
                        "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(InvalidEndIndexOfSumError)
                    )

        with context("call w/ valid args (linear variable)"):
            with it("return the calcuration result"):
                sum_valid_args = {
                    "fn": "sum",
                    "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                    "sup": {"sym": "N"},
                    "arg": [
                        {
                            "fn": "multiply",
                            "arg": [
                                {"sym": "n", "sub": {"sym": "i"}},
                                {"sym": "x", "sub": {"sym": "i"}},
                            ],
                        }
                    ],
                }
                expect(self.parser._fn_sum(sum_valid_args)).to(
                    equal(
                        Sum(
                            0,
                            self.size,
                            lambda i: self.constant_values[i] * self.parser.x[i],
                        )
                    )
                )

        with context("call w/ valid args (quadratic variable)"):
            with before.each:
                self.size = 3
                self.constants = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
                self.parser = Parser(
                    {
                        "type": "binary",
                        "dimension": 2,
                        "size": [self.size, self.size],
                        "label": "x",
                    },
                    [
                        {"label": "N", "values": self.size},
                        {"label": "n", "values": self.constants},
                    ],
                )

            with it("return the calcuration result"):
                sum_valid_args = {
                    "fn": "sum",
                    "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                    "sup": {"sym": "N"},
                    "arg": [
                        {
                            "fn": "sum",
                            "sub": {"fn": "equal", "arg": [{"sym": "j"}, {"num": 1}]},
                            "sup": {"sym": "N"},
                            "arg": [
                                {
                                    "fn": "multiply",
                                    "arg": [
                                        {
                                            "sym": "n",
                                            "sub": {
                                                "fn": "list",
                                                "arg": [{"sym": "i"}, {"sym": "j"}],
                                            },
                                        },
                                        {
                                            "sym": "x",
                                            "sub": {
                                                "fn": "list",
                                                "arg": [{"sym": "i"}, {"sym": "j"}],
                                            },
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                }
                expect(self.parser._fn_sum(sum_valid_args)).to(
                    equal(
                        Sum(
                            0,
                            self.size,
                            lambda i: Sum(
                                0,
                                self.size,
                                lambda j: self.constants[i][j] * self.parser.x[i][j],
                            ),
                        )
                    )
                )

    with description("_sup()"):
        with context("call w/ valid args"):
            with it("return the calcuration result"):
                arg = {
                    "num": 2,
                    "sup": {"num": 2},
                }
                expect(self.parser._sup(2, arg)).to(equal(2 ** 2))

        with context("base is list"):
            with it("raise InvalidSuperScriptError"):
                expect(lambda: self.parser._sup([1, 2], {"sub": {"num": 2}})).to(
                    raise_error(InvalidSuperScriptError)
                )

        with context("sup is list"):
            with it("raise InvalidSuperScriptError"):
                arg = {
                    "num": 2,
                    "sup": {"fn": "list", "arg": [{"num": 1}, {"num": 2}]},
                }
                expect(lambda: self.parser._sup(2.0, arg)).to(
                    raise_error(InvalidSuperScriptError)
                )

        with context("sup is Express"):
            with it("raise InvalidSuperScriptError"):
                arg = {"num": 2, "sup": {"sym": "x", "sub": {"num": 1}}}
                expect(lambda: self.parser._sup(2.0, arg)).to(
                    raise_error(InvalidSuperScriptError)
                )

    with description("_sub()"):
        with context("variable is linear"):
            with before.each:
                self.variable_label = "x"
                self.variable_size = 4
                self.parser = Parser(
                    {
                        "type": "binary",
                        "dimension": 1,
                        "size": self.variable_size,
                        "label": self.variable_label,
                    }
                )

            with context("call with the collect args"):
                with it("return the value of the specified indexed variable"):
                    index = random.randint(1, self.variable_size)
                    arg = {"sym": self.variable_label, "sub": {"num": index}}
                    expect(self.parser._sub(arg)).to(equal(self.parser.x[index - 1]))

            with context("call with the not integer subscript"):
                with it("raise InvalidSubScriptError"):
                    arg = {
                        "sym": self.variable_label,
                        "sub": {"num": 1.1},
                    }
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(InvalidSubScriptError)
                    )

            with context("call with the invalid subscript"):
                with it("raise InvalidSubScriptError"):
                    arg = {
                        "sym": self.variable_label,
                        "sub": {"sym": self.variable_label, "sub": {"num": 1}},
                    }
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(InvalidSubScriptError)
                    )

            with context("call with the variable whose index out of range"):
                with it("raise VariableIndexOutOfRangeError"):
                    arg = {
                        "sym": self.variable_label,
                        "sub": {"num": self.variable_size + 1},
                    }
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(VariableIndexOutOfRangeError)
                    )

            with context("call with the undefined variable"):
                with it("raise NotFoundVariableError"):
                    arg = {"sym": "a", "sub": {"num": 0}}
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(NotFoundVariableError)
                    )

        with context("variable is quadratic"):
            with before.each:
                self.variable_label = "x"
                self.variable_size = (4, 4)
                self.parser = Parser(
                    {
                        "type": "binary",
                        "dimension": 2,
                        "size": self.variable_size,
                        "label": self.variable_label,
                    }
                )

            with context("call with the collect args"):
                with it("return the value of the specified indexed variable"):
                    index1 = random.randint(1, self.variable_size[0])
                    index2 = random.randint(1, self.variable_size[0])
                    arg = {
                        "sym": self.variable_label,
                        "sub": {
                            "fn": "list",
                            "arg": [{"num": index1}, {"num": index2}],
                        },
                    }
                    expect(self.parser._sub(arg)).to(
                        equal(self.parser.x[index1 - 1][index2 - 1])
                    )

            with context("call with the variable whose index out of range"):
                with it("raise VariableIndexOutOfRangeError"):
                    index1 = self.variable_size[0] + 1
                    index2 = self.variable_size[0]
                    arg = {
                        "sym": self.variable_label,
                        "sub": {
                            "fn": "list",
                            "arg": [{"num": index1}, {"num": index2}],
                        },
                    }
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(VariableIndexOutOfRangeError)
                    )

    with description("parse_mathjson()"):
        with before.each:
            self.variable_label = "x"
            self.variable_size = 4
            self.constant_label = "n"
            self.constant_value = 10
            self.parser = Parser(
                {
                    "type": "binary",
                    "dimension": 1,
                    "size": self.variable_size,
                    "label": self.variable_label,
                },
                [{"label": self.constant_label, "values": self.constant_value}],
            )

        with context("invalid mathjson"):
            with it("raise InvalidMathJsonFormatError"):
                arg = {"x": 1}
                expect(lambda: self.parser.parse_mathjson(arg)).to(
                    raise_error(InvalidMathJsonFormatError)
                )

        with context("sym w/ sub"):
            with it(""):
                arg = {"sym": self.variable_label, "sub": {"num": 1}}
                expect(self.parser.parse_mathjson(arg)).to(equal(self.parser.x[0]))

        with context("sym w/o sub"):
            with it(""):
                arg = {"sym": self.constant_label}
                expect(self.parser.parse_mathjson(arg)).to(equal(self.constant_value))

        with context("num"):
            with it(""):
                arg = {"num": 10}
                expect(self.parser.parse_mathjson(arg)).to(equal(arg["num"]))

        with context("num w/ sup"):
            with it(""):
                arg = {"num": 10, "sup": {"num": 2}}
                expect(self.parser.parse_mathjson(arg)).to(equal(10 ** 2))
