from fastapi import APIRouter

from tools.database import Database

_db = None
_towns_router = APIRouter()


def register_towns_router(db: Database):
    global _nlp
    global _db

    _db = db

    return _towns_router

@_towns_router.get("/towns")
async def get_towns():
    towns, _ = await _db.cities.get({}, {"_id": 0})
    return {"data": await towns.to_list(None)}