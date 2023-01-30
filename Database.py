from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase


class Database:
    _con: MongoClient
    _products: MongoDatabase
    _updates: MongoDatabase

    def __init__(self, connectionString: str) -> None:
        super().__init__()
        self._con = MongoClient(connectionString)
        self._updates = self._con["Updates"]
        self._products = self._con["Products"]
