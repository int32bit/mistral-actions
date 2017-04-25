from mistral_actions.cinder.base import Base


class AssertStatus(Base):
    """Assert a volume backup in special status.

    :param backup_id: the volume backup to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, backup_id, status='available'):
        super(AssertStatus, self).__init__()
        self.backup_id = backup_id
        self.status = status

    def run(self):
        backup = self.client.backups.get(self.backup_id)
        assert (backup.status == self.status)
        return True


class Create(Base):
    """Creates a volume backup.

    :param volume_id: The ID of the volume to backup.
    :param container: The name of the backup service container.
    :param name: The name of the backup.
    :param description: The description of the backup.
    :param incremental: Incremental backup.
    :param force: If True, allows an in-use volume to be backed up.
    :rtype: :class:`VolumeBackup`
    """
    __export__ = True

    def __init__(self,
                 volume_id,
                 backup_name,
                 snapshot_id=None,
                 description=None,
                 container=None,
                 incremental=True,
                 force=True):
        super(Create, self).__init__()
        self.volume_id = volume_id
        self.backup_name = backup_name
        self.snapshot_id = snapshot_id
        self.description = description
        self.container = container
        self.incremental = incremental
        self.force = force

    def _has_backups(self):
        search_opts = {'volume_id': self.volume_id}
        backups = self.client.backups.list(
            detailed=False, search_opts=search_opts)
        return len(list(backups)) > 0

    def run(self):
        if self.incremental and not self._has_backups():
            self.incremental = False
        backup = self.client.backups.create(
            self.volume_id,
            container=self.container,
            name=self.backup_name,
            description=self.description,
            incremental=self.incremental,
            force=self.force,
            snapshot_id=self.snapshot_id)
        return backup
