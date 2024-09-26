DOMAIN=registry.gitlab.domain.net
IP=192.168.100.66
openssl genrsa -out $DOMAIN.key 2048

cat << EOF > $DOMAIN.conf
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = NA
ST = NA
L = NA
O = NA
OU = NA
CN = $DOMAIN
[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = $DOMAIN
IP.1 = $IP

EOF

openssl req -new -key $DOMAIN.key -out $DOMAIN.csr -config $DOMAIN.conf

cat << EOF > $DOMAIN.conf 

authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN

EOF


openssl x509 -req \
    -in $DOMAIN.csr \
    -CA root-ca.crt -CAkey sroot-ca.key \
    -CAcreateserial -out $DOMAIN.crt \
    -days 999 \
    -sha256 -extfile $DOMAIN.conf
