from mistral_actions.nova.base import Base


class ServerAssertStatus(Base):
    """Assert a server in special status.

    :param server: the server to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, server, status='ACTIVE'):
        super(ServerAssertStatus, self).__init__()
        self.server = server
        self.status = status

    def run(self):
        server = self.client.servers.get(self.server)
        assert (server.status == self.status)
        return True
