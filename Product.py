from datetime import datetime, timedelta
from dataclasses import dataclass
from random import randint

# Clasa echivalenta cu datele din tabelul Produ.


@dataclass
class Product:

    Name: str
    Warehouse: str
    Price: int
    Quantity: int
    ExpirationDate: datetime = datetime.now() + timedelta(seconds=randint(0, 600))

    # def toDict(self) -> {}:
    #     return {
    #         "Name": self.name,
    #         "Warehouse": self.warehouse,
    #         "Price": self.price,
    #         "Quantity": self.quantity,
    #         "ExpirationDate": self.expirationDate,
    #     }
