import json

from attrdict import AttrDict
from typing import Union, List, Dict

from .core.base import Base

class PropertySchema(Base):
    pass

class StartConfig(Base):
    """
    {
        'property_schema': {
            'properties': {
                '01RMCD5WPLVMF6wDYqO5XPdcBAczCK8MNMP': {
                    'section': 'Input Variables',
                    'title': 'Identity Group Name',
                    'type': 'string'
                },
                'target_id': {
                    'addNewOption': True,
                    'component': 'select',
                    'filterBy': {
                        'schema_id': '01JYJ0OOD9O7P2lkhNF1LsJrTonSOcI3AXu'
                    },
                    'optionsDynamicRef': {
                        'endpoint': 'targets'
                    },
                    'position': 1,
                    'section': 'Target',
                    'title': 'Target'
                }
            },
            'required': ['01RMCD5WPLVMF6wDYqO5XPdcBAczCK8MNMP', 'target_id']
        },
        'view_config': {
            'section_order': ['Target', 'Account Keys', 'Input Variables', 'Start Point']
        }
    }
    """
    @property
    def property_schema(self):
        pass

class Workflow(Base):
    def __getattr__(self, key):
        # TODO: delete this function so there's no magic. All explicitly defined
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
    def start_config(self) -> StartConfig:
        return StartConfig(
            sxo=self._sxo,
            raw=self._sxo._get(url=f'/v1/workflows/ui/start_config?workflow_id={self.id}')
        )

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

    def validate(self):
        # Validate is not paginated so does not need to request all pages
        result = self._sxo._post(paginated=True, url=f'/v1/workflows/{self.id}/validate',)

        if not self._sxo.dry_run:
            if result['workflow_valid'] != True:
                print(f"Workflow is still invalid, Found errors: {result}")

        return {
            # this key indicates a need to be re-validated
            'valid': result['workflow_valid'],
            'result': result
        }
