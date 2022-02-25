import cvxpy as cp
import numpy as np

from .atoms import LPContext, Sense, Solution


def solve_cvxpy(model: LPContext) -> Solution:
    pd = model.problem_definition()
    c, A, b, l, u = pd.c, pd.A, pd.b, pd.l, pd.u

    sense = cp.Maximize if model.sense == Sense.MAXIMIZE else cp.Minimize
    x = cp.Variable(len(pd.vars))

    constraints = [A @ x <= b]
    idx = l > -np.inf
    if np.any(idx):
        constraints += [l[idx] <= x[idx]]
    idx = u < np.inf
    if np.any(idx):
        constraints += [x[idx] <= u[idx]]

    problem = cp.Problem(sense(c @ x), constraints)
    try:
        problem.solve(solver=cp.GLPK)
        optimality = problem.status == cp.OPTIMAL
        message = problem.status
    except cp.SolverError as err:
        optimality = False
        message = str(err)

    if optimality:
        for var, v in zip(pd.vars, x.value):
            var.value = v

    return Solution(
        optimality=optimality,
        message=message,
        value=problem.value
    )
