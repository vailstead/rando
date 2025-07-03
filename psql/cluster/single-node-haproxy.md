```
sudo apt update && sudo apt install haproxy -y

vim /etc/haproxy/haproxy.cfg

sudo systemctl enable haproxy
sudo systemctl restart haproxy
```


```
# /etc/haproxy/haproxy.cfg
        stats timeout 30s
        user haproxy
        group haproxy
        daemon

        # Default SSL material locations
        ca-base /etc/ssl/certs
        crt-base /etc/ssl/private

        # See: https://ssl-config.mozilla.org/#server=haproxy&server-version=2.0.3&config=intermediate
        ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
        ssl-default-bind-ciphersuites TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
        ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
        log     global
        mode    http
        option  httplog
        option  dontlognull
        timeout connect 5000
        timeout client  50000
        timeout server  50000
        errorfile 400 /etc/haproxy/errors/400.http
        errorfile 403 /etc/haproxy/errors/403.http
        errorfile 408 /etc/haproxy/errors/408.http
        errorfile 500 /etc/haproxy/errors/500.http
        errorfile 502 /etc/haproxy/errors/502.http
        errorfile 503 /etc/haproxy/errors/503.http
        errorfile 504 /etc/haproxy/errors/504.http

# ROUTE ALL WRITES TO THE LEADER NODE ONLY
frontend postgres_write
    bind *:5432
    mode tcp
    default_backend patroni_leader

backend patroni_leader
    mode tcp
    option httpchk GET /master
    http-check expect status 200
    server node1 192.168.1.215:5432 check port 8008
    server node2 192.168.1.216:5432 check port 8008
    server node3 192.168.1.217:5432 check port 8008

# OPTIONAL: ROUTE READS TO ALL REPLICAS (INCLUDING LEADER)
#frontend postgres_read
#    bind *:5433
#    default_backend patroni_replicas
#
#backend patroni_replicas
#    option httpchk GET /replica
#    http-check expect status 200
#    server node1 192.168.1.215:5432 check port 8008
#    server node2 192.168.1.216:5432 check port 8008
#    server node3 192.168.1.217:5432 check port 8008
                                                     
```
