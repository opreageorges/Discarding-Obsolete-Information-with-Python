from dataclasses import dataclass
from bson import ObjectId
from typing import Optional
# Clasa echivalenta cu datele din tabelul UpdateIndex.

TypeDELETE = "delete"
TypeINSERT = "insert"
TypeUPDATE = "update"
TypeSYNC = "sync"


@dataclass
class UpdateIndex:
    version: int
    description: str
    updated: [ObjectId]
    updateType: str
    _id: Optional[ObjectId] = None

    def getId(self):
        return self._id

    def toDict(self) -> {}:
        out = {
            "version": self.version,
            "description": self.description,
            "updated": self.updated,
            "updateType": self.updateType
        }
        if self._id is not None:
            out["_id"] = self._id
        return out
