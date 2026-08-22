from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.translate import \
    get_selected_list, simplify_translate
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import BaseModule


class SubnetV6(BaseModule):
    CMDS = {
        'add': 'add_subnet',
        'del': 'del_subnet',
        'set': 'set_subnet',
        'search': 'search_subnet',
        'detail': 'get_subnet',
    }
    API_KEY = 'subnet6'
    API_KEY_PATH = 'subnet6'
    API_MOD = 'kea'
    API_CONT = 'dhcpv6'
    API_CONT_REL = 'service'
    FIELDS_ALL = [
        'subnet', 'interface', 'description', 'pools',
    ]
    FIELDS_CHANGE = FIELDS_ALL.copy()
    FIELDS_CHANGE.append('dns')
    FIELDS_TYPING = {
        'list': ['dns'],
    }
    # Everything subnet6 supports beyond what this (deliberately pragmatic) module manages --
    # prefix delegation, DDNS, per-subnet reservations/options, HA. Left as OPNsense's own
    # defaults; adopt an existing entry only if none of these were customised, or a re-apply
    # here would silently flatten them back to default. Kept out of FIELDS_ALL/FIELDS_CHANGE
    # entirely, ignored here too so simplify_translate's passthrough doesn't clutter the diff
    # with fields this module never reads or writes.
    API_FIELDS_IGNORE = [
        'subnet_id', 'valid_lifetime', 'allocator', 'pd-allocator', 'option_data_autocollect',
        'option', 'dynamic_prefix', 'ddns_forward_zone', 'ddns_reverse_zone',
        'ddns_qualifying_suffix', 'ddns_dns_server', 'ddns_dns_port', 'ddns_domain_key_name',
        'ddns_domain_key_secret', 'ddns_domain_key_algorithm', 'ddns_override_no_update',
        'ddns_override_client_update', 'ddns_update_on_renew', 'ddns_conflict_resolution_mode',
        'option_data', 'option_data.domain_search', 'option_data.v6_dnr',
        'option_data.dns_servers', 'option_data_autocollect',
    ]
    API_ATTR_OPTIONS = 'option_data'
    API_FIELDS_OPTIONS = ['dns']
    POOL_JOIN_CHAR = '\n'
    FIELDS_TRANSLATE_SPECIAL = {
        'dns': 'dns_servers',
    }
    EXIST_ATTR = 'subnet'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.subnet = {}
        self.existing_subnets = None

    def check(self) -> None:
        if self.p['state'] == 'present' and len(self.p['pools']) == 0:
            self.m.fail_json(
                "You need to provide at least one pool -- a subnet6 with none can be created, "
                "but Kea won't hand out any address from it, defeating the point of managing "
                "it here at all."
            )

        self._base_check()

    def simplify_existing(self, entry: dict) -> dict:
        simple = simplify_translate(
            existing=entry,
            typing=self.FIELDS_TYPING,
            translate=self.FIELDS_TRANSLATE,
            ignore=self.API_FIELDS_IGNORE,
        )

        simple['pools'] = simple['pools'].split(self.POOL_JOIN_CHAR) if simple['pools'] else []

        if self.API_ATTR_OPTIONS in entry:
            # get/details call -- nested
            opts = entry[self.API_ATTR_OPTIONS]
            return {
                **simple,
                'dns': get_selected_list(opts[self.FIELDS_TRANSLATE_SPECIAL['dns']], remove_empty=True),
            }

        # search call -- flat, dotted keys
        return {
            **simple,
            'dns': entry[f"option_data.{self.FIELDS_TRANSLATE_SPECIAL['dns']}"],
        }

    def build_request(self) -> dict:
        raw_request = self._base_build_request(ignore_fields=self.API_FIELDS_OPTIONS)

        raw_request[self.API_KEY]['pools'] = self.POOL_JOIN_CHAR.join(self.p['pools'])
        raw_request[self.API_KEY][self.API_ATTR_OPTIONS] = {
            self.FIELDS_TRANSLATE_SPECIAL['dns']: self.RESP_JOIN_CHAR.join(self.p['dns']),
        }

        return raw_request
