#!/bin/sh

# Parametres du backup : 

DEST=/media/EXTERNAL/backup/
DAYS=300
# pour etre plus bavard, decommenter cette option : 
RSYNC_OPTIONS="-P -H"
HOST="laptop"

# On backupe dans un dossier <host>_<date>
NOW="${HOST}_`date +%Y%m%d`"
LINKDEST=""
for i in `ls -rt $DEST|tail -3`
do
if [ "$i" != "$NOW" ]
    then
    LINKDEST="$LINKDEST --link-dest $DEST/$i/"
    fi
done

mkdir "$DEST/$NOW"
rsync / $DEST/$NOW/ -a --delete --numeric-ids --exclude "proc/*" --exclude "sys/*" --exclude "dev/*" --exclude "home/skhaen/.gvfs" --exclude "media/*" --exclude "/mnt/" $LINKDEST $RSYNC_OPTIONS
touch "$DEST/$NOW"
 
# Ensuite on fait du menage : effacement des dossiers de plus de X jours
echo "Cleanup ..."
find "$DEST" -maxdepth 1 -mindepth 1 -type d -mtime +$DAYS -print -exec rm -rf {} \; 

