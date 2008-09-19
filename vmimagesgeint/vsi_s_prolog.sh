#!/bin/sh
#
# invoke the prolog script as
#     prolog=/path/to/prolog/script $job_id

JOBID=$1

echo "prolog: start. hostname="`/bin/hostname` --- JOBID = $JOBID
echo "prolog:        user="$USER

echo "prolog:        start loading VM   = "`/bin/date`
echo sge_queue=$QUEUE
sudo /opt/vmimagesgeint/sbin/vsi_v_start.sh "$QUEUE" "$JOBID"
vmimagemanagerc=$?
echo "prolog:        end   loading VM rc=$vmimagemanagerc  = "`/bin/date`
if [ "0" != "${vmimagemanagerc}" ] ; then
  echo ERROR: Failed to start virtual maschine
  exit ${vmimagemanagerc}
fi

# synchronization
sleep 30                       
echo "prolog:        end synchronization= "`/bin/date`

echo "prolog: stop."

exit 0
