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
        "scipy",
        "cvxpy",
        "aiohttp",
        "nest_asyncio",
        "python-telegram-bot",
        "flask",
        "pymongo",
        "namespaces",
    ]
)
