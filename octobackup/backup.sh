#!/bin/sh

# Paramètres du backup
## Vers quel disque dur
DEST=/media/octobackup/
## Nombre de jours au-delà duquel on supprime les anciens backups
DAYS=300
## Nom de votre ordinateur (pratique si vous en avez plusieurs)
HOST="laptop"

RSYNC_OPTIONS="-P -H"
if [ ! -d "$DEST" ]
then
  echo "Disque de sauvegarde non monté !"
  exit 1
fi
# On backup dans un dossier <host>_<date>
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
 
# Ensuite on fait du ménage : effacement des dossiers de plus de X jours
echo "Cleanup ..."
find "$DEST" -maxdepth 1 -mindepth 1 -type d -mtime +$DAYS -print -exec rm -rf {} \;
