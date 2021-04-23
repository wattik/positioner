# Setup
First set FLASK_APP env variable to server.py
```
$ export FLASK_ENV=development
$ flask run
```

# Example
### Order books
 - To get order books request a GET /order-books endpoint
 - Full path is ```89.221.222.209/flask-api/order-books?start=<START>&end=<END>```
 - The route accepts optional query params for start and end. Both are timestamps in the following format ```DD-MM-YYYY-HH-mm-SS``` and are **inclusive**.
    - For example accessing the endpoint ```/order-books?start=19-04-2021-10-21-23&end=19-04-2021-12-03-00``` will download all order books from **19.04.2021 10:21:23** to **19.04.2021 12:03:00**
    - If you do not provide any parameter, all order books will be downloaded.
    - If you provide only start parameter, all order books from the given start timestamp until most recent will be downloaded.
    - If you provide only end parameter, all order books from the beginning of collecting till the given end timestamp will be downloaded.

