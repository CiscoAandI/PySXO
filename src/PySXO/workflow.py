import json
import logging

from attrdict import AttrDict
from typing import Union, Dict, List

from .core.base import Base

LOGGER = logging.getLogger(__name__)
class Workflow(Base):
    def __getattr__(self, key):
        if isinstance(self._json.get(key), dict):
            return AttrDict(self._json[key])
        return self._json.get(key)

    @property
    def id(self) -> str:
        return self._json.id

    @property
    def name(self) -> str:
        return self._json.name

    @property
    def start_config(self) -> AttrDict[Union[Dict, List]]:
        return AttrDict(self._sxo._get(url=f'/api/v1/workflows/ui/start_config?workflow_id={self.id}'))

    def start(self, **kwargs) -> Union[List, Dict]:
        body = {"input_variables":[]}
        for variable_id, variable_definition in self.start_config.property_schema.properties.items():
            if variable_definition["title"] in kwargs.keys():
                # We have to dump content to string if it came as a dict because of SXO limitations. It can come as either string or dict
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

    def validate(self):
        result = self._sxo._post(paginated=True, url=f'/v1/workflows/{self.id}/validate',)

        if not self._sxo.dry_run:
            if result['workflow_valid'] != True:
                LOGGER.info(f"Workflow is still invalid, Found errors: {result}")

        return {
            # this key indicates a need to be re-validated
            'valid': result['workflow_valid'],
            'result': result
        }
