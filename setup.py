from setuptools import setup

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
    ]
)