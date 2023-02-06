import copy
import datetime
from bson import ObjectId
import pymongo
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from pymongo.database import Collection as MongoCollection
from Models.Product import Product
from Models import UpdateIndex
from typing import Optional


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

    def getProducts(self, getFilter: Optional[dict] = None) -> [Product]:
        if getFilter is None:
            getFilter = {}

        cursor = self._products.find(getFilter)
        output = []
        for elem in cursor:
            output.append(Product(**elem))
        return output

    def getUpdates(self, getFilter: Optional[dict] = None) -> [UpdateIndex.UpdateIndex]:
        if getFilter is None:
            getFilter = {}

        cursor = self._updates.find(getFilter).sort([("version", pymongo.ASCENDING)])
        output = []
        for elem in cursor:
            output.append(UpdateIndex.UpdateIndex(**elem))
        return output

    def addProducts(self,
                    description: Optional[str] = None,
                    *args) -> None:

        if description is None or not isinstance(description, str):
            description = f"Adding new products to the database in {datetime.datetime.now()}"

        if len(args) == 0:
            raise ValueError("You must provide at least one Product to be added")

        for elem in args:
            if not isinstance(elem, Product):
                raise TypeError(r'You can add only products in the "Products" table')

        dictArgs = [i.toDict() for i in args]
        insertResult = self._products.insert_many(dictArgs)

        if description == UpdateIndex.TypeSYNC:
            return

        self._createUpdate(description, UpdateIndex.TypeINSERT, insertResult.inserted_ids)

    def updateProducts(self, description: Optional[str] = None, *args) -> None:
        if len(args) == 0:
            raise ValueError("You must provide at least one Product to be added")

        for elem in args:
            if not isinstance(elem, Product):
                raise TypeError(r'You can add only products in the "Products" table')

        if description is None or not isinstance(description, str):
            description = f"Updated products to the database in {datetime.datetime.now()}"

        updatedIds = []
        for elem in args:
            updatedIds.append(elem.getId())
            updateFilter = {"_id": elem.getId()}
            updateValues = {"$set": elem.toDict()}
            self._products.update_one(updateFilter, updateValues)

        if description == UpdateIndex.TypeSYNC:
            return
        self._createUpdate(description, UpdateIndex.TypeUPDATE, updatedIds)
        return

    def deleteProducts(self, description: Optional[str] = None, *args) -> None:
        if len(args) == 0:
            raise ValueError("You must provide at least one Product to be removed")

        productsToRemoveIds = []

        for elem in args:
            if not isinstance(elem, Product):
                raise TypeError(r'You can remove only products in the "Products" table')
            productsToRemoveIds.append(elem.getId())

        if description is None or not isinstance(description, str):
            description = f"Deleted products to the database in {datetime.datetime.now()}"

        self._products.delete_many({"$or": [{"_id": elem} for elem in productsToRemoveIds]})
        self._createUpdate(description, UpdateIndex.TypeDELETE, productsToRemoveIds)

    def _deleteById(self, *args):
        self._products.delete_many({"$or": [{"_id": elem} for elem in args]})

    def _createUpdate(self, description: Optional[str], updateType: str, arrayOfIds: [ObjectId], version: int = -1):
        maxVersion: int = version
        if version == -1:
            maxVersion = self._updates. \
                find({"version": {"$gt": -1}}). \
                sort([("version", pymongo.DESCENDING)]). \
                next()["version"]

        currentUpdate = UpdateIndex.UpdateIndex(maxVersion + 1, description, arrayOfIds, updateType)
        self._updates.insert_one(currentUpdate.toDict())

    def _purgeUpdates(self, purgeunder: int = -1):
        self._updates.delete_many({"version": {"$lte": purgeunder}})

    def garbageCollection(self):
        products = self.getProducts()
        productsToRemove = []
        for elem in products:
            if (elem.expirationDate - datetime.datetime.now()).total_seconds() < 0:
                productsToRemove.append(elem)

        if len(productsToRemove) == 0:
            return

        self.deleteProducts("Deleted products to the database due to a regular garbage collection cycle",
                            *productsToRemove)
        return

    @staticmethod
    def _mergeUpdateList(inDict1: {}, inDict2: {}) -> {}:
        out = {}
        dictOfUpdates1 = copy.deepcopy(inDict1)
        dictOfUpdates2 = copy.deepcopy(inDict2)
        for key in dictOfUpdates1:
            if key in dictOfUpdates2.keys() and dictOfUpdates2[key]["timeStamp"] > dictOfUpdates1[key]["timeStamp"]:
                out[key] = dictOfUpdates2[key]
                dictOfUpdates2.pop(key)
            else:
                out[key] = dictOfUpdates1[key]
        for key in dictOfUpdates2:
            out[key] = dictOfUpdates2[key]
        return out

    @staticmethod
    def syncAllDatabases():
        taskDict = {}
        maxVersion = 1
        for dbConString in DatabaseController._allConnections:
            db: DatabaseController = DatabaseController._allConnections[dbConString]
            updates = db.getUpdates()
            taskDict[dbConString] = {}
            for update in updates:
                if update.version > maxVersion:
                    maxVersion = update.version
                for elem in update.updated:
                    elem: ObjectId
                    taskDict[dbConString][elem] = {"updateType": update.updateType, "timeStamp": elem.generation_time}
                    if update.updateType != UpdateIndex.TypeDELETE:
                        taskDict[dbConString][elem]["product"] = db.getProducts({"_id": elem})[0]

        for dbConString in DatabaseController._allConnections:
            db: DatabaseController = DatabaseController._allConnections[dbConString]
            updatesForCurrentDb = {}
            for elem in taskDict:
                if elem == dbConString:
                    continue
                updatesForCurrentDb = DatabaseController._mergeUpdateList(updatesForCurrentDb, taskDict[elem])
            print()
            uselessData = []
            for elem in taskDict[dbConString]:
                if elem not in updatesForCurrentDb.keys():
                    continue
                if updatesForCurrentDb[elem]["timeStamp"] <= taskDict[dbConString][elem]["timeStamp"]:
                    updatesForCurrentDb.pop(elem)
                else:
                    uselessData.append(elem)

            [taskDict[dbConString].pop(i) for i in uselessData]
            deleteUpdates = [k for k, v in updatesForCurrentDb.items()
                             if v["updateType"] == UpdateIndex.TypeDELETE]
            insertUpdates = [v["product"] for k, v in updatesForCurrentDb.items()
                             if v["updateType"] == UpdateIndex.TypeINSERT]
            updateUpdates = [v["product"] for k, v in updatesForCurrentDb.items()
                             if v["updateType"] == UpdateIndex.TypeUPDATE]

            if deleteUpdates:
                db._deleteById(*deleteUpdates)
            if insertUpdates:
                db.addProducts(UpdateIndex.TypeSYNC, *insertUpdates)
            if updateUpdates:
                db.updateProducts(UpdateIndex.TypeSYNC, *updateUpdates)

            db._purgeUpdates(maxVersion)
            db._createUpdate("Database sync", UpdateIndex.TypeSYNC, [], maxVersion)

    def __del__(self):
        DatabaseController._allConnections.pop(self._connectionString)
