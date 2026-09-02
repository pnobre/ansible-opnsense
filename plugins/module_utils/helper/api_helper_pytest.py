def test_placeholder():
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.api import \
        _load_credential_file, check_or_load_credentials, check_host, ssl_verification, \
        get_params_path, _clean_response, debug_api, check_response, api_pretty_exception, \
        _safe_response_repr


def test_safe_response_repr_omits_request_body():
    # a failed API call must not echo the POST body (holds the plaintext 'password')
    from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.api import \
        _safe_response_repr

    class _FakeReq:
        body = 'username=admin&password=SUPERSECRET'

    class _FakeResp:
        status_code = 400
        reason = 'Bad Request'
        url = 'https://opnsense.example/api/openvpn/instances/add'
        text = '{"result":"failed"}'
        request = _FakeReq()
        __dict__ = {'request': _FakeReq(), 'status_code': 400}

    out = _safe_response_repr(_FakeResp())
    assert 'SUPERSECRET' not in out
    assert 'password' not in out
    assert '400' in out and 'result' in out
