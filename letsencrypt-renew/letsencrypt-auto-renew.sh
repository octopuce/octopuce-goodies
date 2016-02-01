#!/bin/bash 

# Send alert mail to this address: 
ALERT=sslalert@octopuce.fr 
LETSENCRYPT_BIN=/usr/local/letsencrypt/letsencrypt-auto 
WEBROOT=/var/www/letsencrypt 

cd "$(dirname $0)" 
HERE="$PWD "
DATE_TODAY=$(date +'%s') 
cd /etc/letsencrypt/live || (echo "Can't cd to /etc/letsencrypt/live !" && exit -1) 
for domain in * 
do 
    if [ -f "$domain/cert.pem" ] ; then 
	CERT="$domain/cert.pem" 
	CERT_END_DATE=$(openssl x509 -in "$CERT" -noout -enddate | sed -e "s/.*=//") 
	DATE_CERT=$(date -ud "$CERT_END_DATE" +"%s") 
	DATE_JOURS_DIFF=$(( ( $DATE_CERT - $DATE_TODAY ) / (60*60*24) )) 
	if [[ $DATE_JOURS_DIFF -le 30 ]]; then 
	    echo "Trying to renew certificate for domain $domain expiring in $DATE_JOURS_DIFF days" 
		    # Read the SAN (Subject Alt Names) for this cert (Warn: this code may not be super reliable :/ ) 
	    SAN=$(openssl x509 -in "$CERT"  -text|grep DNS:|sed -e "s/DNS:/-d /g" -e "s/, / /g") 
		        # Try to renew it: 
	    $LETSENCRYPT_BIN certonly --config "$HERE/renew.ini" --webroot -w "$WEBROOT" -d "$domain" $SAN 
	    if [ "$?" -ne "0" ] 
	    then 
		echo "Certificate /etc/letsencrypt/live/$domain has NOT been successfully renewed, please check" | mail -s "Can't renew certificate $domain on $(hostname)" $ALERT 
	    fi 
	fi 
    fi
done 