import pytest

from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.nginx_http_server import HttpServer
from ansible_collections.oxlorg.opnsense.plugins.module_utils.test.mock_pytest import \
    AnsibleError, MockAnsibleModule


BASE_PARAMS = {
    'state': 'present',
    'match_fields': ['uuid'],
    'servername': ['movies.home.pnobre.com'],
    'default_server': False,
    'listen_http_address': ['80', '[::]:80'],
    'listen_https_address': ['443', '[::]:443'],
    'certificate': '617f159780a1d',
    'locations': ['02676411-8b2d-4749-bbdb-e10a2606a650'],
    'real_ip_source': '',
    'https_only': True,
    'http2': True,
    'enable_acme_support': True,
    'log_handshakes': True,
}


def _build(mocker, exists: bool) -> HttpServer:
    module = MockAnsibleModule()
    module.params.update(BASE_PARAMS)
    result = {'changed': False, 'diff': {'before': {}, 'after': {}}}
    http_server = HttpServer(module=module, result=result)

    mocker.patch.object(http_server, 'find', side_effect=lambda **kwargs: setattr(http_server, 'exists', exists))
    mocker.patch.object(http_server, '_base_check')

    return http_server


def test_check_requires_servername(mocker):
    http_server = _build(mocker, exists=False)
    http_server.p['servername'] = []

    with pytest.raises(AnsibleError):
        http_server.check()


def test_check_passes_with_servername(mocker):
    http_server = _build(mocker, exists=False)

    http_server.check()
