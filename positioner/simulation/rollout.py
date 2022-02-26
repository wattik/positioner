from typing import Iterable

from tqdm import tqdm

from positioner.components.option import Option
from positioner.solver.solver import compute_strategy as single_strategy
from .rollout_simulator import RolloutSimulator, SimulationResult


def simulate(
    order_books: Iterable[list[Option]],
    index_prices: list[float],
    timestamps: list,
    total_budget: float,
    final_index_price: float = None,
    single_strategy=single_strategy,
    **kwargs
) -> SimulationResult:
    n_steps = len(timestamps)
    final_index_price = final_index_price or index_prices[-1]
    simulator = RolloutSimulator(single_strategy)

    # could be computed with a budget policy
    budget_delta = total_budget / n_steps

    items = zip(timestamps, order_books, index_prices)
    for ts, order_book, index_price in tqdm(items, total=len(timestamps)):
        simulator.step(
            order_book=order_book,
            index_price=index_price,
            additional_budget=budget_delta,
            timestamp=ts,
            **kwargs
        )

    return simulator.finalize(final_index_price)
