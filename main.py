import threading
import time
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


# TODO remove hardcoded stuff read from file
def readConfigFile():
    return {
        "DataUpdateTimer": 60,
        "GarbageCollectionTime": 60,
        "DataSyncTimer": 65
    }


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


def dataUpdateChecker(dataUpdateTimer):
    while not stopThreads.is_set():
        while dataSyncingActive.is_set() or garbageCollectingActive.is_set():
            time.sleep(10)

        dataUpdateCheckingActive.set()
        DatabaseController.syncAllDatabases()
        dataUpdateCheckingActive.clear()

        time.sleep(dataUpdateTimer)
    return


def main():
    config = readConfigFile()
    threadsList = []
    databases: [DatabaseController] = initDataBasesConnections()

    threadsList.append(threading.Thread(target=garbageCollection,
                                        args=(config["GarbageCollectionTime"], databases),
                                        daemon=True))

    threadsList.append(threading.Thread(target=dataSync,
                                        args=(config["DataSyncTimer"],),
                                        daemon=True))
    # TODO
    # threadsList.append(threading.Thread(target=dataUpdateChecker,
    #                                     args=(config["DataUpdateTimer"], databases),
    #                                     daemon=True))

    for t in threadsList:
        t.start()
    # p = [createRandomProduct(), createRandomProduct(), createRandomProduct(), createRandomProduct(),
    #      createRandomProduct(), createRandomProduct()]
    # databases[0].addProducts("test", *p)
    while True:
        cmd = input(">").strip()
        if cmd == "stop":
            break
    # stopThreads.set()


if __name__ == "__main__":
    main()
