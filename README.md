# redis-om-fastapi

This repository contains an example of how to use [Redis OM Python](https://github.com/redis/redis-om-python) with FastAPI.

## Installing

First, Install app's dependencies into your Python environment:

    $ pip install -r requirements.txt
    
## Running the Examples

This project contains two identical FastAPI applications, one synchronous (main.py) and one asynchronous (async_main.py). Both use Redis OM for Python to save and retrieve data from Redis.

To try the API, first, start the one of the servers.

You can start the synchronous server like this, from your terminal:

```bash
uvicorn main:app
```

Or the async server like this:

```bash
uvicorn async_main:app
```

Then, in another shell, create a customer:

```bash
curl --location 'http://localhost:8000/customer' \
--header 'Content-Type: application/json' \
--data-raw '{"first_name":"Andrew","last_name":"Brookins","email":"a@example.com","age":"38","join_date":"2020-01-02"}'
```

Copy the "pk" value, which is the model's primary key, and make another request to get that customer:

```bash
curl --location 'http://localhost:8000/customer/01FM2G8EP38AVMH7PMTAJ123TA'
```

You can also get a list of all customer PKs:
```bash
curl --location 'http://localhost:8000/customers'
```