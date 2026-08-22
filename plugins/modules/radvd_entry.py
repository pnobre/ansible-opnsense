#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2026, Paulo Nobre
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/radvd.html

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.wrapper import module_wrapper
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG_DEF_FALSE
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.radvd_entry import RadvdEntry

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/radvd.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/radvd.html'


def run_module():
    module_args = dict(
        interface=dict(
            type='str', required=True,
            description='Interface to send Router Advertisements on. One entry per interface -- '
                        "OPNsense itself enforces this uniqueness, this module doesn't need to.",
        ),
        mode=dict(
            type='str', required=False, default='stateless',
            choices=['router', 'unmanaged', 'managed', 'assist', 'stateless'],
            description='router: RA only, no managed/other flags. unmanaged/stateless: SLAAC, '
                        'no DHCPv6 lease needed. managed: clients must get their address from '
                        'DHCPv6 (Kea). assist: SLAAC + DHCPv6 both offered.',
        ),
        enabled=dict(type='bool', required=False, default=True),
        **RELOAD_MOD_ARG_DEF_FALSE,
        **STATE_ONLY_MOD_ARG,
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

    module_wrapper(RadvdEntry(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
