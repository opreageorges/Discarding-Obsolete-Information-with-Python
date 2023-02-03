import datetime
from random import randint
from DatabaseController import DatabaseController
from Product import Product


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
    dataBases = []

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
        dataBases.append(DatabaseController(connectionString))

    if len(dataBases) == 0:
        raise ValueError("You did not provide any connection strings")

    return dataBases


# TODO remove hardcoded stuff read from file
def readConfigFile():
    return {
        "DataUpdateTimer": 60,
        "GarbageCollectionTime": 60,
        "DataSyncTime": datetime.datetime.now() + datetime.timedelta(minutes=1)
    }


def garbageCollection(gcTimer):
    return gcTimer


def dataSync(timeStamps):
    return


def dataUpdateChecker(timer):
    return


def main():
    while True:
        return


if __name__ == "__main__":
    config = readConfigFile()
    databases: [DatabaseController] = initDataBasesConnections()
    # [i._checkConnection() for i in databases]
    # dummyData = [createRandomProduct() for _ in range(15)]
    # databases[0].addProduct(*dummyData)


