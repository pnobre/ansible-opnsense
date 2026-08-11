from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.wireguard_server import Server
from ansible_collections.oxlorg.opnsense.plugins.module_utils.test.mock_pytest import MockAnsibleModule


def test_cmds_uses_real_controller_actions():
    # ServerController.php only has searchServerAction/getServerAction/addServerAction/...
    # (no bare getAction) -- 'search': 'get' silently hit an unrelated route returning
    # nothing usable, so find() could never adopt an existing server.
    assert Server.CMDS['search'] == 'search_server'


def test_api_key_path_matches_getserveraction_response_shape():
    # getServerAction returns getBase('server', 'servers.server', $uuid), which wraps the
    # result as {'server': {...}} -- one level, not a 3-level nested path.
    assert Server.API_KEY_PATH == 'server'


def test_search_call_handles_list_result(mocker):
    # search() (base/logic.py) always returns a list of entries, never a dict -- search_call()
    # used to do raw[list(raw.keys())[0]], which can never work on a list. Dormant until the
    # two fixes above let real (non-empty) data reach this code path.
    module = MockAnsibleModule()
    result = {'changed': False, 'diff': {'before': {}, 'after': {}}}
    server = Server(module=module, result=result)

    mocker.patch.object(server, 'search', return_value=[{'carp_depend_on': 'vip-value'}])

    existing = server.search_call()

    assert existing == [{'carp_depend_on': 'vip-value'}]
    assert server.existing_vips == 'vip-value'
