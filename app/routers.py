from fastapi import APIRouter


items_router = APIRouter(prefix="/items", tags=["items"])


@items_router.get("/")
def list_items():
    return [{"id": 1, "name": "item-one"}, {"id": 2, "name": "item-two"}]


@items_router.get("/{item_id}")
def get_item(item_id: int):
    return {"id": item_id, "name": f"item-{item_id}"}
