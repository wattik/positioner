import configparser

CONFIG = None


def default(*args):
    global CONFIG

    # todo consider reading config each time - that way we can alter values at runtime without recompiling
    if not CONFIG:
        CONFIG = configparser.ConfigParser()
        CONFIG.read("../config.ini")

    sel = CONFIG
    for key in args:
        sel = sel[key]
    return str(sel)
