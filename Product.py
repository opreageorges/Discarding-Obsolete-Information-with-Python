from datetime import datetime, timedelta
from dataclasses import dataclass
from random import randint

# Clasa echivalenta cu datele din tabelul Produ.


@dataclass
class Product:
    name: str
    warehouse: str
    price: int
    quantity: int
    expirationDate: datetime = datetime.now() + timedelta(seconds=randint(0, 600))

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