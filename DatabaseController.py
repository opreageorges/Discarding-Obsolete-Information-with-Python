import datetime
from dataclasses import asdict

import pymongo
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from pymongo.database import Collection as MongoCollection
from Product import Product
from UpdateIndex import UpdateIndex

# Clasa care se ocupa de interactiunea cu baza de date


class DatabaseController:
    _allConnections = {}
    _connectionString: str
    _con: MongoClient
    _stock: MongoDatabase
    _products: MongoCollection
    _updates: MongoCollection

    def __new__(cls, connectionString: str):
        if connectionString in cls._allConnections.keys():
            return cls._allConnections[connectionString]
        return super().__new__(cls)

    def __init__(self, connectionString: str) -> None:
        super().__init__()
        DatabaseController._allConnections[connectionString] = self
        self._connectionString = connectionString
        self._con = MongoClient(connectionString)
        self._stock = self._con["stock"]
        self._updates = self._stock["updateIndex"]
        self._products = self._stock["products"]

    def _checkConnection(self):
        self._con.close()
        print(self._con.server_info())

    def addProduct(self,
                   description: str or None = None,
                   *args):

        if description is None or not isinstance(description, str):
            description = f"Adding new products to the data base in {datetime.datetime.now()}"

        if len(args) == 0:
            raise ValueError("You must provide at least one Product to be added")

        for elem in args:
            if not isinstance(elem, Product):
                raise TypeError(r'You can add only products in the "Products" table')

        dictArgs = [asdict(i) for i in args]
        insertResult = self._products.insert_many(dictArgs)

        maxVersion = self._updates.\
            find({"version": {"$gt": -1}}).\
            sort([("version", pymongo.DESCENDING)]).\
            next()["version"]

        currentUpdate = UpdateIndex(maxVersion + 1, description, insertResult.inserted_ids)
        self._updates.insert_one(asdict(currentUpdate))

    def __del__(self) -> None:
        DatabaseController._allConnections.pop(self._connectionString)
        self._con.close()
        return
