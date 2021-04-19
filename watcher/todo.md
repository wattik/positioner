# TODO

- [x] install packages
    - ```pip install -e C:\Users\pt4ce\Projects\binance\positioner-alert```
- [x] run test from examples, confirm GLPK works as intended
- [x] add binance keys to config.ini
- [x] extract config.py to a separate package (utils)
- [ ] implement periodical fetching of order_book
  1) call ```collect_traded_expiry_dates``` to get list of all dates
  2) for each date in expiry dates, fetch order books
  - save order book every 1 MIN
  - run solver ever 5th order book
  - based on a condition (big profit), send notification of solver result
- [ ] brainstorm capabilities of realtime solver
