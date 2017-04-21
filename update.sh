#!/bin/sh
python setup.py install
python register_actions.py --config-file /etc/mistral/mistral.conf
systemctl restart openstack-mistral-engine openstack-mistral-executor
