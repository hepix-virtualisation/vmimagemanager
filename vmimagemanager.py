#!/usr/bin/python
#import ConfigParser
import logging

import os
import os.path
import string
import sys
import getopt
import commands
import time
import re
import ConfigParser, os
import random
import shutil
#for line in file('vmimagemanager.dict'):
#    cfg = eval(line)
InstallPrefix="/"

ConfigFile = ""

Fillocations = ['vmimagemanager.cfg', os.path.expanduser('~/.vmimagemanager.cfg'),InstallPrefix + '/etc/vmimagemanager/vmimagemanager.cfg']

for fileName in Fillocations:
    if True == os.path.isfile(fileName):
        ConfigFile = fileName
        break

if len(ConfigFile) == 0:
    ConfigFile = '/etc/vmimagemanager/vmimagemanager.cfg'
    

# Add lines to import a namespace and add it to the list of namespaces used
import logging, logging.handlers

#config = ConfigParser.ConfigParser()
#config.read(['vmimagemanager.cfg', os.path.expanduser('~/.vmimagemanager.cfg'),InstallPrefix + '/etc/vmimagemanager.cfg'])
def usage():
    print ' -h, --help                        Display help information'
    print ' -v, --version                     Version'
    print ' -c, --config                      Set config file'
    print ' -p, --print-config                Print config'
    print ' -b, --box       [host]            Set Virtual Box'
    print ' -s, --store     [image]           Store Virtual Box as parameter'
    print ' -r, --restore   [image]           Restore Virtual Box as parameter'
    print ' -i, --insert    [component]:[dir] insert component to a Virtual Box'
    print ' -e, --extract   [component]:[dir] extract component from a Virtual Box'
    print ' -u, --up                          Start Virtual Box'
    print ' -d, --down                        Stop Virtual Box'
    print ' -l, --list-boxes                  List Virtual Boxes'
    print ' -L, --list-images                 List Virtual Box Images'
    print ' -k, --kill                        Kill Virtual Box'
    print ' -z, --tgz                         tar.gz Virtual Box Image'
    print ' -o, --overwrite                   Overwrite the xen config file for a box'
    print ' -D, --diff                        Diff the xen config file to vmimagemanager'
    print ' -m, --locked                      List Locked slots'
    print ' -f, --free                        List Free slots.'
    print ' -U, --used                        List Used slots'
    print ' -y, --rsync                       rsync Virtual Box Image [Default]'


