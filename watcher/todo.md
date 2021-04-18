# TODO

- [x] install packages
    - ```pip install -e C:\Users\pt4ce\Projects\binance\positioner-alert```
- [x] run test from examples, confirm GLPK works as intended
- [x] add binance keys to config.ini
- [x] extract config.py to a separate package (utils)
- [ ] test out the new python-binance vanilla option functions
- [ ] implement periodical fetching of order_book
  - saving it to a file
  - run solver on the order_book file and save result of solver to a file
    - pair it with the order_book file
  - based on a condition (big profit), send notification of solver result
- [ ] brainstorm capabilities of realtime solver
