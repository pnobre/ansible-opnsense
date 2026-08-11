import pytest

from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dyndns_account import Account
from ansible_collections.oxlorg.opnsense.plugins.module_utils.test.mock_pytest import \
    AnsibleError, MockAnsibleModule


BASE_PARAMS = {
    'state': 'present',
    'match_fields': ['description'],
    'description': 'Wire Guard',
    'enabled': True,
    'service': 'cloudflare',
    'protocol': '',
    'server': '',
    'username': 'pnobre@pnobre.com',
    'password': 'dummy-token',
    'resource_id': '',
    'hostnames': ['wg42.pnobre.com'],
    'wildcard': False,
    'zone': 'pnobre.com',
    'checkip': 'if',
    'dynipv6host': '',
    'checkip_timeout': 10,
    'force_ssl': True,
    'ttl': 300,
    'interface': 'wan',
}


def _build(mocker, exists: bool) -> Account:
    module = MockAnsibleModule()
    module.params.update(BASE_PARAMS)
    result = {'changed': False, 'diff': {'before': {}, 'after': {}}}
    account = Account(module=module, result=result)

    mocker.patch.object(account, 'find', side_effect=lambda **kwargs: setattr(account, 'exists', exists))
    mocker.patch.object(account, '_base_check')

    return account


def test_check_requires_hostnames(mocker):
    account = _build(mocker, exists=False)
    account.p['hostnames'] = []

    with pytest.raises(AnsibleError):
        account.check()


def test_check_passes_with_hostnames(mocker):
    account = _build(mocker, exists=False)

    account.check()
