from pymongo import MongoClient, DESCENDING
from dataclasses import asdict
from typing import Any

from models import BaseMethodResponse


class MongoDB:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def store_response(self, response: BaseMethodResponse):
        collection = self._retrieve_collection(response)
        collection.insert_one(asdict(response))

    def retrieve_last_n_by_timestamp(self, collection_name, n=100) -> list[Any]:
        collection = self.db[collection_name]
        cursor = collection.find().sort('timestamp', DESCENDING).limit(n)
        return list(cursor)

    def _retrieve_collection(self, response: BaseMethodResponse):
        collection_name = response.get_method_name()
        collection = self.db[collection_name]
        return collection