class DiscLocking():
    def __init__(self):
        
        self.lockedByMeKnown = False
        self.lockedByOtherKnown = False
    def __del__(self):
        self.Unlock()
    def IsLocked(self):
        if not os.path.isfile(self.LockFile):
            return False
        #print self.LockFile
        return True
    def LockOwners(self):
        if not self.IsLocked():
            return []
        fi  = open(self.LockFile, 'r')
        foundPids= [];
        for line in fi:
            messgDict = {}
            splitline = line.split(" ")
            for split in splitline:
                keyval = split.split("=")
                value = int(keyval[1].strip(' "\n'))
                messgDict[keyval[0].strip()] = value
            foundPids.append(messgDict)
        fi.close()
        if (foundPids == []):
            os.remove(self.LockFile)
        logging.debug("DiscLocking foundPids=%s" % (foundPids))
        return foundPids
    def Lock(self):
        
        if (self.lockedByOtherKnown == True):
            return False
        
        if self.lockedByMeKnown:
            return True
        if self.IsLocked():
            if self.IsLockedByMe():
                return True
            #print "heher"
            return False
        #print "can lock %s" % ( self.LockFile)
        lockfiledir = os.path.dirname(self.LockFile)
        if not os.path.isdir(lockfiledir):
            os.makedirs(lockfiledir)
        pid = os.getpid()
        newlockfileName = self.LockFile + ".new.%d5" % (pid)
        tmplockfileName = self.LockFile + ".tmp.%d5" % (pid)
        #print newlockfileName
        fi = open(newlockfileName, 'w')
        #msg = 'pid="%s" message="%s"\n' % (pid,self.message)
        msg = 'pid="%s"\n' % (pid)
        fi.write(msg)
        fi.close()
        if not os.path.isfile(self.LockFile):
            shutil.move(newlockfileName,self.LockFile)
            return self.IsLockedByMe()
        else:
            os.remove(newlockfileName)
            return False
        
    def IsLockedByMe(self):
        if self.lockedByOtherKnown:
            return False
        
        if self.lockedByMeKnown:
            return True
        pid = os.getpid()
        foundPids= self.LockOwners()
        if (len( foundPids ) == 0):
            #os.remove(self.LockFile)
            return False
        objdisc = foundPids[0]
        if objdisc["pid"] == pid:
            #print "wibble"
            self.lockedByMeKnown = True
            return True
        else:
            #print "processing results"
            self.lockedByOtherKnown = True
            self.lockedByMeKnown = False
            processlist = []
            output = commands.getoutput("ps -e")
            proginfo = string.split(output,"\n")
            for line in  proginfo:
                stripedLine = string.strip(line)
                FirstBit = string.split(stripedLine," ")
                ProcessNight = None
                try:
                    ProcessNight = int(FirstBit[0])
                    processlist.append(ProcessNight)
                except:
                    pass
            
            for owner in foundPids:
                #print ("owner=%s" % (owner['pid']))
                OwnerPid = owner["pid"]
                if OwnerPid in proginfo:
                    self.lockedByOtherKnown = True
            if not self.lockedByOtherKnown:
                os.remove(self.LockFile)
                return False
            return False
            
    def IsLockedStill(self):
        foundPids= self.LockOwners()
        if (len( foundPids ) == 0):
            return False
        pid = os.getpid()
        objdisc = foundPids[0]
        if objdisc["pid"] == pid:
            #print "wibble"
            self.lockedByMeKnown = True
            return True
        else:
            #print "processing results"
            self.lockedByOtherKnown = False
            self.lockedByMeKnown = False
            processlist = []
            output = commands.getoutput("ps -e")
            proginfo = string.split(output,"\n")
            for line in  proginfo:
                stripedLine = string.strip(line)
                FirstBit = string.split(stripedLine," ")
                ProcessNight = None
                try:
                    ProcessNight = int(FirstBit[0])
                    processlist.append(ProcessNight)
                except:
                    pass
            
            for owner in foundPids:
                #print ("owner=%s" % (owner['pid']))
                OwnerPid = owner["pid"]
                if OwnerPid in proginfo:
                    self.lockedByOtherKnown = True
            if self.lockedByOtherKnown:
                return True
            return False
            
    def Unlock(self):
        if self.lockedByOtherKnown:
            return False
        if self.lockedByMeKnown:
            if os.path.isfile(self.LockFile):
                os.remove(self.LockFile)
            self.lockedByMeKnown = False
            return True
        return False
    
def VitualHostsList():
    cmd="xm list | sed -e 's/  */ /g'"
    (rc,cmdoutput) = commands.getstatusoutput(cmd)
    output = {}
    counter = 0
    for line in cmdoutput.split('\n'):
        if counter > 0:
            section = line.split(' ')
	    if len(section) > 5:
	        #output[section[0]] = [section[1],section[2],section[3],section[4],section[5],section[6]]
		output[section[0]] = [section[1],section[2],section[3],section[4],section[5]]
        counter += 1
    return output

