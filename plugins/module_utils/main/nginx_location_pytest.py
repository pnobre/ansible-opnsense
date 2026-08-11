import pytest

from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.nginx_location import Location
from ansible_collections.oxlorg.opnsense.plugins.module_utils.test.mock_pytest import \
    AnsibleError, MockAnsibleModule


BASE_PARAMS = {
    'state': 'present',
    'match_fields': ['description'],
    'description': 'Radarr',
    'urlpattern': '/',
    'matchtype': '',
    'upstream': '5a885965-3f60-466f-958d-3ffa41a30799',
    'force_https': True,
    'php_enable': False,
    'websocket': True,
    'enable_secrules': True,
    'enable_learning_mode': False,
    'proxy_read_timeout': '',
    'ip_acl': '',
    'root': '',
    'index': '',
    'path_prefix': '',
    'authbasicuserfile': '',
    'max_body_size': '',
}


def _build(mocker, exists: bool) -> Location:
    module = MockAnsibleModule()
    module.params.update(BASE_PARAMS)
    result = {'changed': False, 'diff': {'before': {}, 'after': {}}}
    location = Location(module=module, result=result)

    mocker.patch.object(location, 'find', side_effect=lambda **kwargs: setattr(location, 'exists', exists))
    mocker.patch.object(location, '_base_check')

    return location


def test_check_requires_urlpattern(mocker):
    location = _build(mocker, exists=False)
    location.p['urlpattern'] = ''

    with pytest.raises(AnsibleError):
        location.check()


def test_check_passes_with_urlpattern(mocker):
    location = _build(mocker, exists=False)

    location.check()
