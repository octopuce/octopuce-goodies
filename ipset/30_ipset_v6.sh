#!/bin/sh

# "destroy" may fail if iptables not properly flushed before

ipset flush blacknet6

ipset destroy blacknet6

ipset create blacknet6 hash:net family inet6  timeout 14400 maxelem 131072

ip6tables -F fipset 2>/dev/null
ip6tables -X fipset 2>/dev/null

ip6tables -N fipset
# WHITELIST IPSET:
ip6tables -A fipset -s 2001:67c:288::/48  -j RETURN # ipv6 main pi
ip6tables -A fipset -s 2a00:99a0::/32  -j RETURN # ipv6 pa
ip6tables -A fipset -s 2600:3c01:e000:1c::1 -j RETURN # secondary

ip6tables -A fipset -m set --match-set blackip6 src -j REJECT
ip6tables -A fipset -m set --match-set blacknet6 src -j REJECT

ip6tables -A FORWARD -j fipset

