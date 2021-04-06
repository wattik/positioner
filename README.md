# Positioner
Positioner is not a sex postions app but rather a tool that takes a live order book 
in a options market and finds an optimal postion that maximizes average return. 

## Dependencies
- GLPK binary (LP solver)
- python 3.9

## Install

Install GLPK from https://www.gnu.org/software/glpk/. The light version containing GLPSOL only is enough.
Depending on the platform, a pre-compiled
package might be available. For instance, on Debian machines the following command serves the purpose:
```shell
sudo apt-get install glpk-utils
```
Then, create `config.ini` as in the example file `config.example.ini`
and set `glpk_path` to the path of the just-installed executable binary, usually something like
`/bin/glpsol`. 

```ini
[solver]
glpk_path=/bin/glpsol
```

Run the following command which installs the package locally in the current environment.
```shell
pip3 install -e .
```

## Dummy data and "tests"

Run the following command to test whether everything works as expected.
```shell
python examples/test.py
```
The standard output should show solver logs and a position of a single order:
```shell
[OrderType.BUY 20.000USD BTC-210409-62000-C-Side.ASK at 674.560USD]
```