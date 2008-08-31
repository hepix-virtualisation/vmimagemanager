#!/bin/bash
#
# stop the virtual machine
#
# within visudo the path to this file has to checked
#   Cmnd_Alias SGE = /server/vmstore/SGE/prod_vmimage_start.sh, /server/vmstore/
#   SGE/prod_vmimage_stop.sh/server/vmstore/SGE/vmimage_start.sh
#
#
VIRTUALHOST=$1
JOB_ID=$2
export PATH=$PATH:/usr/sbin/
echo "vmimage stop: VM=$VIRTUALHOST "
/usr/bin/vmimagemanager.py -b $VIRTUALHOST -d 
bill=""
while [ -z "$bill" ]
do
  sleep 1
  echo "sleeping 1 sec"
  bill=`/usr/bin/vmimagemanager.py -f | grep "$VIRTUALHOST"`
done
echo tmpfile="/tmp/${JOB_ID}"
ls -l /tmp/${JOB_ID}
rm /tmp/${JOB_ID}
echo "vmimage stop: finished as `id`"
 
exit 0
