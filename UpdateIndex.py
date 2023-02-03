from dataclasses import dataclass
from Product import Product
from bson import ObjectId
from typing import Optional
# Clasa echivalenta cu datele din tabelul UpdateIndex.


@dataclass
class UpdateIndex:
    version: int
    description: str
    updated: [Product]
    _id: Optional[ObjectId] = None

    def getId(self):
        return self._id

    # def toDict(self) -> {}:
    #     return {
    #         "Version": self.version,
    #         "Description": self.description,
    #         "Updated": self.updated,
    #     }
