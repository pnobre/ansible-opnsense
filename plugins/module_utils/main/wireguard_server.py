from ansible.module_utils.basic import AnsibleModule

from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.api import \
    Session
from ansible_collections.oxlorg.opnsense.plugins.module_utils.helper.validate import \
    is_ip, is_ip_or_network, is_unset
from ansible_collections.oxlorg.opnsense.plugins.module_utils.main.wireguard_peer import Peer
from ansible_collections.oxlorg.opnsense.plugins.module_utils.base.module import BaseModule


class Server(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'add_server',
        'del': 'del_server',
        'set': 'set_server',
        # was 'get' -- ServerController.php has no bare getAction, only searchServerAction/
        # getServerAction($uuid). 'get' silently hit some other route returning an empty
        # blank-template result instead of a 404, so find() never matched an existing server
        # -- adopting a live server (e.g. via match_fields/FIELD_ID) would have created a
        # duplicate instead. 'search_server' correctly camelizes to searchServerAction via
        # Phalcon's routing (confirmed against a live OPNsense 26.7 box).
        'search': 'search_server',
        'detail': 'get_server',
        'toggle': 'toggle_server',
    }
    API_KEY = 'server'
    # was f'server.servers.{API_KEY}' ('server.servers.server') -- ServerController's
    # getServerAction returns getBase('server', 'servers.server', $uuid), which wraps the
    # result as {'server': {...}} (one level, matching API_KEY alone), not a 3-level nested
    # path. The wrong path crashed _search_path_handling as soon as find() (now working,
    # see CMDS above) tried to fetch details for a real match.
    API_KEY_PATH = API_KEY
    API_MOD = 'wireguard'
    API_CONT = 'server'
    API_CONT_REL = 'service'
    FIELDS_CHANGE = [
        'public_key', 'private_key', 'port', 'mtu', 'dns_servers', 'allowed_ips',
        'disable_routes', 'gateway', 'peers', 'vip',
    ]
    FIELDS_ALL = [FIELD_ID, 'enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'dns_servers': 'dns',
        'public_key': 'pubkey',
        'private_key': 'privkey',
        'allowed_ips': 'tunneladdress',
        'disable_routes': 'disableroutes',
        'vip': 'carp_depend_on',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'disable_routes'],
        'list': ['dns_servers', 'allowed_ips', 'peers'],
        'int': ['port', 'mtu', 'instance'],
        'select' : ['vip'],
    }
    FIELDS_DIFF_NO_LOG = ['private_key']
    INT_VALIDATIONS = {
        'mtu': {'min': 1, 'max': 9300},
        'port': {'min': 1, 'max': 65535},
    }
    STR_VALIDATIONS = {
        'name': r'^([0-9a-zA-Z._\-]){1,64}$'
    }
    EXIST_ATTR = 'server'
    FIELDS_DIFF_EXCLUDE = []

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.server = {}
        self.existing_peers = None
        self.existing_vips = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['allowed_ips']):
                self.m.fail_json(
                    "You need to provide at least one 'allowed_ips' entry "
                    "to create a server!"
                )

            if not is_unset(self.p['gateway']) and not is_ip(self.p['gateway']):
                self.m.fail_json(
                    f"Gateway '{self.p['gateway']}' is not a valid IP-address!"
                )

            if is_unset(self.p['private_key']):
                self.m.fail_json(
                    "You need to provide a 'private_key'!"
                )

        link_peers = not is_unset(self.p['peers']) or self.p['link_peers']
        if not link_peers:
            self.FIELDS_CHANGE.remove('peers')
            self.FIELDS_DIFF_EXCLUDE.append('peers')

        for entry in self.p['allowed_ips']:
            if not is_ip_or_network(entry):
                self.m.fail_json(
                    f"Allowed-ip entry '{entry}' is neither a valid IP-address "
                    f"nor a valid network!"
                )

        for dns in self.p['dns_servers']:
            if not is_ip(dns):
                self.m.fail_json(f"DNS-value '{dns}' is not a valid IP-address!")

        self.find(match_fields=[self.FIELD_ID])
        if self.exists:
            if is_unset(self.p['public_key']) or is_unset(self.p['private_key']):
                self.p['public_key'] = self.server['public_key']
                self.p['private_key'] = self.server['private_key']

        if self.p['state'] == 'present':
            if link_peers:
                self.p['peers'] = self._find_peers()

            if not is_unset(self.p['vip']):
                self.p['vip'] = self._find_vip()

        self._base_check()

    def _find_peers(self) -> list:
        peers = []
        existing = {}

        if self.existing_peers is None:
            self.existing_peers = Peer(
                module=self.m, result={}, session=self.s
            ).get_existing()

        if len(self.p['peers']) == 0:
            return []

        for peer in self.existing_peers:
            existing[peer['name']] = peer['uuid']

        for peer in self.p['peers']:
            if peer not in existing and peer not in existing.values():
                self.m.fail_json(f"Peer '{peer}' does not exist!")

            if peer in existing:
                peers.append(existing[peer])

            else:
                peers.append(peer)

        return peers

    def _find_vip(self) -> str:
        # "[192.168.1.1]  on opt1 (vhid 1)"
        search_vip = f"[{self.p['vip']}]"
        existing_vips = []

        for uuid, values in self.existing_vips.items():
            if values['value'].find(search_vip) != -1:
                return uuid

            if values['value'].find('[') != -1:
                existing_vips.append(values['value'].split('[', 1)[1].split(']')[0])

        self.m.fail_json(f"Provided VIP '{self.p['vip']}' was not found! Existing ones: {existing_vips}")

    def search_call(self) -> list:
        raw = self.search()
        if len(raw) > 0:
            # was raw[list(raw.keys())[0]][...] -- search() (base/logic.py) always returns a
            # list of entries, never a dict, so raw.keys() could never have worked. Dormant
            # until now: with the old broken CMDS['search'] this method's len(raw) > 0 branch
            # was never reached (search() always came back empty), so this line never ran on
            # a live box.
            self.existing_vips = raw[0][self.FIELDS_TRANSLATE['vip']]

        if len(raw) == 0:
            self.existing_vips = self.s.get(cnf={
                **self.call_cnf,
                'command': self.CMDS['detail'],
            })[self.API_KEY][self.FIELDS_TRANSLATE['vip']]

        return raw
