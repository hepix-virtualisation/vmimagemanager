#!/bin/bash
#
# stop the virtual machine
#
# within visudo the path to this file has to checked
#   Cmnd_Alias SGE = /server/vmstore/SGE/prod_vmimage_start.sh, /server/vmstore/
#   SGE/prod_vmimage_stop.sh/server/vmstore/SGE/vmimage_start.sh
#
#
JOB_ID=$1


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
hostLockFile="/${hostSelectionLockFileDir}/job_host_${JOB_ID}"
if [ ! -f "${hostLockFile}" ] ; then
  echo ERROR: host lock file ${hostLockFile} not found
  return 1
fi
VIRTUALHOST=`cat ${hostLockFile}`
export PATH=$PATH:/usr/sbin/
echo "vmimage stop: VM=$VIRTUALHOST "
/usr/bin/vmimagemanager.py -b $VIRTUALHOST -d 
rm ${hostLockFile}
echo "vmimage stop: finished as `id`"
 
return 0
}


lockfile ${hostSelectionLockFile}
doTheWork
RET=$?
rm -f ${hostSelectionLockFile}
exit ${RET}
