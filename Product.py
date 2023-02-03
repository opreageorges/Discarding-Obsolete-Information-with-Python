from datetime import datetime, timedelta
from dataclasses import dataclass
from random import randint
from bson import ObjectId
from typing import Optional
# Clasa echivalenta cu datele din tabelul Produ.


@dataclass
class Product:
    name: str
    warehouse: str
    price: int
    quantity: int
    expirationDate: datetime = datetime.now() + timedelta(seconds=randint(0, 600))
    _id: Optional[ObjectId] = None

    def getId(self):
        return self._id

    # Exista fuctia asdict, care, momentan, implementeaza perfect tranformarea
    # in date compatibile cu insertul in baza de date
    # def toDict(self) -> {}:
    #     return {
    #         "Name": self.name,
    #         "Warehouse": self.warehouse,
    #         "Price": self.price,
    #         "Quantity": self.quantity,
    #         "ExpirationDate": self.expirationDate,
    #     }
