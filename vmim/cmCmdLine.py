import os
import logging, logging.config
import sys
import optparse
import vmCtrl
import string
from __version__ import version 
def usage():
    print("usage")


# User interface
def displayCommandOutputListBox(Input):
    print('Name                                            Disk Virt')
    print('---------------------------------------------------------')
    for key in Input["vmControl"]["listBox"].keys():
        name = Input["vmControl"]["listBox"][key]["name"]
        nameLen = len(name)
        if nameLen < 30:
            while len(name) < 50:
                name += " "
        
        line = ("%s %s %s" % (name,Input["vmControl"]["listBox"][key]["disk"],Input["vmControl"]["listBox"][key]["libvirt"]))
        print(line)



def displayCommandOutputListImages(Input):
    #import json
    #print json.dumps(Input, sort_keys=True, indent=4)
    print('Name                 Directory                     Format')
    print('---------------------------------------------------------')
    for directory in Input["vmControl"]["listImages"].keys():
        for key in Input["vmControl"]["listImages"][directory].keys():
            availableKeys = Input["vmControl"]["listImages"][directory][key].keys()
            Name = Input["vmControl"]["listImages"][directory][key]['Name']
            ImageType = None
            if 'type' in availableKeys:
                ImageType = Input["vmControl"]["listImages"][directory][key]['type']
            while len(Name) < 20:
                    Name += " "
            Path = None
            if 'Path' in availableKeys:
                Path = Input["vmControl"]["listImages"][directory][key]['Path']
            while len(Path) < 30:
                    Path += " "
            print(Name,Path,ImageType)
          
def displayCommandOutputListOverlay(Input):
    print('Name                 Directory                     Format')
    import json
    print(json.dumps(Input, sort_keys=True, indent=4))

def displayCommandOutput(Input):
    if not isinstance(Input,dict):
        return
        
    inputkeys = Input.keys()
    if not "vmControl" in inputkeys:
        return
    if not isinstance(Input["vmControl"],dict):
        return 
    OuputTypes = Input["vmControl"].keys()
    if "listBox" in OuputTypes:
        displayCommandOutputListBox(Input)
    if "listImages" in OuputTypes:
        displayCommandOutputListImages(Input)
    if "listOverlays" in OuputTypes:
        displayCommandOutputListOverlay(Input)
    

def pairsNnot(list_a,list_b):
    len_generate_list = len(list_a)
    len_image_list = len(list_b)
    ocupies_generate_list = set(range(len_generate_list))
    ocupies_image_list = set(range(len_image_list))
    ocupies_pairs = ocupies_image_list.intersection(ocupies_generate_list)
    diff_a = ocupies_generate_list.difference(ocupies_image_list)
    diff_b = ocupies_image_list.difference(ocupies_generate_list)
    arepairs = []
    for i in ocupies_pairs:
        arepairs.append([list_a[i],list_b[i]])
    notpairs_a = []
    for i in diff_a:
        notpairs_a.append(list_a[i])
    notpairs_b = []
    for i in diff_b:
        notpairs_b.append(list_b[i])

    return arepairs,notpairs_a,notpairs_b


