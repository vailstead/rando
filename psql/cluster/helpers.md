list status
```
patronictl -c /etc/patroni.yml list
```

failover
```
patronictl -c /etc/patroni.yml failover my_cluster1 --candidate node2
```
