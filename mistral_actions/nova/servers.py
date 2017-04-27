from mistral_actions.openstack import OpenstackBase as base


class AssertStatus(base):
    """Assert a server in special status.

    :param server: the server to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, server, status='ACTIVE'):
        super(AssertStatus, self).__init__('nova')
        self.server = server
        self.status = status

    def run(self):
        server = self.client.servers.get(self.server)
        assert (server.status == self.status)
        return True
