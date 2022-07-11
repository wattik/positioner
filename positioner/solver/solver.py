import logging
from collections import Callable
from typing import Literal

from positioner.components.option import Option
from positioner.components.order import Order
from positioner.functional.option import clean_order_book_from_costly_trades, clean_order_book_from_history
from .problem import StrategyComputer
from .solution import Strategy
from .spaces import space_by_index_price
from .state_transformers.always_positive import AlwaysPositivePolicy
from .state_transformers.budget import MaxExpensesPolicy
from .state_transformers.loss_policy import ImprovingPandlPolicy, LowerBoundLossPolicy, MaxLossPolicy
from .state_transformers.objective import GaussianPAndLObjective, MinPandLObjetive


def compute_strategy(
    order_book: list[Option],
    index_price: float,
    budget: float,
    expected_index_price: float = None,
    total_budget: float = None,
    initial_position: list[Order] = None,
    historical_orders: list[Order] = None,
    # Contingency Space
    contingency_space_delta: float = 0.7,
    contingency_space_bounds: tuple[float] = None,
    # Max Loss Policy
    use_max_loss_policy: bool = True,
    maximal_absolute_loss: float = None,
    maximal_relative_loss: float = -0.1,
    # Positivity Policy
    use_always_positivity_policy: bool = False,
    # Loss Lower Bound Policy
    use_lower_bound_loss_policy: bool = False,
    lower_bound_functor: Callable = None,
    # Loss Improving Policy
    use_loss_improving_policy: bool = False,
    improving_discount_rate: float = None,
    # Objective Type
    objective_type: Literal["expected_pandl", "min_pandl"] = "expected_pandl",
    max_shift: float = 10_000,
    objective_relative_bounds: tuple[float] = None,
    objective_absolute_bounds: tuple[float, float] = None,
    use_clean_from_costly_trades: bool = True,
) -> Strategy:
    expected_index_price = expected_index_price or index_price
    initial_position = initial_position or []
    historical_orders = historical_orders or initial_position
    total_budget = total_budget or budget

    order_book = clean_order_book_from_history(order_book, historical_orders)

    if use_clean_from_costly_trades:
        order_book = clean_order_book_from_costly_trades(order_book, budget)

    strategy_comp = StrategyComputer(
        order_book=order_book,
        initial_position=initial_position,
        index_price=index_price,
        budget=budget,
    )
    if objective_type == "expected_pandl":
        strategy_comp.specify(
            GaussianPAndLObjective(
                delta=max_shift,
                space=space_by_index_price(index_price, delta=5, n=1_000),
                total_budget=total_budget,
                current_price=index_price,
                expected_price=expected_index_price,
                initial_position=initial_position,
                budget=budget,
            )
        )
    elif objective_type == "min_pandl":
        strategy_comp.specify(
            MinPandLObjetive(
                space=space_by_index_price(index_price, delta=5, n=1_000),
                total_budget=total_budget,
                current_price=index_price,
                expected_price=expected_index_price,
                initial_position=initial_position,
                budget=budget,
                relative_bounds=objective_relative_bounds,
                absolute_bounds=objective_absolute_bounds,
            )
        )
    else:
        raise ValueError(objective_type)

    if use_always_positivity_policy:
        strategy_comp.specify(
            AlwaysPositivePolicy(
                total_budget=total_budget,
                budget=budget,
                initial_position=initial_position,
                current_price=index_price,
            )
        )

    contingency_space = space_by_index_price(index_price, delta=contingency_space_delta, bounds=contingency_space_bounds, n=600)

    if use_max_loss_policy:
        strategy_comp.specify(
            MaxLossPolicy(
                max_relative_loss=maximal_relative_loss, total_budget=total_budget, space=contingency_space,
                initial_position=initial_position, budget=budget, current_price=index_price,
                max_absolute_loss=maximal_absolute_loss,
            )
        )

    if use_lower_bound_loss_policy:
        assert lower_bound_functor is not None
        strategy_comp.specify(
            LowerBoundLossPolicy(
                total_budget=total_budget, space=contingency_space,
                initial_position=initial_position, budget=budget, current_price=index_price,
                lower_bound_func=lower_bound_functor
            )
        )

    if use_loss_improving_policy:
        strategy_comp.specify(
            ImprovingPandlPolicy(
                total_budget=total_budget, space=contingency_space,
                initial_position=initial_position, budget=budget, current_price=index_price,
                maximal_absolute_loss=maximal_absolute_loss, discount_rate=improving_discount_rate,
            )
        )

    strategy_comp.specify(
        MaxExpensesPolicy(
            budget=budget, initial_position=initial_position, space=contingency_space,
            current_price=index_price)
    )

    strategy = strategy_comp.compute()

    if not strategy.optimal:
        logging.warning(f"Not optimal: {strategy.solver_status}")

    return strategy
