#!/usr/bin/python
#import ConfigParser

import logging, logging.config


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
from xml.etree.ElementTree import Element, SubElement, dump,tostring

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

# Add lines to import a namespace and add it to the list of namespaces used


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
        foundPids = []
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
        self.logger.debug("DiscLocking foundPids=%s" % (foundPids))
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
        #self.logger.error "can lock %s" % ( self.LockFile)
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
        self.logger = logging.getLogger("vmimagemanager.VirtualHostDisk") 
        self.CanMount = False
    def MountIs(self):
        return False

    def ImageMount(self):
        self.logger.debug("ImageMount")
        return False
    def ImageUnMount(self):
        return True

    def PartitionsClose(self):
        return True
    def PartitionsOpen(self):
        return True

    def LibVirtXmlTreeGenerate(self,devices):    
        pass
        #self.logger.debug("LibVirtXmlTreeGenerate")
        #disk = SubElement(devices, "disk",device="disk")
        #self.logger.debug(tostring(disk))



class VirtualHostDiskPartiions(VirtualHostDisk):
    def PartitionsCheck(self):
        return True

class VirtualHostDiskPartitionsShared(VirtualHostDiskPartiions):
    def __init__(self,properties):   
        self.logger = logging.getLogger("vmimagemanager.VirtualHostDiskPartitionsShared") 
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
            self.logging.error('mount Failed with error code %s and the folleowing error:%s' % (rc,cmdoutput))
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
            return True
        #print "fsdfsdfddddddddddddddddd"
        if not os.path.isdir(self.MountPoint):
            #print "os.makedirs(%s)%s" % (self.Mount,self.HostRootSpace)
            os.makedirs(self.MountPoint)
            self.logger.info( 'Made Directory %s' % (self.MountPoint))
        cmd="mount %s %s" % (self.HostRootSpace,self.MountPoint)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.debug( 'self=%s,self.HostRootSpace=%s,self.MountPoint=%s' % (self,self.HostRootSpace,self.MountPoint))
            self.logging.error('Command "%s" Failed' % (cmd))
            self.self.logger.info( 'rc=%s,output=%s' % (rc,cmdoutput))
            return False          
        return True

    def ImageUnMount(self):
        if self.MountIs() == False:
            return True
        if not os.path.isdir(self.MountPoint):
            os.makedirs(self.MountPoint)
        cmd="umount %s" % (self.HostRootSpace)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logging.error('Command "%s" Failed' % (cmd))
            self.logger.info('rc=%s,output=%s' % (rc,cmdoutput))
            return False          
        return True

    def MountTest(self):
        self.logger.debug("MountStatus %s" % (self.MountIs()))
        self.Mount()
        self.logger.debug("MountStatus %s" % (self.MountIs()))
        self.UnMount()
        self.logger.debug("MountStatus %s" % (self.MountIs()))
        sys.exit(0)    
    def LibVirtXmlTreeGenerate(self,devices):    
        self.logger.debug("LibVirtXmlTreeGenerate")
        disk = SubElement(devices, "disk",device="disk")
        disk.set('type', "block")
        source = SubElement(disk, "source")
        try:
            source.set('dev', self.HostDisk)
        except:
            source.set('dev', "/dev/mapper/d430-sysVm002")
        target = SubElement(disk, "target",dev="hda",bus="ide")
        serial = SubElement(devices, "serial")
    


