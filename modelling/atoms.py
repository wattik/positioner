from dataclasses import dataclass
from enum import Enum

import numpy as np


class Variable:
    def __init__(self, id: int, name: str = None, lower_bound: float = -np.inf, upper_bound: float = np.inf):
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.value = None

        self.__id__ = id
        self.__hash_mem__ = None

    def __repr__(self):
        return f"<Var {self.name}>"

    def __eq__(self, other):
        return other.__id__ == self.__id__

    def __hash__(self):
        if self.__hash_mem__ is None:
            self.__hash_mem__ = hash(self.__id__)
        return self.__hash_mem__

    def __lt__(self, other):
        return self.__id__ < other.__id__


class LinearCombination:
    def __init__(self, n_variables: int = None, cons=None):
        self.constants: list[float] = cons or [0] * n_variables
        self.offset: float = 0

    def fork(self):
        return LinearCombination(cons=self.constants[:])

    def add(self, variable: Variable, constant: float):
        self.constants[variable.__id__] += constant


class Constraint:
    def __init__(self, left, right):
        assert isinstance(left, LinearCombination) != isinstance(right, LinearCombination)

        if isinstance(left, LinearCombination):
            self.left = LinearCombination(cons=left.constants)
            self.right = right - left.offset

        else:
            self.left = LinearCombination(cons=[-v for v in right.constants])
            self.right = right.offset - left


class Sense(Enum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


@dataclass
class ProblemDefinition:
    c: np.ndarray
    A: np.ndarray
    b: np.ndarray
    l: np.ndarray
    u: np.ndarray
    vars: list[Variable]


class LPContext:
    def __init__(self, sense=Sense.MAXIMIZE):
        self.sense = sense

        self.constrains: list[Constraint] = []
        self.obj: LinearCombination = None

        self.variables: list[Variable] = []

    def new_variable(self, name: str, lower_bound: float = -np.inf, upper_bound: float = np.inf):
        i = len(self.variables)
        var = Variable(i, name=name, lower_bound=lower_bound, upper_bound=upper_bound)
        self.variables.append(var)
        return var

    def new_linear_combination(self):
        return LinearCombination(n_variables=len(self.variables))

    def constrain(self, left_side, right_side):
        """Constraint: left <= right"""
        self.constrains.append(Constraint(left_side, right_side))

    def objective(self, obj):
        self.obj = obj

    def problem_definition(self) -> ProblemDefinition:
        """
        Returns problem_definition c, A, b, l, u
        """
        assert self.obj is not None

        vars = self.variables[:]

        c = np.asarray(self.obj.constants)
        l = np.asarray([v.lower_bound for v in vars])
        u = np.asarray([v.upper_bound for v in vars])

        A = np.zeros((len(self.constrains), len(vars)))
        b = np.zeros(len(self.constrains))

        for i, con in enumerate(self.constrains):
            A[i, :] = np.asarray(con.left.constants)
            b[i] = con.right

        return ProblemDefinition(c, A, b, l, u, vars)


@dataclass
class Solution:
    optimality: bool
    message: str
    value: float
