from setuptools import setup

# POSITIONER PACKAGES
setup(
    name='positioner',
    version='0.1',
    packages=["positioner"],
    install_requires=[
        "amply",
        "matplotlib",
        "numpy",
        "pandas",
        "PuLP",
        "scipy",
        "aiohttp",
        "nest_asyncio"
    ]
)

# WATCHER PACKAGES
setup(
    name='watcher',
    version='0.1',
    packages=["watcher"],
    install_requires=[
        "python-telegram-bot"
    ]
)