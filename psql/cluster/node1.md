```
## /etc/default/etcd
## etcd(1) daemon options
## See "/usr/share/doc/etcd-server/op-guide/configuration.md.gz"
## for available options.
##
## Use environment to override, for example: ETCD_NAME=default
ETCD_ENABLE_V2=true
#ETCD_LISTEN_PEER_URLS="http://0.0.0.0:2380"
#ETCD_LISTEN_CLIENT_URLS="http://0.0.0.0:2379"
#ETCD_INITIAL_ADVERTISE_PEER_URLS="http://127.0.0.1:2380"
#ETCD_ADVERTISE_CLIENT_URLS="http://127.0.0.1:2379"
#ETCD_INITIAL_CLUSTER="default=http://127.0.0.1:2380"
#ETCD_INITIAL_CLUSTER_STATE="new"
#ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"


ETCD_NAME=node1

ETCD_LISTEN_PEER_URLS="http://192.168.1.215:2380"
ETCD_LISTEN_CLIENT_URLS="http://192.168.1.215:2379,http://127.0.0.1:2379"

ETCD_INITIAL_ADVERTISE_PEER_URLS="http://192.168.1.215:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://192.168.1.215:2379"

ETCD_INITIAL_CLUSTER="node1=http://192.168.1.215:2380,node2=http://192.168.1.216:2380,node3=http://192.168.1.217:2380"
ETCD_INITIAL_CLUSTER_STATE=new
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-01"
```

Check leader status
```
etcdctl --endpoints="http://192.168.1.215:2379,http://192.168.1.216:2379,http://192.168.1.217:2379" endpoint status --write-out=table
```
