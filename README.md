## OpenStack Mistal Actions

Mistral is the OpenStack workflow service. This project aims to provide a mechanism to define tasks and workflows without writing code, manage and execute them in the cloud environment.

Mistral allow user write a new custom action, but must reinstall Mistral if it was installed in system(ref: https://docs.openstack.org/developer/mistral/developer/creating_custom_action.html), it's hardly acceptable for production environment. This project aims to provide a simple tool to auto-discover and register new actions without effecting environment. This project also collect some extra useful actions and workflow examples which don't exist in standard action list.

Features:

* Automatic discovery installed actions in your system.
* Register actions without any change to your Mistral Service, no need reinstall any service.
* Provide a commandline tool to manage custom actions(list, register, unregister, clear, etc.).
* Collect a lot of useful actions and workflow examples.

Potential Improvements:

* Add test.

### Quick Start

For the impatient, assume you are working in mistral node:

```sh
git clone https://github.com/int32bit/mistral-actions.git
cd mistral-actions
sudo pip install .
mistral-actions register
sudo systemctl restart openstack-mistral-engine openstack-mistral-executor
```

#### 1. Installation

Please ensure you are in mistral controller node.

```
$ git clone https://github.com/int32bit/mistral-actions.git
$ cd mistral-actions
$ sudo pip install .
Processing /root/int32bit/mistral-actions
Requirement already satisfied: pbr>=1.6 in /usr/lib/python2.7/site-packages (from mistral-actions==0.0.1.dev21)
Requirement already satisfied: prettytable>=0.7.2 in /usr/lib/python2.7/site-packages (from mistral-actions==0.0.1.dev21)
Installing collected packages: mistral-actions
  Running setup.py install for mistral-actions ... done
Successfully installed mistral-actions-0.0.1.dev21
```

Once you install sucessfully, you can use `mistral-actions` command to manage your custom actions, use `help` subcommand to get help message:

```
$ mistral-actions help
usage: mistral-actions <subcommand> ...

Positional arguments:
  <subcommand>
    action-list    List all actions have been registered in Mistral.
    clear          Unregister all actions from Mistral.
    discover       Discover all actions from this project.
    markdown-dump  Dump all discovered actions to stdout as markdown table.
    register       Register all actions to Mistral.
    unregister     Unregister a action from Mistral.
    bash-completion
                   Prints all of the commands and options to stdout.
    help           Display help about this program or one of its subcommands.

See "mistral-actions help COMMAND" for help on a specific command.
```

#### 3. Discover New Actions

```
$ mistral-actions discover
Follow actions discovered:
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| name                                    | description                                                        | input_str                                                                                                |
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| int32bit.cinder.backups.assert_status   | Assert a volume backup in special status.                          | backup_id, status="available"                                                                            |
| int32bit.cinder.backups.create          | Creates a volume backup.                                           | volume_id, backup_name, snapshot_id=null, description=null, container=null, incremental=true, force=true |
| int32bit.cinder.snapshots.assert_status | Assert a volume snapshot in special status.                        | snapshot_id, status="available"                                                                          |
| int32bit.cinder.volumes.assert_status   | Assert a volume in special status.                                 | volume_id, status="available"                                                                            |
| int32bit.glance.images.assert_status    | Assert a image in special status.                                  | image_id, status="active"                                                                                |
| int32bit.glance.images.filter_by        | List image filtered by id, name, status, etc.                      | **kwargs                                                                                                 |
| int32bit.nova.servers.assert_status     | Assert a server in special status.                                 | server, status="ACTIVE"                                                                                  |
| int32bit.system.exec                    | Run command with arguments and return its output as a byte string. | cmd                                                                                                      |
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
```

#### 4. Register New Actions:

```
$ mistral-actions register
Follow actions have been registered:
int32bit.system.exec(cmd): Run command with arguments and return its output as a byte string.
int32bit.cinder.backups.assert_status(backup_id, status="available"): Assert a volume backup in special status.
int32bit.cinder.backups.create(volume_id, backup_name, snapshot_id=null, description=null, container=null, incremental=true, force=true): Creates a volume backup.
int32bit.cinder.volumes.assert_status(volume_id, status="available"): Assert a volume in special status.
int32bit.cinder.snapshots.assert_status(snapshot_id, status="available"): Assert a volume snapshot in special status.
int32bit.nova.servers.assert_status(server, status="ACTIVE"): Assert a server in special status.
int32bit.glance.images.assert_status(image_id, status="active"): Assert a image in special status.
int32bit.glance.images.filter_by(**kwargs): List image filtered by id, name, status, etc.
```

You need to restart mistral service before use new actions:

```bash
systemctl restart openstack-mistral-{api,engine,executor}
```

#### 5. List Registered Actions:

```
$ mistral-actions action-list
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| name                                    | description                                                        | input_str                                                                                                |
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
| int32bit.cinder.backups.assert_status   | Assert a volume backup in special status.                          | backup_id, status="available"                                                                            |
| int32bit.cinder.backups.create          | Creates a volume backup.                                           | volume_id, backup_name, snapshot_id=null, description=null, container=null, incremental=true, force=true |
| int32bit.cinder.snapshots.assert_status | Assert a volume snapshot in special status.                        | snapshot_id, status="available"                                                                          |
| int32bit.cinder.volumes.assert_status   | Assert a volume in special status.                                 | volume_id, status="available"                                                                            |
| int32bit.glance.images.assert_status    | Assert a image in special status.                                  | image_id, status="active"                                                                                |
| int32bit.glance.images.filter_by        | List image filtered by id, name, status, etc.                      | **kwargs                                                                                                 |
| int32bit.nova.servers.assert_status     | Assert a server in special status.                                 | server, status="ACTIVE"                                                                                  |
| int32bit.system.exec                    | Run command with arguments and return its output as a byte string. | cmd                                                                                                      |
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
```

Once you succeed to register actions, you can use it in your workflow or directly run in place:

```sh
mistral run-action mistral_actions.nova.servers.ServerAssertStatus '{"server":"ef7ee146-1c27-448f-b948-d8821c59ec51"}'
```

### Action Catalog

|name|input_str|description|
|---|---|---|
|int32bit.cinder.backups.assert_status|backup_id, status="available"|Assert a volume backup in special status.|
|int32bit.cinder.backups.create|volume_id, backup_name, snapshot_id=null, description=null, container=null, incremental=true, force=true|Creates a volume backup.|
|int32bit.cinder.snapshots.assert_status|snapshot_id, status="available"|Assert a volume snapshot in special status.|
|int32bit.cinder.volumes.assert_status|volume_id, status="available"|Assert a volume in special status.|
|int32bit.glance.images.assert_status|image_id, status="active"|Assert a image in special status.|
|int32bit.glance.images.filter_by|**kwargs|List image filtered by id, name, status, etc.|
|int32bit.nova.servers.assert_status|server, status="ACTIVE"|Assert a server in special status.|
|int32bit.system.exec|cmd|Run command with arguments and return its output as a byte string.|

Please see [Action Catalog](./action_catalog.md) to get all action list.

### How to write new action ?

Write a class inherited from mistral.actions.base.Action in `mistral_actions` directory:

```python
from mistral_actions.nova.base import Base


class AssertStatus(Base):
    """Assert a server in special status.

    :param server: the server to check.
    :param status: (optional)expect status.
    """
    __export__ = True

    def __init__(self, server, status='ACTIVE'):
        super(AssertStatus, self).__init__()
        self.server = server
        self.status = status

    def run(self):
        server = self.client.servers.get(self.server)
        assert (server.status == self.status)
        return True
```

You just need add a `__export__` attribute to tell us to publish the class, and you don't need change `setup.cfg`.

You can use `format_code.sh` script to format your code to pep8 style. It's better to run `tox -e pep8` to ensure your code in pep8 style.

```
./format_code.sh
tox -e pep8
```

Register your actions and restart mistral services:

```
mistral-actions discover
mistral-actions register
systemctl restart openstack-mistral-engine openstack-mistral-executor
```

Now you can call the action example.runner

```yaml
---
version: "2.0"

start_server:
  type: direct

  input:
    - server_id

  description: start the specified server.

  tasks:
    start_server:
      description: start the specified server.
      action: nova.servers_start server=<% $.server_id %>
      wait-after: 2
      on-error:
        - noop
      on-complete:
        - wait_for_server

    wait_for_server:
      action: int32bit.nova.servers.assert_status server=<% $.server_id %> status='ACTIVE'
      retry:
        delay: 5
        count: 5
```

### Developers

For information on how to contribute to this project, please see the
contents of the CONTRIBUTING.rst.

Any new code must follow the development guidelines detailed
in the HACKING.rst file, and pass all unit tests.

### Workflow Examples

#### Start server

```yaml
---
version: "2.0"

start_server:
  type: direct

  input:
    - server_id

  description: start the specified server.

  tasks:
    start_server:
      description: start the specified server.
      action: nova.servers_start server=<% $.server_id %>
      wait-after: 2
      on-error:
        - noop
      on-complete:
        - wait_for_server

    wait_for_server:
      action: int32bit.nova.servers.assert_status server=<% $.server_id %> status='ACTIVE'
      retry:
        delay: 5
        count: 5
```

#### Create image from a server(snapshot)

```yaml
---
version: "2.0"

create_image:
  type: direct

  input:
    - server_id
    - image_name

  description: create an image(snapshot) from a server.

  tasks:
    create_image:
      description: create an image(snapshot) from a server.
      action: nova.servers_create_image server=<% $.server_id %> image_name=<% $.image_name %>
      on-success:
        - wait_for_image

    wait_for_image:
      action: int32bit.glance.images.filter_by name=<% $.image_name %> status='active'
      retry:
        delay: 10
        count: 30
```

#### Create volume backup

```yaml
---
version: "2.0"

create_volume_backup:
  type: direct

  input:
    - volume_id
    - backup_name
    - force: True
    - incremental: True
    - description: "Created by mistral"

  description: create a backup for a volume.

  tasks:
    create_backup:
      description: create a backup for a volume
      action: int32bit.cinder.backups.create volume_id=<% $.volume_id %> backup_name=<% $.backup_name %> force=<% $.force %> incremental=<% $.incremental %> description=<% $.description %>
      publish:
        backup_id: <% task(create_backup).result.id %>
      on-success:
        - wait_for_active

    wait_for_active:
      action: int32bit.cinder.backups.assert_status backup_id=<% $.backup_id %> status='available'
      retry:
        delay: 10
        count: 30
```

For more workflow examples, see [examples](./examples).

### License

MIT

### Contributors

* int32bit

### References

1. [Mistral’s developer documentation](https://docs.openstack.org/developer/mistral/)
2. [How to write a Custom Action](https://docs.openstack.org/developer/mistral/developer/creating_custom_action.html)
