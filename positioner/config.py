import configparser

CONFIG = None

def default(*args):
    global CONFIG

    if not CONFIG:
        CONFIG = configparser.ConfigParser()
        CONFIG.read("config.ini")

    sel = CONFIG
    for key in args:
        sel = sel[key]
    return str(sel)
