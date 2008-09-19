#!/bin/sh

# qconf -mq <queue.q>
#   ...
#   starter_method        /server/vmstore/SGE/starter_<queue.q>.sh
#   ...


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

hostLockFile="/${hostSelectionLockFileDir}/job_host_${JOB_ID}"


host=`/bin/hostname`
virthost=`cat ${hostLockFile}`
userhost=$USER"@"$virthost

file=$SGE_ROOT"/default/spool/"$host
file=$file"/job_scripts/"$JOB_ID

filerem="/home/"$USER
filerem=$filerem"/"$JOB_ID


echo starter.sh --- hostname: `/bin/hostname` --- USER=$USER
echo starter.sh --- file: $file
echo starter.sh --- filerem: $filerem
echo starter.sh --- VHOST: $virthost
# copy batch job to the virtual machine
scp $file $userhost:$filerem

# set executable rights
ssh $userhost chmod 755 $filerem

# execute the batch job on the virtual machine
ssh $userhost $filerem

exit 0
