"""Bad Docs API — deliberately poor documentation for DriveBy validation testing."""

import os
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(
    title="Bad Docs API",
    version="0.1.0",
    description="An API",
)

# In-memory storage
items_db: dict[int, dict] = {}
next_id = 1

API_KEY = os.environ.get("API_KEY", "default-key")


class Item(BaseModel):
    name: str
    price: float
    quantity: int = 0


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


def verify_auth(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/test/health")
def health():
    return {"status": "healthy"}


@app.get("/items")
def list_items(auth=Depends(verify_auth)):
    return [{"id": k, **v} for k, v in items_db.items()]


@app.post("/items", status_code=201)
def create_item(item: Item, auth=Depends(verify_auth)):
    global next_id
    items_db[next_id] = item.model_dump()
    result = {"id": next_id, **items_db[next_id]}
    next_id += 1
    return result


@app.get("/items/{item_id}")
def get_item(item_id: int, auth=Depends(verify_auth)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items_db[item_id]}


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, auth=Depends(verify_auth)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
