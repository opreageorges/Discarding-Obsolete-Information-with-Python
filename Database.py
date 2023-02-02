import datetime
from dataclasses import asdict

import pymongo
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from pymongo.database import Collection as MongoCollection
from Product import Product
from UpdateIndex import UpdateIndex

# Clasa care se ocupa de interactiunea cu baza de date


class Database:
    _con: MongoClient
    _stock: MongoDatabase
    _products: MongoCollection
    _updates: MongoCollection

    def __init__(self, connectionString: str) -> None:
        super().__init__()
        self._con = MongoClient(connectionString)
        self._stock = self._con["stock"]
        self._updates = self._stock["updateIndex"]
        self._products = self._stock["products"]

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
        ids = self._products.insert_many(dictArgs)

        maxVersion = self._updates.\
            find({"version": {"$gt": -1}}).\
            sort([("version", pymongo.DESCENDING)]).\
            next()["version"]

        currentUpdate = UpdateIndex(maxVersion + 1, description, dictArgs)
        self._updates.insert_one(asdict(currentUpdate))
