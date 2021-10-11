import json

from attrdict import AttrDict
from typing import Union, Dict, List

from .core.base import Base

class Workflow(Base):
    def __init__(self, sxo, raw=None):
        super().__init__(sxo, raw=raw)

    def __getattr__(self, key):
        if isinstance(self._json.get(key), dict):
            return AttrDict(self._json[key])
        return self._json.get(key)

    @property
    def id(self) -> str:
        return self._json.id

    @property
    def start_config(self) -> AttrDict[Union[Dict, List]]:
        return AttrDict(self._sxo._get(url=f'/api/v1/workflows/ui/start_config?workflow_id={self.id}'))

    def start(self, **kwargs) -> Union[List, Dict]:
        body = {"input_variables":[]}
        for variable_id, variable_definition in self.start_config.property_schema.properties.items():
            if variable_definition["title"] in kwargs.keys():
                if isinstance(kwargs[variable_definition["title"]], dict):
                    value = json.dumps(kwargs[variable_definition["title"]])
                else:
                    value = kwargs[variable_definition["title"]]
                body["input_variables"].append({
                    "id": variable_id,
                    "properties": {
                        "value": value,
                        "scope": "input",
                        "name": variable_definition["title"],
                        "type": "string",
                        "is_required": True
                    }
                })
        return self._sxo._post(url=f"/api/v1/workflows/start?workflow_id={self.id}", json=body)

        
        
        



        