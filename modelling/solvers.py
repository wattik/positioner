import cvxpy as cp

from modelling import Model, Solution


def solve_cvxpy(model: Model) -> Solution:
    c, A, b, l, u = model.matrices()
    n = len(c)

    x = cp.Variable(n)
    problem = cp.Problem(cp.Maximize(c.T @ x), [
        A @ x <= b,
        l <= x,
        x >= u
    ])

    problem.solve()

    return Solution(
        optimality=problem.status == cp.OPTIMAL,
        message=problem.status,
        value=problem.value
    )
