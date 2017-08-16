from mistral_actions.openstack import OpenstackBase as base

POWER_STATES = [
    'nostate',  # 0x00
    'running',  # 0x01
    '',  # 0x02
    'paused',  # 0x03
    'shutdown',  # 0x04
    '',  # 0x05
    'crashed',  # 0x06
    'suspended'  # 0x07
]


class InvalidStatusException(Exception):
    pass


class NotExpectedStatusException(Exception):
    pass


class AssertStatus(base):
    """Assert a server in special status.

    :param server: the server to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, server_id, status='ACTIVE'):
        super(AssertStatus, self).__init__('nova')
        self.server_id = server_id
        self.status = status

    def run(self):
        server = self.client.servers.get(self.server_id)
        if server.status != self.status:
            raise NotExpectedStatusException(
                "server status is '%s', expect '%s'" % (server.status,
                                                        self.status))
        return True


class GetStatus(base):
    """Get a server status.

    :param server_id: the server uuid
    """
    __export__ = True

    def __init__(self, server_id):
        super(GetStatus, self).__init__('nova')
        self.server_id = server_id

    def run(self):
        server = self.client.servers.get(self.server_id)
        return server.status


class AssertPowerStatus(base):
    """Assert a server's power in special status.

    :param server: the server uuid.
    :param status: (optional)expect power status.
    """
    __export__ = True

    def __init__(self, server_id, status='running'):
        super(AssertPowerStatus, self).__init__('nova')
        self.server_id = server_id
        self.status = status

    def run(self):
        server = self.client.servers.get(self.server_id)
        if server.status == 'ERROR':
            raise InvalidStatusException("The server is in ERROR status")
        power_state = POWER_STATES[getattr(server, 'OS-EXT-STS:power_state')]
        if power_state != self.status:
            raise NotExpectedStatusException(
                "server status is '%s', expect '%s'" % (power_state,
                                                        self.status))
        return True
