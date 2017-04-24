from mistral_actions.cinder.base import Base


class AssertStatus(Base):
    """Assert a volume snapshot in special status.

    :param snapshot_id: the volume snapshot to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, snapshot_id, status='available'):
        super(AssertStatus, self).__init__()
        self.snapshot_id = snapshot_id
        self.status = status

    def run(self):
        snapshot = self.client.volume_snapshots.get(self.snapshot_id)
        assert (snapshot.status == self.status)
        return True
