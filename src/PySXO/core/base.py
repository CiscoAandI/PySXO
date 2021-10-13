import datetime

from enum import Enum
from typing import List

class Base():
    def __init__(self, sxo, raw=None):
        self._sxo = sxo
        self._json = raw
    
    def _format_date(self, date: datetime.datetime) -> str:
        # Bug in SXO API where it does not accept RFC 3339 syntax as it says it does.
        return date.isoformat() + "Z"
    
    def _format_enum_list(self, enum_list: List[Enum]) -> str:
        # SXO api requires comma delimitted list
        return ','.join([i.value for i in enum_list])
    
    def _validate_kwargs(self, kwargs):
        # API generic query args
        # TODO:
        return kwargs