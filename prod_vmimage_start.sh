#!/bin/bash
#
# start the virtual machine using the image  <queue>
#
# within visudo the path to this file has to checked
#   Cmnd_Alias SGE = /server/vmstore/SGE/prod_vmimage_start.sh, /server/vmstore/
#   SGE/prod_vmimage_stop.sh/server/vmstore/SGE/vmimage_start.sh
#

gethost()
{
local freeHost
RET="XXXXX"
LocalfreeHost=`/usr/bin/vmimagemanager.py -f | head -n 1`
if [ -z "$LocalfreeHost" ] ; then 
  echo "No virtual maschine available"
  exit 1
fi
echo "$LocalfreeHost" > /tmp/$1
RET=$LocalfreeHost
}


Queue=$1
JobId=$2
echo Queue=$Queue
echo JobId=$JobId

export PATH=$PATH:/usr/sbin/

gethost "${JobId}"
freeHost=$RET
count=`grep "$freeHost" /tmp/* | wc -l`
while [ "$count" != 1 ] ; do
  sleep 1
  gethost "${JobId}"
  freeHost=$RET
  count=`grep "$freeHost" /tmp/* | wc -l`
  
done
echo "vmimage start: VM=$freeHost - Queue=$Queue" 
/usr/bin/vmimagemanager.py -b $freeHost -r $Queue
echo "vmimage start: finished"

exit 0
