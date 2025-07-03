# single node setup

Assumes Ubuntu 24  

## 1. Install etcd

```
apt install -y etcd-server etcd-client
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


## 2. Install PostgreSQL 17
```
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
sudo apt update
apt install -y postgresql-17
```

Stop postgresq service (patroni will manage the service)
```
systemctl stop postgresql
systemctl disable postgresql
```

Set /var/lib/postrgresql/17 ownership to postgres user (created during postgres install)
```
chown -R postgres:postgres /var/lib/postgresql/17
```

Either move the default auto-initialized data directory or remove it. Patroni expects to completely manage the PostgreSQL including initializing the data directory, maaging postgresql.conf, pg_hba.conf, WAL setup, and controlling restarts and state
```
mv /var/lib/postgresql/17/main /var/lib/postgresql/17/main.bak
OR
rm -rf /var/lib/postgresql/17/main
```

## 3. Install Patroni
```
apt install -y python3-pip python3-psycopg2 gcc libpq-dev
pip3 install patroni[etcd] --break-system-packages
```

## 4. Create Patroni config
```
scope: my_cluster
name: node1

restapi:
  listen: 127.0.0.1:8008
  connect_address: 127.0.0.1:8008

etcd:
  host: 127.0.0.1:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
  initdb:
    - encoding: UTF8
    - data-checksums
  users:
    postgres:
      password: postgres_password
  post_init: echo 'init complete'

postgresql:
  listen: 127.0.0.1:5432
  connect_address: 127.0.0.1:5432
  data_dir: /var/lib/postgresql/15/main
  bin_dir: /usr/lib/postgresql/15/bin
  authentication:
    superuser:
      username: postgres
      password: postgres_password
    replication:
      username: replicator
      password: replicator_password
  parameters:
    wal_level: replica
    hot_standby: "on"
    max_wal_senders: 10
    max_replication_slots: 10
```

## 5. Start Patroni
```
patroni /etc/patroni.yml
```

## 6. Connect to DB
```
psql -h 127.0.0.1 -U postgres
```
