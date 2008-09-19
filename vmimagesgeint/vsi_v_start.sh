#!/bin/bash
#
# start the virtual machine using the image  <queue>
#
# within visudo the path to this file has to checked
#   Cmnd_Alias SGE = /server/vmstore/SGE/prod_vmimage_start.sh, /server/vmstore/
#   SGE/prod_vmimage_stop.sh/server/vmstore/SGE/vmimage_start.sh
#
Queue=$1
JobId=$2


if [ -z "${prefix}" ] ; then
prefix="/opt/vmimagesgeint/"
fi

if [ -z "${hostSelectionLockFile}" ] ; then
hostSelectionLockFile=${prefix}/var/vmimagesgeint/hostSelectionLockFile
fi


hostSelectionLockFileDir=`dirname ${hostSelectionLockFile}`
if [ ! -d ${hostSelectionLockFileDir} ] ; then
  echo the directory hostSelectionLockFileDir does not exist at patch ${hostSelectionLockFileDir}
  exit 1
fi



doTheWork()
{
echo Queue=$Queue
echo JobId=$JobId

export PATH=$PATH:/usr/sbin/
freeHost=`/usr/bin/vmimagemanager.py -f | head -n 1`
if [ -z "$freeHost" ] ; then 
  echo "No virtual maschine available"
  return 1
fi
echo ${freeHost} > /${hostSelectionLockFileDir}/job_host_${JobId}
echo "vmimage start: VM=$freeHost -Queue=$Queue" 
/usr/bin/vmimagemanager.py -b $freeHost -r $Queue
echo "vmimage start: finished"
}

lockfile ${hostSelectionLockFile}
doTheWork
RET=$?
rm -f ${hostSelectionLockFile}
exit ${RET}
