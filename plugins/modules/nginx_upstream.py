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
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.nginx_upstream import Upstream

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/nginx.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/nginx.html'


def run_module():
    module_args = dict(
        match_fields=dict(
            type='list', required=False, elements='str', default=['description'],
            choices=['description', 'uuid'],
            description='Fields used to match this upstream against the existing config',
        ),
        uuid=dict(type='str', required=False, description='Optionally supply the uuid of an existing upstream'),
        description=dict(type='str', required=True, aliases=['name']),
        serverentries=dict(
            type='list', elements='str', required=False, default=[],
            description='UUIDs (or descriptions) of the nginx_upstream_server entries feeding this upstream',
        ),
        load_balancing_algorithm=dict(type='str', required=False, default='', choices=['', 'ip_hash']),
        keepalive=dict(type='int', required=False),
        keepalive_requests=dict(type='int', required=False),
        keepalive_timeout=dict(type='int', required=False),
        host_port=dict(type='int', required=False),
        x_forwarded_host_verbatim=dict(type='bool', required=False, default=False),
        proxy_protocol=dict(type='bool', required=False, default=False),
        store=dict(type='bool', required=False, default=False),
        tls_enable=dict(type='bool', required=False, default=False),
        tls_client_certificate=dict(type='str', required=False, default=''),
        tls_name_override=dict(type='str', required=False, default=''),
        tls_protocol_versions=dict(
            type='list', elements='str', required=False, default=[],
            choices=['TLSv1', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3'],
        ),
        tls_session_reuse=dict(type='bool', required=False, default=True),
        tls_trusted_certificate=dict(type='list', elements='str', required=False, default=[]),
        tls_verify=dict(type='bool', required=False, default=True),
        tls_verify_depth=dict(type='int', required=False, default=1),
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

    module_wrapper(Upstream(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
