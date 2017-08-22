from datetime import datetime

from mistral_actions.exceptions import InvalidStatusException
from mistral_actions.exceptions import NotExpectedStatusException
from mistral_actions.openstack import OpenstackBase as base

MAX_CHAIN_LENGTH = 5
DESC_PREFIX = 'Created by Mistral'


class AssertStatus(base):
    """Assert a trove backup in special status.

    :param backup_id: the trove backup to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, backup_id, status='COMPLETED'):
        super(AssertStatus, self).__init__('trove')
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
    """Creates a trove backup.

    :param instance_id: The ID of the instance to backup.
    """
    __export__ = True

    def __init__(self, instance_id):
        super(CreateBackup, self).__init__('trove')
        self.instance_id = instance_id

    def _choose_parent_backup(self, chains):
        chains = sorted(chains, key=lambda c: len(c))
        for chain in chains:
            # no shorter candicate
            if len(chain) >= MAX_CHAIN_LENGTH:
                return None
            if chain[0].description and chain[0].description.startswith(
                    DESC_PREFIX):
                return chain[len(chain) - 1]
        return None

    def _create_backup(self,
                       instance_id,
                       name,
                       description,
                       incremental=False,
                       parent_id=None):
        return self.client.backups.create(
            name,
            instance_id,
            description=description,
            parent_id=parent_id,
            incremental=incremental)

    def run(self):
        time = datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H_%M_%S")
        backups = _get_backups_by_instance(self.client, self.instance_id)
        chains = _get_backups_chains(backups)
        parent = self._choose_parent_backup(chains)
        instance = self.client.instances.get(self.instance_id)
        if instance.status != 'ACTIVE':
            raise InvalidStatusException(
                ("The instance status should be 'ACTIVE', "
                 "but current status is '%s'") % instance.status)
        name = "%(instance_name)s_snap_%(time)s" % {
            'instance_name': instance.name,
            'time': time
        }
        description = "%s at %s" % (DESC_PREFIX, datetime.utcnow())
        if parent:
            backup = self._create_backup(self.instance_id, name, description,
                                         True, parent.id)
        else:
            backup = self._create_backup(self.instance_id, name, description)
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


def _get_backups_by_instance(client, instance_id):
    resultset = []
    # Trove doesn't support to get backup list by instance
    backups = client.backups.list()
    for backup in backups:
        if backup.instance_id == instance_id:
            resultset.append(backup)
    return resultset
