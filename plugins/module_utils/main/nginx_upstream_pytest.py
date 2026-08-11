import pytest

from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.nginx_upstream import Upstream
from ansible_collections.oxlorg.opnsense.plugins.module_utils.test.mock_pytest import \
    AnsibleError, MockAnsibleModule


BASE_PARAMS = {
    'state': 'present',
    'match_fields': ['description'],
    'description': 'Radarr',
    'serverentries': ['4efe0840-8ebc-4b4b-8147-041f5e2ecdbd'],
    'load_balancing_algorithm': '',
    'keepalive': None,
    'keepalive_requests': None,
    'keepalive_timeout': None,
    'host_port': None,
    'x_forwarded_host_verbatim': False,
    'proxy_protocol': False,
    'store': False,
    'tls_enable': False,
    'tls_client_certificate': '',
    'tls_name_override': '',
    'tls_protocol_versions': [],
    'tls_session_reuse': True,
    'tls_trusted_certificate': [],
    'tls_verify': True,
    'tls_verify_depth': 1,
}


def _build(mocker, exists: bool) -> Upstream:
    module = MockAnsibleModule()
    module.params.update(BASE_PARAMS)
    result = {'changed': False, 'diff': {'before': {}, 'after': {}}}
    upstream = Upstream(module=module, result=result)

    mocker.patch.object(upstream, 'find', side_effect=lambda **kwargs: setattr(upstream, 'exists', exists))
    mocker.patch.object(upstream, '_base_check')

    return upstream


def test_check_requires_serverentries(mocker):
    upstream = _build(mocker, exists=False)
    upstream.p['serverentries'] = []

    with pytest.raises(AnsibleError):
        upstream.check()


def test_check_passes_with_serverentries(mocker):
    upstream = _build(mocker, exists=False)

    upstream.check()
