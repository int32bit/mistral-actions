import datetime

from mistral_actions.exceptions import NotExpectedStatusException
from mistral_actions.openstack import OpenstackBase as base


class AssertStatus(base):
    """Assert a volume snapshot in special status.

    :param snapshot_id: the volume snapshot to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, snapshot_id, status='available'):
        super(AssertStatus, self).__init__('cinder')
        self.snapshot_id = snapshot_id
        self.status = status

    def run(self):
        snapshot = self.client.volume_snapshots.get(self.snapshot_id)
        if snapshot.status != self.status:
            raise NotExpectedStatusException(
                "snapshot status is '%s', expect '%s'" % (snapshot.status,
                                                          self.status))
        return True


class CreateSnapshot(base):
    """Create a snapshot for a volume.

    :param volume_id: volume uuid.
    """
    __export__ = True

    def __init__(self, volume_id):
        super(CreateSnapshot, self).__init__('cinder')
        self.volume_id = volume_id

    def run(self):
        time = datetime.datetime.strftime(datetime.datetime.utcnow(),
                                          "%Y_%m_%d_%H_%M_%S")
        volume = self.client.volumes.get(self.volume_id)
        snapshot_name = "%(volume_name)s_snap_%(time)s" % {
            'volume_name': volume.name,
            'time': time
        }
        description = "Created by Mistral at %s" % datetime.datetime.utcnow()
        snapshot = self.client.volume_snapshots.create(
            self.volume_id,
            force=True,
            name=snapshot_name,
            description=description)
        return snapshot
