#!/bin/sh
python setup.py install
mistral-actions clear
mistral-actions register
systemctl restart openstack-mistral-engine openstack-mistral-executor
