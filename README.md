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


## Sync with upstream
```
git fetch upstream
git checkout master
git merge upstream/master
```


## Run Parameter Sweep
To run a parameter sweep, set accordingly parameters in `sweep.yaml`. Then create a new sweep:
```shell
wandb sweep sweep.yaml
```
The command registers the sweep into the wandb database and yields a unique identifier e.g. `ptajman/min_pandl_1000/5uz5flxe` 
which is used later on to start an agent within the sweep context. 

Modify `docker-compose.yml` and add the unique identifier of the sweep under the `command` key. 

Then launch for example 4 sweep agents (potentially using `sudo`):
```shell
 docker-compose up -d --build --scale sweeper=4
```
The `-d` starts the containers in background. `--build` rebuilds the source image to ensure it contains all recent modifications.
`--scale SERVICE=NUM` launches `NUM` replicas of `SERVICE` (defined in `docker-compose.yml`).
