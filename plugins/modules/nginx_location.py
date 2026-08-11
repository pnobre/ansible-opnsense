#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2026, Paulo Nobre <pnobre@pnobre.com>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/nginx.html

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.wrapper import module_wrapper
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG_DEF_FALSE
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.nginx_location import Location

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/nginx.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/nginx.html'


def run_module():
    module_args = dict(
        match_fields=dict(
            type='list', required=False, elements='str', default=['description'],
            choices=['description', 'uuid'],
            description='Fields used to match this location against the existing config',
        ),
        uuid=dict(type='str', required=False, description='Optionally supply the uuid of an existing location'),
        description=dict(type='str', required=True, aliases=['name']),
        urlpattern=dict(type='str', required=False, default='/', aliases=['url_pattern', 'path']),
        matchtype=dict(type='str', required=False, default='', choices=['', '=', '~', '~*', '^~']),
        upstream=dict(
            type='str', required=False, default='',
            description='UUID (or description) of the nginx_upstream this location proxies to',
        ),
        force_https=dict(type='bool', required=False, default=False),
        php_enable=dict(type='bool', required=False, default=False),
        websocket=dict(type='bool', required=False, default=False),
        enable_secrules=dict(type='bool', required=False, default=True),
        enable_learning_mode=dict(type='bool', required=False, default=False),
        proxy_read_timeout=dict(type='str', required=False, default=''),
        ip_acl=dict(type='str', required=False, default=''),
        root=dict(type='str', required=False, default=''),
        index=dict(type='str', required=False, default=''),
        path_prefix=dict(type='str', required=False, default=''),
        authbasicuserfile=dict(type='str', required=False, default=''),
        max_body_size=dict(type='str', required=False, default=''),
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

    module_wrapper(Location(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