def main():
    log = logging.getLogger("main")
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-b', '--box', action ='append',help="Select box(s) to operate.")
    p.add_option('-u', '--up', action ='store_true',help='Start boxes.')
    p.add_option('-d', '--down', action ='store_true',help='Stop boxes.')
    p.add_option('-k', '--kill', action ='store_true',help='Boxes to kill. Simulates power off for box.', metavar='ACTION')
    p.add_option('-l', '--list-boxes', action ='store_true',help='List Boxes.')
    p.add_option('-L', '--list-images', action ='store_true',help='List images.')
    p.add_option('--list-inserts', action ='store_true',help='List images overlays.')
    p.add_option('-s', '--store', action ='append', help='Image name(s) to store for box(s)')
    p.add_option('-r', '--restore', action ='append',help='Image name(s) to restore for box(s).')
    p.add_option('-i', '--insert', action ='append',help='Insert name(s) to restore for box(s).')
    p.add_option('-e', '--extract', action ='append',help='Extract name(s) to restore for box(s).')
    p.add_option('--extract-directory', action ='append',help='Extract name(s) need a target directory to store.')


    #p.add_option('-v', '--version', action ='store_true',help='Event application to launch.', metavar='EVENT')    
    p.add_option('-y', '--rsync', action ='store_true',help="Sets storeage options to 'rsync'. (default)")
    p.add_option('-w', '--cpio-bzip', action ='store_true',help="Sets storeage options to 'cpio.bz2'.")
    p.add_option('-z', '--tgz', action ='store_true',help="Sets storeage options to 'tar.gzip'.")
    p.add_option('--lvm', action ='store_true',help="Sets storeage options to 'lvm'. (experimental)")
    p.add_option('--core', action ='store',help='Sets the number of cores to start VM with. Overrides the configureds value.', metavar='CORE')
    p.add_option('--mount', action ='store_true',help='Mount the box(es) disk.')
    p.add_option('--release', action ='store_true',help='Release box(es) disk.')
    
    p.add_option('--config', action ='store',help='Read vmimagemanager configutration file', metavar='VMIM_CFG')
    p.add_option('--print-config', action ='store',help='Write a vmimagemanager configuration file.', metavar='OUTPUTFILE')
    p.add_option('-v','--verbose', action ='count',help='Change global log level, increasing log output.', metavar='LOGFILE')
    p.add_option('-q','--quiet', action ='count',help='Change global log level, decreasing log output.', metavar='LOGFILE')
    p.add_option('--log-config', action ='store',help='Logfile configuration file, (overrides command line).', metavar='LOGFILE')
    
    
    
    options, arguments = p.parse_args()
    # OptionValues
    logFile = None
    box = []
    actions = set()
    actionsReqBoxes = set(['up','down','store','restore','extract','insert','kill','mount','release'])
    actionsReqStorageFormat = set(['store','restore','extract','insert'])
    actionsReqStorageName = set(['store'])
    actionsReqStorageRestoreName = set(['restore'])
    actionsReqStorageExtracts = set(['extract'])
    actionsReqStorageInsert = set(['insert'])
    actionsReqSingleBox = set(['extract'])
    cmdFormatOptions = set([])
    ConfigurationFilePath = '/etc/vmimagemanager/vmimagemanager.cfg'
    store = []
    insert = []
    extract = []
    extractDirectory = []
    storageFormat = None  
    Control = vmCtrl.vmControl()
    LoggingLevel = logging.WARNING
    LoggingLevelCounter = 2
    if 'VMIM_CFG' in os.environ:
        ConfigurationFilePath = os.environ['VMIM_CFG']
    if 'VMIM_LOG_CONF' in os.environ:
        logFile = os.environ['VMILS_LOG_CONF']
    
    # Set up log file
    if options.verbose:
        LoggingLevelCounter = LoggingLevelCounter - options.verbose
        if options.verbose == 1:
            LoggingLevel = logging.INFO
        if options.verbose == 2:
            LoggingLevel = logging.DEBUG
    if options.quiet:
        LoggingLevelCounter = LoggingLevelCounter + options.quiet
    if LoggingLevelCounter <= 0:
        LoggingLevel = logging.DEBUG
    if LoggingLevelCounter == 1:
        LoggingLevel = logging.INFO
    if LoggingLevelCounter == 2:
        LoggingLevel = logging.WARNING
    if LoggingLevelCounter == 3:
        LoggingLevel = logging.ERROR
    if LoggingLevelCounter == 4:
        LoggingLevel = logging.FATAL
    if LoggingLevelCounter >= 5:
        LoggingLevel = logging.CRITICAL
    
    if options.log_config:
        logFile = options.log_config
    if logFile != None:
        if os.path.isfile(str(options.log_config)):
            logging.config.fileConfig(options.log_config)
        else:
            logging.basicConfig(level=LoggingLevel)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.log_config))
            sys.exit(1)
    else:
        
        logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    # Now logging is set up process other options
    if options.box:
        box = options.box
    if options.store:
        store = options.store
        actions.add("store")
    if options.restore:
        restore = options.restore
        actions.add("restore")
    if options.insert:
        insert = options.insert
        actions.add("insert")
    if options.extract:
        extract = options.extract
        actions.add("extract")
    if options.extract_directory:
        extractDirectory = options.extract_directory
        actions.add("extract")
        
    if options.config != None:
        if os.path.isfile(str(options.config)):
            ConfigurationFilePath = str(options.config)
        else:
            log.error("Configuration file '%s' was not found." % (options.config))
            sys.exit(1)
        
    if options.core:
        log.error("Not implemented")
    if options.up:
        actions.add("up")
    if options.down:
        actions.add("down")
    if options.mount:
        actions.add("mount")
    if options.release:
        actions.add("release")
    if options.list_boxes:
        actions.add("list_boxes")
    if options.list_images:
        actions.add("list_images")
    if options.list_inserts:
        actions.add("list_inserts")
    if options.kill:
        actions.add("kill")
    if options.tgz:
        cmdFormatOptions.add("tgz")
    if options.rsync:
        cmdFormatOptions.add("rsync")
    if options.cpio_bzip:
        cmdFormatOptions.add("cpio.bz2")
    if options.print_config:
        log.error("Not implemented")
    
    
    # 1 So we have some command line validation
    if len(actions) == 0:
        log.error("No actions selected")
        sys.exit(1)
    #if len(actions) > 1:
    #    log.error("More than one action selected.")
    #    sys.exit(1)

    Control.LoadConfigCfg(ConfigurationFilePath)
    
    # Handle conflicting actions
    actions_req_sel = actionsReqBoxes.intersection(actions)
    lenActions_req_sel = len(actions_req_sel)

    # Check Data for only sending in available boxes.
    
    availableBoxes = []
    if (lenActions_req_sel > 0):
        instructions = {'vmControl': {'actions': ['list_boxes']}}
        boxStruct = Control.Process(instructions)
        #print "boxStruct",boxStruct
        setOfBoxes = set()
        for key in boxStruct['vmControl']['listBox'].keys():
            name = boxStruct['vmControl']['listBox'][key]['name']
            setOfBoxes.add(str(name))
        boxesSet = set(box)
        #print  "boxesSet",boxesSet,setOfBoxes
        
        availableBoxes = boxesSet.intersection(setOfBoxes)
        #print "availableBoxes",availableBoxes
        setOfUnavailableBox = boxesSet.difference(availableBoxes)
        
        #print "setOfUnavailableBox",setOfUnavailableBox
        lenSetOfUnavailableBox = len(setOfUnavailableBox)
        if lenSetOfUnavailableBox > 0:
            print("The following boxes do not exist:%s" % (string.join(setOfUnavailableBox,", ")))
            displayCommandOutput(boxStruct)
            sys.exit(1)
    lenAvailableBoxes = len(availableBoxes)
    
    if (lenActions_req_sel > 0) and (lenAvailableBoxes == 0):
        log.error('Box selections are reqired with these actions:%s.', string.join(actions_req_sel,','))
        sys.exit(1)
    actionsSingleBox = actionsReqSingleBox.intersection(actions)
    if len(actionsSingleBox) >0 and (lenAvailableBoxes > 1):
        log.error('Action(s) only availbale with a single box :%s.', string.join(actionsSingleBox,','))
        sys.exit(1)
    #if len(actions) > 1:
    #    log.error("More than one action selected.")
    #    sys.exit(1)
    
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
        if (lenNeedStorageName != lenAvailableBoxes):
            if (lenNeedStorageName > lenAvailableBoxes):
                log.error('More boxes than storage names.')
            if (lenNeedStorageName < lenAvailableBoxes):
                log.error('More storage names then boxes.')
            sys.exit(1)
    
    needStorageRestoreName = actionsReqStorageRestoreName.intersection(actions)
    lenNeedStorageRestoreName = len(needStorageRestoreName)
    if lenNeedStorageRestoreName > 0:
        if (lenNeedStorageRestoreName != lenAvailableBoxes):
            if (lenNeedStorageRestoreName > lenAvailableBoxes):
                log.error('More boxes than storage names.')
            if (lenNeedStorageRestoreName < lenAvailableBoxes):
                log.error('More storage names then boxes.')
            sys.exit(1)
    needStorageExtracts = actionsReqStorageExtracts.intersection(actions)
    lenNeedStorageExtracts = len(needStorageExtracts)
    if lenNeedStorageExtracts > 0:
        if (lenNeedStorageExtracts != lenAvailableBoxes):
            if (lenNeedStorageExtracts > lenAvailableBoxes):
                log.error('More boxes than storage names.')
            if (lenNeedStorageExtracts < lenAvailableBoxes):
                log.error('More storage names then boxes.')
            sys.exit(1)
    
    
    needStorageInsert = actionsReqStorageInsert.intersection(actions)
    lenNeedStorageInsert = len(needStorageInsert)
    if lenNeedStorageInsert > 0:
        if (lenNeedStorageInsert != lenAvailableBoxes):
            if (lenNeedStorageInsert > lenAvailableBoxes):
                log.error('More boxes than Insert.')
            if (lenNeedStorageInsert < lenAvailableBoxes):
                log.error('More Insert names then boxes.')
            sys.exit(1)
    
    
    extractList = []
    arepairs,notpairs_a,notpairs_b = pairsNnot(extract,extractDirectory)
    for (extractName,extractDir) in arepairs:
         extractList.append({'name' : extractName, 'directory' : extractDir})
    insertList = []
    for item in insert:
        insertList.append({'name' : item})
    actionsList = []
    if "list_boxes" in actions:
        pass
        #print Control.ListBoxes()
        actionsList.append("list_boxes")
    if "list_images" in actions:
        actionsList.append("list_images")
    if "list_inserts" in actions:
        actionsList.append("list_inserts")
    
    if "down" in actions:
        actionsList.append("down")
    if "store" in actions:
        actionsList.append("store")
    if "restore" in actions:
        actionsList.append("restore")
    if "extract" in actions:
        actionsList.append("extract")
    if "insert" in actions:
        actionsList.append("insert")
    if "up" in actions:
        actionsList.append("up")
    if "mount" in actions:
        actionsList.append("mount")
    if "release" in actions:
        actionsList.append("release")
    
    hostdetails = {}
    for index in range(lenAvailableBoxes):
        thisBox = box[index]
        boxdetails = {'libVirtName' : thisBox}
        if storageFormat != None:
            boxdetails['storeFormat'] = storageFormat
        if lenNeedStorageName > 0:
            boxdetails['storeName'] = store[index]
        if lenNeedStorageRestoreName > 0:
            boxdetails['restoreName'] = restore[index]
        if lenNeedStorageInsert > 0:
            boxdetails['storeInsert'] = insertList
        if lenNeedStorageExtracts > 0:
            boxdetails['storeExtract'] = extractList
        
        
        hostdetails[thisBox] = boxdetails
    instructions = { 'vmControl' : { 'actions' : actionsList} }
    
    if len(hostdetails) > 0:
        instructions['hostdetails'] = hostdetails
    log.debug('Control.Process(instructions) instructions="%s"' % (instructions))
    output = Control.Process(instructions)
    displayCommandOutput(output)

if __name__ == "__main__":
    main()
    
