from ..core.base import Base

class Instance(Base):
    """
    Example:
    {
        'base_type': 'workflow',
        'created_by': 'foobar@foo.com',
        'created_on': '2021-07-27T17:40:23Z',
        'definition_id': '01PVN46YF6DS24U8min4MCzUouiKa4Ewox8',
        'ended_on': '2021-07-27T17:40:26Z',
        'id': '01Q759VYJHRBE5OlrsVI8XAsQw95tmIN3IM',
        'name': 'foo name',
        'owner': 'foobar@foo.com',
        'properties': {'atomic': {'is_atomic': False},
                        'delete_workflow_instance': False,
                        'display_name': 'foo name',
                        'runtime_user': {'target_default': True},
                        'target': {'execute_on_workflow_target': True,
                                'target_id': '01PCLP3E7SQC701swc9lUzodN6maHAoq4Tz',
                                'target_type': '01JXZ68PF6GB83PenphK3ObzhzfW3k7wYoY'}},
        'root_workflow_id': '01Q758996GREB32rowzrbljoI166RblVKZU',
        'schema_id': '01JXZ64VQ0NG97ZSrsONB4o38iICpACXFE3',
        'started_by': '01Q7589D9XXFP6D0ztc69XsP27mO69byIbM',
        'started_on': '2021-07-27T17:40:23Z',
        'status': {'state': 'success'},
        'type': 'generic.workflow',
        'ui_config': {'01Q7589D9XXFP6D0ztc69XsP27mO69byIbM': 'some sub workflow'},
        'updated_by': 'foobar@foo.com',
        'updated_on': '2021-07-27T17:40:26Z',
        'version': '1.0.0'
    }
    """
