from random import randint
from Database import Database
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


def initDataBasesConnections() -> [Database]:
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
        dataBases.append(Database(connectionString))

    if len(dataBases) == 0:
        raise ValueError("You did not provide any connection strings")

    return dataBases


if __name__ == "__main__":
    databases: [Database] = initDataBasesConnections()
    dummyData = [createRandomProduct() for _ in range(15)]
    databases[0].addProduct(*dummyData)
