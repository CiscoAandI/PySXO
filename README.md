# PySXO
A Python SDK for SecureX Orchestrator (SXO)

## Quickstart

``` python
from PySXO import SXOClient

sxo = SXOClient(
    client_id=secrets['client_id'],
    client_password=secrets['client_password'],
    dry_run=False
)

workflows = sxo.workflows