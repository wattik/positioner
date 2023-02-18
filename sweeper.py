import logging
from itertools import islice
import numpy as np
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
            start_price * (1 - conf["contingency_space_delta"]),
            start_price * (1 + conf["contingency_space_delta"])
        )
    elif conf["contingency_space_type"] == "relative":
        p["contingency_space_delta"] = conf["contingency_space_delta"]
    else:
        raise ValueError(conf["contingency_space_type"])

    if conf["loss_policy_type"] == "threshold":
        p["use_max_loss_policy"] = True
        if conf["max_loss_policy_type"] == "absolute":
            p["maximal_absolute_loss"] = conf["maximal_absolute_loss"]
        elif conf["max_loss_policy_type"] == "relative":
            p["maximal_relative_loss"] = conf["maximal_relative_loss"]
        else:
            raise ValueError(conf["max_loss_policy_type"])
    elif conf["loss_policy_type"] == "improving":
        p["use_loss_improving_policy"] = True
        p["maximal_absolute_loss"] = conf["maximal_absolute_loss"]
        p["improving_discount_rate"] = conf["improving_discount_rate"]

    p["objective_type"] = conf["objective_type"]
    if conf["objective_type"] == "expected_pandl":
        p["max_shift"] = conf["max_shift"]
    elif conf["objective_type"] == "min_pandl":
        if conf["min_pandl_space_type"] == "absolute":
            p["objective_absolute_bounds"] = (
                start_price * (1 - conf["objective_absolute_delta"]),
                start_price * (1 + conf["objective_absolute_delta"])
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

    stride = len(timestamps) // max_steps + 1

    order_books = islice(order_books, None, None, stride)
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
    wandb.init(project="test-project", config=default_config)
    config = wandb.config

    logging.info(f"New Run")
    logging.info(pformat(config))

    option_groups = fetch_option_groups(
        config["experiment_first_group"],
        config["experiment_last_group"],
        min_expiration_days=config["min_expiration_days"],
        max_expiration_days=config["max_expiration_days"],
    )
    logging.info(f"Option Groups: {option_groups}")
    logging.info("=" * 50)

    results = []
    for i, og in enumerate(option_groups):
        logging.info(f"Processing: {og}")
        res = simulate_option_group(og, config)
        results.append(dict(
            option_group=og,
            profitability=res.profitability,
            fail_rate=res.fail_rate,
        ))

        logging.info("log to wandb: init")
        wandb.log({"group_profitability": res.profitability}, step=i)
        logging.info("log to wandb: successful")

    df = pd.DataFrame(results)

    wandb.log(dict(
        profitability_med=df["profitability"].median(),
        profitability_mean=df["profitability"].mean(),
        profitability_min=df["profitability"].min(),
        profitability_max=df["profitability"].max(),
        profitability_compound=df["profitability"].product(),
        fail_rate_mean=df["fail_rate"].mean(),
    ))


if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    config = dict(
        total_budget=1000,
        max_steps=100,
        contingency_space_type="absolute",
        contingency_space_delta=0.7,
        loss_policy_type="improving",
        max_loss_policy_type="absolute",
        maximal_absolute_loss=0,
        improving_discount_rate=0.50,
        objective_type="min_pandl",
        min_pandl_space_type="absolute",
        objective_absolute_delta=0.45,
        experiment_first_group="BTC-210507",
        experiment_last_group="BTC-220201",
        max_expiration_days=10000,
        min_expiration_days=20,
    )

    run(config)
