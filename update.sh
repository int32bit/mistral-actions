#!/bin/sh
python setup.py install

echo
mistral-actions register --override
systemctl restart openstack-mistral-engine openstack-mistral-executor

cat >action_catalog.md <<EOF
## Action List

$(mistral-actions markdown-dump 2>/dev/null)

Update at $(date -u +'%Y-%m-%d %H:%M:%S %Z')
EOF
