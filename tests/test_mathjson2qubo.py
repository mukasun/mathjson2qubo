import random

from expects import expect, raise_error
from expects.matchers.built_in.equal import equal
from mamba import before, context, description, it
from mathjson2qubo.errors import (
    CalculationError,
    MathJsonFormatError,
    ParserInitArgumentsError,
    SubScriptError,
    SumFunctionError,
    SuperScriptError,
    VariableAccessError,
)
from mathjson2qubo.parser import Parser
from pyqubo import Sum
from pyqubo.core.express import Binary, Spin

with description("Parser") as self:
    with before.each:
        self.parser = Parser(
            variables=[{"dimension": 1, "size": 4, "symbol": "x", "type": "BINARY"}]
        )

    with description("__init__()"):
        with context("call with variable whose symbol is more than 2 characters"):
            with it("raise ParserInitArgumentsError"):
                expect(
                    lambda: Parser(
                        variables=[
                            {"symbol": "s1", "dimension": 0, "size": 0, "type": "SPIN"}
                        ],
                    )
                ).to(raise_error(ParserInitArgumentsError))

        with context("call with variable whose dimension is negative"):
            with it("raise ParserInitArgumentsError"):
                expect(
                    lambda: Parser(
                        variables=[
                            {"symbol": "s", "dimension": -1, "size": 0, "type": "SPIN"}
                        ],
                    )
                ).to(raise_error(ParserInitArgumentsError))

        with context("call with variable whose dimension is 0"):
            with context("vartype is SPIN"):
                with it("set single SPIN"):
                    parser = Parser(
                        variables=[
                            {"symbol": "x", "dimension": 0, "size": 0, "type": "SPIN"}
                        ],
                    )
                    expect(parser.x).to(equal(Spin("x")))

            with context("vartype is binary"):
                with it("set single binary"):
                    parser = Parser(
                        variables=[
                            {
                                "symbol": "x",
                                "dimension": 0,
                                "size": 0,
                                "type": "BINARY",
                            }
                        ],
                    )
                    expect(parser.x).to(equal(Binary("x")))

    with description("_fn_add()"):
        with it("return convorutional sum"):
            args = [1.0, 2.0, 3.0]
            expect(self.parser._fn_add(args)).to(equal(1.0 + 2.0 + 3.0))

    with description("_fn_subtract"):
        with context("call w/ 2 elements argument"):
            with it("return subtract the second from the first"):
                args = [1.0, 2.0]
                expect(self.parser._fn_subtract(args)).to(equal(1.0 - 2.0))

    with description("_fn_multiply()"):
        with it("return convorutional product"):
            args = [4.0, 5.0, 6.0]
            expect(self.parser._fn_multiply(args)).to(equal(4.0 * 5.0 * 6.0))

    with description("_fn_divide"):
        with context("call w/ 2 elements argument"):
            with it("return the firstr divided by the second"):
                args = [1.0, 2.0]
                expect(self.parser._fn_divide(args)).to(equal(1.0 / 2.0))

        with context("call w/ zero division"):
            with it("raise Caluc"):
                args = [1.0, 0]
                expect(lambda: self.parser._fn_divide(args)).to(
                    raise_error(CalculationError)
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
                variables=[
                    {"dimension": 1, "size": self.size, "symbol": "x", "type": "BINARY"}
                ],
                constants=[
                    {"symbol": "N", "values": self.size},
                    {"symbol": "n", "values": self.constant_values},
                ],
            )

        with context("call w/o sub or sup"):
            with it("raise SumFunctionError"):
                sum_arg_wo_sub = {
                    "fn": "sum",
                    "sup": {"sym": "N"},
                }
                sum_arg_wo_sup = {
                    "fn": "sum",
                    "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                }
                expect(lambda: self.parser._fn_sum(sum_arg_wo_sub)).to(
                    raise_error(SumFunctionError)
                )
                expect(lambda: self.parser._fn_sum(sum_arg_wo_sup)).to(
                    raise_error(SumFunctionError)
                )

        with context("call w/o index variable"):
            with it("raise SumFunctionError"):
                sum_arg = {
                    "fn": "sum",
                    "sup": {"sym": "N"},
                    "sub": {"fn": "equal", "arg": [{"num": 1}]},
                }
                expect(lambda: self.parser._fn_sum(sum_arg)).to(
                    raise_error(SumFunctionError)
                )

        with context("call w/ invalid start index"):
            with context("subscript is not equal"):
                with it("raise SumFunctionError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"sym": "N"},
                        "sub": {"fn": "elementof", "arg": [{"sym": "i"}, {"num": "G"}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(SumFunctionError)
                    )

            with context("equal of subscript is invalid"):
                with it("raise SumFunctionError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"sym": "N"},
                        "sub": {
                            "fn": "equal",
                            "arg": [{"sym": "i"}, {"sym": "j"}, {"num": 1}],
                        },
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(SumFunctionError)
                    )

            with context("start index is float"):
                with it("raise SumFunctionError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"num": 5},
                        "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1.5}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(SumFunctionError)
                    )

            with context("start index is Express"):
                with it("raise SumFunctionError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"num": 5},
                        "sub": {
                            "fn": "equal",
                            "arg": [{"sym": "i"}, {"sym": "x", "sub": {"num": 1}}],
                        },
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(SumFunctionError)
                    )

        with context("call w/ invalid end index"):
            with context("end index is float"):
                with it("raise SumFunctionError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"num": 1.5},
                        "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(SumFunctionError)
                    )

            with context("end index is Express"):
                with it("raise SumFunctionError"):
                    sum_arg = {
                        "fn": "sum",
                        "sup": {"sym": "x", "sub": {"num": 1}},
                        "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
                    }
                    expect(lambda: self.parser._fn_sum(sum_arg)).to(
                        raise_error(SumFunctionError)
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
                self.constants = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
                self.parser = Parser(
                    variables=[
                        {
                            "dimension": 2,
                            "size": [self.size, self.size],
                            "symbol": "x",
                            "type": "BINARY",
                        },
                    ],
                    constants=[
                        {"symbol": "N", "values": self.size},
                        {"symbol": "n", "values": self.constants},
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
            with it("raise SuperScriptError"):
                expect(lambda: self.parser._sup([1, 2], {"sub": {"num": 2}})).to(
                    raise_error(SuperScriptError)
                )

        with context("sup is list"):
            with it("raise SuperScriptError"):
                arg = {
                    "num": 2,
                    "sup": {"fn": "list", "arg": [{"num": 1}, {"num": 2}]},
                }
                expect(lambda: self.parser._sup(2.0, arg)).to(
                    raise_error(SuperScriptError)
                )

        with context("sup is Express"):
            with it("raise SuperScriptError"):
                arg = {"num": 2, "sup": {"sym": "x", "sub": {"num": 1}}}
                expect(lambda: self.parser._sup(2.0, arg)).to(
                    raise_error(SuperScriptError)
                )

        with context("include a cubic (and more) term"):
            with it("raise SuperScriptError"):
                arg = {"sym": "x", "sup": {"num": 3}}
                expect(lambda: self.parser._sup(Binary("x"), arg)).to(
                    raise_error(SuperScriptError)
                )

                arg = {"sym": "x", "sup": {"num": 4}}
                expect(lambda: self.parser._sup(Binary("x"), arg)).to(
                    raise_error(SuperScriptError)
                )

    with description("_sub()"):
        with context("variable is linear"):
            with before.each:
                self.variable_label = "x"
                self.variable_size = 4
                self.parser = Parser(
                    variables=[
                        {
                            "dimension": 1,
                            "size": self.variable_size,
                            "symbol": self.variable_label,
                            "type": "BINARY",
                        }
                    ],
                )

            with context("call with the collect args"):
                with it("return the value of the specified indexed variable"):
                    index = random.randint(1, self.variable_size)
                    arg = {"sym": self.variable_label, "sub": {"num": index}}
                    expect(self.parser._sub(arg)).to(equal(self.parser.x[index - 1]))

            with context("call with the not integer subscript"):
                with it("raise SubScriptError"):
                    arg = {
                        "sym": self.variable_label,
                        "sub": {"num": 1.1},
                    }
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(SubScriptError)
                    )

            with context("call with the invalid subscript"):
                with it("raise SubScriptError"):
                    arg = {
                        "sym": self.variable_label,
                        "sub": {"sym": self.variable_label, "sub": {"num": 1}},
                    }
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(SubScriptError)
                    )

            with context("call with the variable whose index out of range"):
                with it("raise VariableAccessError"):
                    arg = {
                        "sym": self.variable_label,
                        "sub": {"num": self.variable_size + 1},
                    }
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(VariableAccessError)
                    )

            with context("call with the undefined variable"):
                with it("raise VariableAccessError"):
                    arg = {"sym": "a", "sub": {"num": 0}}
                    expect(lambda: self.parser._sub(arg)).to(
                        raise_error(VariableAccessError)
                    )

        with context("variable is quadratic"):
            with before.each:
                self.variable_label = "x"
                self.variable_size = [4, 4]
                self.parser = Parser(
                    variables=[
                        {
                            "dimension": 2,
                            "size": self.variable_size,
                            "symbol": self.variable_label,
                            "type": "BINARY",
                        }
                    ],
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
                with it("raise VariableAccessError"):
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
                        raise_error(VariableAccessError)
                    )

    with description("parse_mathjson()"):
        with before.each:
            self.variable_label = "x"
            self.variable_size = 4
            self.constant_label = "n"
            self.constant_value = 10
            self.parser = Parser(
                variables=[
                    {
                        "dimension": 1,
                        "size": self.variable_size,
                        "symbol": self.variable_label,
                        "type": "BINARY",
                    },
                ],
                constants=[
                    {"symbol": self.constant_label, "values": self.constant_value}
                ],
            )

        with context("invalid mathjson"):
            with it("raise MathJsonFormatError"):
                arg = {"x": 1}
                expect(lambda: self.parser.parse_mathjson(arg)).to(
                    raise_error(MathJsonFormatError)
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
