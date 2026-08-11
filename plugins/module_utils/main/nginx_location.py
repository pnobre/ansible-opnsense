from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import BaseModule
from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.main import is_unset


class Location(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'addlocation',
        'del': 'dellocation',
        'detail': 'getlocation',
        'search': 'searchlocation',
        'set': 'setlocation',
    }
    API_KEY_PATH = 'location'
    API_MOD = 'nginx'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    # This is a pragmatic subset, not every field the OPNsense form exposes (~45 total,
    # mostly WAF/cache/naxsi tuning this project doesn't use) -- covers what's actually
    # needed to describe a reverse-proxy location. Extend as real use cases show up.
    FIELDS_CHANGE = [
        'description', 'urlpattern', 'matchtype', 'upstream', 'force_https', 'php_enable',
        'websocket', 'enable_secrules', 'enable_learning_mode', 'proxy_read_timeout',
        'ip_acl', 'root', 'index', 'path_prefix', 'authbasicuserfile', 'max_body_size',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TYPING = {
        'bool': ['force_https', 'php_enable', 'websocket', 'enable_secrules', 'enable_learning_mode'],
        'select': ['matchtype', 'upstream', 'ip_acl', 'index', 'authbasicuserfile'],
    }
    EXIST_ATTR = 'location'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.location = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['urlpattern']):
                self.m.fail_json(
                    "You need to provide a 'urlpattern' to create a location!"
                )

        self._base_check()

    def update(self) -> None:
        self._base_update(enable_switch=False)
