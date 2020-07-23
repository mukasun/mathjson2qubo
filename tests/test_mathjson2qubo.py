import random

from expects import expect, raise_error
from expects.matchers.built_in.equal import equal
from mamba import before, context, description, it
from mathjson2qubo.parser import Parser
from mathjson2qubo.parser_exeptions import (
    InvalidSubScriptError,
    InvalidSuperScriptError,
    NotFoundVariableError,
    VariableIndexOutOfRangeError,
)

with description("Parser") as self:
    with before.each:
        self.parser = Parser(
            {"type": "binary", "dimension": 1, "size": 4, "label": "x"}
        )

    with description("_fn_add()"):
        with it("return convorutional sum"):
            args = [1.0, 2.0, 3.0]
            expect(self.parser._fn_add(args)).to(equal(1.0 + 2.0 + 3.0))

    with description("_fn_multiply()"):
        with it("return convorutional product"):
            args = [4.0, 5.0, 6.0]
            expect(self.parser._fn_multiply(args)).to(equal(4.0 * 5.0 * 6.0))

    with description("_fn_negate()"):
        with it("return negated value"):
            args = [1.0]
            expect(self.parser._fn_negate(args)).to(equal(-args[0]))

    with description("_fn_list()"):
        with it("return int list"):
            args = [1.0, 2.0, 3.0]
            expect(self.parser._fn_list(args)).to(equal(list(map(int, args))))

    with description("_sup()"):
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