class VirtualHostDiskKpartx(VirtualHostDiskPartitionsShared):
    def __init__(self,properties):
        self.logger = logging.getLogger("vmimagemanager.VirtualHostDiskKpartx")
        self.MountPoint = properties["MountPoint"]
        #self.logger.debug("properties['HostPartition'] %s" % (properties["HostPartition"]))
        self.HostPartition = int(properties["HostPartition"])
        self.HostDisk = properties["HostDisk"]
        self.CanMount = True
    def GetPartitionList(self):
        pass
    def MountIs(self):
        # Returns False for not mounted
        # Returns True for device mounted
        result = False
        cmd="mount"
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logging.error('mount Failed with error code %s and the folleowing error:%s' % (rc,cmdoutput))
            sys.exit(1)            
        #print "%s %s" % (self.PropertyHostRootSpaceGet(),self.PropertyMountGet())
        for mntline in cmdoutput.split("\n"):
            mntsplit = mntline.split(" ")
            if len(mntsplit) < 3:
                self.logging.error("Error parsing mount command!")
            #print mntsplit[2]    
            if mntsplit[2] == self.MountPoint:
                # Assumes no VM host maps to same directory
                self.HostRootSpace = mntsplit[0]
                result = True
        return result   
    def PartitionsCheck(self):
        cmd = 'kpartx -p vmim -lv %s' % (self.HostDisk)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Failed "%s"' % (cmd))
            self.logger.error(cmdoutput)
            self.logger.error('Return Code=%s' % (rc))
            sys.exit(1)
        if "" == cmdoutput:
            self.logger.error('The Disk "%s" has no partitons' % (self.HostDisk))
            sys.exit(1)
        
        rootStripLen = None
        DiskPartitionD = []
        DiskPartitions = cmdoutput.split("\n")
        
        for PartitionLine in cmdoutput.split("\n"):
            
            
                
            PartitionLineSplit = PartitionLine.split(" ")
            #self.logger.debug("PartitionLineSplit=%s" % (PartitionLineSplit))     
            if len(PartitionLineSplit) > 3:
                Partition = {}
                Partition['Line'] = PartitionLine
                Partition['Path'] = PartitionLineSplit[0]
                if None == rootStripLen:
                    rootStrip = len(string.rstrip(Partition['Path'],string.digits))
                    if rootStrip > 0:
                        rootStripLen = rootStrip
                Partition['Number'] = int(PartitionLineSplit[0][(rootStripLen):])
                #self.logger.debug("Partition=%s" % (Partition))
                DiskPartitionD.append(Partition)
        
        correct = None  
        for item in DiskPartitionD:
            if item['Number'] == self.HostPartition:
                
                correct = item
        if correct == None:
            partitionList = []
            self.logger.error('Partiton  "%s" does not exist.' % (self.HostPartition))
            for item in DiskPartitionD:
                print "%s" % (item['Number'])
            self.logger.debug(cmdoutput)
            sys.exit(1)
        
        #print correct
        
        
        self.HostRootSpace = "/dev/mapper/" + correct['Path']
        return True
    def PartitionsOpen(self):
        self.logger.debug("HostPartition=%s" % (self.HostPartition))
        cmd = 'kpartx -p vmim -av %s' % (self.HostDisk)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Failed "%s"' % (cmd))
            self.logger.error(cmdoutput)
            self.logger.error('Return Code=%s' % (rc))
            sys.exit(1)
        return True
    
    def ImageMount(self):
        if self.MountIs():
            return True
        if not self.PartitionsOpen():
            raise "error"
        if not os.path.isdir(self.MountPoint):
            self.logger.info("os.makedirs(%s)%s" % (self.Mount,self.HostRootSpace))
            os.makedirs(self.MountPoint)
            self.logger.info( 'Made Directory %s' % (self.MountPoint))
        cmd="mount %s %s" % (self.HostRootSpace,self.MountPoint)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.debug( 'gggggggggggself=%s,self.HostRootSpace=%s,self.MountPoint=%s' % (self,self.HostRootSpace,self.MountPoint))
            self.logger.error('Command "%s" Failed' % (cmd))
            self.logger.info( 'rc=%s,output=%s' % (rc,cmdoutput))
            sys.exit(1)            
        return    

    def ImageUnMount(self):
        if not self.MountIs():
            self.logger.debug("Not Mounted")
            return True
        cmd="umount %s" % (self.HostRootSpace)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Command "%s" Failed' % (cmd))
            self.logger.info('rc=%s,output=%s' % (rc,cmdoutput))
            sys.exit(1)       
        
        return True
    def PartitionsClose(self):
        cmd = 'kpartx -p vmim -d %s' % ( self.HostDisk)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Failed "%s"' % (cmd))
            self.logger.error(cmdoutput)
            self.logger.error('Return Code=%s' % (rc))
            sys.exit(1)
        if hasattr(self,"HostRootSpace"):
           del self.HostRootSpace
        return True
        
    def LibVirtXmlTreeGenerate(self,devices):    
        disk = SubElement(devices, "disk",device="disk")
        disk.set('type', "block")
        source = SubElement(disk, "source")
        try:
            source.set('dev', self.HostDisk)
        except:
            source.set('dev', "/dev/mapper/d430-sysVm002")
        target = SubElement(disk, "target",dev="hda",bus="ide")
        serial = SubElement(devices, "serial")



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
                self.logger.info(cmdoutput)
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
            self.DiskSubsystem = VirtualHostDiskPartitionsShared(self.DcgDict)
            
            found = True
            #self.logger.debug("setting  self.DiskSubsystem %s to VirtualHostDiskPartitionsShared" % self.HostName)
            
        if ("HostDisk" in self.DcgDict.keys()) and ("HostPartition" in self.DcgDict.keys()):
            self.DiskSubsystem = VirtualHostDiskKpartx(self.DcgDict)
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
            self.DiskSubsystem = VirtualHostDisk(self.DcgDict)
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
            DiscLocking.__init__(self,self.DcgDict["LockFile"])
        
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
        (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
        if state in (1,2,3):
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
                except :
                    print "exception thrown"
            else:
                self.logger.warning("Timed out shutting down domain")
                counter = 0
                #print "timed Out"
                rc = self.libvirtObj.destroy()
            time.sleep(1)
            (state,maxMem,memory,nrVirtCpu,cpuTime) =  self.libvirtObj.info()
            self.logger.debug("state=%s, timeout in %s" %( state, timeout-  counter))
            
            #print dir(self.libvirtObj)
            #print self.libvirtObj.destroy()
        self.RealiseDevice()
        self.DiskSubsystem.PartitionsOpen()
        #self.logger.debug("self.DiskSubsystem %s " %(self.DiskSubsystem))
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
    def genXmlShouldExist(self):
        domain = Element("domain")
        domain.set('type', "kvm")
        name = SubElement(domain, "name",)
        name.text = self.HostName
        memory = SubElement(domain, "memory")
        memory.text = str(self.DcgDict["memory"])
        cmemory = SubElement(domain, "currentMemory")
        cmemory.text = str(self.DcgDict["currentMemory"])
        vcpu = SubElement(domain, "vcpu")
        vcpu.text = str(self.DcgDict["vcpu"])
        os = SubElement(domain, "os")
        os_type = SubElement(os, "type",arch="x86_64",machine="pc")
        os_type.text = str("hvm")
        os_boot = SubElement(os, "boot",dev="hd")
        features = SubElement(domain, "features")
        acpi = SubElement(features, "acpi")
        apic = SubElement(features, "apic")
        pae = SubElement(features, "pae")
        
        clock = SubElement(domain, "clock",offset="utc")
        on_power_off  = SubElement(domain, "on_poweroff")
        on_power_off.text = "destroy"
        on_reboot = SubElement(domain, "on_reboot")
        on_reboot.text = "destroy"
        on_crash = SubElement(domain, "on_crash")
        on_crash.text = "destroy"
        devices = SubElement(domain, "devices")
        emulator = SubElement(devices, "emulator")
        emulator.text = "/usr/bin/kvm"
        
        self.RealiseDevice()
        self.DiskSubsystem.LibVirtXmlTreeGenerate(devices)
        self.logger.debug("DiskSubsystem %s" %(self.DiskSubsystem))
        serial = SubElement(devices, "serial")
        serial.set('type', "pty")
        serial_target  = SubElement(serial, "target",port="0")
        console = SubElement(devices, "console")
        console.set('type', "pty")
        console_target  = SubElement(console, "target",port="0")
        
        #print "self.genXml=" + self.genXml()
        #print "genXmlShouldExist=" + text
        text = tostring(domain)
        #self.logger.debug(text)
        return text

 
    def LoadCfg(self,Config,Defaults):
        
        pass
        
    
class virtualHostContainer:
    
    def __init__(self):
        self.hostlist = []
        self.cfgDefault = {}
        
        self.logger = logging.getLogger("vmimagemanager.virtualHostContainer") 
        
        
    def PropertyVmSlotVarDirSet(self, value):
        for aHost in self.hostlist:
            aHost.VmSlotVarDir = value
            logging.error("aHost.VmSlotVarDir=%s" % (aHost.VmSlotVarDir))
            aHost.PropertyVmSlotVarDirSet(value)
        self.__VmSlotVarDir = value
    def libvirtImport(self):
        self.VmHostServer
        self.conection = libvirt.open(str(self.VmHostServer))
        #print "libvirtImport" + str(dir(self.conection))
        #print self.conection.listDevices()
        #print self.conection.listDomainsID()
        self.KnownHosts = []
        libVirtNames = self.conection.listDefinedDomains()
        #print "libVirtNames=%s"  % (libVirtNames)
        TmpHostNames = []
        for libVritId in self.hostlist:
            TmpHostNames.append(libVritId.HostName)
        #print "TmpHostNames" + str(TmpHostNames)
         
        for Name in libVirtNames:
            if not Name in TmpHostNames:
                cfgDict = {}
                cfgDict["Connection"] = self.conection
                #if has(libVritId
                #sif not libVritId
                libvirtdConnection = self.conection.lookupByName(Name)
                cfgDict["HostName"]  = Name
                fred =  self.virtualHostGenerator(cfgDict)
                #print fred
                #Host.libvirtObj = libvirt.open(self.VmHostServer)
                #print "sdfsfhjkf"
                #self.hostlist.append(Host)
            #print len(self.hostlist)
        return True
    def LoadConfigFile(self,fileName):
        
        GeneralSection = "VmImageManager"
        HostListSection = "AvailalableHosts"
        RequiredSections = [GeneralSection]
        #RequiredSections = [GeneralSection,HostListSection]
        self.config = ConfigParser.ConfigParser()
        cmdFormatFilter = "mkfs.ext3 -L / %s"
        self.config.readfp(open(fileName,'r'))
        #logging.warning( config.sections()
        configurationSections = self.config.sections()
        for ASection in RequiredSections:
            if not ASection in configurationSections:
                logging.fatal( "Configuration file does not have a section '%s'"  % (ASection))
                return False
        
        self.cfgHosts = self.config.sections()
        
        
        self.newvmconfdir = self.config.get(GeneralSection,'vmconfdir')
        if len(self.newvmconfdir) == 0:
            logging.fatal( "Configuration file does not have a section '%s' with a key in it 'vmconfdir'" % (GeneralSection))
            return False
        ##self.VmSlotVarDir = newvmconfdir
        self.PropertyVmSlotVarDirSet(self.newvmconfdir)
        #logging.warning( self.__VmSlotVarDir
        newConfTemplateXen = self.config.get(GeneralSection,'xenconftemplate')
        if len(newConfTemplateXen) == 0:
            logging.fatal( "Configuration file does not have a section '%s' with a key in it 'xenconftemplate'" % (GeneralSection))
            return False
        self.ConfTemplateXen = newConfTemplateXen
        
        newXenImageDir = self.config.get(GeneralSection,'vmimages')
        if len(newXenImageDir) == 0:
            logging.fatal( "Configuration file does not have a section '%s' with a key in it 'vmimages'" % (GeneralSection))
            sys.exit(1)
        self.XenImageDir = newXenImageDir
        self.VmExtractsDir = newXenImageDir
        
        newVmExtractsDir = self.config.get(GeneralSection,'vmextracts')
        if len(newVmExtractsDir) == 0:
            logging.warning("Configuration file does not have a section '%s' with a key in it 'vmextracts' defaulting to '%s'" % (GeneralSection,GeneralSection))
        else:            
            self.VmExtractsDir = newVmExtractsDir
	VmMountsBaseDir = "/mnt/vmimagemanager/"
	
        VmMountsBaseDir = self.config.get(GeneralSection,'mount')
	
        ThisKey = 'virthost'
        if (self.config.has_option(GeneralSection, ThisKey)):
            self.VmHostServer = str(self.config.get(GeneralSection,ThisKey))
        else:
            default = 'qemu:///system'
            logging.warning("Configuration file does not have a section '%s' with a key in it 'virthost' defaulting to '%s'" % (GeneralSection,default))
            self.VmHostServer = default
        
        
        if (self.config.has_option(GeneralSection, "formatFilter")):
            cmdFormatFilter = self.config.get(GeneralSection,'formatFilter')
        
        if (self.config.has_option(GeneralSection, "vAlocatedMemory")):
            self.cfgDefault["memory"] = self.config.get(GeneralSection,'vAlocatedMemory')
        else:
            default = 2097152
            self.logger.warning("Configuration file does not have a section '%s' with a key in it 'vAlocatedMemory' defaulting to '%s'" % (GeneralSection,default))
            self.cfgDefault["memory"] = default
        
        if (self.config.has_option(GeneralSection, "cAlocatedMemory")):
            self.cfgDefault["currentMemory"] = self.config.get(GeneralSection,'cAlocatedMemory')
        else:
            default = 2097152
            self.logger.warning("Configuration file does not have a section '%s' with a key in it 'cAlocatedMemory' defaulting to '%s'" % (GeneralSection,default))
            self.cfgDefault["currentMemory"] = default
        self.cfgDefault["vcpu"] = 1
        
    def virtualHostGenerator(self,cfg):
        hostName = str(cfg["HostName"])
        index = -1
        for x in range (0 , len(self.hostlist)):
           
            if str(self.hostlist[x].HostName) == hostName:
               index= x
               break
            #print self.hostlist[x].HostName
        if index == -1:
            #self.logger.debug("creating %s as index= %s" % (self.hostlist,index))
            #self.logger.debug("cfg=%s" % (cfg))
            newhost = virtualhost(cfg)
            #newhost.loadCfg(self.cfgDefault)
            newhost.Container = self
            newhost.HostName = hostName
            self.hostlist.append(newhost)
            return newhost
        else:
            self.hostlist[x].loadCfg(cfg)
            return self.hostlist[x]
                    
    def cfgHostsLoad(self):
        
        for cfgSection in self.cfgHosts:
                #print cfgSection
                isanImage = 0
		VmMountsBaseDir = "/tmp/vmimagemanager"
                if (self.config.has_option(cfgSection, "vm_slot_enabled")):
                    isanImageStr = self.config.get(cfgSection,"vm_slot_enabled")
                    if (isanImageStr in (["Yes","YES","yes","y","On","on","ON","1"])):
                        isanImage = 1
                if isanImage > 0:
                    cfgDict = {}
                    cfgDict["Connection"] = self.conection
                    #ThisVirtualHost =  virtualhost()
                    
                    if (self.config.has_option(cfgSection, "HostName")):
                        cfgDict["HostName"]  = self.config.get(cfgSection,"HostName")
                    if (self.config.has_option(cfgSection, "mac")):
                        cfgDict["HostMacAddress"]  = self.config.get(cfgSection,"mac")
                    if (self.config.has_option(cfgSection, "ip")):
                        cfgDict["HostIp4Address"]  = self.config.get(cfgSection,"ip")
                
                    if (self.config.has_option(cfgSection, "root")):
                        cfgDict["HostRootSpace"]  = self.config.get(cfgSection,"root")
                    if (self.config.has_option(cfgSection, "swap")):
                        cfgDict["HostSwapSpace"]  = self.config.get(cfgSection,"swap")
                    if (self.config.has_option(cfgSection, "hostdisk")):
                        cfgDict["HostDisk"]  = self.config.get(cfgSection,"hostdisk")
                    if (self.config.has_option(cfgSection, "partition")):
                        cfgDict["HostPartition"]  = self.config.get(cfgSection,"partition")
                        #print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxXX %s,%s" %(cfgDict["HostName"],cfgDict["HostPartition"] )
                    if (self.config.has_option(cfgSection, "vmimages")):
                        cfgDict["ImageStoreDir"]  = self.config.get(cfgSection,"vmimages")                
                    else:
                        cfgDict["ImageStoreDir"] = os.path.join(self.XenImageDir , cfgDict["HostName"])
                    if (self.config.has_option(cfgSection, "mount")):
                        cfgDict["MountPoint"]  = self.config.get(cfgSection,"mount")
                    else:
                        cfgDict["MountPoint"]  = os.path.join(VmMountsBaseDir ,cfgDict["HostName"])
                    
                    
                    if (self.config.has_option(cfgSection, "memory")):
                        cfgDict["memory"]  = self.config.get(cfgSection,"memory")
                    else:
                        cfgDict["memory"]  = self.cfgDefault["memory"]
                    
                   
                    if (self.config.has_option(cfgSection, "currentMemory")):
                        cfgDict["currentMemory"]  = self.config.get(cfgSection,"currentMemory")
                    else:
                        cfgDict["currentMemory"]  = self.cfgDefault["currentMemory"]
                    #print "tskjdfhksjldf=%s" % (cfgDict["Mount)
                    cfgDict["VmSlotVarDir"] = os.path.join(self.newvmconfdir , cfgDict["HostName"])
                    
                    cfgDict["XenCfgFile"]  =  os.path.join(cfgDict["VmSlotVarDir"] , "xen")
                    if (self.config.has_option(cfgSection, "vmcfg")):
                        cfgDict["XenCfgFile"]  = self.config.get(cfgSection,"vmcfg")
                    
                    cfgDict["LockFile"]  = os.path.join( self.newvmconfdir , cfgDict["HostName"] ,"lock")
                    #print cfgDict["LockFile
                    if (self.config.has_option(cfgSection, "vmlock")):
                       
                        cfgDict["LockFile"]  = self.config.get(cfgSection,"vmlock")
                    
                    if (self.config.has_option(cfgSection, "vmextracts")):
                       
                        cfgDict["VmExtractsDir"]  = self.config.get(cfgSection,"vmextracts")
                    else:
                        cfgDict["VmExtractsDir"] = self.VmExtractsDir
                    
                    
                    
                    if (self.config.has_option(cfgSection, "formatFilter")):
                        cfgDict["FormatFilter"]  = self.config.get(cfgSection,"formatFilter")
                    else:
                        pass
                        #cfgDict["FormatFilter"] = self.cmdFormatFilter
                    
                    if (self.config.has_option(cfgSection, "ConfTemplateXen")):
                        cfgDict["ConfTemplateXen"]  = self.config.get(cfgSection,"ConfTemplateXen")
                    else:
                        cfgDict["ConfTemplateXen"] = self.ConfTemplateXen
                    
                    
                    
                    try:      
                        newhost = self.virtualHostGenerator(cfgDict)
                        
                    except InputError, (instance):
                        print repr(instance.Message)
        
    def libVirtExport(self):
        hostNames = []
        libVirtNames = self.conection.listDefinedDomains()
        for x in range (0 , len(self.hostlist)):
            try:
                if not hasattr(self.hostlist[x],"libvirtObj"):
                    self.hostlist[x].libvirtObj = self.conection.lookupByName(self.hostlist[x].HostName)
            except libvirt.libvirtError, e:
                #print "errot=%s" %(e)
                if (e.get_error_code() == 42):
                    #print "sdfDSF"
                    self.hostlist[x].cfgApply()
                    self.hostlist[x].RealiseDevice()
                    
                    generatorXml = self.hostlist[x].genXmlShouldExist()
                    if generatorXml != "":
                        try:
                            
                            self.hostlist[x].libvirtObj = self.conection.defineXML(generatorXml)
                        except libvirt.libvirtError, e:
                            #print KnownHosts
                            #print "Exception Generating " + self.hostlist[x].HostName
                            self.logger.debug("generatorXml=%s" % (generatorXml))
                            self.logger.error("Exception Generating " + self.hostlist[x].HostName)
                            self.logger.debug(e)
                            #print dir(e)
                            #print e.get_error_level()
                            #print e
                            #raise e
                        
                
                    
if __name__ == "__main__":


    InstallPrefix="/"

    ConfigFile = ""

    Fillocations = ['vmimagemanager.cfg', os.path.expanduser('~/.vmimagemanager.cfg'),InstallPrefix + '/etc/vmimagemanager/vmimagemanager.cfg']

    for fileName in Fillocations:
	    if True == os.path.isfile(fileName):
		    ConfigFile = fileName
		    break
    if len(ConfigFile) == 0:
	    ConfigFile = '/etc/vmimagemanager/vmimagemanager.cfg'
    logger = logging.getLogger("vmimagemanager")
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    ch.setFormatter(formatter)
#add ch to logger
    logger.addHandler(ch)

    #create formatter
    
    #logging.config.fileConfig("logging.conf")
    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:s:r:e:i:c:udlLhvkzypfm", ["box=", "store=","restore=","extract=","insert=","config=","up","down","list-boxes","list-images","help","version","kill","tgz","rsync","print-config","free","locked"])
    except :
        usage()
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
        lcfg2c = HostContainer.LoadConfigFile(ConfigFile)
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
    if len(boxlist) >0:       
        notfound = False
        for box in boxlist:
            found = False
            for x in range (0 , len(HostContainer.hostlist)):
                #logger.debug("boxy=%s ahostsdebug=%s" % (box ,HostContainer.hostlist[x].DcgDict))
                if HostContainer.hostlist[x].HostName == box:
                    found = True
            if found:
                pbindex.append(x)
    #print pbindex
    #for index in pbindex:
        #print index
        #print HostContainer.hostlist
        #logger.debug("asdsshostsdebug=%s" % (HostContainer.hostlist[index].DcgDict))
        #HostContainer.hostlist[index].cfgApply()
        #logger.debug("asssshostsdebug=%s" % (HostContainer.hostlist[index].DcgDict))
        #Lockfile = HostContainer.hostlist[index].DcgDict["LockFile"]
        #DiscLocking.__init__(HostContainer.hostlist[index],Lockfile)
        
    if len(boxlist) >0:       
        notfound = False
        for box in boxlist:
            found = False            
            for ahost in HostContainer.hostlist:
                if ahost.HostName == box:
                    found = True
        
                    ahost.cfgApply()
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
        potentiallyFree = []
        for ahost in HostContainer.hostlist:
            if ahost.isRunning():
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
                    logging.error("Host %s is nn Use")
                
    
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
