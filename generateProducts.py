from pymongo import MongoClient
import random
from bson import ObjectId
import datetime

# Scot toate adresele de conexiune
f = open("MiscFiles/MongoDBConnectionStrings", "r")
strings = f.read()
f.close()
conStrings = strings.split("\n")

# Fac o lista pentru fiecare tabel
dataBasesUpdateIndex = []
dataBasesProducts = []
for connectionString in conStrings:
    connectionString = connectionString.strip()

    if connectionString[0] == '#':
        continue

    dataBasesProducts.append(MongoClient(connectionString)["stock"]["products"])
    dataBasesUpdateIndex.append(MongoClient(connectionString)["stock"]["updateIndex"])


# Doua liste constante cu elemente ca sa fac niste date random
availableProducts = ["Castraveti", "Varza", "Castraveti", "Paine", "Vaselina", "Alcool ", "Alcool Izopropilic",
                     "Lichid de Parbriz", "hrană pentru pisici", "hrană pentru câini", "săpun", "șampon",
                     "deodorant", "pizza", "legume" "congelate", "fructe congelate", "pui", "vită", "porc", "miel"]

availableWarehouse = ["Grozavesti1", "Grozavesti2", "Bragadiru1", "Pitesti1", "Baicoi1", "Pitesti2"]

# Dau purge la datele vechi
for elem in availableWarehouse:
    for dbP, dbInd in zip(dataBasesProducts, dataBasesUpdateIndex):
        x = dbP.delete_many({"warehouse": elem})
        y = dbInd.delete_many({"version": {"$gt": -1}})

# Creez niste date random
database_ready_elems = []
for elem in availableProducts:
    database_ready_elems.append({"_id": ObjectId(),
                                 "name": elem,
                                 "warehouse": availableWarehouse[random.randint(0, len(availableWarehouse) - 1)],
                                 "price": random.randint(0, 1000),
                                 "quantity": random.randint(0, 10000),
                                 "expirationDate": datetime.datetime.now() + datetime.timedelta(
                                     seconds=random.randint(0, 60000))}
                                )

# Adaug datele si un update index initial
for dbP, dbInd in zip(dataBasesProducts, dataBasesUpdateIndex):
    dbP.insert_many(database_ready_elems)
    dbInd.insert_one({"version": 1, "description": "Initialization", "updated": []})

    dbP.database.client.close()
