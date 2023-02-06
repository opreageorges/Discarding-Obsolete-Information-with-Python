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

    def toDict(self) -> {}:
        out = {
            "name": self.name,
            "warehouse": self.warehouse,
            "price": self.price,
            "quantity": self.quantity,
            "expirationDate": self.expirationDate,
        }
        if self._id is not None:
            out["_id"] = self._id

        return out
