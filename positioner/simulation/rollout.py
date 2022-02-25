from collections import Callable

from tqdm import tqdm

from positioner.components.option import Option
from positioner.solver.solver import compute_strategy as single_strategy
from .rollout_simulator import RolloutSimulator, SimulationResult


def simulate(
    order_books: list[list[Option]],
    index_prices: list[float],
    timestamps: list,
    total_budget: float,
    final_index_price: float = None,
    max_shift: float = 10_000,
    maximal_relative_loss: float = -0.1,
    loss_space_delta: float = 0.7,
    single_strategy=single_strategy,
    **kwargs
) -> SimulationResult:
    assert len(index_prices) == len(order_books)
    n_steps = len(order_books)
    final_index_price = final_index_price or index_prices[-1]
    simulator = RolloutSimulator(single_strategy)

    # could be computed with a budget policy
    budget_delta = total_budget / n_steps

    items = zip(timestamps, order_books, index_prices)
    for ts, order_book, index_price in tqdm(items, total=len(index_prices)):
        simulator.step(
            order_book=order_book,
            index_price=index_price,
            additional_budget=budget_delta,
            max_shift=max_shift,
            maximal_relative_loss=maximal_relative_loss,
            loss_space_delta=loss_space_delta,
            timestamp=ts,
            **kwargs
        )

    return simulator.finalize(final_index_price)
