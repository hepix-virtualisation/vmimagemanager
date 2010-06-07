#!/usr/bin/python

import logging
import os.path
import sys
import getopt
import commands
import time
import re
import ConfigParser, os

import cui


import cinterface 

import cvirthost

import clibvirt


if __name__ == "__main__":
    pass
def start():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    ch.setFormatter(formatter)
    #add ch to logger
    
    logging.basicConfig(level=logging.WARNING)
    vmimlog = logging.getLogger("vmimagemanager")
    #vmimlog.setLevel(logging.DEBUG)
    vmimlog.addHandler(ch)
    
    InstallPrefix="/"

    ConfigFile = ""

    Fillocations = ['/etc/vmimagemanager/vmimagemanager.cfg']

    for fileName in Fillocations:
	    if True == os.path.isfile(fileName):
		    ConfigFile = fileName
		    break
    if len(ConfigFile) == 0:
	    ConfigFile = Fillocations[0]
    logger = logging.getLogger("vmimagemanager")
    
    #create formatter
    debugFileName = None
    #logging.config.fileConfig("logging.conf")
    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:s:r:e:i:c:D:C:udlLhvkzypfm", ["box=", "store=","restore=","extract=","insert=","config=","cpu","up","down","list-boxes","list-images","help","version","kill","tgz","rsync","print-config","free","locked"])
    except :
        cui.usage()
        logger.error('Command line option error')
        sys.exit(1)
    hostName = None
    storeImage = None
    restoreImage = None
    restoreExtension = None
    insertions = []
    extractions = []
    start = False
    stop = False
    kill = False
    actionList = []
    boxlist = []
    ParsedImage = None
    ParsedConfigFile = ""
    ParsedCpu = -1
    for o, a in opts:
        if o in ("-h", "--help"):
            cui.usage()
            sys.exit(0)
        if o in ("-v", "--version"):
            cvsTag = "$Name:  $"
            cvsTag = cvsTag[7:-2]
            if cvsTag == "": 
                cvsTag = "Development"
                print "vmimagemanager.py version: " + cvsTag
            sys.exit(0)
        if o in ("-b", "--box"):
            if a != None:
                boxlist.append(a)
        if o in ("-s", "--store"):
            actionList.append("store")
            storeImage = a
        if o in ("-r", "--restore"):
            actionList.append("restore")
            restoreImage = a
        if o in ("-e", "--extract"):
            actionList.append("extract")
            extractions.append(a)
        if o in ("-i", "--insert"):
            actionList.append("insert")
            insertions.append(a)
        
        if o in ("-c", "--config"):
            ParsedConfigFile = a
        if o in ("-C", "--cpu"):
            try:
                ParsedCpu = int(a)
            except:
                cui.usage()
                logger.error('cpu settings must be an integer.')
                sys.exit(1)
        if o in ("-D", "--debug"):
            debugFileName  = str(a)
            
        if o in ("-u", "--up"):
            actionList.append("up")
            start = True
        if o in ("-d", "--down"):
            actionList.append("down")
            stop = True
        if o in ("-k", "--kill"):
            actionList.append("kill")
            kill = True
        if o in ("-l", "--list-boxes"):
            actionList.append("list-boxes")
        if o in ("-L", "--list-images"):
            actionList.append("list-images")
        if o in ("-z", "--tgz"):
            ParsedImage = "tgz"
        if o in ("-y", "--rsync"):
            ParsedImage = "rsync"
        if o in ("-p", "--print-config"):
            actionList.append("print-config")
        if o in ("-f", "--free"):
            actionList.append("free")       
        if o in ("-m", "--locked"):
            actionList.append("locked")
        
    
    #print "foof",ParsedConfigFile,"fd"
    
    #hostlist = makeConfig()
    
    if debugFileName != None:
        logger.config.fileConfig(debugFileName)

    HostContainer = clibvirt.virtualHostContainerLibVirt()
    logger.debug('actionList=%s' % (actionList))
    if ParsedConfigFile != "":
        ConfigFile = ParsedConfigFile
    if os.path.isfile(ConfigFile):
        lcfg2c = cui.HostContainerLoadConfigFile(HostContainer,ConfigFile)
        if False == lcfg2c:
            sys.exit(1)
        
    else:
        logger.fatal("Error: Configuration File '%s' not found" % (ConfigFile))
        sys.exit(1)
    HostContainer.libvirtImport()
    
    HostContainer.cfgHostsLoad()
    HostContainer.libVirtExport()
    #print "scxxC"
    
    
    
    #print "cxxC"
    
    if ParsedImage != None:
        HostContainer.ImageMode = ParsedImage
    processingBoxes = []
    pbindex = []
    notfoundllist = []
    if len(boxlist) >0:       
        notfound = False
        foundindex = -1
        for box in boxlist:
            found = False
            for x in range (0 , len(HostContainer.hostlist)):
                #logger.debug("boxy=%s ahostsdebug=%s" % (box ,HostContainer.hostlist[x].DcgDict))
                if HostContainer.hostlist[x].HostName == box:
                    found = True
                    foundindex = x
            if found:
                pbindex.append(foundindex)
            else:
                notfoundllist.append(box)
    
    
        
        #for index in pbindex:
        #print index
        #print HostContainer.hostlist
        #logger.debug("asdsshostsdebug=%s" % (HostContainer.hostlist[index].DcgDict))
        #HostContainer.hostlist[index].cfgApply()
        #logger.debug("asssshostsdebug=%s" % (HostContainer.hostlist[index].DcgDict))
        #Lockfile = HostContainer.hostlist[index].DcgDict["LockFile"]
        #DiscLocking.__init__(HostContainer.hostlist[index],Lockfile)
    
    for x in pbindex:
        if int(ParsedCpu) > 0:
            HostContainer.hostlist[x].DcgDict["vcpu"] = int(ParsedCpu)
        HostContainer.hostlist[x].cfgApply()
        HostContainer.hostlist[x].Lock()
    #print "dslkjsdljsdlkjsd"
    
    if (len(notfoundllist) != 0):
        message = ""
        message += "The following hosts where not found:"
        for i in notfoundllist:
            message += str(i + ", ")
        logging.error(message)
        actionList.append("list-boxes")
    if "list-boxes" in actionList:
        #print  HostContainer.hostlist
        for x in range (0 , len(HostContainer.hostlist)):
            print HostContainer.hostlist[x].HostName
        sys.exit(0)
    if "print-config" in actionList:
        #if cfg.has_key("hosts"):
        #    hostlist = ""
        #    for host in cfg["hosts"]:
        #        hostlist += ":" + host 
        #    print "HOSTS=%s" % (hostlist[1:])
        #if cfg.has_key("general"):
        #    if cfg["general"].has_key("vmimages"):
        #        print "vmimages=%s" % (cfg["general"]["vmimages"])
        #    if cfg["general"].has_key("vmextracts"):
        #        print "vmextracts=%s" % (cfg["general"]["vmextracts"])
        sys.exit(0)
    if "free" in actionList:
        potentiallyFree = []
        for x in range (0 , len(HostContainer.hostlist)):
            logger.debug( "checking %s" % (HostContainer.hostlist[x].HostName))
            if not HostContainer.hostlist[x].isRunning():
                potentiallyFree.append(x)
        couldbeLocked = []
        for x in potentiallyFree:
            if not HostContainer.hostlist[x].IsLocked():
                couldbeLocked.append(x)
        for x in couldbeLocked:
            print HostContainer.hostlist[x].HostName
        sys.exit(0)       
    if "locked" in actionList:
        domainList = VitualHostsList()
        potentiallyFree = []
        for x in range (0 , len(HostContainer.hostlist)):
            if not domainList.has_key(HostContainer.hostlist[x].HostName):
                potentiallyFree.append(x)
        definatelyIsLocked = []
        for x in potentiallyFree:
            if HostContainer.hostlist[x].IsLocked():
                definatelyIsLocked.append(x)
        for ahost in definatelyIsLocked:
            print ahost.HostName
        sys.exit(0)     
    
    
    if len(actionList) == 0:
        logging.error("Error: No task selected")
        cui.usage()
        sys.exit(1)
        
    if len(pbindex) == 0:
        message = "No slot selected. The following Host slots exist:"
        logging.error(message)
        for x in range (0 , len(HostContainer.hostlist)):
            print HostContainer.hostlist[x].HostName
        sys.exit(1) 
    if "list-images" in actionList:
        for x in pbindex:
            #print dir(box)
            for image in HostContainer.hostlist[x].AvailableImageListGet():
                print image
        sys.exit(0)
    extractionsDict = {}
    for component in extractions:
        compdecp = component.split(':')
        if len(compdecp) != 2:
            logging.error("Extraction '%s' is invalid it must conatain name:dir" % (compdecp))
            cui.usage()
            sys.exit(1)
        extractionsDict[compdecp[0]] = compdecp[1]
        #print "extractionsDict=%s" % (extractionsDict)
    insertionsDict = {}
    for component in insertions:
        compdecp = component.split(':')
        if len(compdecp) != 2:
            logging.error("Insertion '%s' is invalid it must conatain name:dir" % (compdecp))
            cui.usage()
            sys.exit(1)
        insertionsDict[compdecp[0]] = compdecp[1]
    for x in pbindex:
        HostContainer.hostlist[x].PropertyExtractionsSet(extractionsDict)
        HostContainer.hostlist[x].PropertyInsertionsSet(insertionsDict)        
        #print "avirtualHost.PropertyExtractionsGet=%s" % (avirtualHost.PropertyExtractionsGet())
        if ParsedImage != None:
            HostContainer.hostlist[x].PropertyImageModeSet(ParsedImage)
    
        HostContainer.hostlist[x].PropertyImageRestoreNameSet(restoreImage)
        HostContainer.hostlist[x].PropertyImageStoreNameSet(storeImage)
        #print restoreImage
        imageList = []
        if "restore" in actionList:
            if not HostContainer.hostlist[x].AvailableImage():
                mesage = "Image '%s' not found in directory '%s'" % (restoreImage,HostContainer.hostlist[x].ImageStoreDir)
                logging.error(mesage)
                AvailableImageList = HostContainer.hostlist[x].AvailableImageListGet()
                if len(AvailableImageList) > 0:
                    mesage = "The following images where found:"
                    for item in AvailableImageList:
                        mesage += "\n" + item
                    logging.warning(mesage)
                sys.exit(1)
            
        if "insert" in actionList:
            if not HostContainer.hostlist[x].AvailableExtract():
                insertions = HostContainer.hostlist[x].PropertyInsertionsGet()
                for ext in HostContainer.hostlist[x].PropertyInsertionsGet().keys():
                    ImageName = "%s/%s" % (HostContainer.hostlist[x].ExtractDir(),ext)
                    if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
                        logging.error("Error: Insert '%s' not found in directory '%s'" % (ext,box.ExtractDir()))
                sys.exit(1)
    HaveToCheckBoxes = []
    lockedBoxes = []
    for x in pbindex:
        logging.debug("Processing=%s" % (HostContainer.hostlist[x].HostName))
        if HostContainer.hostlist[x].IsLockedByMe():
            #print "dabox.HostName"
            lockedBoxes.append(x)
            logging.debug("IsLockedByMe x=%s,hostnam=%s" % (x,HostContainer.hostlist[x].HostName))
        else:
            #print "dabox.fffffffffHostName"
            if HostContainer.hostlist[x].Lock():
                HaveToCheckBoxes.append(x)
            else:
                #print "Locked %s" % (abox)
                if not HostContainer.hostlist[x].IsLockedStill():
                    #print "foor %s,%s,%s" % (abox.IsLockedByMe(),abox.IsLockedStill(),abox.IsLocked())
                    if HostContainer.hostlist[x].Lock():
                        HaveToCheckBoxes.append(x)
                else:
                    logging.error("Host %s is nn Use")
                
    
    if (len(HaveToCheckBoxes) > 0):
        time.sleep(1)
        for x in HaveToCheckBoxes:
            if HostContainer.hostlist[x].IsLockedByMe():
                lockedBoxes.append(x)
    logging.debug("lockedBoxes=%s" % (lockedBoxes) )
    logging.debug( "pbindex=%s" % (pbindex) )
    #logging.debug(  HostContainer.hostlist[3].HostName)
    for x in lockedBoxes:
        
                
        for command in actionList:
            if command in ["kill"]:
                HostContainer.hostlist[x].Kill()
        for command in actionList:
            if command in ["extract","insert","store","restore","down"]:
                HostContainer.hostlist[x].ShutDown()
        for command in actionList:
            if command in ["extract"]:
                HostContainer.hostlist[x].Extract()
        for command in actionList:
            if command in ["store"]:
                HostContainer.hostlist[x].StoreHost()
        for command in actionList:
            if command in ["restore"]:
                HostContainer.hostlist[x].RestoreHost()
        for command in actionList:
            if command in ["insert"]:
                HostContainer.hostlist[x].Insert()
        for command in actionList:
            if command in ["extract","insert","store","restore","up"]:
                HostContainer.hostlist[x].StartUp()
                #print "called startup here"
        HostContainer.hostlist[x].Unlock()
    FoundLockedBox = False
    
    for abox in processingBoxes:
        #print abox.HostName
        if not abox in lockedBoxes:
            logging.error("Slot '%s' was locked when it was attempted to be used" % (abox.HostName))
            HostContainer.hostlist[x].Unlock()
            FoundLockedBox = True
    if FoundLockedBox:
        sys.exit(100)

