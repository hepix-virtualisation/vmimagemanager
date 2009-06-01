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
import libvirt
import xml.dom.minidom 

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, Message):
        self.Message = Message



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
    print ' -D, --debug     [Level]           Set the debug  level'
    print ' -u, --up                          Start Virtual Box'
    print ' -d, --down                        Stop Virtual Box'
    print ' -l, --list-boxes                  List Virtual Boxes'
    print ' -L, --list-images                 List Virtual Box Images'
    print ' -k, --kill                        Kill Virtual Box'
    print ' -z, --tgz                         tar.gz Virtual Box Image'
    print ' -m, --locked                      List Locked slots'
    print ' -f, --free                        List Free slots.'
    print ' -U, --used                        List Used slots'
    print ' -y, --rsync                       rsync Virtual Box Image [Default]'


class DiscLocking:
    def __init__(self,LockFile):
        
        self.lockedByMeKnown = False
        self.lockedByOtherKnown = False
        self.LockFile = LockFile
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
            if os.path.isfile(self.LockFile):
                os.remove(self.LockFile)
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


class VirtualHostDisk():
    def __init__(self,properties):
        self.CanMount = False
        
    def MountIs(self):
        # Returns False for not mounted
        # Returns True for device mounted
        result = False
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
            if mntsplit[2] == self.MountPoint:
                # Assumes no VM host maps to same directory
                #print "sdsdSD"
                result = True
        return result


    def ImageMount(self):
        print "sdfsdsssssssssssssssssf"
        return False
    def ImageUnMount(self):
        return not self.MountIs()

class VirtualHostDiskPartitionsShared(VirtualHostDisk):
    def __init__(self,properties):    
        self.CanMount = True
        self.HostRootSpace = properties["HostRootSpace"]
        self.MountPoint = properties["MountPoint"]
        
    def MountIs(self):
        # Returns False for not mounted
        # Returns True for device mounted
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
            if mntsplit[0] == self.HostRootSpace or mntsplit[2] == self.MountPoint:
                # Assumes no VM host maps to same directory
                #print "sdsdSD"
                result = 1
        return result
    
    
    def ImageMount(self):
        if self.MountIs() == True:
            return
        print "fsdfsdfddddddddddddddddd"
        if not os.path.isdir(self.MountPoint):
            #print "os.makedirs(%s)%s" % (self.Mount,self.HostRootSpace)
            os.makedirs(self.MountPoint)
            logging.info( 'Made Directory %s' % (self.MountPoint))
        cmd="mount %s %s" % (self.HostRootSpace,self.MountPoint)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            
            logging.error('Command "%s" Failed' % (cmd))
            logging.info( 'rc=%s,output=%s' % (rc,cmdoutput))
            sys.exit(1)            
        return

    def ImageUnMount(self):
        if self.MountStatus() == 0:
            return
        if not os.path.isdir(self.MountPoint):
            os.makedirs(self.MountPoint)
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
    
   

