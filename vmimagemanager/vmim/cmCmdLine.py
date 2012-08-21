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
    p.add_option('-b', '--box', action ='append',help="Select box(s) to operate.")
    p.add_option('-s', '--store', action ='append', help='Image name(s) to store for box(s)')
    p.add_option('-r', '--restore', action ='append',help='Image name(s) to restore for box(s).')
    p.add_option('-e', '--extract', action ='append',help='Extract name(s) to restore for box(s).')
    p.add_option('-i', '--insert', action ='append',help='Insert name(s) to restore for box(s).')
    p.add_option('-u', '--up', action ='store_true',help='Start boxes.')
    p.add_option('-d', '--down', action ='store_true',help='Stop boxes.')
    p.add_option('-l', '--list-boxes', action ='store_true',help='List Boxes.')
    p.add_option('-L', '--list-images', action ='store_true',help='List images.')
    #p.add_option('-v', '--version', action ='store_true',help='Event application to launch.', metavar='EVENT')    
    p.add_option('-k', '--kill', action ='store_true',help='Boxes to kill. Simulates power off for box.')
    p.add_option('-y', '--rsync', action ='store_true',help="Sets storeage options to 'rsync'. (default)")
    p.add_option('-w', '--cpio-bzip', action ='store_true',help="Sets storeage options to 'cpio.bz2'.")
    p.add_option('-z', '--tgz', action ='store_true',help="Sets storeage options to 'tar.gzip'.")
    p.add_option('--lvm', action ='store_true',help="Sets storeage options to 'lvm'. (experimental)")
    p.add_option('--cpu', action ='store',help='Sets the number of cores to start VM with. Overrides the configureds value.')
    p.add_option('--config', action ='append',help='Read vmimagemanager configutration file', metavar='VMIM_CFG')
    p.add_option('--print-config', action ='store',help='Write a vmimagemanager configuration file.', metavar='OUTPUTFILE')
    p.add_option('--log-config', action ='store',help='Logfile configuration file.', metavar='LOGFILE')
    
    
    
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
    storageFormat = None
    
    
    Control = vmCtrl.vmControl()
    
    if 'VMIM_CFG' in os.environ:
        ConfigurationFilePath = os.environ['VMIM_CFG']
    if 'VMIM_LOG_CONF' in os.environ:
        logFile = os.environ['VMILS_LOG_CONF']
    
    # Set up log file
    if options.log_config:
        logFile = options.log_config
    if logFile != None:
        if os.path.isfile(str(options.log_config)):
            logging.config.fileConfig(options.log_config)
        else:
            logging.basicConfig(level=logging.INFO)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.log_config))
            sys.exit(1)
    else:
        logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("main")
    # Now logging is set up process other options
    if options.box:
        box = options.box
    if options.store:
        store = options.store
        actions.add("store")
    if options.restore:
        restore = options.restore
    if options.insert:
        insert = options.insert
    if options.extract:
        extract = options.extract
    if options.config != None:
        if os.path.isfile(str(options.log_config)):
            ConfigurationFilePath = str(options.config)
        else:
            log.error("Configuration file '%s' was not found." % (options.config))
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
        cmdFormatOptions.add("tgz")
    if options.rsync:
        cmdFormatOptions.add("rsync")
    if options.cpio_bzip:
        cmdFormatOptions.add("cpio.bz2")
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
    
    
    
    
    availableBoxes = []
    if (lenActions_req_sel > 0):
        instructions = {'vmControl': {
            'actions': ['list_boxes'],
            'hostdetails': {},
            }
        }
        boxStruct = Control.Process(instructions)
        #print "boxStruct",boxStruct
        setOfBoxes = set()
        for key in boxStruct['vmControl']['listBox'].keys():
            name = boxStruct['vmControl']['listBox'][key]['libVirtName']
            setOfBoxes.add(name)
        for ThisBox in box:
            if ThisBox in setOfBoxes:
                availableBoxes.append(ThisBox)
            else:
                log.error("Ignoring actions for unregistered box '%s'" % (ThisBox))    
        
    lenAvailableBoxes = len(availableBoxes)
    
    
    if (lenActions_req_sel > 0) and (lenAvailableBoxes == 0):
        log.error('Box selections are reqired with these actions:%s.', string.join(actionsReqBoxes,','))
        sys.exit(1)
    
    
    
    lenCmdFormatOptions = len(cmdFormatOptions)
    
    needStorageFormat = actionsReqStorageFormat.intersection(actions)
    lenNeedStorageFormat = len(needStorageFormat)
    if lenNeedStorageFormat > 0:
        if (lenCmdFormatOptions > 1):
            log.error('Conflicting storage format options.')
            sys.exit(1)
        if (lenCmdFormatOptions == 0):
            storageFormat = "rsync"
            log.info("Defaulting storage format to 'rsync'.")
        else:
            storageFormat = cmdFormatOptions.pop()
    
    needStorageName = actionsReqStorageName.intersection(actions)
    lenNeedStorageName = len(needStorageName)
    if lenNeedStorageName > 0:
        if (lenAvailableBoxes != lenStore):
            if (lenAvailableBoxes > lenStore):
                log.error('More boxes than storage names.')
            if (lenAvailableBoxes < lenStore):
                log.error('More storage names then boxes.')
            sys.exit(1)
    
    needStorageExtracts = actionsReqStorageExtracts.intersection(actions)
    lenNeedStorageExtracts = len(needStorageExtracts)
    if lenNeedStorageExtracts > 0:
        if (lenAvailableBoxes != lenStore):
            if (lenAvailableBoxes > lenStore):
                log.error('More boxes than storage names.')
            if (lenAvailableBoxes < lenStore):
                log.error('More storage names then boxes.')
            sys.exit(1)
    
    
    needStorageInsert = actionsReqStorageInsert.intersection(actions)
    lenNeedStorageInsert = len(needStorageInsert)
    if lenNeedStorageInsert > 0:
        if (lenAvailableBoxes != lenStore):
            if (lenAvailableBoxes > lenStore):
                log.error('More boxes than storage names.')
            if (lenAvailableBoxes < lenStore):
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
    if "store" in actions:
        actionsList.append("store")
    
    hostdetails = {}
    for index in range(lenAvailableBoxes):
        thisBox = box[index]
        boxdetails = {'libVirtName' : thisBox,
                'storeFormat' : storageFormat,}
        if lenNeedStorageName > 0:
            boxdetails['storeName'] = store[index]
        if lenNeedStorageInsert > 0:
            boxdetails['storeInsert'] = store[index]
        if lenNeedStorageExtracts > 0:
            boxdetails['storeExtract'] = store[index]
        
        
        hostdetails[thisBox] = boxdetails
    instructions = { 'vmControl' : { 'actions' : actionsList,
            'hostdetails' : hostdetails
            }
        }
    print 'input',instructions
    print "output='%s'"% (Control.Process(instructions))

if __name__ == "__main__":
    main()
    
