from typing import Dict, Optional
from app.models.base_model import BaseModel

class InMemoryRepository:
    def __init__(self): # plus de model_class
        self._storage = {}
    
    def add(self, obj: BaseModel) -> None:
        if obj.id in self._storage:
            raise ValueError("Object already exists")
        self._storage[obj.id] = obj  # Stocke l'objet avec son ID comme clé
    
    def get(self, id: str) -> Optional[BaseModel]:
        return self._storage.get(id)  # Recherche rapide O(1)
    
    def update(self, obj_id: str, data: dict):
        obj = self._storage.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save() # BaseModel.save() — pas obj.update()
        return obj
        
    def get_all(self):
        return list(self._storage.values())
        
    def delete(self, obj_id: str):
        self._storage.pop(obj_id, None)
        
    def get_by_attribute(self, attr: str, value):
        return next((o for o in self._storage.values()
            if getattr(o, attr, None) == value), None)
