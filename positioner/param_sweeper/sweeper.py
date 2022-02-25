import wandb
import logging
from pprint import pformat

from positioner.simulation.rollout import simulate


def to_sim_params(conf: dict) -> dict:
    p = dict()
    p["total_budget"] = conf["total_budget"]

    if conf["contingency_space_type"] == "absolute":
        p["contingency_space_bounds"] = conf["contingency_space_bounds"]
    elif conf["contingency_space_type"] == "relative":
        p["contingency_space_delta"] = conf["contingency_space_delta"]
    else:
        raise ValueError(conf["contingency_space_type"])

    if conf["use_max_loss_policy"]:
        p["use_max_loss_policy"] = conf["use_max_loss_policy"]
        if conf["max_loss_policy_type"] == "absolute":
            p["maximal_absolute_loss"] = conf["maximal_absolute_loss"]
        elif conf["max_loss_policy_type"] == "relative":
            p["maximal_relative_loss"] = conf["maximal_relative_loss"]
        else:
            raise ValueError(conf["max_loss_policy_type"])

    if conf["use_loss_improving_policy"]:
        p["use_loss_improving_policy"] = conf["use_loss_improving_policy"]
        p["improving_discount_rate"] = conf["improving_discount_rate"]

    p["objective_type"] = conf["objective_type"]
    if conf["objective_type"] == "expected_pandl":
        p["max_shift"] = conf["max_shift"]
    elif conf["objective_type"] == "min_pandl":
        if conf["min_pandl_space_type"] == "absolute":
            p["objective_absolute_bounds"] = conf["objective_absolute_bounds"]
        elif conf["min_pandl_space_type"] == "relative":
            p["objective_relative_bounds"] = conf["objective_relative_bounds"]
        else:
            raise ValueError(conf["min_pandl_space_type"])
    else:
        raise ValueError([conf["objective_type"]])

    return p


def simulate_option_group(option_group: str, config: dict):
    stride = config["stride"]

    order_books = ...[::stride]
    index_prices = ...[::stride]
    timestamps = ...[::stride]

    sim_params = to_sim_params(config)

    res = simulate(
        order_books=order_books,
        index_prices=index_prices,
        timestamps=timestamps,
        **sim_params
    )

    return res


def run(config: dict):
    option_groups = ...

    wandb.init(project="test-project", config=config, )
    logging.info(f"New Run")
    logging.info(pformat(config))
    logging.info(f"Option Groups: {option_groups}")
    logging.info("="*50)

    for og in option_groups:
        logging.info(f"Processing: {og}")
        res = simulate_option_group(og, config)
