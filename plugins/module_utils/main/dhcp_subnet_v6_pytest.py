import pytest

from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.dhcp_subnet_v6 import SubnetV6
from ansible_collections.oxlorg.opnsense.plugins.module_utils.test.mock_pytest import \
    AnsibleError, MockAnsibleModule


BASE_PARAMS = {
    'state': 'present',
    'match_fields': ['subnet'],
    'subnet': '2001:bb6:97c5:8a06::/64',
    'interface': 'opt6',
    'description': 'WiFi',
    'pools': ['2001:bb6:97c5:8a06::1000-2001:bb6:97c5:8a06::2000'],
    'dns': [],
}


def _build(mocker, exists: bool) -> SubnetV6:
    module = MockAnsibleModule()
    module.params.update(BASE_PARAMS)
    result = {'changed': False, 'diff': {'before': {}, 'after': {}}}
    subnet = SubnetV6(module=module, result=result)

    mocker.patch.object(subnet, 'find', side_effect=lambda **kwargs: setattr(subnet, 'exists', exists))
    mocker.patch.object(subnet, '_base_check')

    return subnet


def test_check_requires_pools(mocker):
    subnet = _build(mocker, exists=False)
    subnet.p['pools'] = []

    with pytest.raises(AnsibleError):
        subnet.check()


def test_check_passes_with_pools(mocker):
    subnet = _build(mocker, exists=False)

    subnet.check()
