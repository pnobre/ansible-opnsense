from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import BaseModule


class RadvdEntry(BaseModule):
    FIELD_ID = 'interface'
    CMDS = {
        'add': 'add_entry',
        'del': 'del_entry',
        'set': 'set_entry',
        'search': 'search_entry',
        'detail': 'get_entry',
    }
    API_KEY_PATH = 'entries'
    API_MOD = 'radvd'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    # Router Advertisements per interface. Deliberately just enabled/interface/mode --
    # Radvd's real model also covers prefix routes, RDNSS/DNSSL, and per-field lifetime/
    # interval tuning (MinRtrAdvInterval, AdvDefaultLifetime, ...), all left at OPNsense's
    # own defaults. Adopt an existing entry only if none of those were customised through
    # the UI, or a re-apply here would silently reset them.
    FIELDS_ALL = ['interface', 'mode', 'enabled']
    FIELDS_CHANGE = FIELDS_ALL
    FIELDS_TYPING = {
        'select': ['mode'],
        'bool': ['enabled'],
    }
    EXIST_ATTR = 'entry'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.entry = {}