class VirtualHostDiskKpartx(VirtualHostDiskPartitionsShared):
    def __init__(self,properties):
        self.MountPoint = properties["MountPoint"]
        self.HostPartition = int(properties["HostPartition"])
        self.HostDisk = properties["HostDisk"]
        self.CanMount = True

    def MountIs(self):
        # Returns False for not mounted
        # Returns True for device mounted
        result = False
        cmd="mount"
        logging.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('mount Failed with error code %s and the folleowing error:%s' % (rc,cmdoutput))
            sys.exit(1)            
        #print "%s %s" % (self.PropertyHostRootSpaceGet(),self.PropertyMountGet())
        for mntline in cmdoutput.split("\n"):
            mntsplit = mntline.split(" ")
            if len(mntsplit) < 3:
                logging.error("Error parsing mount command!")
            #print mntsplit[2]    
            if mntsplit[2] == self.MountPoint:
                # Assumes no VM host maps to same directory
                self.HostRootSpace = mntsplit[0]
                result = True
        return result   

    def PartitionsOpen(self):
        cmd = 'kpartx -p vmim -av %s' % (self.HostDisk)
        logging.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('Failed "%s"' % (cmd))
            logging.error(cmdoutput)
            logging.error('Return Code=%s' % (rc))
            sys.exit(1)
        if "" == cmdoutput:
            logging.error('The Disk "%s" has no partitons' % (self.HostDisk))
            sys.exit(1)
        DiskPartitions = cmdoutput.split("\n")
        if len(DiskPartitions) <= self.HostPartition -1:
            logging.error('Partiton  "%s" is greater than "%s" the number of avilaable partitons' % (self.HostPartition,len(DiskPartitions) ))
            logging.error(cmdoutput)
            sys.exit(1)
        PartitonLine = DiskPartitions[self.HostPartition -1].split(" ")
        #logging.debug("PartitonLine=%s" % (PartitonLine))        
        self.HostRootSpace = "/dev/mapper/" + PartitonLine[2]
        return True
    def ImageMount(self):
        if self.MountIs():
            return True
        self.PartitionsOpen()
        if not os.path.isdir(self.MountPoint):
            #print "os.makedirs(%s)%s" % (self.Mount,self.HostRootSpace)
            os.makedirs(self.MountPoint)
            logging.info( 'Made Directory %s' % (self.MountPoint))
        cmd="mount %s %s" % (self.HostRootSpace,self.MountPoint)
        logging.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            
            logging.error('Command "%s" Failed' % (cmd))
            logging.info( 'rc=%s,output=%s' % (rc,cmdoutput))
            sys.exit(1)            
        return    

    def ImageUnMount(self):
        if not self.MountIs():
            logging.debug("Not Mounted")
            return True
        cmd="umount %s" % (self.HostRootSpace)
        logging.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('Command "%s" Failed' % (cmd))
            logging.info('rc=%s,output=%s' % (rc,cmdoutput))
            sys.exit(1)       
        
        return True
    def PartitionsClose(self):
        cmd = 'kpartx -p vmim -d %s' % ( self.HostDisk)
        logging.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('Failed "%s"' % (cmd))
            logging.error(cmdoutput)
            logging.error('Return Code=%s' % (rc))
            sys.exit(1)
        if hasattr(self,"HostRootSpace"):
           del self.HostRootSpace
        return True
        
        
    
