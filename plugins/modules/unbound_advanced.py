#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/unbound.html

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.wrapper import module_wrapper
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, RELOAD_MOD_ARG
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.unbound_advanced import Advanced

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/unbound_advanced.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/unbound_advanced.html'


def run_module():
    module_args = dict(
        hideidentity=dict(
            type='bool', required=False, default=False,
            description='Whether Unbound will refuse id.server/hostname.bind CH TXT queries'
        ),
        hideversion=dict(
            type='bool', required=False, default=False,
            description='Whether Unbound will refuse version.server/version.bind CH TXT queries'
        ),
        dnssecstripped=dict(
            type='bool', required=False, default=True,
            description='Whether Unbound requires DNSSEC data for trust-anchored zones, '
                        'answering SERVFAIL if it was stripped in transit'
        ),
        belownxdomain=dict(
            type='bool', required=False, default=True,
            description='Whether Unbound enables the RFC 8020 NXDOMAIN cache optimization '
                        '(harden-below-nxdomain)'
        ),
        aggressivensec=dict(
            type='bool', required=False, default=True,
            description='Whether Unbound uses aggressive NSEC/NSEC3 cache use to reduue queries '
                        'towards authoritative nameservers (aggressive-nsec)'
        ),
        prefetch=dict(
            type='bool', required=False, default=False,
            description='Whether message cache elements are prefetched shortly before they expire'
        ),
        prefetchkey=dict(
            type='bool', required=False, default=False,
            description='Whether the DNSKEY needed for validation is fetched earlier in the '
                        'validation process, when a DS record is encountered'
        ),
        qnameminstrict=dict(
            type='bool', required=False, default=False,
            description='Whether QNAME minimisation is enforced strictly, dropping the fallback '
                        'to non-minimised queries if a resolver breaks with it'
        ),
        serveexpired=dict(
            type='bool', required=False, default=False,
            description='Whether Unbound will answer with expired cache data immediately, '
                        'before trying to refresh it'
        ),
        unwantedreplythreshold=dict(
            type='int', required=False, default=0,
            description='Number of unwanted replies to detect spoofed/cache-poisoning traffic '
                        'before Unbound clears the RRset and message cache and logs a warning. '
                        '0 disables the check'
        ),
        logservfail=dict(
            type='bool', required=False, default=False,
            description='Whether SERVFAIL responses get an extra log line explaining why '
                        'validation failed'
        ),
        **OPN_MOD_ARGS,
        **RELOAD_MOD_ARG,
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

    module_wrapper(Advanced(module=module, result=result))
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
