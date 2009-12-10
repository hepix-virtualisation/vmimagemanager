#!/usr/bin/python

import logging, logging.config


import os
import os.path
import string
import sys
import getopt
import commands
import time
import re

import libvirt
import cdisk

import clock
        
class virtualhost(clock.DiscLocking):
    def __init__(self):
        self.HostName = ""
        self.HostMacAddress = ""
        self.HostIp4Address = ""
        self.HostRootSpace = ""
        self.HostSwapSpace = ""
        self.ImageMode = ""
        self.PropertyInsertionsSet({})
        self.PropertyExtractionsSet({})
        self.PropertyImageRestoreNameSet("")
        self.PropertyImageStoreNameSet("")
        self.ImageStoreDir = ""
        self.ImageMode = "rsync"
        
        self.LockFileFixed = False
        self.DcgDict = {}
        
        
    def __init__(self,properties):
        self.logger = logging.getLogger("vmimagemanager.virtualhost")
        self.DcgDict = {}
        self.loadCfg(properties)
        
    def loadCfg(self,properties):
        #print "Loaded config"
        for prop in properties.keys():
            #for each property
            if not prop in self.DcgDict.keys():
                # if the property is not in the keys
                self.DcgDict[prop] = properties[prop]
                
    def RealiseDevice(self):
        found = False
        if ("HostRootSpace" in self.DcgDict.keys()) and ("HostSwapSpace" in self.DcgDict.keys()):
            self.logger.debug("sebug=%s" % (self.DcgDict))
            self.DiskSubsystem = cdisk.VirtualHostDiskPartitionsShared(self.DcgDict)
            
            found = True
            #self.logger.debug("setting  self.DiskSubsystem %s to VirtualHostDiskPartitionsShared" % self.HostName)
            
        if ("HostDisk" in self.DcgDict.keys()) and ("HostPartition" in self.DcgDict.keys()):
            self.DiskSubsystem = cdisk.VirtualHostDiskKpartx(self.DcgDict)
            found = True
            #self.logger.debug("setting  self.DiskSubsystem %s to " % self.HostName)        
        if not found:
            RequiredFields = ["HostRootSpace","HostSwapSpace","HostDisk","HostPartition"]
            FoundFields = []
            for Field in RequiredFields:
                if Field in self.DcgDict.keys():
                    FoundFields.append(Field)
            if len(FoundFields) == 0:
                self.logger.debug("%s has teh following fields set %s" % (self.DcgDict["HostName"]),FoundFields)
            for Field in FoundFields:
                if ("HostRootSpace" in self.DcgDict.keys()):
                    self.logger.warning("%s has incomplete disk settings."% (self.DcgDict["HostName"]))
                    self.logger.warning("HostRootSpace is set, but not HostSwapSpace.")
                if ( "HostSwapSpace" in self.DcgDict.keys()):
                    self.logger.warning("%s has incomplete disk settings."% (self.DcgDict["HostName"]))
                    self.logger.warning("HostSwapSpace is set, but not HostSwapSpace.")
                if ( "HostDisk" in self.DcgDict.keys()):
                    self.logger.warning("%s has incomplete disk settings."% (self.DcgDict["HostName"]))
                    self.logger.warning("HostDisk is set, but not HostPartition.")
                if ( "HostPartition" in self.DcgDict.keys()):
                    self.logger.warning("%s has incomplete disk settings."% (self.DcgDict["HostName"]))
                    self.logger.warning("HostPartition is set, but not HostDisk.")
            self.logger.info("No DiskSubsystem found using base Object To Avoid Errors please set %s to Null driver" % self.HostName)
            self.logger.debug("self.config %s"% self.DcgDict)
            self.logger.debug("adding  self.DiskSubsystem %s to " % self.HostName)
            self.DiskSubsystem = cdisk.VirtualHostDisk(self.DcgDict)
            return False
        if not self.DiskSubsystem.PartitionsCheck():
            self.logger.debug("Disk subsystem incorectly set up %s"% self.DcgDict)
            return False
        return True
        #print "dsfdsF"
    def cfgApply(self):
        
        found = False
        #self.logger.debug("cfgApply:dict:%s" % (self.DcgDict))
        if "HostName" in self.DcgDict.keys():
            self.HostName = self.DcgDict["HostName"]
            
            #self.logger.debug("setting HostName" + self.HostName)
        if "LockFile" in self.DcgDict.keys():
            self.LockFile = self.DcgDict["LockFile"]
            clock.DiscLocking.__init__(self,self.DcgDict["LockFile"])
        
        if "HostMacAddress" in self.DcgDict.keys():
            found = True
            self.HostMacAddress = self.DcgDict["HostMacAddress"]
        if "HostIp4Address" in self.DcgDict.keys():
            found = True
            self.HostIp4Address = self.DcgDict["HostIp4Address"]
    
        #if not found:
        #    raise InputError("HostMacAddress or HostIp4Address must be set for %s" %  self.HostName)
        
        found = False
        #self.DiskSubsystem = VirtualHostDisk(self.DcgDict)
        
        #if not found:
        #    raise InputError("(HostRootSpace and HostSwapSpace) or (HostPartition and HostDisk) must be set for %s" %  self.HostName)
        if "ConfTemplateXen" in self.DcgDict.keys():
            self.ConfTemplateXen = self.DcgDict["ConfTemplateXen"]
        if "ImageStoreDir" in self.DcgDict.keys():
            self.ImageStoreDir = self.DcgDict["ImageStoreDir"]
        else:
            pass
            #raise InputError("ImageStoreDir must be set for %s" %  self.HostName)
        if "FormatFilter" in self.DcgDict.keys():
            self.cmdFormatFilter = properties["FormatFilter"]
        else:
            self.cmdFormatFilter = 'mkfs.ext3 -L / %s'
        self.PropertyImageModeSet("rsync")
        if "memory" in self.DcgDict.keys():
            self.memory = self.DcgDict["memory"]
        else:
            self.memory = 2097152
        if "currentMemory" in self.DcgDict.keys():
            self.currentMemory = self.DcgDict["currentMemory"]
        else:
            self.currentMemory = 2097152
        if not "vcpu" in self.DcgDict.keys():
            self.DcgDict["vcpu"] = "1"
    
    def isRunning(self):
        (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
        if state in (1,2,3):
            return True
        self.logger.debug("isRunning libvirt state=%s,maxMem=%s,memory=%s,nrVirtCpu=%s,cpuTime=%s" % (state,maxMem,memory,nrVirtCpu,cpuTime))
        return False    
    def PropertyHostNameSet(self, value):
        self.__HostName = value
        
    def PropertyHostNameGet(self):
        return self.__HostName
    def PropertyHostIdSet(self, value):
        self.__HostName = value
        
    def PropertyHostIdGet(self):
        return self.__HostName
        
    def PropertyHostIp4AddressSet(self, value):
        self.__HostIp4Address = value

    def PropertyHostIp4AddressGet(self):
        if hasattr(self,"__HostIp4Address" ):
            return self.__HostIp4Address
        else:
            return ""

    def PropertyHostMacAddressSet(self, value):
        self.__HostMacAddress = value
        
    def PropertyHostMacAddressGet(self):
        return self.__HostMacAddress

    def PropertyHostSwapSpaceSet(self, value):
        self.__HostSwapSpace = value
    def PropertyHostSwapSpaceGet(self):
        if hasattr(self,"__HostSwapSpace" ):
            return self.__HostSwapSpace
        else:
            return ""

    def PropertyHostRootSpaceSet(self, value):
        self.__HostRootSpace = value
    def PropertyHostRootSpaceGet(self):
        return self.__HostRootSpace

    def PropertyMountSet(self, value):
        self.__Mount = os.path.normpath(value)
    def PropertyMountGet(self):
        
        if hasattr(self,"__Mount" ):
            return self.__Mount
        else:
            return ""

    def PropertyImageModeSet(self, value):
        self.__ImageMode = value
        
    def PropertyImageModeGet(self):
        return self.__ImageMode

    def PropertyExtensionModeSet(self, value):
        self.__ExtensionMode = value
        
    def PropertyExtensionModeGet(self):
        return self.__ExtensionMode
    
    def PropertyExtractionsSet(self, value):
        self.__Extractions = value
        
    def PropertyExtractionsGet(self):
        return self.__Extractions
    
    def PropertyInsertionsSet(self, value):
        self.__Insertions = value
        
    def PropertyInsertionsGet(self):
        return self.__Insertions
     
    def PropertyImageRestoreNameSet(self, value):
        self.__ImageRestoreName = value
    def PropertyImageRestoreNameGet(self):
        return self.__ImageRestoreName
    
    def PropertyImageStoreNameSet(self, value):
        self.__ImageStoreName = value
    def PropertyImageStoreNameGet(self):
        return self.__ImageStoreName
        
    def PropertyImageStoreDirSet(self, value):
        self.__ImageStoreDir = os.path.normpath(value)
        
    def PropertyImageStoreDirGet(self):
        return self.__ImageStoreDir

    def PropertyXenCfgFileGet(self):
        if not hasattr(self,"self.__XenCfgFile" ):
            return os.path.join(self.VmSlotVarDir, "/xen")
        return self.__XenCfgFile
    def PropertyXenCfgFileSet(self, value):
        self.__XenCfgFile = os.path.normpath(value)


    def PropertyVmSlotVarDirGet(self):

        #return self.__VmSlotVarDir
        if hasattr(self,"__VmSlotVarDir" ):
            return self.__VmSlotVarDir
        else:
            return "/tmp/" +  self.HostName 
    def PropertyVmSlotVarDirSet(self, value):
        self.__VmSlotVarDir = value
    
    def PropertyLockFileGet(self):
        if hasattr(self,"lockfile" ):
            return self.lockfile
        return (self.VmSlotVarDir + "/lock" )
        
    def PropertyLockFileSet(self, value):
        if not hasattr(self,"lockfile" ):
            self.lockfile = os.path.normpath(value)
        self.__LockFile = value 
    
    
    def delx(self): 
        del self.HostRootSpace
    
    HostName = property(PropertyHostNameGet, PropertyHostNameSet)
    HostId = property(PropertyHostIdGet, PropertyHostIdSet)
    HostIp4Address = property(PropertyHostIp4AddressGet, PropertyHostIp4AddressSet)
    HostMacAddress = property(PropertyHostMacAddressGet, PropertyHostMacAddressSet)
    HostSwapSpace = property(PropertyHostSwapSpaceGet, PropertyHostSwapSpaceSet)
    #HostRootSpace = property(PropertyHostRootSpaceGet, PropertyHostRootSpaceSet)
    HostRootSpace = property(PropertyHostRootSpaceGet, PropertyHostRootSpaceSet, delx, "I'm the HostRootSpace property.")
    ImageMode = property(PropertyImageModeGet, PropertyImageModeSet)
    ExtensionMode = property(PropertyExtensionModeGet, PropertyExtensionModeSet)
    Mount = property(PropertyMountGet, PropertyMountSet)
    Extractions = property(PropertyExtractionsGet, PropertyExtractionsSet)
    Insertions = property(PropertyInsertionsGet,PropertyInsertionsSet)
    ImageStoreName = property(PropertyImageStoreNameGet,PropertyImageStoreNameSet)
    ImageRestoreName = property(PropertyImageRestoreNameGet,PropertyImageRestoreNameSet)
    ImageStoreDir = property(PropertyImageStoreDirGet,PropertyImageStoreDirSet)
    XenCfgFile = property(PropertyXenCfgFileGet,PropertyXenCfgFileSet)
    VmSlotVarDir = property(PropertyVmSlotVarDirGet,PropertyVmSlotVarDirSet)
    LockFile = property(PropertyLockFileGet,PropertyLockFileSet)
    
    

    def StartUp(self):
        self.logger.debug( "starting up method %s" % (self.HostName))
        (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
        #VIR_DOMAIN_EVENT_DEFINED	 = 	0
        #VIR_DOMAIN_EVENT_UNDEFINED	= 	1
        #VIR_DOMAIN_EVENT_STARTED	= 	2
        #VIR_DOMAIN_EVENT_SUSPENDED	= 	3
        #VIR_DOMAIN_EVENT_RESUMED	= 	4
        #VIR_DOMAIN_EVENT_STOPPED	= 	5
        #print "exiting here %s" % (state)
        if state in [1,2]:
            
            return True
        self.RealiseDevice()
        if not self.DiskSubsystem.ImageUnMount():
            print "Failed unmount A"
            sys.exit(1)
        if not self.DiskSubsystem.PartitionsClose():
            print "Failed unmount B"
        
        #VIR_DOMAIN_NOSTATE= 0: no state
        #VIR_DOMAIN_RUNNING= 1: the domain is running
        #VIR_DOMAIN_BLOCKED= 2: the domain is blocked on resource
        #VIR_DOMAIN_PAUSED= 3: the domain is paused by user
        #VIR_DOMAIN_SHUTDOWN= 4: the domain is being shut down
        #VIR_DOMAIN_SHUTOFF= 5: the domain is shut off
        #VIR_DOMAIN_CRASHED= 6: the domain is crashed
#        if not hasattr(self,"libvirtObj"):
#            test = "startep bad for %s" % (self.HostName)
#            print test
#            raise InputError(test)
        self.libvirtObj.setVcpus(int(self.DcgDict["vcpu"]))
        rc = self.libvirtObj.create()
        (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
        while state not in (1,2,3):
            time.sleep(1)
            (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
        return True
    def ShutDown(self):
        counter = 0
        (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
        #VIR_DOMAIN_NOSTATE= 0: no state
        #VIR_DOMAIN_RUNNING= 1: the domain is running
        #VIR_DOMAIN_BLOCKED= 2: the domain is blocked on resource
        #VIR_DOMAIN_PAUSED= 3: the domain is paused by user
        #VIR_DOMAIN_SHUTDOWN= 4: the domain is being shut down
        #VIR_DOMAIN_SHUTOFF= 5: the domain is shut off
        #VIR_DOMAIN_CRASHED= 6: the domain is crashed
        timeout = 180
        while state in (1,2,3):
            counter += 1
            if counter < timeout:
                try:
                    rc = self.libvirtObj.shutdown()
                    #print rc
                except :
                    print "exception thrown"
            else:
                self.logger.warning("Timed out shutting down domain")
                counter = 0
                #print "timed Out"
                rc = self.libvirtObj.destroy()
                #print rc
            time.sleep(1)
            (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
            self.logger.info("state=%s, timeout in %s" %( state, timeout-  counter))
            
            #print dir(self.libvirtObj)
            #print self.libvirtObj.destroy()
        self.RealiseDevice()
        self.DiskSubsystem.PartitionsOpen()
        #self.logger.debug("self.DiskSubsystem %s " %(self.DiskSubsystem))
        self.DiskSubsystem.ImageMount()
        
        
        return True
        
    def Kill(self):
        if self.isRunning():
            self.libvirtObj.destroy()
        return True 
    def StorageDir(self):
        return self.ImageStoreDir
        
    def AvailableImage(self):
        restoreImage = self.PropertyImageRestoreNameGet()
        ImageName = os.path.join(self.StorageDir(),restoreImage)
        ImageName = os.path.realpath(ImageName)
        #print "imageName=%s" % (ImageName)
        if os.path.isdir(ImageName):
            return True
        if os.path.isfile(ImageName.strip()):
            return True
        #print "dfsdfsdF"
        return False
        
    def AvailableImageListGet(self):
        
        output = []
        if os.path.isdir(self.ImageStoreDir):
            for filename in os.listdir(self.ImageStoreDir):
                output.append(filename)
        return output


    
    def ExtractDir(self):
        return self.VmExtractsDir
        
    def AvailableExtract(self):
        if not os.path.isdir(self.ExtractDir()):
            return False
        for ext in self.PropertyInsertionsGet().keys():
            ImageName = os.path.join(self.ExtractDir(),ext)
            if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
                return False
        return True        
    def AvailableExtractListGet(self):
        output = []
        for filename in os.listdir(self.ExtractDir()):
            output.append(filename)
        return output


    def Restart(self):
        self.ShutDown()
        self.StartUp()

    def StoreHost(self):
        ImageName = self.PropertyImageStoreNameGet()
        if not self.ShutDown():
            logging.critical('Requesting to store host wher Running Programming error')
            sys.exit(1)
        self.DiskSubsystem.PartitionsOpen()
        self.DiskSubsystem.ImageMount()
        cmd = ""
        storedir =  os.path.normpath(self.ImageStoreDir)
        if not os.path.isdir(storedir):
            os.makedirs(storedir)
        if os.path.isdir('%s/%s' % (storedir,ImageName)):
            self.PropertyImageModeSet("rsync")
        if "tgz" == self.PropertyImageModeGet():
            cmd = "tar -zcsf %s/%s --exclude=lost+found -C %s ." % (storedir,ImageName,self.DiskSubsystem.MountPoint)
        if "rsync" == self.PropertyImageModeGet():
            cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/%s/" % (self.DiskSubsystem.MountPoint,storedir,ImageName)
        if cmd == "":
            logging.error( "Error: Failing to store images")
            sys.exit(1)
            
        
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.debug("command='%s'" % (cmd))
            message = 'The command failed "%s"\n' % (cmd)
            message += cmdoutput + '\nReturn Code=%s' % (rc)
            logging.error(message)
            return rc
        
        self.StartUp()
    def RestoreHost(self):
        
        restoreImage = self.PropertyImageRestoreNameGet()
        
        storedir =  self.ImageStoreDir
        ImageName = "%s/%s" % (storedir,restoreImage)
        
        if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
            message =  "Image '%s' not found these images where found in directory %s" % (restoreImage,storedir)
            
            for filename in os.listdir(storedir):
                message += "\n%s" % (filename)
            logging.error(message)
            sys.exit(1)
        
        if True == os.path.isfile(ImageName):
            self.PropertyImageModeSet("tgz")
        if True == os.path.isdir(ImageName):
            self.PropertyImageModeSet("rsync")
        if not self.ShutDown():
            logging.critical('Requesting to restore host when host is not shut down yet.')
            sys.exit(1)
        
        if len(self.DiskSubsystem.MountPoint) == 0 :
            logging.error('Failed to get mount point aborting "%s"' % (self.PropertyMountGet()))
            sys.exit(1)
        self.Lock()
        if self.PropertyImageModeGet() == None:
            logging.warning("Warning: Could not find image type")
        else:
            cmd = ""
            if "tgz" == self.PropertyImageModeGet():
                self.DiskSubsystem.ImageUnMount()
                # Formatting is faster but we have a catch, 
                # With dcache must give it an option for XFS
                # cmdFormatFilter="mkfs.xfs %s"
                if not self.DiskSubsystem.PartitionsOpen():
                    self.logger.error("Failed Partition Open")
                    sys.exit(1)
                cmd=self.cmdFormatFilter % (self.DiskSubsystem.HostRootSpace)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                if rc != 0:
                    self.logger.error(cmdoutput)
                    self.logger.error("command line failed running %s" % (cmd))
                    return -1
                self.DiskSubsystem.ImageMount()
                if len(self.DiskSubsystem.MountPoint) == 0:
                    self.logger.error("Mount Point Undefined ")
                    sys.exit(1)                    
                cmd = "rm -rf %s" % (self.DiskSubsystem.MountPoint)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                cmd = "tar -zxf %s --exclude=lost+found   -C %s" % (ImageName,self.DiskSubsystem.MountPoint)
            if "rsync" == self.PropertyImageModeGet():
                cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/" % (ImageName,self.DiskSubsystem.MountPoint)
                self.logger.debug('Running command "%s".' % (cmd))
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                self.logger.error('Failed Running command "%s"' % (cmd))
                self.logger.error(cmdoutput)
                self.logger.error('Return Code=%s' % (rc))
                return rc
        filename="%s/sourceimage" % (self.DiskSubsystem.MountPoint)
        fpvmconftemp = open(filename,'w+')
        fpvmconftemp.write("%s\n" % (ImageName))
        fpvmconftemp.close()
        self.logger.debug("Wrote '%s' with content '%s'." % (filename,ImageName))
        return 0
        

    def Extract(self):
        if not os.path.isdir(self.ExtractDir()):
            os.makedirs(self.ExtractDir())
        for ext in self.PropertyExtractionsGet().keys():
            target = "%s/%s" % (self.PropertyMountGet(),ext)
            if "tgz" == self.PropertyImageModeGet():
                selectedDir = self.PropertyExtractionsGet()[ext].strip('/')
                cmd = "tar -zcsf %s/%s --exclude=lost+found -C %s %s" % (self.ExtractDir(),ext,self.PropertyMountGet(),selectedDir)
            if "rsync" == self.PropertyImageModeGet():
                cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/%s %s/%s/" % (self.PropertyMountGet(),self.PropertyExtractionsGet()[ext],self.ExtractDir(),ext)
        #print cmd
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('Failed "%s"' % (cmd))
            logging.error(cmdoutput)
            logging.error('Return Code=%s' % (rc))
        return 0
        
            
    def Insert(self):
        #print "Debug: PropertyInsertionsGet=%s" % (self.PropertyInsertionsGet())
        #print "Debug: ExtractDir=%s" % (self.ExtractDir())
        #print "Debug: MountDir=%s" % (self.PropertyMountGet())
        #print "Debug: PropertyImageModeGet=%s" % (self.PropertyImageModeGet())
        if not os.path.isdir(self.ExtractDir()):
            self.logger.error("Error: Directory %s is not found" % (self.ExtractDir()))
            sys.exit(1)
        for ext in self.PropertyInsertionsGet().keys():
            #ImageName = "%s/%s" % (self.ExtractDir(),ext)
            ImageName = os.path.join(self.ExtractDir(),ext)
            ImageName = os.path.realpath(ImageName)
            if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
                logging.error("Insert '%s' is not found in '%s'" % (ext,self.ExtractDir()))
                continue
            insertFormat = ""
            insertDone = False
            
            if True == os.path.isfile(ImageName):
                insertFormat = "tgz"
            if True == os.path.isdir(ImageName):
                insertFormat = "rsync"
            
            #print "insertFormat=%s" % (insertFormat)
            if "tgz" == insertFormat:
                cmd=  "tar -zxf %s --exclude=lost+found   -C %s" % (ImageName,self.PropertyMountGet())
            if "rsync" == insertFormat:
                cmd = "rsync -ra --numeric-ids --exclude=lost+found %s/ %s/%s" % (ImageName,self.PropertyMountGet(),self.PropertyInsertionsGet()[ext])
            #print cmd
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error('Failed "%s"' % (cmd))
                logging.error(cmdoutput)
                logging.error('Return Code=%s' % (rc))
        return 0        

 
    def LoadCfg(self,Config,Defaults):
        
        pass
        
    
