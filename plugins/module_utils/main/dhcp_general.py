from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import GeneralModule


class General(GeneralModule):
    CMDS = {
        'set': 'set',
        'search': 'get'
    }
    API_KEY_PATH = 'dhcpv4'
    API_KEY_PATH_REQ = API_KEY_PATH
    API_MOD = 'kea'
    API_CONT = 'dhcpv4'
    API_CONT_REL = 'service'
    FIELDS_CHANGE = [
        'enabled', 'interfaces', 'socket_type', 'fw_rules', 'lifetime',
        'ha_enabled', 'ha_this_server_name', 'ha_max_unacked_clients'
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TRANSLATE = {
        'enabled': ('general', 'enabled'),
        'interfaces': ('general', 'interfaces'),
        'lifetime': ('general', 'valid_lifetime'),
        'fw_rules': ('general', 'fwrules'),
        'socket_type': ('general', 'dhcp_socket_type'),
        'ha_enabled': ('ha', 'enabled'),
        'ha_this_server_name': ('ha', 'this_server_name'),
        'ha_max_unacked_clients': ('ha', 'max_unacked_clients'),
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'fw_rules', 'ha_enabled'],
        'int': ['lifetime', 'ha_max_unacked_clients'],
        'list': ['interfaces'],
        'select': ['socket_type'],
    }
    INT_VALIDATIONS = {
        'lifetime': {'min': 0},
        'ha_max_unacked_clients': {'min': 0},
    }
    FIELDS_OPTIONAL = ['ha_enabled', 'ha_this_server_name', 'ha_max_unacked_clients']

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        # NOT module.params['ha'] - the 'list' module instantiates us without the module-args
        ha = module.params.get('ha')
        if ha is not None:
            for key, value in ha.items():
                module.params[f'ha_{key}'] = value

        GeneralModule.__init__(self=self, m=module, r=result, s=session)


class GeneralV6(General):
    # Kea's DHCPv6 'general' node (api/kea/dhcpv6/get|set) is the DHCPv4 one minus
    # 'dhcp_socket_type' and 'compatibility', plus 'mac_sources'. This module only
    # manages the overlap that also matters for v6 -- enabled / interfaces / fwrules /
    # valid_lifetime -- so 'socket_type' is dropped here (the module arg still exists
    # but is ignored for ipv=6, same as 'interface' is for dhcp_subnet ipv=4).
    # 'mac_sources' is deliberately not modelled. The DHCPv4 General class does the same
    # with 'compatibility' and OPNsense's set endpoints normally deep-merge, so a partial
    # payload should leave it alone -- but that has NOT been round-trip tested for v6
    # specifically (adoption was changed=0, so no set fired). First time a set actually
    # runs, re-GET dhcpv6/general and confirm mac_sources survived. Do NOT add it to
    # FIELDS_* without also giving it list/select typing.
    API_KEY_PATH = 'dhcpv6.general'
    API_KEY_PATH_REQ = API_KEY_PATH
    API_CONT = 'dhcpv6'
    FIELDS_CHANGE = [
        'enabled', 'interfaces', 'fw_rules', 'lifetime'
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TRANSLATE = {
        'lifetime': 'valid_lifetime',
        'fw_rules': 'fwrules',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'fw_rules'],
        'int': ['lifetime'],
        'list': ['interfaces'],
    }
