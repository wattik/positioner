from positioner.components.option import Option
from positioner.components.order import Order
from positioner.functional.option import clean_order_book_from_costly_trades, clean_order_book_from_position
from .problem import StrategyComputer
from .solution import Strategy
from .spaces import space_by_index_price
from .state_transformers.budget import MaxExpensesPolicy
from .state_transformers.loss_policy import MaxRelativeLossPolicy
from .state_transformers.objective import GaussianPAndLObjective


def compute_strategy(
    order_book: list[Option],
    index_price: float,
    budget: float,
    total_budget: float = None,
    initial_position: list[Order] = None,
    expected_index_price: float = None,
    max_shift: float = 10_000,
    maximal_relative_loss: float = -0.1,
    use_max_relative_loss_policy: bool = True,
    loss_space_delta: float = 0.7,
    historical_orders: list[Order] = None
) -> Strategy:
    expected_index_price = expected_index_price or index_price
    initial_position = initial_position or []
    historical_orders = historical_orders or initial_position
    total_budget = total_budget or budget

    order_book = clean_order_book_from_position(order_book, historical_orders)
    order_book = clean_order_book_from_costly_trades(order_book, budget)

    strategy_comp = StrategyComputer(
        order_book=order_book,
        initial_position=initial_position,
        index_price=index_price,
        budget=budget
    )

    strategy_comp.specify(
        GaussianPAndLObjective(
            center=expected_index_price,
            delta=max_shift,
            space=space_by_index_price(index_price, 0.9, n=1_000),
            total_budget=total_budget,
            available=budget,
            current_price=index_price
        )
    )

    contingency_space = space_by_index_price(index_price, loss_space_delta, n=600)

    if use_max_relative_loss_policy:
        strategy_comp.specify(
            MaxRelativeLossPolicy(
                maximal_relative_loss, total_budget=total_budget, space=contingency_space,
                initial_position=initial_position, budget=budget, current_price=index_price
            )
        )
    strategy_comp.specify(
        MaxExpensesPolicy(
            budget=budget, initial_position=initial_position, space=contingency_space,
            current_price=index_price)
    )

    return strategy_comp.compute()
