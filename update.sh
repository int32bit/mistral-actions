#!/bin/sh
python setup.py install
mistral-actions register --override
systemctl restart openstack-mistral-engine openstack-mistral-executor
mistral-actions markdown-dump 2>/dev/null >action_catalog.md
