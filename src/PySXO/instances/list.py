import requests
import time
import datetime

from .get import Instance
from ..core.decorators import cache
from ..core.base import Base
from ..enum import InstanceState


class Instances(Base):
    @cache('_all')
    def all(
        self,
        workflow_ids: list[str]=[],
        date_from: datetime.datetime=None,
        date_to: datetime.datetime=None,
        state: list[InstanceState]=[InstanceState.ALL],
        **kwargs
    ) -> list[Instance]:
        """[summary]

        Args:
            workflow_ids (list[str]): A list of string workflow IDs for which to query.
            state (list[InstanceState]): A list of Instance States for which to query.
            date_from (datetime.datetime, optional): A datetime that describes the beginning of a target range. Defaults to None.
            date_to (datetime.datetime, optional): A datetime that describes the end of a target range. Defaults to None.

        Returns:
            list[Instance]: List of instance objects that meet all the parameter criteria.
        """
        date_from = self._format_date(date_from) if date_from else date_from
        date_to = self._format_date(date_to) if date_to else date_to
        state = self._format_enum_list(state)

        return [
            Instance(self, i) for i in self._sxo._post(url=f"/api/v1.1/instances", params={
                **({'date_from': date_from} if date_from else {}),
                **({'date_to': date_to} if date_to else {}),
                **({'state': state} if state else {})
            }, json={
                **({'workflow_ids': workflow_ids} if workflow_ids else {}),
            })
        ]