class virtualhost(DiscLocking):
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
        self.ImageMode = "tgz"
        DiscLocking.__init__(self)
        self.LockFileFixed = False
        
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
        return self.__HostIp4Address

    def PropertyHostMacAddressSet(self, value):
        self.__HostMacAddress = value
        
    def PropertyHostMacAddressGet(self):
        return self.__HostMacAddress

    def PropertyHostSwapSpaceSet(self, value):
        self.__HostSwapSpace = value
    def PropertyHostSwapSpaceGet(self):
        return self.__HostSwapSpace

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
    
    def MountStatus(self):
        # Returns 0 for not mounted
        # Returns 1 for device mounted
        result = 0
        cmd="mount"
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('mount Failed with error code %s and the folleowing error:%s' % (rc,cmdoutput))
            sys.exit(1)            
        #print "%s %s" % (self.PropertyHostRootSpaceGet(),self.PropertyMountGet())
        for mntline in cmdoutput.split("\n"):
            mntsplit = mntline.split(" ")
            if len(mntsplit) < 3:
                print "Error parsing mount command!"   
            #print mntsplit[2]    
            if mntsplit[0] == self.HostRootSpace or mntsplit[2] == self.Mount:
                # Assumes no VM host maps to same directory
                #print "sdsdSD"
                result = 1
        return result
    
    
    def MountImage(self):
        if self.MountStatus() == 1:
            return
        if not os.path.isdir(self.Mount):
            #print "os.makedirs(%s)%s" % (self.Mount,self.HostRootSpace)
            os.makedirs(self.Mount)
        cmd="mount %s %s" % (self.HostRootSpace,self.Mount)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            
            logging.error('Command "%s" Failed' % (cmd))
            logging.info( 'rc=%s,output=%s' % (rc,cmdoutput))
            sys.exit(1)            
        return

    def UnMount(self):
        if self.MountStatus() == 0:
            return
        if not os.path.isdir(self.Mount):
            os.makedirs(self.Mount)
        cmd="umount %s" % (self.HostRootSpace)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('Command "%s" Failed' % (cmd))
            logging.info('rc=%s,output=%s' % (rc,cmdoutput))
            sys.exit(1)            
        return

    def MountTest(self):
        logging.debug("MountStatus %s" % (self.MountStatus()))
        self.Mount()
        logging.debug("MountStatus %s" % (self.MountStatus()))
        self.UnMount()
        logging.debug("MountStatus %s" % (self.MountStatus()))
        sys.exit(0)    
    


        
    def ShutDown(self):
        domainList = VitualHostsList()
        if domainList.has_key(self.HostName):
            cmd = "xm shutdown %s" % self.HostName
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error("Failed to shut down '%s'" % self.HostName)
            else:
                for n in range(60):
                    time.sleep(1)
                    domainList = VitualHostsList()
                    #print domainList
                    if not domainList.has_key(self.HostName):
                        break
            domainList = VitualHostsList()
        if domainList.has_key(self.HostName):
            return False
        self.MountImage()
	
        return True
        

    def Kill(self):
        self.ShutDown()
        if domainList.has_key(self.HostName):
            cmd = "xm destroy %s" % (self.HostName)
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error("Failed to shut down or kill '%s'" % self.HostName)
                logging.info(cmdoutput)
            return False
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


    def StartUp(self):
        self.UnMount()
        if not os.access(self.XenCfgFile,os.R_OK):
            d = dict(
                DomainRootDev=self.HostRootSpace,
                DomainIp4Address=self.HostIp4Address,
                DomainName=self.HostName,
                DomainSwapDev=self.HostSwapSpace,
                DomainMac=self.HostMacAddress
            )
            directory = os.path.dirname( self.XenCfgFile)
            if not os.path.isdir(directory):
                try:
                    os.makedirs(directory)
                except:
                    logging.error("could not create directory '%s'" %(directory))
                    sys.exit(1)
            self.xenconftemplate
            fpxenconftemp = open(self.xenconftemplate,'r')
            newconfig = open(self.XenCfgFile,'w')
            for line in fpxenconftemp:
                subline = line
                #print line
                try:
                    newconfig.write(string.Template(line).safe_substitute(d))
                except:
                    for key in d.keys():
                        subline = subline.replace("${%s}" % (key), d[key])
                    newconfig.write(subline)
            newconfig.close()
            fpxenconftemp.close()
                                    
        domainList = VitualHostsList()
        if not domainList.has_key(self.HostName):
            cmd = "xm create %s  %s" % (self.HostName,self.XenCfgFile)
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error("Failed to start up '%s'" % self.HostName)
                logging.warning(cmdoutput)
            else:
                for n in range(60):
                    time.sleep(1)
                    domainList = VitualHostsList()
                    if domainList.has_key(self.HostName):
                        break
            domainList = VitualHostsList()
        if not domainList.has_key(self.HostName):
            return False
        return True
    def Restart(self):
        self.ShutDown()
        self.StartUp()

    def StoreHost(self):
        ImageName = self.PropertyImageStoreNameGet()
        if not self.ShutDown():
            logging.critical('Requesting to store host wher Running Programming error')
            sys.exit(1)
        self.MountImage()
        cmd = ""
        storedir =  os.path.normpath(self.ImageStoreDir)
        if not os.path.isdir(storedir):
            os.makedirs(storedir)
        if os.path.isdir('%s/%s' % (storedir,ImageName)):
            self.ImageMode = "rsync"
        if "tgz" == self.ImageMode:
            cmd = "tar -zcsf %s/%s --exclude=lost+found -C %s ." % (storedir,ImageName,self.Mount)
        if "rsync" == self.ImageMode:
            cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/%s/" % (self.PropertyMountGet(),storedir,ImageName)
        if cmd == "":
            logging.error( "Error: Failing to store images")
            sys.exit(1)
            
        #print "command='%s'" % (cmd)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
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
            logging.critical('Requesting to store host wher Running Programming error')
            sys.exit(1)
        if len(self.Mount) == 0 :
            logging.error('Failed to get mount point aborting "%s"' % (self.PropertyMountGet()))
            sys.exit(1)
        
        if self.PropertyImageModeGet() == None:
            logging.warning("Warning: Could not find image type")
        else:
            cmd = ""
            if "tgz" == self.PropertyImageModeGet():
                self.UnMount()
                # Formatting is faster but we have a catch, 
                # With dcache must give it an option for XFS
                # cmdFormatFilter="mkfs.xfs %s"
                
                cmd=self.cmdFormatFilter % (self.HostRootSpace)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                if rc != 0:
                    logging.error(cmdoutput)
                    logging.error("command line failed running %s" % (cmd))
                    return -1
                self.MountImage()
                cmd = "rm -rf %s" % (self.Mount)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                cmd = "tar -zxf %s --exclude=lost+found   -C %s" % (ImageName,self.Mount)
            if "rsync" == self.PropertyImageModeGet():
                cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/" % (ImageName,self.Mount)
            #print cmd
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error('Failed "%s"' % (cmd))
                logging.error(cmdoutput)
                logging.error('Return Code=%s' % (rc))
                return rc
        filename="%s/sourceimage" % (self.Mount)
        fpvmconftemp = open(filename,'w+')
        fpvmconftemp.write("%s\n" % (ImageName))
        fpvmconftemp.close()
        
        

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
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('Failed "%s"' % (cmd))
            logging.error(cmdoutput)
            logging.error('Return Code=%s' % (rc))
            
    def Insert(self):
        #print "Debug: PropertyInsertionsGet=%s" % (self.PropertyInsertionsGet())
        #print "Debug: ExtractDir=%s" % (self.ExtractDir())
        #print "Debug: MountDir=%s" % (self.PropertyMountGet())
        #print "Debug: PropertyImageModeGet=%s" % (self.PropertyImageModeGet())
        if not os.path.isdir(self.ExtractDir()):
            logging.error("Error: Directory %s is not found" % (self.ExtractDir()))
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
            
    
class virtualHostContainer:
    
    def __init__(self):
        self.hostlist = []
    def PropertyVmSlotVarDirSet(self, value):
        for aHost in self.hostlist:
            aHost.VmSlotVarDir = value
            logging.error("aHost.VmSlotVarDir=%s" % (aHost.VmSlotVarDir))
            aHost.PropertyVmSlotVarDirSet(value)
        self.__VmSlotVarDir = value
    
        
    def LoadConfigFile(self,fileName):
        
        GeneralSection = "VmImageManager"
        HostListSection = "AvailalableHosts"
        RequiredSections = [GeneralSection]
        #RequiredSections = [GeneralSection,HostListSection]
        self.hostlist = []
        config = ConfigParser.ConfigParser()
        cmdFormatFilter = "mkfs.ext3 %s"
        config.readfp(open(fileName,'r'))
        #logging.warning( config.sections()
        configurationSections = config.sections()
        for ASection in RequiredSections:
            if not ASection in configurationSections:
                logging.fatal( "Configuration file does not have a section '%s'"  % (ASection))
                sys.exit(1)
        
        cfgHosts = config.sections()
        
        
        newvmconfdir = config.get(GeneralSection,'vmconfdir')
        if len(newvmconfdir) == 0:
            logging.fatal( "Configuration file does not have a section '%s' with a key in it 'vmconfdir'" % (GeneralSection))
            sys.exit(1)
        ##self.VmSlotVarDir = newvmconfdir
        self.PropertyVmSlotVarDirSet(newvmconfdir)
        #logging.warning( self.__VmSlotVarDir
        newxenconftemplate = config.get(GeneralSection,'xenconftemplate')
        if len(newxenconftemplate) == 0:
            logging.fatal( "Configuration file does not have a section '%s' with a key in it 'vmconfdir'" % (GeneralSection))
            sys.exit(1)
        self.xenconftemplate = newxenconftemplate
        
        newXenImageDir = config.get(GeneralSection,'vmimages')
        if len(newXenImageDir) == 0:
            logging.fatal( "Configuration file does not have a section '%s' with a key in it 'vmimages'" % (GeneralSection))
            sys.exit(1)
        self.XenImageDir = newXenImageDir
        self.VmExtractsDir = newXenImageDir
        
        newVmExtractsDir = config.get(GeneralSection,'vmextracts')
        if len(newVmExtractsDir) == 0:
            logging.warning("Configuration file does not have a section '%s' with a key in it 'vmextracts' defaulting to '%s'" % (GeneralSection,GeneralSection))
        else:            
            self.VmExtractsDir = newVmExtractsDir
        VmMountsBaseDir = config.get(GeneralSection,'mount')
        
        
        if (config.has_option(GeneralSection, "formatFilter")):
            cmdFormatFilter = config.get(GeneralSection,'formatFilter')
        
        for cfgSection in cfgHosts:
                #print cfgSection
                isanImage = 0
                if (config.has_option(cfgSection, "vm_slot_enabled")):
                    isanImageStr = config.get(cfgSection,"vm_slot_enabled")
                    if (isanImageStr in (["Yes","YES","yes","y","On","on","ON","1"])):
                        isanImage = 1
                if isanImage > 0:
                
                    ThisVirtualHost =  virtualhost()
                    
                    if (config.has_option(cfgSection, "HostName")):
                        ThisVirtualHost.HostName  = config.get(cfgSection,"HostName")
                    else:
                        ThisVirtualHost.HostName = cfgSection
                    
                    
                    
                    if (config.has_option(cfgSection, "mac")):
                        ThisVirtualHost.HostMacAddress  = config.get(cfgSection,"mac")
                    if (config.has_option(cfgSection, "ip")):
                        ThisVirtualHost.HostIp4Address  = config.get(cfgSection,"ip")
                
                    if (config.has_option(cfgSection, "root")):
                        ThisVirtualHost.HostRootSpace  = config.get(cfgSection,"root")
                    if (config.has_option(cfgSection, "swap")):
                        ThisVirtualHost.HostSwapSpace  = config.get(cfgSection,"swap")
                    if (config.has_option(cfgSection, "vmimages")):
                        ThisVirtualHost.ImageStoreDir  = config.get(cfgSection,"vmimages")
                    else:
                        ThisVirtualHost.ImageStoreDir = os.path.join(self.XenImageDir , ThisVirtualHost.HostName)
                    if (config.has_option(cfgSection, "mount")):
                        ThisVirtualHost.Mount  = config.get(cfgSection,"mount")
                    else:
                        ThisVirtualHost.Mount  = os.path.join(VmMountsBaseDir ,ThisVirtualHost.HostName)
                    ThisVirtualHost.VmSlotVarDir = os.path.join(newvmconfdir , ThisVirtualHost.HostName)
                    
                    ThisVirtualHost.XenCfgFile  =  os.path.join(ThisVirtualHost.VmSlotVarDir , "xen")
                    if (config.has_option(cfgSection, "vmcfg")):
                        ThisVirtualHost.XenCfgFile  = config.get(cfgSection,"vmcfg")
                    
                    ThisVirtualHost.LockFile  = os.path.join( newvmconfdir , ThisVirtualHost.HostName ,"lock")
                    #print ThisVirtualHost.LockFile
                    if (config.has_option(cfgSection, "vmlock")):
                       
                        ThisVirtualHost.LockFile  = config.get(cfgSection,"vmlock")
                    
                    if (config.has_option(cfgSection, "vmextracts")):
                       
                        ThisVirtualHost.VmExtractsDir  = config.get(cfgSection,"vmextracts")
                    else:
                        ThisVirtualHost.VmExtractsDir = self.VmExtractsDir
                    
                    
                    
                    if (config.has_option(cfgSection, "formatFilter")):
                        ThisVirtualHost.cmdFormatFilter  = config.get(cfgSection,"formatFilter")
                    else:
                        ThisVirtualHost.cmdFormatFilter = cmdFormatFilter
                    
                    if (config.has_option(cfgSection, "xenconftemplate")):
                        ThisVirtualHost.xenconftemplate  = config.get(cfgSection,"xenconftemplate")
                    else:
                        ThisVirtualHost.xenconftemplate = self.xenconftemplate
                    self.hostlist.append(ThisVirtualHost)


