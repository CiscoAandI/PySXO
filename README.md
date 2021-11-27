# PySXO

Note: This SDK is beta and is supported at best-effort. Please raise issues as you find them. Pull requests are more than welcome.

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
