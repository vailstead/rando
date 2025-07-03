list status
```
patronictl -c /etc/patroni.yml list
```

failover
```
patronictl -c /etc/patroni.yml failover my_cluster1 --candidate node2
```

validating replication:
1. leader
```
SELECT client_addr, state, sync_state, write_lag, flush_lag, replay_lag
FROM pg_stat_replication;

FROM pg_stat_replication;
  client_addr  |   state   | sync_state | write_lag | flush_lag | replay_lag
---------------+-----------+------------+-----------+-----------+------------
 192.168.1.217 | streaming | async      |           |           |
 192.168.1.216 | streaming | async      |           |           |
```

optional - create and write to test table
```
CREATE TABLE replicate_test (id serial PRIMARY KEY, note text);
INSERT INTO replicate_test (note) VALUES ('replication works!');
```

2. Now from another node
```
SELECT * FROM replicate_test;

postgres=# SELECT * FROM replicate_test;
 id |        note
----+--------------------
  1 | replication works!
(1 row)
```

## ETCD
basic health check
```
ETCDCTL_API=3 etcdctl \
  --endpoints="http://192.168.1.215:2379,http://192.168.1.216:2379,http://192.168.1.217:2379" \
  endpoint health --write-out=table
```

check status
```
ETCDCTL_API=3 etcdctl \
  --endpoints="http://192.168.1.215:2379,http://192.168.1.216:2379,http://192.168.1.217:2379" \
  endpoint status --write-out=table
```

