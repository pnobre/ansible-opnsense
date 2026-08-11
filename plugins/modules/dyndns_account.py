#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2026, Paulo Nobre <pnobre@pnobre.com>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.wrapper import module_wrapper
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG_DEF_FALSE
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dyndns_account import Account

except MODULE_EXCEPTIONS:
    module_dependency_error()


def run_module():
    module_args = dict(
        match_fields=dict(
            type='list', required=False, elements='str', default=['description'],
            choices=['description', 'uuid'],
            description='Fields used to match this account against the existing config',
        ),
        uuid=dict(type='str', required=False, description='Optionally supply the uuid of an existing account'),
        description=dict(type='str', required=True, aliases=['name']),
        enabled=dict(type='bool', required=False, default=True),
        service=dict(
            type='str', required=True,
            description="Provider, e.g. 'cloudflare'. The 'Custom' service type (with its "
                        "own 'protocol' field) isn't supported by this module.",
        ),
        server=dict(type='str', required=False, default=''),
        username=dict(type='str', required=False, default=''),
        password=dict(type='str', required=False, default='', no_log=True),
        resource_id=dict(type='str', required=False, default=''),
        hostnames=dict(
            type='list', elements='str', required=False, default=[],
            description='Hostname(s) this account keeps updated',
        ),
        wildcard=dict(type='bool', required=False, default=False),
        zone=dict(type='str', required=False, default=''),
        checkip=dict(type='str', required=False, default='if'),
        dynipv6host=dict(type='str', required=False, default=''),
        checkip_timeout=dict(type='int', required=False, default=10),
        force_ssl=dict(type='bool', required=False, default=True),
        ttl=dict(type='int', required=False, default=300),
        interface=dict(type='str', required=False, default=''),
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

    module_wrapper(Account(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
