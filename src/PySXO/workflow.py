from .core.base import Base
from attrdict import AttrDict

class Workflow(Base):
    def __getattr__(self, key):
        if isinstance(self._json.get(key), dict):
            return AttrDict(self._json[key])
        return self._json.get(key)

    def validate(self):
        result = self._sxo._post(paginated=True, url=f'/v1/workflows/{self.id}/validate',)

        if not self._sxo.dry_run:
            if result['workflow_valid'] != True:
                print(f"Workflow is still invalid, Found errors: {result}")

        return {
            # this key indicates a need to be re-validated
            'valid': result['workflow_valid'],
            'result': result
        }