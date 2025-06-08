"""
Integration with FastAPI.
=========================

To test, first, start the server:

    $ poetry run uvicorn async_main:app

Then, in another shell, create a customer:

    $ curl -X POST  "http://localhost:8000/customer" -H 'Content-Type: application/json' -d '{"first_name":"Andrew","last_name":"Brookins","email":"a@example.com","age":"38","join_date":"2020
-01-02"}'
    {"pk":"01FM2G8EP38AVMH7PMTAJ123TA","first_name":"Andrew","last_name":"Brookins","email":"a@example.com","join_date":"2020-01-02","age":38,"bio":""}

Get a copy of the value for "pk" and make another request to get that customer:

    $ curl "http://localhost:8000/customer/01FM2G8EP38AVMH7PMTAJ123TA"
    {"pk":"01FM2G8EP38AVMH7PMTAJ123TA","first_name":"Andrew","last_name":"Brookins","email":"a@example.com","join_date":"2020-01-02","age":38,"bio":""}

You can also get a list of all customer PKs:

    $ curl "http://localhost:8000/customers"
    {"customers":["01FM2G8EP38AVMH7PMTAJ123TA"]}
"""
import datetime
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Optional

from aredis_om.connections import get_redis_connection
from aredis_om.model import HashModel, NotFoundError
from fastapi import FastAPI, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pydantic import EmailStr
from redis import asyncio as aioredis
from starlette.requests import Request
from starlette.responses import Response

# This Redis instance is tuned for durability.
REDIS_DATA_URL = "redis://localhost:6379"

# This Redis instance is tuned for cache performance.
REDIS_CACHE_URL = "redis://localhost:6379"


class Customer(HashModel):
    first_name: str
    last_name: str
    email: EmailStr
    join_date: datetime.date
    age: int
    bio: Optional[str]

    # You can set the Redis OM URL using the REDIS_OM_URL environment
    # variable, or by manually creating the connection using your model's
    # Meta object.
    class Meta:
        database = get_redis_connection(url=REDIS_DATA_URL, decode_responses=True)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(REDIS_CACHE_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/customer")
async def save_customer(customer: Customer):
    # We can save the model to Redis by calling `save()`:
    return await customer.save()


@app.get("/customers")
async def list_customers(request: Request, response: Response):
    # To retrieve this customer with its primary key, we use `Customer.get()`:
    return {"customers": [pk async for pk in await Customer.all_pks()]}


@app.get("/customer/{pk}")
@cache(expire=10)
async def get_customer(pk: str, request: Request, response: Response):
    # To retrieve this customer with its primary key, we use `Customer.get()`:
    try:
        return await Customer.get(pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Customer not found")
