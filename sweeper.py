import logging
from datetime import datetime
from pprint import pformat

import pandas as pd
import wandb

from positioner.remotedata.fetch import fetch_option_groups, fetch_order_books
from positioner.simulation.rollout import simulate


def to_sim_params(conf: dict, start_price) -> dict:
    p = dict()
    p["total_budget"] = conf["total_budget"]

    if conf["contingency_space_type"] == "absolute":
        p["contingency_space_bounds"] = (
            start_price * conf["contingency_space_lb"],
            start_price * conf["contingency_space_ub"]
        )
    elif conf["contingency_space_type"] == "relative":
        p["contingency_space_delta"] = conf["contingency_space_delta"]
    else:
        raise ValueError(conf["contingency_space_type"])

    p["use_max_loss_policy"] = conf["use_max_loss_policy"]
    if conf["use_max_loss_policy"]:
        if conf["max_loss_policy_type"] == "absolute":
            p["maximal_absolute_loss"] = conf["maximal_absolute_loss"]
        elif conf["max_loss_policy_type"] == "relative":
            p["maximal_relative_loss"] = conf["maximal_relative_loss"]
        else:
            raise ValueError(conf["max_loss_policy_type"])

    p["use_loss_improving_policy"] = conf["use_loss_improving_policy"]
    if conf["use_loss_improving_policy"]:
        p["maximal_absolute_loss"] = conf["maximal_absolute_loss"]
        p["use_loss_improving_policy"] = conf["use_loss_improving_policy"]
        p["improving_discount_rate"] = conf["improving_discount_rate"]

    p["objective_type"] = conf["objective_type"]
    if conf["objective_type"] == "expected_pandl":
        p["max_shift"] = conf["max_shift"]
    elif conf["objective_type"] == "min_pandl":
        if conf["min_pandl_space_type"] == "absolute":
            p["objective_absolute_bounds"] = (
                start_price * conf["objective_absolute_lb"],
                start_price * conf["objective_absolute_ub"]
            )
        elif conf["min_pandl_space_type"] == "relative":
            p["objective_relative_bounds"] = conf["objective_relative_bounds"]
        else:
            raise ValueError(conf["min_pandl_space_type"])
    else:
        raise ValueError([conf["objective_type"]])

    return p


def simulate_option_group(option_group: str, config: dict):
    max_steps = config["max_steps"]

    order_books, index_prices, timestamps = fetch_order_books(option_group)

    stride = len(order_books) // max_steps + 1

    order_books = order_books[::stride]
    index_prices = index_prices[::stride]
    timestamps = timestamps[::stride]

    start_price = index_prices[0]

    sim_params = to_sim_params(config, start_price)

    res = simulate(
        order_books=order_books,
        index_prices=index_prices,
        timestamps=timestamps,
        **sim_params
    )

    return res


def run(default_config: dict):
    option_groups = fetch_option_groups(default_config["experiment_last_group"])

    wandb.init(project="test-project", config=default_config)
    config = wandb.config

    logging.info(f"New Run")
    logging.info(pformat(config))
    logging.info(f"Option Groups: {option_groups}")
    logging.info("=" * 50)

    results = []

    for og in option_groups:
        logging.info(f"Processing: {og}")
        res = simulate_option_group(og, config)

        results.append(dict(
            option_group=og,
            profitability=res.profitability,
            fail_rate=res.fail_rate,
        ))
    df = pd.DataFrame(results)

    wandb.log(dict(
        profitability_med=df["profitability"].median(),
        profitability_mean=df["profitability"].mean(),
        profitability_min=df["profitability"].min(),
        profitability_max=df["profitability"].max(),
        profitability_compound=df["profitability"].product(),
        fail_rate_mean=df["fail_rate"].mean()
    ))


if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    config = dict(
        total_budget=1000,
        max_steps=50,
        contingency_space_type="absolute",
        contingency_space_lb=0.3,
        contingency_space_ub=0.7,
        use_max_loss_policy=False,
        use_loss_improving_policy=True,
        maximal_absolute_loss=-10,
        improving_discount_rate=0.90,
        objective_type="min_pandl",
        min_pandl_space_type="absolute",
        objective_absolute_lb=0.6,
        objective_absolute_ub=1.4,
        experiment_last_group="BTC-210531"
    )

    run(config)
