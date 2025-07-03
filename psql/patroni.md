# single node setup

## 1. Install etcd

```
apt install -y etcd
```

Edit config
```
vim /etc/default/etcd
```

```
ETCD_LISTEN_PEER_URLS="http://0.0.0.0:2380"
ETCD_LISTEN_CLIENT_URLS="http://0.0.0.0:2379"
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://localhost:2380"
ETCD_ADVERTISE_CLIENT_URLS="http://localhost:2379"
ETCD_INITIAL_CLUSTER="default=http://localhost:2380"
ETCD_INITIAL_CLUSTER_STATE="new"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"
```

Start etcd
```
sudo systemctl enable etcd
sudo systemctl restart etcd
```

Verify
```
etcdctl --endpoints=http://localhost:2379 member list
```
