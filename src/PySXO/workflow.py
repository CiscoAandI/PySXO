import json
import logging

from typing import Union, List, Dict

from .core.base import Base
from .core.enum import PropertySection

from . import LOGGER

TYPE_MAP = {
    bool: 'boolean',
    str: 'string',
    int: 'integer'
}

class WorkflowVariable(Base):

    def __init__(self, sxo, _id, raw):
        self._id = _id
        super().__init__(sxo=sxo, raw=raw)

    @property
    def id(self):
        return self._id

    @property
    def section(self):
        return self._json['section']

    @property
    def title(self):
        return self._json['title']

    @property
    def property_type(self):
        return self._json['type']

    @property
    def default(self):
        return self._json.get('default')


class PropertySchema(Base):
    @property
    def _properties(self):
        return self._json['properties']

    @property
    def variables(self):
        return [WorkflowVariable(sxo=self._sxo, _id=k, raw=v) for k, v in self._json['properties'].items()]

    @property
    def input_variables(self):
        return [i for i in self.variables if i.section == PropertySection.INPUT_VARIABLES.value]
    
    @property
    def required_variables(self):
        return [
            WorkflowVariable(sxo=self._sxo, _id=k, raw=v) for k, v in self._json['properties'].items()
            if k in self._json.get('required', [])
        ]


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
        return PropertySchema(sxo=self._sxo, raw=self._json['property_schema'])

class WorkflowRunRequest(Base):
    @property
    def base_type(self):
        self._json['base_type']

    @property
    def created_by(self):
        # TODO: user object instead of string
        self._json['created_by']

    @property
    def created_on(self):
        # TODO: Date object instead of string
        self._json['created_on']

    @property
    def definition_id(self):
        self._json['definition_id']

    @property
    def id(self):
        self._json['id']

    @property
    def schema_id(self):
        self._json['schema_id']

    @property
    def status(self):
        # TODO: return object instead of {"state": "created"}
        self._json['status']

    @property
    def workflow_type(self):
        self._json['type']

    @property
    def version(self):
        self._json['version']
    

class Workflow(Base):
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
            raw=self._sxo._get(paginated=True, url=f'/api/v1/workflows/ui/start_config?workflow_id={self.id}')
        )

    def start(self, **input_variables) -> Union[List, Dict]:
        # Input variable qwargs are human-readable by SXO so may contain spaces
        # or other prohibitted python function-arg symbols
        missing_required_args = []
        for required_variable in self.start_config.property_schema.required_variables:
            if required_variable.title not in input_variables:
                missing_required_args.append(required_variable.title)

        if missing_required_args:
            raise TypeError(
                f"start() missing {len(missing_required_args)} required input variables: {' and '.join(missing_required_args)}"
            )

        return [WorkflowRunRequest(sxo=self._sxo, raw=i) for i in self._sxo._post(
            paginated=True,
            url=f"/api/v1/workflows/start?workflow_id={self.id}",
            json={"input_variables": [{
                    "id": i.id,
                    "properties": {
                        "value": input_variables[i.title],
                        "scope": "input",
                        "name": i.title,
                        "type": 'string',
                        # TODO: hardcoding is_required as true here...is this right?
                        # This may not be generic enough. More research required.
                        "is_required": True
                    }
                }
                for i in self.start_config.property_schema.input_variables
                if i.title in input_variables
            ]}
        )]

    def validate(self):
        # Validate is not paginated so does not need to request all pages
        result = self._sxo._post(paginated=True, url=f'/api/v1/workflows/{self.id}/validate',)

        if not self._sxo.dry_run:
            if result['workflow_valid'] != True:
                LOGGER.info(f"Workflow is still invalid, Found errors: {result}")

        return {
            # this key indicates a need to be re-validated
            'valid': result['workflow_valid'],
            'result': result
        }
