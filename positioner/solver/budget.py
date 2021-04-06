from .problem import State


class MaxCostPolicy:
    def __init__(self, budget):
        self.budget = budget

    def __call__(self, state: State):
        costs = 0.0
        for amount in state.vars.buy.values():
            costs += amount

        state.constrain(costs <= self.budget)