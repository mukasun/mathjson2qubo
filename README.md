# mathjson2qubo

[![PyPI version](https://badge.fury.io/py/mathjson2qubo.svg)](https://badge.fury.io/py/mathjson2qubo)
[![Test](https://github.com/mks1412/mathjson2qubo/workflows/Test/badge.svg)](https://github.com/mks1412/mathjson2qubo/actions?query=workflow%3ATest)
[![codecov](https://codecov.io/gh/mks1412/mathjson2qubo/branch/master/graph/badge.svg)](https://codecov.io/gh/mks1412/mathjson2qubo)

> :warning: **This package is work in progress!**

## About

mathjson2qubo allows you to convert [MathJSON](https://cortexjs.io/guides/math-json/) into [PyQUBO](https://github.com/recruit-communications/pyqubo) expression.

Assume that a Quadratic Unconstrained Binary Optimizationthe (QUBO) model as the following equation.

<img src="https://latex.codecogs.com/gif.latex?\sum^N_i\sum^N_jv_{i,j}x_ix_j,~~x_i\in\{0,1\}." title="QUBO equation" />

In MathJSON format, the above equation is formatted as the below json based on the latex abstract syntax tree (AST).

```json
{
  "fn": "sum",
  "sub": { "sym": "i" },
  "sup": { "sym": "N" },
  "arg": [
    {
      "fn": "sum",
      "sub": { "sym": "j" },
      "sup": { "sym": "N" },
      "arg": [
        {
          "fn": "multiply",
          "arg": [
            {
              "sym": "v",
              "sub": {
                "fn": "list",
                "arg": [
                  { "sym": "i" },
                  { "sym": "j" }
                ]
              }
            },
            { "sym": "x", "sub": { "sym": "i" } },
            { "sym": "x", "sub": { "sym": "j" } }
          ]
        }
      ]
    }
  ]
}
```

In PyQUBO, the equation is expressed by the following code.

```python
from pyqubo import Array, Sum

# Note that `v` in the equation is defined appropriately here.

x = Array.create("x", N, "BINARY")
eq = Sum(0, N,
    lambda i: Sum(0, N,
        lambda j: v[i][j] * x[i] * x[j]
    )
)
```

mathjson2qubo generates PyQUBO model from mathematical expressions formatted MathJSON (with constant values).


## Example Usage

### Install

```
pip install mathjson2qubo
```


We introduce the example of number partitioning.

> Number partitioning is the task of deciding whether a given multiset S of positive integers can be partitioned into two subsets S1 and S2 such that the sum of the numbers in S1 equals the sum of the numbers in S2.

Number partitioning problem is formulated as follows.

<img src="https://latex.codecogs.com/gif.latex?\sum^{|S|}_in_is_i,~~n_i\in S,~~s_i\in\{-1,1\}." title="QUBO equation" />


```python
from mathjson2qubo import Parser

numbers = [3, 1, 1, 2, 2, 1]

parser = Parser(
    vartype="spin",
    variables=[
      {"symbol": "s", "dimension": 1, "size": len(numbers) }
    ],
    constants=[
      {"symbol": "N", "values": len(numbers)},
      {"symbol": "n", "values": numbers}
    ]
)

mathjson = {
    "fn": "add",
    "arg": [
        {"num": 0},
        {
            "fn": "sum",
            "sub": {"fn": "equal", "arg": [{"sym": "i"}, {"num": 1}]},
            "sup": {"sym": "N"},
            "arg": [
                {
                    "fn": "multiply",
                    "arg": [
                        {"sym": "n", "sub": {"sym": "i"}},
                        {"sym": "s", "sub": {"sym": "i"}},
                    ],
                }
            ],
        },
    ],
    "sup": {"num": 2},
}

objectives = [{"label": "obj", "weight": 1, "tex": mathjson}]

parser.parse_to_pyqubo_model(objectives=objectives, constraints=[])
# > pyqubo.core.model.Model instance

# Support solution by simulated annealing built in pyqubo.
parser.solve(
  objectives=objectives,
  constraints=[],
  num_reads=10,
  sweeps=1000,
  beta_range=(1, 50)
)
# > ({'s': {0: 1.0, 1: 1.0, 2: -1.0, 3: -1.0, 4: -1.0, 5: 1.0}}, {}, 0.0)

```
