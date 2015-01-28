#!/bin/sh

# flush & destroy ipsets:
ipset flush blackip4
# this next one may fail if iptables not properly flushed before
ipset destroy blackip4

ipset flush blackip6
# this next one may fail if iptables not properly flushed before
ipset destroy blackip6
