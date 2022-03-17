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

    def __init__(self, sxo, raw):
        super().__init__(sxo=sxo, raw=raw)

    @property
    def id(self):
        return self._json['id']

    @property
    def scope(self):
        return self._json['properties']["scope"]

    @property
    def name(self):
        return self._json['properties']["name"]

    @property
    def property_type(self):
        return self._json['properties']["type"]

    @property
    def default(self):
        return self._json['properties']["value"]

    @property
    def is_required(self):
        return self._json['properties']["is_required"]

    def __repr__(self):
        return f"Workflow variable, id: {self.id}"


class PropertySchema(Base):

    @property
    def input_variables(self):
        return [WorkflowVariable(sxo=self._sxo, raw=v) for v in self._json]

    @property
    def required_variables(self):
        return [i for i in self.input_variables if i.is_required]


class StartConfig(Base):
    """
    {
    "input_variables": [
        {
            "id": "01SZK637QK7SU60M21u7jJzggcPDtUNjIG0",
            "schema_id": "01JYJ0PDP6GDE68JLuGA8NkJ1pyMUa65Hkw",
            "properties": {
                "value": "",
                "scope": "input",
                "name": "alert_input",
                "type": "datatype.string",
                "description": "input for alert event",
                "is_required": true,
                "is_invisible": false
            },
            "created_on": "2021-11-22T18:27:18.047Z",
            "created_by": "user@cisco.com",
            "updated_on": "2021-11-22T18:27:18.047Z",
            "updated_by": "user@cisco.com",
            "owner": "user@cisco.com",
            "base_type": "datatype",
            "unique_name": "variable_workflow_01SZK6381G3LE72ivN2M3RDl5x3YsgAd9rE"
        },
    ]
}
    """

    @property
    def property_schema(self):
        return PropertySchema(sxo=self._sxo, raw=self._json.get('input_variables', []))


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
        return self._json['id']

    @property
    def name(self) -> str:
        return self._json['name']

    @property
    def unique_name(self) -> str:
        return self._json['unique_name']

    @property
    def start_config(self) -> StartConfig:
        return StartConfig(
            sxo=self._sxo,
            raw=self._sxo._get(paginated=True, url=f'/api/v1/workflows/start_config?workflow_id={self.id}')
        )

    def start(self, **input_variables) -> Union[List, Dict]:
        # Input variable qwargs are human-readable by SXO so may contain spaces
        # or other prohibitted python function-arg symbols
        missing_required_args = []
        input_variables_definitions = self.start_config.property_schema.input_variables
        required_variables = self.start_config.property_schema.required_variables
        LOGGER.debug(f"Input variables definitions: {input_variables_definitions}")
        LOGGER.debug(f"Required variables: {required_variables}")
        for required_variable in required_variables:
            if required_variable.name not in input_variables:
                missing_required_args.append(required_variable.name)

        if missing_required_args:
            LOGGER.error(f"Missing required variables: {missing_required_args} ")
            raise TypeError(
                f"start() missing {len(missing_required_args)} required input variables: {' and '.join(missing_required_args)}"
            )
        payload = {
            "input_variables": [
                {
                    "id": i.id,
                    "properties": {
                        "value": input_variables[i.name],
                        "scope": "input",
                        "name": i.name,
                        "type": 'string',
                        "is_required": i.is_required
                    }
                }
                for i in input_variables_definitions
                if i.name in input_variables
            ]
        }
        LOGGER.debug(f"Start workflow payload: {payload}")
        return [WorkflowRunRequest(sxo=self._sxo, raw=i) for i in self._sxo._post(
            paginated=True,
            url=f"/api/v1/workflows/start?workflow_id={self.id}",
            json=payload,
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
