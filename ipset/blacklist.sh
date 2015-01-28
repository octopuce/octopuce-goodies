#!/bin/bash

if [ ! "$1" ]
then 
    echo "Manages a blacklist of IPV4 addresses or network, and IPV6 networks"
    echo "Usage: "
    echo " cat iplist|blacklist add   - add IP or network to the blacklist"
    echo " cat iplist|blacklist del   - removes IP from the blacklist"
    echo " blacklist list             - list all ip/net in the blacklist"
    echo " blacklist flush            - purge all blacklisting on this machine"
    echo "   blacklist add and del can take an ip or net as second parameter, "
    echo "   in that case, stdin is not used" 
    echo 
    exit
fi

if [ "$1" = "flush" ]
then
    ipset flush blackip4
    ipset flush blacknet4
    ipset flush blacknet6
    echo "Flushed"
    exit
fi

if [ "$1" = "list" ]
then
    ipset list
fi

function ips {
    OPERATION="$1"
    IP="$2"
    if echo "$IP" | grep -q ":" 
    then
	# IPV6 NET
	ipset "$OPERATION" blacknet6 "$IP" 2>/dev/null
    else
	# IPV4, net or ip ?
	if echo "$IP" | grep -q "/"
	then
	    # IPV4 IP
	    ipset "$OPERATION" blackip4 "$IP" 2>/dev/null
	else
	    # IPV4 NET
	    ipset "$OPERATION" blacknet4 "$IP" 2>/dev/null
	fi
    fi
    if [ "$?" = "0" ]
    then
	echo "$OPERATION $IP OK"
    else 
	echo "ERROR $OPERATION $IP"
    fi
}


if [ "$1" = "add" ]
then
    if [ "$2" != "" ]
    then
	ips add "$2"
    else
	while read IP 
	do
	    ips add "$IP"
	done
    fi
fi


if [ "$1" = "del" ]
then
    if [ "$2" != "" ]
    then
	ips del "$2" 
    else
	while read IP 
	do
	    ips del "$IP"
	done
    fi
fi
