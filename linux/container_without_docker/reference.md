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
```