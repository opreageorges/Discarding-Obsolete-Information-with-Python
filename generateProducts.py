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

    dataBasesProducts.append(MongoClient(connectionString)["Stock"]["Products"])
    dataBasesUpdateIndex.append(MongoClient(connectionString)["Stock"]["UpdateIndex"])


# Doua liste constante cu elemente ca sa fac niste date random
availableProducts = ["Castraveti", "Varza", "Castraveti", "Paine", "Vaselina", "Alcool ", "Alcool Izopropilic",
                     "Lichid de Parbriz", "hrană pentru pisici", "hrană pentru câini", "săpun", "șampon",
                     "deodorant", "pizza", "legume" "congelate", "fructe congelate", "pui", "vită", "porc", "miel"]

availableWarehouse = ["Grozavesti1", "Grozavesti2", "Bragadiru1", "Pitesti1", "Baicoi1", "Pitesti2"]

# Dau purge la datele vechi
for elem in availableWarehouse:
    for dbP, dbInd in zip(dataBasesProducts, dataBasesUpdateIndex):
        dbP.delete_many({"Warehouse": elem})
        dbInd.delete_many({"Version": {"$gt": -1}})

# Creez niste date random
database_ready_elems = []
for elem in availableProducts:
    database_ready_elems.append({"_id": ObjectId(),
                                 "Name": elem,
                                 "Warehouse": availableWarehouse[random.randint(0, len(availableWarehouse) - 1)],
                                 "Price": random.randint(0, 1000),
                                 "Quantity": random.randint(0, 10000),
                                 "ExpirationDate": datetime.datetime.now() + datetime.timedelta(
                                     seconds=random.randint(0, 60000))}
                                )

# Adaug datele si un update index initial
for dbP, dbInd in zip(dataBasesProducts, dataBasesUpdateIndex):
    dbP.insert_many(database_ready_elems)
    dbInd.insert_one({"Version": 1, "Description": "Initialization", "Updated": []})

    dbP.database.client.close()
