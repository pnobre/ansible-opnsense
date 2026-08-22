from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import GeneralModule


# Supported as of OPNsense 23.7 (same generation as unbound_general)
class Advanced(GeneralModule):
    CMDS = {
        'set': 'set',
        'search': 'get',
    }
    API_KEY_PATH = 'unbound.advanced'
    API_KEY_PATH_REQ = API_KEY_PATH
    API_MOD = 'unbound'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    # Plain 'reconfigure' (ApiMutableServiceControllerBase's own generic action, confirmed via
    # the live box's ServiceController.php), not General's 'reconfigureGeneral' -- that one only
    # exists because changing General also needs a dns/dhcp reload hook; Advanced doesn't.
    API_CMD_REL = 'reconfigure'
    # Raw field names already match the model's own XML tags 1:1 (unlike General's fields,
    # several of which are Python-friendly aliases for oddly-named raw fields) -- no
    # FIELDS_TRANSLATE or FIELDS_BOOL_INVERT needed here.
    FIELDS_CHANGE = [
        'hideidentity', 'hideversion', 'dnssecstripped', 'belownxdomain', 'aggressivensec',
        'prefetch', 'prefetchkey', 'qnameminstrict', 'serveexpired', 'unwantedreplythreshold',
        'logservfail',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TYPING = {
        'bool': [
            'hideidentity', 'hideversion', 'dnssecstripped', 'belownxdomain', 'aggressivensec',
            'prefetch', 'prefetchkey', 'qnameminstrict', 'serveexpired', 'logservfail',
        ],
        'int': ['unwantedreplythreshold'],
    }

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        GeneralModule.__init__(self=self, m=module, r=result, s=session)
