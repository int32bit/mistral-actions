## Action List

|name|description|input_str|
|---|---|---|
|int32bit.cinder.backups.assert_status|Assert a volume backup in special status.|backup_id, status="available"|
|int32bit.cinder.backups.create|Creates a volume backup.|volume_id, backup_name, snapshot_id=null, description=null, container=null, incremental=true, force=true|
|int32bit.cinder.snapshots.assert_status|Assert a volume snapshot in special status.|snapshot_id, status="available"|
|int32bit.cinder.volumes.assert_status|Assert a volume in special status.|volume_id, status="available"|
|int32bit.glance.images.assert_status|Assert a image in special status.|image_id, status="active"|
|int32bit.glance.images.filter_by|List image filtered by id, name, status, etc.|**kwargs|
|int32bit.nova.servers.assert_status|Assert a server in special status.|server, status="ACTIVE"|
|int32bit.system.exec|Run command with arguments and return its output as a byte string.|cmd|

Update at 2017-04-27 05:51:07 UTC
