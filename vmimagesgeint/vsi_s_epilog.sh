#!/bin/sh
#
# invoke the epilog script as
#    epilog path/to/epilog/script

virthost=`cat /tmp/$JOB_ID`

echo start epilog: hostname=`/bin/hostname` --- JOBID = $JOB_ID 
echo sge_queue=$QUEUE
# shutdown the virtual machine
sudo /opt/vmimagesgeint/sbin/vsi_v_stop.sh "$JOB_ID"

echo epilog script: end

exit 0
