import sys
import logging, logging.handlers
import commands
import random
import pexpect

#!/bin/bash
#
# start the virtual machine using the image  <queue>
#
# within visudo the path to this file has to checked
#   Cmnd_Alias SGE = /server/vmstore/SGE/prod_vmimage_start.sh, /server/vmstore/
#   SGE/prod_vmimage_stop.sh/server/vmstore/SGE/vmimage_start.sh
#

## ORIGINAL bash script based comment.if [ -z "${prefix}" ] ; then
## ORIGINAL bash script based comment.prefix="/opt/vmimagesgeint"
## ORIGINAL bash script based comment.fi
## ORIGINAL bash script based comment.
Prefix = "/opt/vmimagesgeint"


## ORIGINAL bash script based comment.doTheWork()
## ORIGINAL bash script based comment.{
## ORIGINAL bash script based comment.echo Queue=$Queue
## ORIGINAL bash script based comment.echo JobId=$JobId
## ORIGINAL bash script based comment.
## ORIGINAL bash script based comment.export PATH=$PATH:/usr/sbin/
## ORIGINAL bash script based comment.freeHost=`/usr/bin/vmimagemanager.py -f | head -n 1`
## ORIGINAL bash script based comment.if [ -z "$freeHost" ] ; then 
## ORIGINAL bash script based comment.  echo "No virtual maschine available"
## ORIGINAL bash script based comment.  return 1
## ORIGINAL bash script based comment.fi


def lock():
    cmd="lockfile %s/var/vmimagesgeint/hostSelectionLockFile" % (Prefix)
    (rc,cmdoutput) = commands.getstatusoutput(cmd)
    if rc != 0:
        logging.error('Command "%s" Failed' % (cmd))
        logging.info( 'rc=%s,output=%s' % (rc,cmdoutput))
        return -1
    return 0
    
def unlock():
    cmd="rm -f %s/var/vmimagesgeint/hostSelectionLockFile" % (Prefix)
    (rc,cmdoutput) = commands.getstatusoutput(cmd)
    if rc != 0:
        logging.error('Command "%s" Failed' % (cmd))
        logging.info( 'rc=%s,output=%s' % (rc,cmdoutput))
        return -1
    return 0
    
    


def getAvailableHostList():
    #freeHost=`/usr/bin/vmimagemanager.py -f `
    freeHostList = []
    
    cmd="vmimagemanager.py -f"
    (rc,cmdoutput) = commands.getstatusoutput(cmd)
    if rc != 0:
        logging.error('Command "%s" Failed' % (cmd))
        logging.info( 'rc=%s,output=%s' % (rc,cmdoutput))
        return -1
    freeHostList = cmdoutput.strip().split('\n')
    parsedlist = []
    #print freeHostList
    for i in range (0,len( freeHostList)):
        if "" != freeHostList[i].strip():
            parsedlist.append(freeHostList[i].strip())
    return parsedlist
    
def registerHost( HostName,   JobId):
    fileName = "/%s/job_host_%s" % (hostSelectionLockFileDir,JobId)
    fp = open (fileName,"w")
    fp.write(HostName + '\n')
    fp.close()
def startHost(HostName,Image):

    # ORIGINAL bash script based comment.echo ${freeHost} > /${hostSelectionLockFileDir}/job_host_${JobId}
    ## ORIGINAL bash script based comment.echo "vmimage start: VM=$freeHost -Queue=$Queue"  
    ## ORIGINAL bash script based comment./usr/bin/vmimagemanager.py -b $freeHost -r $Queue
    cmd="/usr/bin/vmimagemanager.py -b %s -r %s" % (HostName ,Image)
    (rc,cmdoutput) = commands.getstatusoutput(cmd)
    if rc != 0:
        logging.error('Command "%s" Failed' % (cmd))
        logging.info( 'rc=%s,output=%s' % (rc,cmdoutput))
        return -1
    
    return 0
    

def waitHostUp(host):
    cmd = 'xm console %s' % (host)
    print cmd
    child = pexpect.spawn (cmd)
    child.logfile = sys.stdout
    i = -1
    while i <= 0:
        try:
            i = child.expect (['\n','login:', 'Password:'], timeout=1)
            print str(child.before) + str(child.after)
        except pexpect.EOF:
            logging.error('Console conection failed')
            return 4
        except pexpect.TIMEOUT:
            child.sendline ('\n')
    child.close(True)
    return 5
    
def doTheWork(Queue,JobId):
    
    freeHostList = getAvailableHostList()
    if len(freeHostList) == 0:
        logging.error('No available hosts.')
        return 1
    randomHost = freeHostList[random.randrange(len(freeHostList))]
    registerHost(randomHost,JobId)
    
    logging.debug('randomHost=%s' % (randomHost))
    startedOk = startHost(randomHost,Queue)
    if not startedOk:
        return 2
    bootedOk = waitHostUp(randomHost)
    if bootedOk != 0:
        return bootedOk
    return 0
    
    
if __name__ == "__main__":

    ## ORIGINAL bash script based comment.Queue=$1
    ## ORIGINAL bash script based comment.JobId=$2

    if len(sys.argv) < 3:
        logging.error('Not enough parameter %s' %(sys.argv))
        displayhelp()
        sys.exit(1)
    
    Queue = sys.argv[1]
    JobId = sys.argv[2]

    logging.info('Queue =  "%s" JobId =  "%s"' % (Queue,JobId))
    ## ORIGINAL bash script based comment.if [ -z "${hostSelectionLockFile}" ] ; then
    ## ORIGINAL bash script based comment.hostSelectionLockFile=${prefix}/var/vmimagesgeint/hostSelectionLockFile
    ## ORIGINAL bash script based comment.fi
    
    hostSelectionLockFile="%s/var/vmimagesgeint/hostSelectionLockFile" % (Prefix)
    
    ## ORIGINAL bash script based comment.hostSelectionLockFileDir=`dirname ${hostSelectionLockFile}`

    hostSelectionLockFileDir="%s/var/vmimagesgeint/" % (Prefix)

    ## ORIGINAL bash script based comment.if [ ! -d ${hostSelectionLockFileDir} ] ; then
    ## ORIGINAL bash script based comment.  echo the directory hostSelectionLockFileDir does not exist at patch ${hostSelectionLockFileDir}
    ## ORIGINAL bash script based comment.  exit 1
    ## ORIGINAL bash script based comment.fi



    ## ORIGINAL bash script based comment.lockfile ${hostSelectionLockFile}
    ## ORIGINAL bash script based comment.doTheWork
    ## ORIGINAL bash script based comment.RET=$?
    try:
        lock()
        WorkedOk = doTheWork(Queue,JobId)
    finally:
        unlock()
        ## ORIGINAL bash script based comment.rm -f ${hostSelectionLockFile}
        ## ORIGINAL bash script based comment.exit ${RET}
    if WorkedOk == True:
        sys.exit(1)
    else:
        sys.exit(0)      
