from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import BaseModule
from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.main import is_unset


class Upstream(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'addupstream',
        'del': 'delupstream',
        'detail': 'getupstream',
        'search': 'searchupstream',
        'set': 'setupstream',
    }
    API_KEY_PATH = 'upstream'
    API_MOD = 'nginx'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    FIELDS_CHANGE = [
        'description', 'serverentries', 'load_balancing_algorithm', 'keepalive',
        'keepalive_requests', 'keepalive_timeout', 'host_port', 'x_forwarded_host_verbatim',
        'proxy_protocol', 'store', 'tls_enable', 'tls_client_certificate', 'tls_name_override',
        'tls_protocol_versions', 'tls_session_reuse', 'tls_trusted_certificate', 'tls_verify',
        'tls_verify_depth',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TYPING = {
        'bool': [
            'x_forwarded_host_verbatim', 'proxy_protocol', 'store', 'tls_enable',
            'tls_session_reuse', 'tls_verify',
        ],
        'select': ['load_balancing_algorithm', 'tls_client_certificate'],
        'list': ['serverentries', 'tls_protocol_versions', 'tls_trusted_certificate'],
        'int': ['keepalive', 'keepalive_requests', 'keepalive_timeout', 'host_port', 'tls_verify_depth'],
    }
    EXIST_ATTR = 'upstream'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.upstream = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['serverentries']):
                self.m.fail_json(
                    "You need to provide at least one 'serverentries' to create an upstream!"
                )

        self._base_check()

    def update(self) -> None:
        self._base_update(enable_switch=False)
