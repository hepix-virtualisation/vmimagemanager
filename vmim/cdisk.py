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

try:
    from xml.etree.ElementTree import Element, SubElement, dump,tostring
except ImportError:
    from elementtree.ElementTree  import Element, SubElement, dump,tostring

# Note this methos may not be needed    
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






class VirtualHostDisk:
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
            self.loggererror('mount Failed with error code %s and the folleowing error:%s' % (rc,cmdoutput))
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
            self.logger.error('Command "%s" Failed' % (cmd))
            self.logger.info( 'rc=%s,output=%s' % (rc,cmdoutput))
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
            self.logger.error('Command "%s" Failed' % (cmd))
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
            self.logger.warning(' Cant mount The Disk "%s" has no partitons' % (self.HostDisk))
            return False
        
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
            self.logger.info("os.makedirs(%s)" % (self.MountPoint))
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


