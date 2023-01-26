from pymongo import MongoClient
import random
from bson import ObjectId
import datetime

f = open("./MongoDBConnectionStrings", "r")
strings = f.read()
f.close()
conStrings = strings.split("\n")

dataBasesUpdateIndex = []
dataBasesProducts = []
for connectionString in conStrings:
    connectionString = connectionString.strip()

    if connectionString[0] == '#':
        continue

    dataBasesProducts.append(MongoClient(connectionString)["Stock"]["Products"])
    dataBasesUpdateIndex.append(MongoClient(connectionString)["Stock"]["UpdateIndex"])


availableProducts = ["Castraveti", "Varza", "Castraveti", "Paine", "Vaselina", "Alcool ", "Alcool Izopropilic",
                     "Lichid de Parbriz", "hrană pentru pisici", "hrană pentru câini", "săpun", "șampon",
                     "deodorant", "pizza", "legume" "congelate", "fructe congelate", "pui", "vită", "porc", "miel"]

availableDeposit = ["Grozavesti1", "Grozavesti2", "Bragadiru1", "Pitesti1", "Baicoi1", "Pitesti2"]

for elem in availableDeposit:
    for dbP, dbInd in zip(dataBasesProducts, dataBasesUpdateIndex):
        dbP.delete_many({"Deposit": elem})
        dbInd.delete_many({"Name": ""})

database_ready_elems = []
for elem in availableProducts:
    database_ready_elems.append({"_id": ObjectId(),
                                 "Name": elem,
                                 "Deposit": availableDeposit[random.randint(0, len(availableDeposit) - 1)],
                                 "Price": random.randint(0, 1000),
                                 "Quantity": random.randint(0, 10000),
                                 "ExpirationDate": datetime.datetime.now() + datetime.timedelta(
                                     minutes=random.randint(0, 3650))}
                                )
for dbP, dbInd in zip(dataBasesProducts, dataBasesUpdateIndex):
    dbP.insert_many(database_ready_elems)
    dbInd.insert_one({"Name": "Self", "Version": 1})

    dbP.database.client.close()
