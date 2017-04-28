## OpenStack Mistal Actions

👉[English](./README.md)

Mistral是Mirantis公司为Openstack开发的工作流组件，提供Workflow As a Service服务。其中最典型的应用为创建定时任务，比如定时磁盘备份、定时开关机等。应用场景包括任务计划服务Cloud Cron,任务调度Task Scheduling, 复杂的运行时间长的业务流程等。对应的是AWS的SWS(Simple Workflow Serivce)。其愿景是：

>The project is to provide capability to define, execute and manage tasks and workflows without writing code.

虽然官方愿景是零代码实现任务管理和调度，但如果需要自定义action还是需要写代码的，实际上自己写action的可能性非常大，一方面因为官方提供的action存在不少问题，比如`nova.servers_find`这个action常常作为创建虚拟机的workflow实例，其中用了`id`过滤参数，事实上`nova.servers_find`并不支持`id`过滤，这是由nova API服务决定的。另一方面是常常满足不了我们的实际需求，比如一个应用场景是定时给用户创建磁盘增量备份，如果备份链超过某个长度，则创建一个新的备份链，这由`cinder.backups_create`action是难以实现的。

可惜的是官方并没有提供灵活方便注册新action的方法，根据[官方开发文档](https://docs.openstack.org/developer/mistral/developer/creating_custom_action.html)，创建新的action必须重新安装Mistral服务，这在生产环境是完全不能接受的。

这个项目旨在提供一个非常简单易用的工具来管理Mistral自定义action，包含的特性如下：

* 支持自动发现已安装的actions，不需要修改任何配置项和entry point。
* 支持自动注册actions，免重新安装和配置，不需要中止已运行的Mistral服务。
* 提供简单的命令行工具管理action，支持列举、注册、注销、清空等操作。
* 收集了一些常用的action和workflow。


### 快速入门

如果你没有耐心读下去，这里提供一个一键脚本完成初始化工作，请确保你目前工作在mistral控制节点。

```sh
git clone https://github.com/int32bit/mistral-actions.git
cd mistral-actions
sudo pip install .
mistral-actions register
sudo systemctl restart openstack-mistral-engine openstack-mistral-executor
mistral-actions action-list
```

执行成功后会输出已注册的action列表。接下来是详细步骤。

#### 1. 安装

该插件需要安装在所有的Mistral节点上，因此以下脚本需要在所有的Mistral节点执行：

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

安装完后，你可以使用`mistral-actions`命令行工具来管理action，使用`help`子命令查看帮助信息：

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

#### 2. 自动发现

运行`discover`子命令会自动发现系统已经安装的action：

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
| int32bit.nova.servers.assert_status     | Assert a server in special status.                                 | server_id, status="ACTIVE"                                                                                  |
| int32bit.system.exec                    | Run command with arguments and return its output as a byte string. | cmd                                                                                                      |
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
```

#### 3. 注册

前面自动发现了在系统上的所有action，如果检查没有问题后就可以执行注册了，注册使用`register`子命令：

```
$ mistral-actions register
Follow actions have been registered:
int32bit.system.exec(cmd): Run command with arguments and return its output as a byte string.
int32bit.cinder.backups.assert_status(backup_id, status="available"): Assert a volume backup in special status.
int32bit.cinder.backups.create(volume_id, backup_name, snapshot_id=null, description=null, container=null, incremental=true, force=true): Creates a volume backup.
int32bit.cinder.volumes.assert_status(volume_id, status="available"): Assert a volume in special status.
int32bit.cinder.snapshots.assert_status(snapshot_id, status="available"): Assert a volume snapshot in special status.
int32bit.nova.servers.assert_status(server_id, status="ACTIVE"): Assert a server in special status.
int32bit.glance.images.assert_status(image_id, status="active"): Assert a image in special status.
int32bit.glance.images.filter_by(**kwargs): List image filtered by id, name, status, etc.
```

**注:** 你可以使用`--override`参数强制覆盖系统已有的action。

注册完成，需要重启所有的Mistral服务:

```bash
systemctl restart openstack-mistral-{api,engine,executor}
```

#### 4. 查看已注册的action列表:

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
| int32bit.nova.servers.assert_status     | Assert a server in special status.                                 | server_id, status="ACTIVE"                                                                                  |
| int32bit.system.exec                    | Run command with arguments and return its output as a byte string. | cmd                                                                                                      |
+-----------------------------------------+--------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------+
```

有输出结果看，action已经成功注册到Mistral中了，你可以在你的workflow使用或者直接运行action：

```sh
mistral run-action mistral_actions.nova.servers.ServerAssertStatus '{"server_id":"ef7ee146-1c27-448f-b948-d8821c59ec51"}'
```

### Action列表

|name|description|input_str|
|---|---|---|
|int32bit.cinder.backups.assert_status|Assert a volume backup in special status.|backup_id, status="available"|
|int32bit.cinder.backups.create|Creates a volume backup.|volume_id, backup_name, snapshot_id=null, description=null, container=null, incremental=true, force=true|
|int32bit.cinder.snapshots.assert_status|Assert a volume snapshot in special status.|snapshot_id, status="available"|
|int32bit.cinder.volumes.assert_status|Assert a volume in special status.|volume_id, status="available"|
|int32bit.glance.images.assert_status|Assert a image in special status.|image_id, status="active"|
|int32bit.glance.images.filter_by|List image filtered by id, name, status, etc.|**kwargs|
|int32bit.nova.servers.assert_status|Assert a server in special status.|server_id, status="ACTIVE"|
|int32bit.system.exec|Run command with arguments and return its output as a byte string.|cmd|

请访问[Action Catalog](./action_catalog.md)查看完整的action列表。

### 如何写一个自己的action

非常简单，你只需要写一个类继承自`mistral_actions.openstack.OpenstackBase`，并把你的模块放到`mistral_actions`目录即可，你需要修改任何配置文件，如下:

```python
from mistral_actions.openstack import OpenstackBase as base


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
        assert (server.status == self.status)
        return True
```

**注意：你需要添上`__export__` 属性标识它为一个action类。**

你可以使用`format_code.sh`脚本来格式化你的代码保证它符合pep8标准。最后运行`tox -e pep8`保证最终代码符合pep8标准：

```
./format_code.sh
tox -e pep8
```

重新注册服务并重启Mistral服务：

```
mistral-actions discover
mistral-actions register
systemctl restart openstack-mistral-engine openstack-mistral-executor
```

你现在就可以在你的workflow中使用你自己的action了:

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
      action: int32bit.nova.servers.assert_status server_id=<% $.server_id %> status='ACTIVE'
      retry:
        delay: 5
        count: 5
```

### 开发文档

For information on how to contribute to this project, please see the
contents of the CONTRIBUTING.rst.

Any new code must follow the development guidelines detailed
in the HACKING.rst file, and pass all unit tests.

### Workflow实例

#### 虚拟机开机

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
      action: int32bit.nova.servers.assert_status server_id=<% $.server_id %> status='ACTIVE'
      retry:
        delay: 5
        count: 5
```

#### 创建虚拟机快照

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

#### 创建磁盘备份

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

访问[examples](./examples)获取更多的workflow例子。

### License

MIT

### 贡献列表

* int32bit

### 外部链接

1. [Mistral’s developer documentation](https://docs.openstack.org/developer/mistral/)
2. [How to write a Custom Action](https://docs.openstack.org/developer/mistral/developer/creating_custom_action.html)
