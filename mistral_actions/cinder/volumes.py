from mistral_actions.cinder.base import Base


class AssertStatus(Base):
    """Assert a volume in special status.

    :param volume_id: the volume to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, volume_id, status='available'):
        super(AssertStatus, self).__init__()
        self.volume_id = volume_id
        self.status = status

    def run(self):
        volume = self.client.volumes.get(self.volume_id)
        assert (volume.status == self.status)
        return True
