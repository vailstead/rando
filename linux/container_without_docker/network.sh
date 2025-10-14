CONTAINER_NETWORK=my-container-network
HOST_ETH=hosteth
CONTAINER_ETH=containereth

ip netns add $CONTAINER_NETWORK

ip link add $HOST_ETH type veth peer name $CONTAINER_ETH


ip link set $CONTAINER_ETH netns $CONTAINER_NETWORK

ip addr add 10.0.0.1/24 dev $HOST_ETH
ip link set $HOST_ETH up

ip netns exec $CONTAINER_NETWORK ip addr add 10.0.0.2/24 dev $CONTAINER_ETH
ip netns exec $CONTAINER_NETWORK ip link set $CONTAINER_ETH up

ping -c 3 10.0.0.2
ip netns exec $CONTAINER_NETWORK ping -c 3 10.0.0.1

iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -j MASQUERADE

ip netns exec $CONTAINER_NETWORK ip route add default via 10.0.0.1


EXT_IF=$(ip -4 route show default 0.0.0.0/0 | awk '{print $5}' | head -n1)
iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o "$EXT_IF" -j MASQUERADE
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i "$HOST_ETH" -o "$EXT_IF" -s 10.0.0.0/24 -j ACCEPT

# Old commands getting container -> internet working
# 0) Pick your real uplink (replace with your actual interface, e.g. eth0, eno1, wlan0)
# EXT_IF=eth0
# 1) Enable IPv4 forwarding (router behavior)
# sysctl -w net.ipv4.ip_forward=1
# # (optional, persist)  echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-forwarding.conf

# # 2) NAT traffic from 10.0.0.0/24 out your real uplink
# sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o "$EXT_IF" -j MASQUERADE

# # 3) Allow forwarding in the filter table
# #    a) allow established/related back in
# sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
# #    b) allow new flows from the veth side to the uplink
# sudo iptables -A FORWARD -i "$HOST_ETH" -o "$EXT_IF" -s 10.0.0.0/24 -j ACCEPT
