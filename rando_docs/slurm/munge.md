# reference: https://github.com/dun/munge/wiki/Installation-Guide
adduser --system --group munge  

wget https://github.com/dun/munge/releases/download/munge-0.5.16/munge-0.5.16.tar.xz  

tar xJf munge-0.5.16.tar.x  

cd munge-0.5.16  

apt install libssl-dev
./configure \
 --prefix=/usr \
 --sysconfdir=/etc \
 --localstatedir=/var \
 --runstatedir=/run  

make  
make check  

chown -R munge:munge /etc/munge  
chmod -R 700 /etc/munge

chown -R munge:munge /var/lib/munge  
chmod -R 711 /var/lib/munge

chown -R munge:munge /var/log/munge  
chmod -R 700 /var/log/munge/

mkdir /run/munge  
chown -R munge:munge /run/munge  
chmod -R 755 /run/munge  

sudo -u munge /usr/sbin/mungekey --verbose

sudo systemctl enable munge.service  
sudo systemctl start munge.service  
sudo systemctl status munge  

# verify
munge -n | unmunge