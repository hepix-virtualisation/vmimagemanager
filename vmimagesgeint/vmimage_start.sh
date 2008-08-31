#!/bin/bash
#
# start the virtual machine virtual-sge01.desy.de using the image  <queue>
#
# within visudo the path to this file has to checked
#   Cmnd_Alias SGE = /server/vmstore/SGE/vmimage_start.sh
#
#
echo vmstart: queue=$1

freeHost=`/usr/bin/vmimagemanager.py -f | head -n 1`
if [ -z "$freeHost" ] ; then 
  echo "No virtual maschine available"
  exit 1
fi
/usr/bin/vmimagemanager.py -b $freeHost -r $1

exit 0
