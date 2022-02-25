import numpy as np

import modelling as ml


def test():
    model = ml.LPContext(sense=ml.Sense.MINIMIZE)
    x0 = model.new_variable(name="x0")
    x1 = model.new_variable(name="x1", lower_bound=-3)

    model.objective(ml.LinearCombination(cons=[-1, 4]))
    model.constrain(ml.LinearCombination(cons=[-3, 1]), 6)
    model.constrain(-4, ml.LinearCombination(cons=[-1, -2]))

    res = ml.solve_cvxpy(model)

    assert np.isclose(res.value, -22), res
