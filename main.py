import os
import threading
import time
import json
import pandas as pd
from random import randint
from DatabaseController import DatabaseController
from Models.Product import Product

stopThreads = threading.Event()
garbageCollectingActive = threading.Event()
dataSyncingActive = threading.Event()
dataUpdateCheckingActive = threading.Event()


def createRandomProduct():
    availableProducts = ["Cheese Pizza", "Veggie Pizza", "Pepperoni Pizza", "Meat Pizza", "Margherita Pizza",
                         "BBQ Chicken Pizza", "Hawaiian Pizza", "Buffalo Pizza"]

    availableWarehouse = ["Grozavesti1", "Grozavesti2", "Bragadiru1", "Pitesti1", "Baicoi1", "Pitesti2"]
    return Product(availableProducts[randint(0, len(availableProducts) - 1)],
                   availableWarehouse[randint(0, len(availableWarehouse) - 1)],
                   randint(0, 1000),
                   randint(0, 10000)
                   )


def initDataBasesConnections() -> [DatabaseController]:
    databases = []

    f = open("MiscFiles/MongoDBConnectionStrings", "r")
    fileContent = f.read()
    f.close()

    if len(fileContent.strip()) == 0:
        raise ValueError("You did not provide any connection strings")

    conStrings = fileContent.split("\n")
    for connectionString in conStrings:
        connectionString = connectionString.strip()

        if connectionString[0] == '#':
            continue
        databases.append(DatabaseController(connectionString))

    if len(databases) == 0:
        raise ValueError("You did not provide any connection strings")

    return databases


def readConfigFile():
    with open('MiscFiles/config.json', 'r') as f:
        config = json.load(f)

    return config


def garbageCollection(garbageCollectionTimer, databases: [DatabaseController]):
    while not stopThreads.is_set():

        while dataSyncingActive.is_set() or dataUpdateCheckingActive.is_set():
            time.sleep(10)

        garbageCollectingActive.set()
        for db in databases:
            db.garbageCollection()
        garbageCollectingActive.clear()
        time.sleep(garbageCollectionTimer)


def dataSync(dataSyncTimer):
    while not stopThreads.is_set():

        while garbageCollectingActive.is_set() or dataUpdateCheckingActive.is_set():
            time.sleep(10)

        dataSyncingActive.set()
        DatabaseController.syncAllDatabases()
        dataSyncingActive.clear()

        time.sleep(dataSyncTimer)


def dataRead(databases: [DatabaseController]):
    while dataSyncingActive.is_set() or garbageCollectingActive.is_set():
        time.sleep(10)

    dataUpdateCheckingActive.set()

    for entry in os.listdir("."):
        if "lock.FrontEnd.xlsx" in str(entry):
            print("Visualization file is open. Close it before update!")
            return

    with pd.ExcelWriter("FrontEnd.xlsx", engine='xlsxwriter') as writer:
        for db in databases:
            products = [i.toDict() for i in db.getProducts()]
            [i.pop("_id") for i in products]

            frame = pd.DataFrame(products)
            sheetName = db.getConnectionString().replace('/', '').replace(':', ' ')

            frame.to_excel(writer, sheet_name=sheetName)

            col_idx = frame.columns.get_loc('expirationDate') + 1
            writer.sheets[sheetName].set_column(col_idx, col_idx, 20)

            col_idx = frame.columns.get_loc('name') + 1
            writer.sheets[sheetName].set_column(col_idx, col_idx, 35)

            col_idx = frame.columns.get_loc('warehouse') + 1
            writer.sheets[sheetName].set_column(col_idx, col_idx, 15)

    dataUpdateCheckingActive.clear()


def dataWrite(databases: [DatabaseController]):
    while dataSyncingActive.is_set() or garbageCollectingActive.is_set():
        time.sleep(10)

    dataUpdateCheckingActive.set()

    dataExists = False
    for entry in os.listdir("."):
        if "lock.FrontEnd.xlsx" in str(entry):
            print("Visualization file is open. Close it before update!")
            return
        elif "FrontEnd.xlsx" in str(entry):
            dataExists = True

    if not dataExists:
        print("There is no file to read data from. Try 'r' command first")

    for db in databases:
        sheetName = db.getConnectionString().replace('/', '').replace(':', ' ')
        dictRaw = pd.read_excel("FrontEnd.xlsx",
                                sheet_name=sheetName
                                ).to_dict()

        for ind, elem in dictRaw["expirationDate"].items():
            # elem:pd.Timestamp
            dictRaw["expirationDate"][ind] = elem.to_pydatetime()
        uselessData = []
        for i in dictRaw.keys():
            if "unnamed" in str(i).lower():
                uselessData.append(i)
        [dictRaw.pop(i) for i in uselessData]

        columns = len(dictRaw.keys())
        dictRawLen = len(dictRaw[list(dictRaw.keys())[0]])
        productsNew = [Product(*[dictRaw[list(dictRaw.keys())[i]][j] for i in range(columns)]) for j in range(dictRawLen)]

        productsOld = [i.toDict() for i in db.getProducts()]
        for i in productsOld:
            i["_id"] = None
        productsOld = [Product(**i) for i in productsOld]

        unmodifiedData = []

        for elem in productsNew:
            if elem in productsOld:
                unmodifiedData.append(elem)
                productsOld.remove(elem)

        [productsNew.remove(elem) for elem in unmodifiedData]

        if productsOld:
            db.deleteProducts(None, *productsOld)
        if productsNew:
            db.addProducts(None, *productsNew)

    dataUpdateCheckingActive.clear()


def main():
    config = readConfigFile()
    threadsList = []
    databases: [DatabaseController] = initDataBasesConnections()

    threadsList.append(threading.Thread(target=garbageCollection,
                                        args=(config["GarbageCollectionTimer"], databases),
                                        daemon=True))

    threadsList.append(threading.Thread(target=dataSync,
                                        args=(config["DataSyncTimer"],),
                                        daemon=True))

    for t in threadsList:
        t.start()

    while True:
        cmd = input(">").strip()
        if cmd == "s":
            break
        elif cmd == "r":
            dataRead(databases)
        elif cmd == "w":
            dataWrite(databases)
        elif cmd == "fs":
            dataUpdateCheckingActive.set()
            DatabaseController.syncAllDatabases()
            dataUpdateCheckingActive.clear()
        elif cmd == "help":
            print("Available command: \n"
                  "s - To stop this application\n"
                  "r - To read data from databases\n"
                  "w - to write data to databases\n ")
        else:
            print("Try help for information\n")
    stopThreads.set()


if __name__ == "__main__":
    main()
