import time

from typing import List

from .workflow import Workflow
from .core.decorators import cache
from .core.base import Base

class WorkFlowNotFound(Exception):
    pass

class Workflows(Base):
    IMPORT_URI = '/be-importexport'
    
    def import_workflow(self, workflow_id, workflow, create_new=False, overwrite=True, skip_all_runtime_users=True):
        # create_new will *not* create a new workflow or new subworkflows. This is so that copies of subworkflows
        # dont get wildly out of hand during imports.
        result = self._sxo._post(
            paginated=True,
            uri=Workflows.IMPORT_URI,
            url=f'/api/v1/workflows/import',
            params={
                'workflow_id': workflow_id,
                'workflow_unique_name': workflow['workflow']['unique_name'],
                'create_new': create_new,
                'overwrite': overwrite,
                'skip_all_runtime_users': skip_all_runtime_users
            }, 
            json=workflow
        )
        
        valid = True
        if not self._sxo.dry_run:
            # Wait for import to complete
            for i in range(120):
                # Wait 120 seconds before timing out
                if result['status']['state'] == 'import_in_progress':
                    time.sleep(1)
                    result = self._sxo._get(paginated=True, url=f'/v1/workflows/{result["id"]}')
                else:
                    break

            if not result['workflow_valid']:
                # TODO: logger
                print(result['name'], "is not valid. Caching to validate after import.")
                valid = False
        
        return {
            # this key indicates a need to be re-validated
            'valid': valid,
            'result': result
        }

    @cache('_all')
    def all(self, **kwargs) -> List[Workflow]:
        results = list()
        for page in self._sxo._paginated_request(url=f"/api/v1.1/workflows", **kwargs):
            results += page
        return [ Workflow(self._sxo, raw=i) for i in results ]

    def get(self, workflow_id=None, unique_name=None) -> Workflow:
        if not workflow_id and not unique_name:
            raise Exception("Workflow ID or unique name must be provided")
        
        if workflow_id:
            return Workflow(self._sxo, raw=self._sxo._get(url=f'/api/v1/workflows/{workflow_id}')) #FIXME Use v1.1
        else:
            for workflow in self.all():
                if workflow.unique_name == unique_name:
                    return workflow
        raise WorkFlowNotFound



