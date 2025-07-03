node ip: 192.168.1.217
```
## /etc/default/etcd
## etcd(1) daemon options
## See "/usr/share/doc/etcd-server/op-guide/configuration.md.gz"
## for available options.
##
## Use environment to override, for example: ETCD_NAME=default

ETCD_NAME=node3

ETCD_LISTEN_PEER_URLS="http://192.168.1.217:2380"
ETCD_LISTEN_CLIENT_URLS="http://192.168.1.217:2379,http://127.0.0.1:2379"

ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.1.217:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.1.217:2379"

ETCD_INITIAL_CLUSTER="node1=http://192.168.1.215:2380,node2=http://192.168.1.216:2380,node3=http://192.168.1.217:2380"
ETCD_INITIAL_CLUSTER_STATE=new
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-01"
```

patroni conf
```
# /etc/patroni.yml
scope: my_cluster1

name: node3

restapi:
  listen: 0.0.0.0:8008
  connect_address: 192.168.1.217:8008

etcd3:
  hosts:
    - 192.168.1.215:2379
    - 192.168.1.216:2379
    - 192.168.1.217:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        max_connections: 100
        max_wal_senders: 5
        wal_keep_segments: 8
        wal_level: replica
        hot_standby: "on"

  initdb:
    - encoding: UTF8
    - data-checksums

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 192.168.1.217:5432
  data_dir: /var/lib/postgresql/data
  bin_dir: /usr/lib/postgresql/17/bin
  authentication:
    superuser:
      username: postgres
      password: your_superuser_password_here
    replication:
      username: replicator
      password: your_replication_password_here
  pg_hba:
    - host replication replicator 127.0.0.1/32 md5 # used for local Patroni checks
    - host replication replicator 192.168.1.0/24 md5 # used for streaming replication from other members
    - host all all 0.0.0.0/0 md5


watchdog:
  mode: off

```
