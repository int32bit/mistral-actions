## OpenStack Mistal Actions

### How to run ?

#### 1. Clone this project to your mistral api node

```sh
git clone https://github.com/int32bit/mistral-actions.git
```

#### 2. Install

```sh
sudo python setup.py install
```

#### 3. Register actions

```sh
python register_actions.py --config-file /etc/mistral/mistral.conf
```

#### 4. Check actions

```sh
mistral action-list
```

#### 5. Run action

Once you succeed to register actions, you can use it in your workflow or directly run in place:

```sh
mistral run-action mistral_actions.nova.servers.ServerAssertStatus '{"server":"ef7ee146-1c27-448f-b948-d8821c59ec51"}'
```

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

You just need add a `__export__` attribute to tell us to publish the class, and you don't need change setup.cfg.

It's better to run `tox -e pep8` to ensure your code in pep8 style.

```
tox -e pep8
```

Register your actions using our script:

```
python register_actions.py --config-file /etc/mistral/mistral.conf
```

Now you can call the action example.runner

```
$ mistral-db-manage --config-file <path-to-config> populate
Now you can call the action example.runner
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