class vmControlXen():
    def StartUp(self):
        self.DiskSubsystem.ImageUnMount()
        self.DiskSubsystem.UnLock()
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
            fpxenconftemp = open(self.ConfTemplateXen,'r')
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
        self.DiskSubsystem.PartitionsOpen()
        self.DiskSubsystem.ImageMount()
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
        self.ImageMode = "rsync"
        DiscLocking.__init__(self)
        self.LockFileFixed = False
        
        
        
    def __init__(self,properties):
        if not "HostName" in properties:
            raise InputError("No HostName Spcified for virtualhost")
        self.HostName = properties["HostName"]
        DiscLocking.__init__(self,properties["LockFile"])
        found = False
        if "HostMacAddress" in properties:
            found = True
            self.HostMacAddress = properties["HostMacAddress"]
        if "HostIp4Address" in properties:
            found = True
            self.HostIp4Address = properties["HostIp4Address"]
    
        if not found:
            raise InputError("HostMacAddress or HostIp4Address must be set for %s" %  self.HostName)
        
        found = False
        self.DiskSubsystem = VirtualHostDisk(properties)

        if ("HostRootSpace" in properties) and ("HostSwapSpace" in properties):
            self.DiskSubsystem = VirtualHostDiskPartitionsShared(properties)
            found = True
        if ("HostDisk" in properties) and ("HostPartition" in properties):
            self.DiskSubsystem = VirtualHostDiskKpartx(properties)
            found = True

        if not found:
            raise InputError("(HostRootSpace and HostSwapSpace) or (HostPartition and HostDisk) must be set for %s" %  self.HostName)
        if "ConfTemplateXen" in properties:
            self.ConfTemplateXen = properties["ConfTemplateXen"]
        if "ImageStoreDir" in properties:
            self.ImageStoreDir = properties["ImageStoreDir"]
        else:
            raise InputError("ImageStoreDir must be set for %s" %  self.HostName)
        if "FormatFilter" in properties:
            self.cmdFormatFilter = properties["FormatFilter"]
        else:
            self.cmdFormatFilter = 'mkfs.ext3 -L / %s'
        self.PropertyImageModeSet("rsync")
        
        self.memory = 2097152
        self.currentMemory = 2097152
        self.vcpu = 1
        
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
        if not self.DiskSubsystem.ImageUnMount():
            print "Failed unmount A"
            sys.exit(1)
        if not self.DiskSubsystem.PartitionsClose():
            print "Failed unmount B"
            sys.exit(1)
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
        while state in (1,2,3):
            counter += 1
            if counter < 180:
                try:
                    rc = self.libvirtObj.shutdown()
                except:
                    pass
            else:
                counter = 0
                rc = self.libvirtObj.destroy()
            time.sleep(1)
            (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
            #print "state %s" %( state)
        self.DiskSubsystem.PartitionsOpen()
        self.DiskSubsystem.ImageMount()
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
            
        logging.debug("command='%s'" % (cmd))
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
                    print "Failed Partition Open"
                    sys.exit(1)
                cmd=self.cmdFormatFilter % (self.DiskSubsystem.HostRootSpace)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                if rc != 0:
                    logging.error(cmdoutput)
                    logging.error("command line failed running %s" % (cmd))
                    return -1
                self.DiskSubsystem.ImageMount()
                if len(self.DiskSubsystem.MountPoint) == 0:
                    logging.error("Mount Point Undefined ")
                    sys.exit(1)                    
                cmd = "rm -rf %s" % (self.DiskSubsystem.MountPoint)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                cmd = "tar -zxf %s --exclude=lost+found   -C %s" % (ImageName,self.DiskSubsystem.MountPoint)
            if "rsync" == self.PropertyImageModeGet():
                cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/" % (ImageName,self.DiskSubsystem.MountPoint)
                logging.debug('Running command "%s".' % (cmd))
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error('Failed "%s"' % (cmd))
                logging.error(cmdoutput)
                logging.error('Return Code=%s' % (rc))
                return rc
        filename="%s/sourceimage" % (self.DiskSubsystem.MountPoint)
        fpvmconftemp = open(filename,'w+')
        fpvmconftemp.write("%s\n" % (ImageName))
        fpvmconftemp.close()
        logging.debug("Wrote '%s' with content '%s'." % (filename,ImageName))
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
    def genXml(self):
        rawxml = """<?xml version="1.0" ?>
        <domain type='kvm'>
  <name>${DomainName}</name>
  <memory>2097152</memory>
  <currentMemory>2097152</currentMemory>
  <vcpu>1</vcpu>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/bin/kvm</emulator>
    <disk type='block' device='disk'>
      <source dev='${DomainDev}'/>
      <target dev='hda' bus='ide'/>
    </disk>
    <disk type='file' device='cdrom'>
      <target dev='hdc' bus='ide'/>
      <readonly/>
    </disk>
    <interface type='bridge'>
      <mac address='${DomainMac}'/>
      <source bridge='br0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target port='0'/>
    </console>
    <input type='mouse' bus='ps2'/>
    <graphics type='vnc' port='-1' autoport='yes' keymap='en-us'/>
    <sound model='es1370'/>
  </devices>
</domain>
        """
        try:
            d = dict(
                DomainDev=self.DiskSubsystem.HostDisk,
                DomainRootDev="",
                DomainIp4Address="",
                DomainName=self.HostName,
                DomainSwapDev="",
                DomainMac=self.HostMacAddress
            )
            for key in d.keys():
                rawxml = rawxml.replace("${%s}" % (key), d[key])
        except:
            rawxml = ""
        impl = xml.dom.minidom.getDOMImplementation()
        newdoc = impl.createDocument(None, "domain", None)
        top_element = newdoc.documentElement
        a= newdoc.createAttribute("type")
        a.nodeValue = "kvm"
        top_element.setAttributeNode(a)
        name_element = newdoc.createElement("name")
        text = newdoc.createTextNode(self.HostName)
        name_element.appendChild(text)
        top_element.appendChild(name_element)
        memory_element = newdoc.createElement("memory")
        text = newdoc.createTextNode(str(self.memory))
        memory_element.appendChild(text)
        top_element.appendChild(memory_element)
        currentMemory_element = newdoc.createElement("currentMemory")
        text = newdoc.createTextNode(str(self.currentMemory))
        currentMemory_element.appendChild(text)
        top_element.appendChild(currentMemory_element)
        vcpu_element = newdoc.createElement("vcpu")
        text = newdoc.createTextNode(str(self.vcpu))
        vcpu_element.appendChild(text)
        top_element.appendChild(vcpu_element)
        os_element = newdoc.createElement("os")
        type_element = newdoc.createElement("type")
        a= newdoc.createAttribute("arch")
        a.nodeValue = "x86_64"
        type_element.setAttributeNode(a)
        a = newdoc.createAttribute("machine")
        a.nodeValue = "pc"
        type_element.setAttributeNode(a)
        text = newdoc.createTextNode("hvm")
        os_element.appendChild(type_element)
        boot_element =newdoc.createElement("boot")
        a = newdoc.createAttribute("dev")
        a.nodeValue = "hd"
        boot_element.setAttributeNode(a)
        os_element.appendChild(boot_element)
        top_element.appendChild(os_element)
        features_element =newdoc.createElement("features")
        acpi_element =newdoc.createElement("acpi")
        features_element.appendChild(acpi_element)
        apic_element =newdoc.createElement("apic")
        features_element.appendChild(apic_element)
        pae_element =newdoc.createElement("pae")
        features_element.appendChild(pae_element)
        top_element.appendChild(features_element)        
        
        clock_element =newdoc.createElement("clock")
        a= newdoc.createAttribute("offset")
        a.nodeValue = "utc"
        clock_element.setAttributeNode(a)
        top_element.appendChild(clock_element)        
        on_poweroff_element =newdoc.createElement("on_poweroff")
        text = newdoc.createTextNode("destroy")
        on_poweroff_element.appendChild(text)
        top_element.appendChild(on_poweroff_element) 
        
        on_reboot_element =newdoc.createElement("on_reboot")
        text = newdoc.createTextNode("destroy")
        on_reboot_element.appendChild(text)
        top_element.appendChild(on_reboot_element) 
        
        on_crash_element =newdoc.createElement("on_crash")
        text = newdoc.createTextNode("destroy")
        on_crash_element.appendChild(text)
        top_element.appendChild(on_crash_element) 
        devices_element =newdoc.createElement("devices")
        emulator_element =newdoc.createElement("emulator")
        text = newdoc.createTextNode("/usr/bin/kvm")
        emulator_element.appendChild(text) 
        devices_element.appendChild(emulator_element) 
        disk_element =newdoc.createElement("disk")
        a= newdoc.createAttribute("type")
        a.nodeValue = "block"
        disk_element.setAttributeNode(a)
        a= newdoc.createAttribute("device")
        a.nodeValue = "disk"
        disk_element.setAttributeNode(a)
        source_element =newdoc.createElement("source")
        try:
            a= newdoc.createAttribute("dev")
            a.nodeValue = self.DiskSubsystem.HostDisk
            source_element.setAttributeNode(a)
            disk_element.appendChild(source_element)
        except:
            pass
        target_element =newdoc.createElement("target")
        a= newdoc.createAttribute("dev")
        a.nodeValue = "hda"
        
        target_element.setAttributeNode(a)
        a= newdoc.createAttribute("bus")
        a.nodeValue = "ide"
        target_element.setAttributeNode(a)
        
        disk_element.appendChild(target_element)
        devices_element.appendChild(disk_element)
        top_element.appendChild(devices_element)
        

        #thisdata = xml.dom.minidom.parseString(rawxml)
        print newdoc.toxml()
        return rawxml
        
    
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
        cmdFormatFilter = "mkfs.ext3 -L / %s"
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
        newConfTemplateXen = config.get(GeneralSection,'xenconftemplate')
        if len(newConfTemplateXen) == 0:
            logging.fatal( "Configuration file does not have a section '%s' with a key in it 'xenconftemplate'" % (GeneralSection))
            sys.exit(1)
        self.ConfTemplateXen = newConfTemplateXen
        
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
        ThisKey = 'virthost'
        if (config.has_option(GeneralSection, ThisKey)):
            self.VmHostServer = config.get(GeneralSection,ThisKey)
        else:
            default = 'qemu:///system'
            logging.warning("Configuration file does not have a section '%s' with a key in it 'virthost' defaulting to '%s'" % (GeneralSection,default))
            self.VmHostServer = default
        
        self.conection = libvirt.open(self.VmHostServer)
        
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
                    cfgDict = {}
                    cfgDict["Connection"] = self.conection
                    #ThisVirtualHost =  virtualhost()
                    
                    if (config.has_option(cfgSection, "HostName")):
                        cfgDict["HostName"]  = config.get(cfgSection,"HostName")
                    if (config.has_option(cfgSection, "mac")):
                        cfgDict["HostMacAddress"]  = config.get(cfgSection,"mac")
                    if (config.has_option(cfgSection, "ip")):
                        cfgDict["HostIp4Address"]  = config.get(cfgSection,"ip")
                
                    if (config.has_option(cfgSection, "root")):
                        cfgDict["HostRootSpace"]  = config.get(cfgSection,"root")
                    if (config.has_option(cfgSection, "swap")):
                        cfgDict["HostSwapSpace"]  = config.get(cfgSection,"swap")
                    if (config.has_option(cfgSection, "disk")):
                        cfgDict["HostDisk"]  = config.get(cfgSection,"disk")
                    if (config.has_option(cfgSection, "partition")):
                        cfgDict["HostPartition"]  = config.get(cfgSection,"partition")
                    
                    if (config.has_option(cfgSection, "vmimages")):
                        cfgDict["ImageStoreDir"]  = config.get(cfgSection,"vmimages")                
                    else:
                        cfgDict["ImageStoreDir"] = os.path.join(self.XenImageDir , cfgDict["HostName"])
                    if (config.has_option(cfgSection, "mount")):
                        cfgDict["MountPoint"]  = config.get(cfgSection,"mount")
                    else:
                        cfgDict["MountPoint"]  = os.path.join(VmMountsBaseDir ,cfgDict["HostName"])
                    #print "tskjdfhksjldf=%s" % (cfgDict["Mount)
                    cfgDict["VmSlotVarDir"] = os.path.join(newvmconfdir , cfgDict["HostName"])
                    
                    cfgDict["XenCfgFile"]  =  os.path.join(cfgDict["VmSlotVarDir"] , "xen")
                    if (config.has_option(cfgSection, "vmcfg")):
                        cfgDict["XenCfgFile"]  = config.get(cfgSection,"vmcfg")
                    
                    cfgDict["LockFile"]  = os.path.join( newvmconfdir , cfgDict["HostName"] ,"lock")
                    #print cfgDict["LockFile
                    if (config.has_option(cfgSection, "vmlock")):
                       
                        cfgDict["LockFile"]  = config.get(cfgSection,"vmlock")
                    
                    if (config.has_option(cfgSection, "vmextracts")):
                       
                        cfgDict["VmExtractsDir"]  = config.get(cfgSection,"vmextracts")
                    else:
                        cfgDict["VmExtractsDir"] = self.VmExtractsDir
                    
                    
                    
                    if (config.has_option(cfgSection, "formatFilter")):
                        cfgDict["FormatFilter"]  = config.get(cfgSection,"formatFilter")
                    else:
                        cfgDict["FormatFilter"] = cmdFormatFilter
                    
                    if (config.has_option(cfgSection, "ConfTemplateXen")):
                        cfgDict["ConfTemplateXen"]  = config.get(cfgSection,"ConfTemplateXen")
                    else:
                        cfgDict["ConfTemplateXen"] = self.ConfTemplateXen
                    try:      
                        newhost = virtualhost(cfgDict)
                        newhost.Container = self
                        self.hostlist.append(newhost)
                    except InputError, (instance):
                        print repr(instance.Message)
        KnownHosts = []
        for libVritId in self.conection.listDomainsID():
            dom=self.conection.lookupByID(libVritId)
            HostName = dom.name()
            for x in range (0 , len(self.hostlist)):
                if self.hostlist[x].HostName == HostName:
                    self.hostlist[x].libvirtObj = dom
            KnownHosts.append(dom.name())
        #print len(self.hostlist)
        for x in range (0 , len(self.hostlist)):
            #print self.hostlist[x].HostName
            if not self.hostlist[x].HostName in KnownHosts:
                host = self.hostlist[x]
                generatorXml = host.genXml()
                if generatorXml != "":
                    host.libvirtObj = self.conection.defineXML(generatorXml)
                    self.hostlist[x] = host
                    #print dir(self.hostlist[x])
        #print len(self.hostlist)
                    
                    
if __name__ == "__main__":
    #opts = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:s:r:e:i:c:udlLhvkzypfm", ["box=", "store=","restore=","extract=","insert=","config=","up","down","list-boxes","list-images","help","version","kill","tgz","rsync","print-config","free","locked"])
    except :
        usage()
        logging.error('Command line option error')
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
