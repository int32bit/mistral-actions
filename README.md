## OpenStack Mistal Actions

Mistral is the OpenStack workflow service. This project aims to provide a mechanism to define tasks and workflows without writing code, manage and execute them in the cloud environment.

Mistral allow user write a new custom action, but must reinstall Mistral if it was installed in system(ref: https://docs.openstack.org/developer/mistral/developer/creating_custom_action.html), it's hardly acceptable for production environment. This project aims to provide a simple tool to auto-discover new actions, and register it without effecting environment. This project also collect some extra useful actions which don't exist in standard action list.

### How to run ?

For the impatient:

```sh
git clone https://github.com/int32bit/mistral-actions.git
cd mistral-actions
python setup.py install
python register_actions.py --config-file /etc/mistral/mistral.conf
systemctl restart openstack-mistral-engine openstack-mistral-executor
```

#### 1. Clone this project to your mistral api node

```sh
git clone https://github.com/int32bit/mistral-actions.git
cd mistral-actions
```

#### 2. Install

```sh
sudo python setup.py install
```

#### 3. Register actions

```sh
python register_actions.py --config-file /etc/mistral/mistral.conf
```

#### 4. Restart mistral services

```sh
systemctl restart openstack-mistral-engine openstack-mistral-executor
```

#### 5. Run action

Once you succeed to register actions, you can use it in your workflow or directly run in place:

```sh
mistral run-action mistral_actions.nova.servers.ServerAssertStatus '{"server":"ef7ee146-1c27-448f-b948-d8821c59ec51"}'
```

### Action Catalog

| name | input | description |
|----|----|----|
| systems.ExecAction | cmd  |Run command with arguments and return its output as a byte string. Note you can use at most one pipe, like 'ls -l | wc -l'.|
| nova.servers.ServerAssertStatus|server, status='ACTIVE'|Assert a server in special status.|
|...|...|...|


### How to write new action ?

Write a class inherited from mistral.actions.base.Action in `mistral_actions` directory:

```python
from mistral.actions import base

class RunnerAction(base.Action):
    
    def __init__(self, param):
        # store the incoming params
        self.param = param

    def run(self):
        # return your results here
        return {'status': 0}
```

You just need add a `__export__` attribute to tell us to publish the class, and you don't need change `setup.cfg`.

You can use `format_code.sh` script to format your code to pep8 style. It's better to run `tox -e pep8` to ensure your code in pep8 style.

```
./format_code.sh
tox -e pep8
```

Register your actions and restart mistral services:

```
python setup.py install
python register_actions.py --config-file /etc/mistral/mistral.conf
systemctl restart openstack-mistral-engine openstack-mistral-executor
```

Now you can call the action example.runner

```yaml
my_workflow:
  tasks:
    my_action_task:
      action: example.runner
      input:
        param: avalue_to_pass_in
```

### Developers

For information on how to contribute to this project, please see the
contents of the CONTRIBUTING.rst.

Any new code must follow the development guidelines detailed
in the HACKING.rst file, and pass all unit tests.

### License

MIT

### Contributors

* int32bit

### References

1. [Mistral’s developer documentation](https://docs.openstack.org/developer/mistral/)
2. [How to write a Custom Action](https://docs.openstack.org/developer/mistral/developer/creating_custom_action.html)
