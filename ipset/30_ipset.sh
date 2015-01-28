#!/bin/sh

# "destroy" may fail if iptables not properly flushed before

ipset flush blackip4
ipset flush blacknet4

ipset destroy blackip4
ipset destroy blacknet4

ipset create blackip4  hash:ip  family inet   timeout 14400 maxelem 131072
ipset create blacknet4 hash:net family inet   timeout 14400 maxelem 65536

iptables -F fipset 2>/dev/null
iptables -X fipset 2>/dev/null

iptables -N fipset
# WHITELIST IPSET:
iptables -A fipset -s 91.194.60.0/23  -j RETURN # ipv4 main pi
iptables -A fipset -s 193.56.58.0/24  -j RETURN # ipv4 cursys pi
iptables -A fipset -s 185.34.32.0/22  -j RETURN # ipv4 pa
iptables -A fipset -s 212.83.165.226  -j RETURN # benedict
iptables -A fipset -s 173.230.154.187 -j RETURN # secondary

iptables -A fipset -m set --match-set blackip4 src -j REJECT
iptables -A fipset -m set --match-set blacknet4 src -j REJECT

iptables -A FORWARD -j fipset

