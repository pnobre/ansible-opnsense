from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import BaseModule
from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.main import is_unset


class Account(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'addItem',
        'del': 'delItem',
        'set': 'setItem',
        'search': 'searchItem',
        'detail': 'getItem',
        'toggle': 'toggleItem',
    }
    API_KEY_PATH = 'account'
    API_MOD = 'dyndns'
    API_CONT = 'accounts'
    API_CONT_REL = 'service'
    # 'protocol' deliberately excluded: the controller strips it from search results
    # entirely unless service='Custom' (AccountsController::searchItemAction unsets it and
    # folds it into the service string instead) -- only relevant for the 'Custom' service
    # type, which isn't supported by this module.
    #
    # 'password' deliberately excluded from FIELDS_CHANGE (but kept in FIELDS_ALL, below):
    # this field is an UpdateOnlyTextField in OPNsense's own model, meaning the detail
    # ('getItem') endpoint that search()/find() uses for comparison always returns it blank
    # -- confirmed empirically, not documented anywhere. Comparing against that blank value
    # would make every run see a permanent false "changed". Since OPNsense never lets us
    # read the real value back, there is no way to detect drift here at all -- the value is
    # asserted once on create/update (FIELDS_ALL still includes it, so it's sent whenever any
    # *other* field change triggers a write) and otherwise left alone.
    FIELDS_CHANGE = [
        'enabled', 'service', 'server', 'username', 'resource_id',
        'hostnames', 'wildcard', 'zone', 'checkip', 'dynipv6host', 'checkip_timeout',
        'force_ssl', 'ttl', 'interface', 'description',
    ]
    FIELDS_ALL = FIELDS_CHANGE + ['password']
    FIELDS_TRANSLATE = {
        'resource_id': 'resourceId',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'wildcard', 'force_ssl'],
        'select': ['service', 'checkip', 'interface'],
        'list': ['hostnames'],
        'int': ['checkip_timeout', 'ttl'],
    }
    # DynDNS account passwords are API tokens/credentials for the provider (e.g. a
    # Cloudflare API token) -- never surface them in check-mode diffs or logs.
    FIELDS_DIFF_NO_LOG = ['password']
    EXIST_ATTR = 'account'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.account = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['hostnames']):
                self.m.fail_json(
                    "You need to provide 'hostnames' to create a dyndns account!"
                )

        self._base_check()

    def update(self) -> None:
        self._base_update(enable_switch=False)
