# TODO

- [x] install packages
    - ```pip install -e C:\Users\pt4ce\Projects\binance\positioner-alert```
- [x] run test from examples, confirm GLPK works as intended
- [x] add binance keys to config.ini
- [x] extract config.py to a separate package (utils)
- [x] implement periodical fetching of order_book
- [ ] brainstorm capabilities of realtime solver with websockets

nohup python3.9 watcher/watch.py > output.log &

ps ax | grep watcher.py

python3.9 -m pip install -e .