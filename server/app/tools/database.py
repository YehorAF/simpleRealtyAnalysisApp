import asyncio
from motor.core import AgnosticCursor
import motor.core as core
import motor.motor_asyncio as mtr
import typing
import os


class Collection:
    def __init__(self, collection) -> None:
        self._collection: core.AgnosticCollection = collection


    async def add_one(self, data: dict):
        return await self._collection.insert_one(data)
    

    async def add_many(self, data: list[dict]):
        return await self._collection.insert_many(data)
    

    async def update(self, query: dict, data: dict, *args, **kwargs):
        return await self._collection.update_many(
            query, {"$set": data}, *args, **kwargs)
    

    async def delete(self, query: dict):
        return await self._collection.delete_many(query)
    

    async def get(self, query: dict, *args, **kwargs
                  ) -> typing.Tuple[AgnosticCursor, int]:
        return (self._collection.find(query, *args, **kwargs), 
                      await self._collection.count_documents(query))
    

    @property
    def r(self):
        return self._collection
    

class Apartments(Collection):
    pass


class Database:
    def __init__(self, url: str, dbname: str) -> None:
        self._client: core.AgnosticClient = mtr.AsyncIOMotorClient(url)
        self._db: core.AgnosticBase = self._client[dbname]
        self.apartments = Apartments(self._db.apartments)
        self.cities = Apartments(self._db.cities)
        self.clusters = Apartments(self._db.clusters)


    @property
    def db(self):
        return self._db