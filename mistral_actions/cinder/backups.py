from datetime import datetime

from mistral_actions.exceptions import NotExpectedStatusException
from mistral_actions.openstack import OpenstackBase as base

MAX_CHAIN_LENGTH = 5
DESC_PREFIX = 'Created by Mistral'


class AssertStatus(base):
    """Assert a volume backup in special status.

    :param backup_id: the volume backup to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, backup_id, status='available'):
        super(AssertStatus, self).__init__('cinder')
        self.backup_id = backup_id
        self.status = status

    def run(self):
        backup = self.client.backups.get(self.backup_id)
        if backup.status != self.status:
            raise NotExpectedStatusException(
                "backup status is '%s', expect '%s'" % (backup.status,
                                                        self.status))
        return True


class CreateBackup(base):
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

    def __init__(self, volume_id):
        super(CreateBackup, self).__init__('cinder')
        self.volume_id = volume_id

    def _choose_parent_backup(self, chains):
        chains = sorted(chains, key=lambda c: len(c))
        for chain in chains:
            # no shorter candicate
            if len(chain) >= MAX_CHAIN_LENGTH:
                return None
            if chain[0].description.startswith(DESC_PREFIX):
                return chain[len(chain) - 1]
        return None

    def _create_backup(self,
                       volume_id,
                       name,
                       description,
                       incremental=False,
                       parent_id=None):
        body = {
            'backup': {
                'volume_id': volume_id,
                'name': name,
                'description': description,
                'incremental': incremental,
                'force': True,
                'backup_id': parent_id,
            }
        }
        return self.client.backups._create('/backups', body, 'backup')

    def run(self):
        time = datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H_%M_%S")
        backups = _get_backups_by_volume(self.client, self.volume_id)
        chains = _get_backups_chains(backups)
        parent = self._choose_parent_backup(chains)
        volume = self.client.volumes.get(self.volume_id)
        name = "%(volume_name)s_snap_%(time)s" % {
            'volume_name': volume.name,
            'time': time
        }
        description = "%s at %s" % (DESC_PREFIX, datetime.utcnow())
        if parent:
            backup = self._create_backup(self.volume_id, name, description,
                                         True, parent.id)
        else:
            backup = self._create_backup(self.volume_id, name, description)
        return backup


def _get_backups_chains(backups):
    chains = []
    while backups:
        found = False
        backup = backups.pop()
        if backup.parent_id is None:
            chains.append([backup])
            found = True
        else:
            for i in range(0, len(chains)):
                ids = [b.id for b in chains[i]]
                if backup.parent_id in ids:
                    chains[i].append(backup)
                    found = True
                    break
        if not found:
            backups.insert(0, backup)
    return chains


def _get_backups_by_volume(client, volume_id):
    search_opts = {'volume_id': volume_id}
    backups = client.backups.list(search_opts=search_opts)
    return backups
