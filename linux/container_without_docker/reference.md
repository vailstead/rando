debootstrap - Bootstrap a Debian base system into a target directory.
```
debootstrap --variant=minbase stable ./my-container https://deb.debian.org/debian/
```

chroot - Run COMMAND with root directory set to NEWROOT.
```
chroot ./my-container
```

apt-get - retrieval of packages
```
apt-get install iputils-ping procps vim nodejs iproute2 -y

iputils-ping - Tools to test the reachability of network hosts (ping)
procps - /proc file system utilities (top)
vim - VIM - Vi IMproved editor
nodejs - evented I/O for V8 javascript - runtime executable
iproute2 - networking and traffic control tools
dnsutils - DNS utilities (nslookup)
```

unshare - Run a program with some namespaces unshared from the parent
```
# unshare [options] [<program> [<argument>...]]
unshare --mount --pid --uts --net --cgroup --fork /bin/bash
```

ip netns - manage network namespaces
```
##
# ip - show / manipulate routing, network devices, interfaces and tunnels
# A network namespace is logically another copy of the network stack, with its own routes, firewall rules, and network devices
# ip-netns - process network namespace management
# ip netns add NAME - create a new named network namespace
# ip-link - network device configuration
##

# list current network namepsaces
ip netns

# add namespace
ip netns add my-container-ns

# create a virtual Ethernet (veth) pair - two linked virtual network interfaces that act like the ends of a cable.
ip link add hosteth type veth peer name containereth

# Move the 'containereth' end of the veth pair into the container namespace
ip link show containereth # <--- shows interfaces in the current (default) namespace 
ip netns exec my-container-ns ip link show # <---- shows interfaces in the namespaced arg after exec. i.e. my-container-ns

ip link set containereth netns my-container-ns # <---- adds the containereth interface to the my-container-ns network namespace

ip addr add 10.0.0.1/24 dev hosteth # <--- add an ip to the hosteth device, OUTSIDE of the container NS
ip link set hosteth up # <--- bring the link up

ip netns exec my-container-ns ip add add 10.0.0.2/24 dev containereth # <--- INSIDE the container ns, add an ip to the container eth device
ip netns exec my-container-ns ip link set containereth up # <---- INSIDE the container ns, set the link up

ping 10.0.0.2 # <--- check connection from host -> container ns
ip netns exec my-container-ns ping 10.0.0.1 # <---- check connection from container ns -> host
ip netns exec my-container-ns ping 8.8.8.8 # <--- expected to fail, this will check connection from container ns -> internet. we'll fix this in a second

# iptables	The legacy Linux firewall / packet filter utility.
# -t nat	Use the NAT table — handles address translation.
# -A POSTROUTING	Append a rule to the POSTROUTING chain — this acts after packets are routed, right before they leave the host.
# -s 10.0.0.0/24	Match packets with a source IP in your namespace subnet (the virtual network you created).
# -j MASQUERADE	The “jump” action — masquerade replaces the packet’s source IP with the host’s outgoing IP.
# When a packet from 10.0.0.x is about to leave the host, rewrite its source IP to the host’s external IP, so replies come back
# correctly. The host keeps a connection tracking table, so when a reply returns, it knows how to un-NAT it and send it back to
# the namespace
ip tables -t nat -A POSTROUTING -s 10.0.0.0/24 -j MASQUERADE

# add a default route in the container namespace
ip netns exec my-container-ns ip route add default via 10.0.0.1

ip netns exec my-container-ns ping 8.8.8.8 # show work now
```

DNS inside container - needs /etc/resolve.conf 
```
unshare --mount --pid --uts --net --cgroup --fork /bin/bash
ip netns exec my-container-ns chroot ./my-container /bin/bash
cp /etc/resolv.conf /etc/resolve.conf-bak
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

Mount proc inside container for process isolation
```
mount -t proc proc /proc
# mount — attach a filesystem.
# -t proc — filesystem type is proc (procfs).
# proc — the (dummy) source label; often written as proc or none.
# /proc — the target mountpoint.
```