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
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.nginx_http_server import HttpServer

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/nginx.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/nginx.html'


def run_module():
    module_args = dict(
        match_fields=dict(
            type='list', required=True, elements='str',
            choices=['uuid'],
            description="Fields used to match this vhost against the existing config -- "
                        "'servername' can't be used here since it's a multi-value field",
        ),
        uuid=dict(type='str', required=False, description='Optionally supply the uuid of an existing vhost'),
        servername=dict(
            type='list', elements='str', required=False, default=[],
            description='Hostname(s) this vhost answers to',
        ),
        default_server=dict(type='bool', required=False, default=False),
        listen_http_address=dict(type='list', elements='str', required=False, default=[]),
        listen_https_address=dict(type='list', elements='str', required=False, default=[]),
        certificate=dict(type='str', required=False, default=''),
        locations=dict(
            type='list', elements='str', required=False, default=[],
            description='UUIDs (or descriptions) of the nginx_location entries served by this vhost',
        ),
        real_ip_source=dict(type='str', required=False, default=''),
        https_only=dict(type='bool', required=False, default=True),
        http2=dict(type='bool', required=False, default=True),
        enable_acme_support=dict(type='bool', required=False, default=True),
        log_handshakes=dict(type='bool', required=False, default=True),
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

    module_wrapper(HttpServer(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
