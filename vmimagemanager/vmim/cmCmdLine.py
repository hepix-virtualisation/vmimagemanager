import os
import logging, logging.config
import sys
import optparse
import vmCtrl
import string
from __version__ import version 
def usage():
    print "usage"


# User interface


def main():
    log = logging.getLogger("main")
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-b', '--box', action ='append',help="Select 'boxes' to operate.")
    p.add_option('-s', '--store', action ='append', help='Database Initiation string')
    p.add_option('-r', '--restore', action ='append',help='Add endorser in your subscribe to imagelist action.')
    p.add_option('-e', '--extract', action ='append',help='Certificate directory.', metavar='INPUTDIR')
    p.add_option('-i', '--insert', action ='append',help='Select subscription', metavar='UUID')
    p.add_option('-c', '--config', action ='append',help='Select subscription', metavar='URL')
    p.add_option('--cpu', action ='store',help='Sets the output format')
    p.add_option('-u', '--up', action ='store_true',help='Delete subscription')
    p.add_option('-d', '--down', action ='store_true',help='Information on subscription')
    p.add_option('-l', '--list-boxes', action ='store_true',help='Export File.', metavar='OUTPUTFILE')
    p.add_option('-L', '--list-images', action ='store_true',help='Logfile configuration file.', metavar='LOGFILE')
    #p.add_option('-v', '--version', action ='store_true',help='Event application to launch.', metavar='EVENT')    
    p.add_option('-k', '--kill', action ='store_true',help='Export File.', metavar='OUTPUTFILE')
    p.add_option('-z', '--tgz', action ='store_true',help='Logfile configuration file.', metavar='LOGFILE')
    p.add_option('-y', '--rsync', action ='store_true',help='Event application to launch.', metavar='EVENT')
    p.add_option('-w', '--cpio-bzip', action ='store_true',help='Event application to launch.', metavar='EVENT')
    p.add_option('--lvm', action ='store_true',help='Event application to launch.', metavar='EVENT')
    p.add_option('-o', '--print-config', action ='append',help='Export File.', metavar='OUTPUTFILE')
    p.add_option('--logfile', action ='store',help='Logfile configuration file.', metavar='LOGFILE')
    
    
    
    options, arguments = p.parse_args()
    # OptionValues
    logFile = None
    box = []
    actions = set()
    actionsReqBoxes = set(['up','down','store','restore','extract','insert','kill'])
    actionsReqStorageFormat = set(['store','restore','extract','insert'])
    actionsReqStorageName = set(['store','restore'])
    actionsReqStorageExtracts = set(['extract'])
    actionsReqStorageInsert = set(['insert'])
    
    cmdFormatOptions = set([])
    ConfigurationFilePath = '/etc/vmimagemanager/vmimagemanager.cfg'
    print_config = False
    store = []
    cmdInserts = []
    Control = vmCtrl.vmControl()
    
    if 'VMIM_CFG' in os.environ:
        ConfigurationFilePath = os.environ['VMIM_CFG']
    if 'VMIM_LOG_CONF' in os.environ:
        logFile = os.environ['VMILS_LOG_CONF']
    
    # Set up log file
    if options.logfile:
        logFile = options.logfile
    if logFile != None:
        if os.path.isfile(str(options.logfile)):
            logging.config.fileConfig(options.logfile)
        else:
            logging.basicConfig(level=logging.INFO)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.logfile))
            sys.exit(1)
    else:
        logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("main")
    # Now logging is set up process other options
    if options.box:
        box = options.box
    if options.store:
        store = options.store
        print "sssssssss",store
    if options.restore:
        restore = options.restore
    if options.insert:
        insert = options.insert
    if options.extract:
        extract = options.extract
    if options.config != None:
        if os.path.isfile(str(options.logfile)):
            ConfigurationFilePath = str(options.config)
        else:
            log.error("Configuration file '%s' was not found." % (options.logfile))
            sys.exit(1)
        
    if options.cpu:
        cpu = options.cpu
    if options.up:
        actions.add("up")
    if options.down:
        actions.add("down")
    if options.list_boxes:
        actions.add("list_boxes")
    if options.list_images:
        actions.add("list_images")
    if options.kill:
        actions.add("kill")
    if options.tgz:
        cmdFormatOptions.add("tar_gz")
    if options.rsync:
        cmdFormatOptions.add("rsync")
    if options.cpio_bzip:
        cmdFormatOptions.add("cpio_bzip")
    if options.print_config:
        print_config = True

    # 1 So we have some command line validation
    if len(actions) == 0:
        log.error("No actions selected")
        sys.exit(1)
    if len(actions) > 1:
        log.error("More than one action selected.")
        sys.exit(1)

    Control.LoadConfigCfg(ConfigurationFilePath)
    # Handle conflicting actions
    actions_req_sel = actionsReqBoxes.intersection(actions)
    lenActions_req_sel = len(actions_req_sel)
    lenBoxes = len(box)
    lenStore = len(store)
    
    if (lenActions_req_sel > 0) and (lenBoxes == 0):
        log.error('Box selections are reqired with these actions:%s.', string.join(actionsReqBoxes,','))
        sys.exit(1)
    lenCmdFormatOptions = len(cmdFormatOptions)
    
    needStorageFormat = actionsReqStorageFormat.intersection(actions)
    lenNeedStorageFormat = len(needStorageFormat)
    if lenNeedStorageFormat > 0:
        if (lenCmdFormatOptions == 0):
            cmdFormatOptions.add("rsync")
            log.info("Defaulting storage format to 'rsync'.")
            lenCmdFormatOptions = len(cmdFormatOptions)
        if (lenCmdFormatOptions > 1):
            log.error('Conflicting storage format options.')
            sys.exit(1)
    
    needStorageName = actionsReqStorageName.intersection(actions)
    lenNeedStorageName = len(needStorageName)
    if lenNeedStorageName > 0:
        if (lenBoxes != lenStore):
            if (lenBoxes > lenStore):
                log.error('More boxes than storage names.')
            if (lenBoxes < lenStore):
                log.error('More storage names then boxes.')
            sys.exit(1)
    
    needStorageExtracts = actionsReqStorageExtracts.intersection(actions)
    lenNeedStorageExtracts = len(needStorageExtracts)
    if lenNeedStorageExtracts > 0:
        if (lenBoxes != lenStore):
            if (lenBoxes > lenStore):
                log.error('More boxes than storage names.')
            if (lenBoxes < lenStore):
                log.error('More storage names then boxes.')
            sys.exit(1)
    
    
    needStorageInsert = actionsReqStorageInsert.intersection(actions)
    lenNeedStorageInsert = len(needStorageInsert)
    if lenNeedStorageInsert > 0:
        if (lenBoxes != lenStore):
            if (lenBoxes > lenStore):
                log.error('More boxes than storage names.')
            if (lenBoxes < lenStore):
                log.error('More storage names then boxes.')
            sys.exit(1)
    
    # Handle conflicting identifiers

    
    actionsList = []
    if "list_boxes" in actions:
        actionsList.append("list_boxes")
    if "list_images" in actions:
        actionsList.append("list_images")
    if "up" in actions:
        actionsList.append("up")
    if "down" in actions:
        actionsList.append("down")
    hostdetails = {}
    
    
    for index in range(lenBoxes):
        thisBox = box[index]
        boxdetails = {'libVirtName' : thisBox,
                'storeFormat' : 'rsync',}
        if lenNeedStorageInsert > 0:
            boxdetails['storeName'] = store[index]
        if lenNeedStorageInsert > 0:
            boxdetails['storeInsert'] = store[index]
        if lenNeedStorageExtracts > 0:
            boxdetails['storeExtract'] = store[index]
        
        print 'yyyyyyyyy',boxdetails
        hostdetails[thisBox] = boxdetails
    instructions = { 'vmControl' : { 'actions' : actionsList,
            'hostdetails' : hostdetails
            }
        }

    Control.Process(instructions)

if __name__ == "__main__":
    main()
    
