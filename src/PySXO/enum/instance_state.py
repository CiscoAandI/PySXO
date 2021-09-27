from enum import Enum


class InstanceState(Enum):
    CANCELLED = 'cancelled'
    FAILED = 'failed'
    SUCCESS = 'success'
    WAITING_FOR_EVENT = 'waiting_for_event'
    PAUSED = 'paused'
    RUNNING = 'running'
    ALL = 'all'