if __name__ == "__main__":
    #opts = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:s:r:e:i:c:udlLhvkzypfm", ["box=", "store=","restore=","extract=","insert=","config=","up","down","list-boxes","list-images","help","version","kill","tgz","rsync","print-config","free","locked"])
    except:
        pass
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
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
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
    HostContainer = virtualHostContainer()
    #hostlist = makeConfig()
    if ParsedConfigFile != "":
        #print "foof"
        ConfigFile = ParsedConfigFile
    if os.path.isfile(ConfigFile):
        HostContainer.LoadConfigFile(ConfigFile)
    else:
        logging.fatal("Error: Configuration File '%s' not found" % (ConfigFile))
        sys.exit(1)
    
    if ParsedImage != None:
        HostContainer.ImageMode = ParsedImage
    processingBoxes = []
    if len(boxlist) >0:       
        notfound = False
        for box in boxlist:
            found = False
            for ahost in HostContainer.hostlist:
                if ahost.HostName == box:
                    found = True
                    ahost.Lock()
                    processingBoxes.append(ahost)
            if found == False:
               notfound = True 
        if (notfound):
            message = None
            hostlist = HostContainer.hostlist
            if len (hostlist) == 0:
                message = "No bokes Configured Please Check your configuration"
            else:
                message = "box slot '%s' not found! The following Host slots exist." % (box)
                for ahost in HostContainer.hostlist:
                    message += '\n' + ahost.HostName
            logging.error(message)
            sys.exit(1) 
    #print "dslkjsdljsdlkjsd"
    if "list-boxes" in actionList:
        #print  HostContainer.hostlist
        for ahost in HostContainer.hostlist:
            print ahost.HostName
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
        domainList = VitualHostsList()
        potentiallyFree = []
        for ahost in HostContainer.hostlist:
            if not domainList.has_key(ahost.HostName):
                potentiallyFree.append(ahost)
        couldbeLocked = []
        for ahost in potentiallyFree:
            if not ahost.IsLocked():
                couldbeLocked.append(ahost)
        for ahost in couldbeLocked:
            print ahost.HostName
        sys.exit(0)       
    if "locked" in actionList:
        domainList = VitualHostsList()
        potentiallyFree = []
        for ahost in HostContainer.hostlist:
            if not domainList.has_key(ahost.HostName):
                potentiallyFree.append(ahost)
        definatelyIsLocked = []
        for ahost in potentiallyFree:
            if ahost.IsLocked():
                definatelyIsLocked.append(ahost)
        for ahost in definatelyIsLocked:
            print ahost.HostName
        sys.exit(0)     
    if len(processingBoxes) == 0:
        logging.error("No Valid 'boxes' not stated on command line.")
        sys.exit(1)
    
    if len(actionList) == 0:
        logging.error("Error: No task selected")
        usage()
        sys.exit(1)
        
    
    if "list-images" in actionList:
        for box in processingBoxes:
            #print dir(box)
            for image in box.AvailableImageListGet():
                print image
        sys.exit(0)



    extractionsDict = {}
    for component in extractions:
        compdecp = component.split(':')
        if len(compdecp) != 2:
            logging.error("Extraction '%s' is invalid it must conatain name:dir" % (compdecp))
            usage()
            sys.exit(1)
        extractionsDict[compdecp[0]] = compdecp[1]
    #print "extractionsDict=%s" % (extractionsDict)
    insertionsDict = {}
    for component in insertions:
        compdecp = component.split(':')
        if len(compdecp) != 2:
            logging.error("Insertion '%s' is invalid it must conatain name:dir" % (compdecp))
            usage()
            sys.exit(1)
        insertionsDict[compdecp[0]] = compdecp[1]
    for box in processingBoxes:
        box.PropertyExtractionsSet(extractionsDict)
        box.PropertyInsertionsSet(insertionsDict)        
    #print "avirtualHost.PropertyExtractionsGet=%s" % (avirtualHost.PropertyExtractionsGet())
        if ParsedImage != None:
            box.PropertyImageModeSet(ParsedImage)
    
        box.PropertyImageRestoreNameSet(restoreImage)
        box.PropertyImageStoreNameSet(storeImage)
        #print restoreImage
        imageList = []
        if "restore" in actionList:
            if not box.AvailableImage():
                mesage = "Image '%s' not found in directory '%s'" % (restoreImage,box.ImageStoreDir)
                logging.error(mesage)
                AvailableImageList = box.AvailableImageListGet()
                if len(AvailableImageList) > 0:
                    mesage = "The following images where found:"
                    for item in AvailableImageList:
                        mesage += "\n" + item
                    logging.warning(mesage)
                sys.exit(1)
            
        if "insert" in actionList:
            if not box.AvailableExtract():
                insertions = box.PropertyInsertionsGet()
                for ext in box.PropertyInsertionsGet().keys():
                    ImageName = "%s/%s" % (box.ExtractDir(),ext)
                    if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
                        logging.error("Error: Insert '%s' not found in directory '%s'" % (ext,box.ExtractDir()))
                sys.exit(1)
    HaveToCheckBoxes = []
    lockedBoxes = []
    for abox in processingBoxes:
        #print abox.HostName
        if abox.IsLockedByMe():
            #print "dabox.HostName"
            lockedBoxes.append(abox)
        else:
            #print "dabox.fffffffffHostName"
            if abox.Lock():
                HaveToCheckBoxes.append(abox)
            else:
                #print "Locked %s" % (abox)
                if not abox.IsLockedStill():
                    #print "foor %s,%s,%s" % (abox.IsLockedByMe(),abox.IsLockedStill(),abox.IsLocked())
                    if abox.Lock():
                        HaveToCheckBoxes.append(abox)
                else:
                    logging.error("In Use")
                
    
    if (len(HaveToCheckBoxes) > 0):
        time.sleep(1)
        for abox in HaveToCheckBoxes:
            if abox.IsLockedByMe():
                lockedBoxes.append(abox)
                
    for abox in lockedBoxes:
        box = processingBoxes.pop()
        boxLocked = box.Lock()
        #print boxLocked 
        
                
        for command in actionList:
            if command in ["kill"]:
                box.Kill()
        for command in actionList:
            if command in ["extract","insert","store","restore","down"]:
                box.ShutDown()
        for command in actionList:
            if command in ["extract"]:
                box.Extract()
        for command in actionList:
            if command in ["store"]:
                box.StoreHost()
        for command in actionList:
            if command in ["restore"]:
                box.RestoreHost()
        for command in actionList:
            if command in ["insert"]:
                box.Insert()
        for command in actionList:
            if command in ["extract","insert","store","restore","up"]:
                box.StartUp()
       
        box.Unlock()
    FoundLockedBox = False
    
    for abox in processingBoxes:
        #print abox.HostName
        if not abox in lockedBoxes:
            logging.error("Slot '%s' was locked when it was attempted to be used" % (abox.HostName))
            abox.Unlock()
            FoundLockedBox = True
    if FoundLockedBox:
        sys.exit(100)
