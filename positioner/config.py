import configparser
import pathlib

CONFIG = None

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()


def default(*args):
    global CONFIG

    # if not CONFIG:
    #     CONFIG = configparser.ConfigParser()
    #     CONFIG.read("config.ini")
    CONFIG = configparser.ConfigParser()
    CONFIG.read(PROJECT_ROOT / "config.ini")

    sel = CONFIG
    for key in args:
        sel = sel[key]
    return str(sel)
