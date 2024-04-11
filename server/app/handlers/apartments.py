from fastapi import APIRouter, Query
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import spacy

import bson
from typing import Annotated


from tools.database import Database

_nlp = None
_db = None
_apartments_router = APIRouter()
_kmeans = None
_lm = None
_scaler = None


def register_apartments_router(
    db: Database, 
    nlp: spacy.language.Language,
    kmeans: KMeans,
    lm: LinearRegression,
    scaler: StandardScaler
):
    global _nlp
    global _db
    global _kmeans
    global _lm
    global _scaler

    _db = db
    _nlp = nlp
    _kmeans = kmeans
    _lm = lm
    _scaler = scaler

    return _apartments_router


@_apartments_router.get("/apartments")
async def get_apartments(
    skip: Annotated[int, Query(ge=0)] = 0, 
    limit: Annotated[int, Query(ge=0, le=100)] = 20, 
    q: Annotated[str | None, Query(max_length=250)] = None,
    min_price: Annotated[float, Query(ge=0, le=1_000_000_000_000)] = 0,
    max_price: Annotated[float, Query(ge=0, le=1_000_000_000_000)] = 1_000_000_000_000,
    min_size: Annotated[float, Query(ge=1, le=1_000_000_000_000)] = 1,
    max_size: Annotated[float, Query(ge=1, le=1_000_000_000_000)] = 1_000_000_000_000,
    min_rooms: Annotated[int, Query(ge=1, le=1_000_000_000_000)] = 1,
    max_rooms: Annotated[int, Query(ge=1, le=1_000_000_000_000)] = 1_000_000_000_000,
    towns: Annotated[list[str] | None, Query()] = None,
    tags: Annotated[list[str] | None, Query()] = None
):
    query = {}

    if q:
        texts = _nlp(q)
        words = [word.lemma_ for word in texts]
        query |= {"words": {"$elemMatch": {"$in": words}}}

    if towns:
        query |= {"location.city": {"$in": towns}}
        print(query)

    if tags:
        query |= {"tags": tags}

    cursor, amount = await _db.apartments.get(
        {
            "price": {"$gte": min_price, "$lte": max_price},
            "size": {"$gte": min_size, "$lte": max_size},
            "rooms": {"$gte": min_rooms, "$lte": max_rooms}
        } | query
    )
    data = []
    
    for document in await cursor.skip(skip).to_list(limit):
        data.append(document | {"_id": str(document["_id"])})

    return {"data": data, "amount": amount}


@_apartments_router.get("/apartments/{apartment_id}")
async def get_apartment(apartment_id: str):
    try:
        apartment_id = bson.ObjectId(apartment_id)
    except:
        pass

    cursor, count = await _db.apartments.get({"_id": apartment_id}, {"_id": 0})

    if count < 1:
        return {"data": None}
    
    apartment = (await cursor.to_list(1))[0]

    return {"data": apartment}


@_apartments_router.get("/statistic")
async def get_statistic(
    min_price: Annotated[float, Query(ge=0, le=1_000_000_000_000)] = 0,
    max_price: Annotated[float, Query(ge=0, le=1_000_000_000_000)] = 1_000_000_000_000,
    min_size: Annotated[float, Query(ge=1, le=1_000_000_000_000)] = 1,
    max_size: Annotated[float, Query(ge=1, le=1_000_000_000_000)] = 1_000_000_000_000,
    min_rooms: Annotated[int, Query(ge=1, le=1_000_000_000_000)] = 1,
    max_rooms: Annotated[int, Query(ge=1, le=1_000_000_000_000)] = 1_000_000_000_000,
    towns: Annotated[list[str] | None, Query()] = None,
):
    query = {}

    if towns:
        query |= {"location.city": {"$in": towns}}

    pipeline = [
        {
            "$match": {
                "price": {"$gte": min_price, "$lte": max_price},
                "size": {"$gte": min_size, "$lte": max_size},
                "rooms": {"$gte": min_rooms, "$lte": max_rooms}
            } | query
        },
        {
            "$group": {
                "_id": "$location.city", 
                "price": {"$avg": "$price"}, 
                "amount": {"$sum": 1}, 
                "rooms": {"$avg": "$rooms"}, 
                "size": {"$avg": "$size"}
            }
        }
    ]
    answer = await _db.apartments.r.aggregate(pipeline).to_list(None)
    
    return {"data": answer}


@_apartments_router.get("/compare")
async def compare(
    price: Annotated[float, Query(ge=0, le=1_000_000_000_000)],
    size: Annotated[float, Query(ge=0, le=1_000_000_000_000)],
    rooms: Annotated[int, Query(ge=1, le=1_000_000_000_000)],
    towns: Annotated[list[str], Query()] = None,
    price_eps: Annotated[float, Query(ge=1, le=1_000_000_000_000)] = None,
    size_eps: Annotated[float, Query(ge=1, le=1_000_000_000_000)] = None,
    rooms_eps: Annotated[int, Query(ge=1, le=1_000_000_000_000)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    cluster_id: int | None = None
):
    query = {}

    if towns:
        query |= {"location.city": {"$in": towns}}

    if not price_eps:
        price_eps = price / 10

    if not size_eps:
        size_eps = size / 10
    
    if not rooms_eps:
        rooms_eps = 0

    if cluster_id is not None:
        query |= {"cluster_id": cluster_id}

    cursor, _ = await _db.apartments.get({
        "price": {"$gte": price - price_eps, "$lte": price + price_eps},
        "size": {"$gte": size - size_eps, "$lte": size + size_eps},
        "rooms": {"$gte": rooms - rooms_eps, "$lte": rooms + rooms_eps}
    } | query)
    data = []

    for document in await cursor.to_list(limit):
        data.append(document | {"_id": str(document["_id"])})

    return {"data": data}


@_apartments_router.get("/predict")
async def predict(
    price: Annotated[float, Query(ge=20000, le=130000)],
    size: Annotated[float, Query(ge=10, le=120)],
):
    norm = _scaler.transform([[size, price]])
    ids = _kmeans.predict(norm)
    cluster_id = int(ids[0])

    clusters, _ = await _db.clusters.get({"cluster_id": cluster_id})
    cluster = (await clusters.to_list(1))[0]

    avg_size = cluster["avg_size"]
    avg_price = cluster["avg_price"]
    optimal_price = _lm.predict([[avg_price, size]])
    optimal_price = float(optimal_price[0])

    return {"data": {
        "cluster_id": cluster_id, 
        "optimal_price": optimal_price, 
        "avg_size": avg_size,
        "avg_price": avg_price
    }}