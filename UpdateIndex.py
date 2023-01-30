from dataclasses import dataclass
from Product import Product

# Clasa echivalenta cu datele din tabelul UpdateIndex.


@dataclass
class UpdateIndex:
    Version: int
    Description: str
    Updated: [Product]

    # def toDict(self) -> {}:
    #     return {
    #         "Version": self.version,
    #         "Description": self.description,
    #         "Updated": self.updated,
    #     }
