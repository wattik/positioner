from positioner.orderbook import Option
from positioner.solver.budget import MaxCostPolicy
from positioner.solver.loss_policy import MaxRelativeLossPolicy
from positioner.solver.objective import GaussianObjective
from positioner.solver.problem import StrategyComputer, Strategy
from positioner.spaces import space_by_index_price


def compute_strategy(
        order_book: list[Option],
        index_price: float,
        budget: float,
        expected_index_price: float = None,
        volatility: float = 5_000,
        maximal_relative_loss: float= -0.1,
        loss_space_delta: float = 0.7
) -> Strategy:
    expected_index_price = expected_index_price or index_price

    strategy_comp = StrategyComputer(order_book)

    strategy_comp.specify(
        GaussianObjective(center=expected_index_price, scale=volatility, space=space_by_index_price(index_price, 0.9, n=1_000))
    )
    strategy_comp.specify(
        MaxRelativeLossPolicy(maximal_relative_loss, space=space_by_index_price(index_price, loss_space_delta, n=600))
    )
    strategy_comp.specify(
        MaxCostPolicy(budget)
    )

    return strategy_comp.compute()