https://github.com/prometheus-community/postgres_exporter/releases/

```
mkdir -p /opt/postgres-exporter && cd /opt/postgres-exporter
wget https://github.com/prometheus-community/postgres_exporter/releases/download/v0.17.1/postgres_exporter-0.17.1.linux-amd64.tar.gz
tar -xzf postgres_exporter-0.17.1.linux-amd64.tar.gz
mv postgres_exporter-0.17.1.linux-amd64/postgres_exporter /usr/local/bin
chmod +x /usr/local/bin/postgres_exporter
```

/etc/systemd/system/postgres_exporter.service
```
# /etc/systemd/system/postgres_exporter.service
[Unit]
Description=Prometheus PostgreSQL Exporter
After=network.target

[Service]
Environment=DATA_SOURCE_NAME=postgresql://postgres_exporter:exporterpass@localhost:5432/postgres?sslmode=disable
ExecStart=/usr/local/bin/postgres_exporter
Restart=always
User=postgres

[Install]
WantedBy=multi-user.target

```
