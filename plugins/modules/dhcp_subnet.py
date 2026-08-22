#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/kea.html

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.wrapper import module_wrapper
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dhcp_subnet_v4 import SubnetV4
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dhcp_subnet_v6 import SubnetV6

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/dhcp.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/dhcp.html'


def run_module():
    module_args = dict(
        subnet=dict(
            type='str', required=True,
            description='Subnet to use, should be large enough to hold the specified pools and reservations',
        ),
        description=dict(
            type='str', required=False, aliases=['desc'], default='',
        ),
        pools=dict(
            type='list', elements='str', required=False, default=[],
            description='List of pools, one per line in range or subnet format '
                        '(e.g. 192.168.0.100 - 192.168.0.200 , 192.0.2.64/26)'
        ),
        auto_options=dict(
            type='bool', required=False, default=True, aliases=['option_data_autocollect'],
            description='Automatically update option data for relevant attributes as routers, '
                        'dns servers and ntp servers when applying settings from the gui.'
        ),
        gateway=dict(
            type='list', elements='str', required=False, aliases=['gw', 'routers'], default=[],
            description='Default gateways to offer to the clients',
        ),
        routes=dict(
            type='str', required=False, aliases=['static_routes'], default='',
            description='Static routes that the client should install in its routing cache, '
                        'defined as dest-ip1,router-ip1;dest-ip2,router-ip2',
        ),
        dns=dict(
            type='list', elements='str', required=False, aliases=['dns_servers', 'dns_srv'], default=[],
            description='DNS servers to offer to the clients',
        ),
        domain=dict(
            type='str', required=False, aliases=['domain_name', 'dom_name', 'dom'], default='',
            description="The domain name to offer to the client, set to this firewall's domain name when left empty",
        ),
        domain_search=dict(
            type='list', elements='str', required=False, aliases=['dom_search'], default=[],
            description="Specifies a ´search list´ of Domain Names to be used by the client to locate "
                        'not-fully-qualified domain names.',
        ),
        ntp_servers=dict(
            type='list', elements='str', required=False, aliases=['ntp_srv', 'ntp'], default=[],
            description='Specifies a list of IP addresses indicating NTP (RFC 5905) servers available to the client.',
        ),
        time_servers=dict(
            type='list', elements='str', required=False, aliases=['time_srv'], default=[],
            description='Specifies a list of RFC 868 time servers available to the client.',
        ),
        next_server=dict(
            type='str', required=False, aliases=['next_srv'], default='',
            description='Next server IP address',
        ),
        tftp_server=dict(
            type='str', required=False, aliases=['tftp', 'tftp_srv', 'tftp_server_name'], default='',
            description='TFTP server address or fqdn',
        ),
        tftp_file=dict(
            type='str', required=False, aliases=['tftp_boot_file', 'boot_file_name'], default='',
            description='TFTP Boot filename to request',
        ),
        ipv=dict(type='int', required=False, default=4, choices=[4, 6], aliases=['ip_version']),
        v6_only_preferred=dict(
            type='int', required=False, aliases=['v6_preferred'],
            description='The number of seconds for which the client should disable DHCPv4. '
                        'The minimum value is 300 seconds.'
        ),
        interface=dict(
            type='str', required=False, default=None,
            description='Interface this subnet6 is served on. Required when ipv=6, ignored for ipv=4 '
                        '(DHCPv4 subnets are matched to an interface by their own network, not this field).',
        ),
        match_fields=dict(
            type='list', required=False, elements='str',
            description='Fields that are used to match configured interface with the running config - '
                        "if any of those fields are changed, the module will think it's a new entry",
            choices=['subnet', 'description'],
            default=['subnet'],
        ),
        **RELOAD_MOD_ARG,
        **STATE_MOD_ARG,
        **OPN_MOD_ARGS,
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        }
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.params['ipv'] == 6:
        # Deliberately pragmatic, mirroring SubnetV4's own scope: subnet, interface,
        # description, pools and dns_servers only. Prefix delegation (dynamic_prefix,
        # pd_pools), DDNS, per-subnet reservations/options and HA are all real subnet6
        # fields OPNsense supports that this does not manage -- adopt an existing entry
        # only if none of those were customised through the UI, or a re-apply here would
        # silently reset them to default. See SubnetV6's own API_FIELDS_IGNORE for the
        # exact list.
        if not module.params['interface']:
            module.fail_json("'interface' is required when ipv=6")

        module_wrapper(SubnetV6(module=module, result=result))
        module.exit_json(**result)

    module_wrapper(SubnetV4(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
