import json

from collections import OrderedDict
from typing import Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel


class LongUrlData(BaseModel):
    url: str


def to_base62(num: int) -> str:
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base62 = ""

    while num > 0:
        remainder: int = num % 62
        base62: str = characters[remainder] + base62
        num //= 62

    return base62 if base62 else "0"


def insert_long_url(url: str) -> str:
    with open('long_urls.db', 'r+') as f:
        db: OrderedDict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        last_idx: int = list(db.values())[-1] if len(db) > 0 else 0
        current_idx: int = last_idx + 1
        db[url] = current_idx
        f.seek(0)
        f.write(json.dumps(db))
        short_url: str = to_base62(current_idx)
        insert_short_url(current_idx, short_url)
        return short_url


def insert_short_url(id: int, short_url: str) -> None:
    with open('short_urls.db', 'r+') as f:
        db: OrderedDict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        db[id] = short_url
        f.seek(0)
        f.write(json.dumps(db))


def get_short_url(url: str) -> Optional[str]:
    with open('long_urls.db', 'r') as f:
        db: OrderedDict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        short_url_id: str = str(db.get(url, None))

    if short_url_id is None:
        return None

    with open('short_urls.db', 'r') as f:
        db: OrderedDict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        return db.get(short_url_id, None)


app = FastAPI()


@app.get("/{short_url}")
def get_original_url(short_url: str):
    with open('short_urls.db', 'r') as f:
        db: OrderedDict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        for idx, item in enumerate(db.items()):
            print(item)
            print(idx, item)
    return ""


@app.post("/generate")
def generate_short_url(long_url_data: LongUrlData):
    short_url: Optional[str] = get_short_url(long_url_data.url)
    short_url = short_url if short_url is not None else insert_long_url(long_url_data.url)
    return f"http://localhost:8000/{short_url}"
