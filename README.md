# Positioner

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
