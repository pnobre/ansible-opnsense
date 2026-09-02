from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import BaseModule
from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.main import is_unset


class HttpServer(BaseModule):
    # 'servername' is a multi-value field (a vhost can answer to more than one name), so
    # unlike every other module in this collection it can't safely be the implicit default
    # match key -- match_fields is required here, no FIELD_ID fallback.
    CMDS = {
        'add': 'addhttpserver',
        'del': 'delhttpserver',
        'detail': 'gethttpserver',
        'search': 'searchhttpserver',
        'set': 'sethttpserver',
    }
    API_KEY_PATH = 'httpserver'
    API_MOD = 'nginx'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    # Pragmatic subset -- the OPNsense form has ~60 fields (WAF/OCSP/ciphers/NAXSI tuning
    # this project doesn't touch). Covers what's needed to describe a reverse-proxy vhost.
    #
    # verify_client is in the set purely so it's sent on create: addhttpserver rejects a
    # brand-new vhost that omits it ("Option [] not in list" -- it has no stored default on
    # an object that's never existed), so without it every new vhost has to be bootstrapped
    # with a raw API POST. Default 'off' is what the webUI writes and what every existing
    # vhost already stores, so adding it churns nothing on update.
    FIELDS_CHANGE = [
        'servername', 'default_server', 'listen_http_address', 'listen_https_address',
        'certificate', 'locations', 'real_ip_source', 'https_only', 'http2',
        'enable_acme_support', 'log_handshakes', 'verify_client',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TYPING = {
        'bool': ['default_server', 'https_only', 'http2', 'enable_acme_support', 'log_handshakes'],
        'select': ['certificate', 'real_ip_source', 'verify_client'],
        'list': ['servername', 'listen_http_address', 'listen_https_address', 'locations'],
    }
    EXIST_ATTR = 'httpserver'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.httpserver = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['servername']):
                self.m.fail_json(
                    "You need to provide at least one 'servername' to create a vhost!"
                )

        self._base_check()

    def update(self) -> None:
        self._base_update(enable_switch=False)
