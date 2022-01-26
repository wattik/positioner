from dataclasses import dataclass
import numpy as np


class Variable:
    def __init__(self, name: str, lower_bound: float, upper_bound: float):
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.value = None

    def __eq__(self, other):
        return other.name == self.name

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return self.name.__lt__(other.name)


class LinearCombination:
    def __init__(self, vars=None, cons=None):
        self.variables: list[Variable] = vars or []
        self.constants: list[float] = cons or []
        self.offset: float = 0.0

    def add(self, variable: Variable, constant: float):
        self.variables.append(variable)
        self.constants.append(constant)

    def to_dict(self):
        return dict(zip(self.variables, self.constants))

    def reorded(self, keys: list[Variable]):
        d = self.to_dict()
        return [d.get(k, 0.0) for k in keys]


class Constraint:
    def __init__(self, left, right):
        assert isinstance(left, LinearCombination) != isinstance(right, LinearCombination)

        if isinstance(left, LinearCombination):
            self.left = LinearCombination(left.variables, left.constants)
            self.right = right - left.offset

        else:
            self.left = LinearCombination(right.variables, [-v for v in right.constants])
            self.right = right.offset - left


class Model:
    def __init__(self, sense="maximize"):
        assert sense == "maximize"

        self.constrains: list[Constraint] = []
        self.obj: LinearCombination = None

    def constrain(self, left_side, right_side):
        """Constraint: X <= A"""
        self.constrains.append(Constraint(left_side, right_side))

    def objective(self, obj):
        self.obj = obj

    def variables(self) -> list[Variable]:
        vars = set()

        if self.obj:
            vars |= set(self.obj.variables)

        for con in self.constrains:
            vars |= set(con.left.variables)

        return sorted(vars)

    def matrices(self):
        """
        Returns matrices c, A, b, l, u
        """
        assert self.obj is not None

        vars = self.variables()

        c = np.asarray(self.obj.reorded(vars))
        l = np.asarray([v.lower_bound for v in vars])
        u = np.asarray([v.upper_bound for v in vars])

        A = np.zeros((len(self.constrains), len(vars)))
        b = np.zeros(len(self.constrains))

        for i, con in enumerate(self.constrains):
            A[i, :] = np.asarray(con.left.reorded(vars))
            b[i] = float(con.right)

        return c, A, b, l, u


@dataclass
class Solution:
    optimality: bool
    message: str
    value: float
