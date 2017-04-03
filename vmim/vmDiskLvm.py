from vmDiskAbstract import diskMounterBaseClass
import os
import logging, logging.config
import commands
import sys

def Property(func):
    return property(**func())



class lvmControl:
    doc = "Makes LVM abstraction"
    def __init__(self):
        
        self.logger = logging.getLogger("vmimagemanager.lvmControl") 
        
    def updateModel(self):
        self.attiribtes = [ "lv_uuid","lv_name","lv_path","lv_attr","lv_major","lv_minor","lv_read_ahead",
            "lv_kernel_major","lv_kernel_minor","lv_kernel_read_ahead","lv_size","seg_count","origin",
            "origin_size","snap_percent","copy_percent","move_pv","convert_lv","lv_tags","mirror_log",
            "modules","segtype","stripes","stripesize","regionsize","chunksize",
            "seg_start","seg_start_pe","seg_size","seg_tags","seg_pe_ranges","devices"]
        optionsString = ",".join(self.attiribtes)
        cmd = 'lvs -o+%s --separator vmDiskLm' % (optionsString)
        self.logger.debug("Running command %s" % (cmd))
        (rc,output) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Failed "%s"' % (cmd))
            self.logger.error(output)
            self.logger.error('Return Code=%s' % (rc))
            sys.exit(1)
        if "" == output:
            self.logger.warning(' Cant mount The Disk "%s" has no partitons' % (self.path))
            return False
        rootStripLen = None
        newVolumesByPath = {}
        newVolumeGroups = {}
        CurrentGroup = None
        ouputLines = output.split("\n")
        ouputLinesLen = len(ouputLines)
        if ouputLinesLen == 0:
            self.logger.warning(' Cant mount The Disk "%s" has no partitons' % (self.path))
            return False
        Keys = ouputLines[0].split('vmDiskLm')
        #self.logger.debug( 'Keys=%s' % (Keys))
        lenKeys = len(Keys)
        foundlist = []
        for i in range(1,ouputLinesLen):
            line = ouputLines[i].split('vmDiskLm')
            lenline = len (line)
            dictionary = {}
            for j in range(0,lenKeys):
                #print i,j
                #print line[j]
                #dictionary[Keys[j]] = line[i][j]
                value = line[j]
                if len(value) == 0:
                    continue
                
                dictionary[Keys[j]] = line[j]
            foundlist.append(dictionary)
        #print foundlist
        logicalVolsByUUID = {}
        logicalVolsByPath = {}
        volumeGroups = set([])
        for item in foundlist:
            if item.has_key('LV UUID'):
               logicalVolsByUUID[item['LV UUID']] = item
            if item.has_key('Path'):
               logicalVolsByPath[item['Path']] = item
            if item.has_key('VG'):
                volumeGroups.add(item['VG'])
            
                
        self.logicalVolsByUUID = logicalVolsByUUID
        self.logicalVolsByPath = logicalVolsByPath
        self.volumeGroups = volumeGroups
        #print self.volumeGroups
        return True
    def getUUIDbyVolumeGroupLogicalVolume(self,VolumeGroup,LogicalVolume):
        for item in self.logicalVolsByUUID.keys():
            dictionary = self.logicalVolsByUUID[item]
            #print dictionary
            
            if not dictionary.has_key('LV'):
                continue
            if not dictionary.has_key('VG'):
                continue
            Volume = dictionary['LV']
            Group = dictionary['VG']
            if ((Volume == LogicalVolume) and (Group == VolumeGroup)):
                return item
                


class diskMounterLvm(diskMounterBaseClass):
    lvm = lvmControl()
    def __init__(self):
        diskMounterBaseClass.__init__(self)
        self.requireAtribs = set(['_lvmVolumeGroup','_target','_lvmVolume'])
        self.logger = logging.getLogger("vmimagemanager.diskMounterLvm") 
        self.HostRootSpace = None
        self.lvmProperties = None
    @Property
    def lvmVolumeGroup():
        doc = "The lvmVolumeGroup on the local file system of the diskImage"
        def fget(self):
            return self._lvmVolumeGroup

        def fset(self, lvmVolumeGroup):
            self._lvmVolumeGroup = lvmVolumeGroup
            if self._hasAtribs():
               self._loadpartitions()
        
        def fdel(self):
            del self._lvmVolumeGroup
        return locals()
        

    @Property
    def target():
        doc = "The target on the local file system of the diskImage"
        def fget(self):
            return self._target

        def fset(self, target):
            self._target = target
            if self._hasAtribs():
               self._loadpartitions()
        
        def fdel(self):
            del self._target
        return locals()


    @Property
    def lvmVolume():
        doc = "The lvmVolume on the local file system of the diskImage"
        def fget(self):
            return self._lvmVolume

        def fset(self, lvmVolume):
            #print 'ssssssssssssssssssssssssssssssssssssssss',lvmVolume
            self._lvmVolume = lvmVolume
            if self._hasAtribs():
               self._loadpartitions()
        
        def fdel(self):
            del self._lvmVolume
        return locals()

    @Property
    def path():
        doc = "The path on the local file system of the diskImage"
        def fget(self):
            return self._path

        def fset(self, path):
            self._path = path
            if self._hasAtribs():
               self._loadpartitions()
        
        def fdel(self):
            del self._path
        return locals()
   
        
    def _hasAtribs(self):
        knownvariables = self.__dict__.keys()
        if not self.requireAtribs.issubset(knownvariables):    
            return False
        
        for item in self.requireAtribs:
            if None == getattr(self,item):
                return False
        return True
    
    def _loadpartitions(self):
        if not self._hasAtribs():
            return False
        self.lvm.updateModel()
        self.uuid = self.lvm.getUUIDbyVolumeGroupLogicalVolume(self.lvmVolumeGroup,self.lvmVolume)
        HostRootSpace = None
        self.logger.debug("lvm uuid=%s" % self.uuid)
        if self.uuid != None:
            partition = self.lvm.logicalVolsByUUID[self.uuid]
            self.logger.debug(partition.has_key('Path'))
            if partition.has_key('Path'):
                HostRootSpace = partition['Path']
        self.HostRootSpace = HostRootSpace
        return True
        
                    
    def updateFromMtab(self,ByTarget,BySource):
        #self.log.debug("ByTarget=%s" % (ByTarget))
        #self.log.debug("BySource=%s" % (BySource))
        mounted =  True
        if not hasattr(self, 'target'):
            mounted = False
        if self.HostRootSpace == None:
            
            mounted = False
        
        if not self.target in ByTarget.keys():
            #print 'no match',ByTarget.keys(),self.target
            mounted = False
        if not self.HostRootSpace in BySource.keys():
            #print 'no match',self.HostRootSpace ,BySource.keys()
            mounted = False
        oldState = self.state.get()
        currentState = oldState
        #self.log.info("statechange=%s->%s" % (oldState,currentState))
        if ((currentState & 2) == 2) and (not mounted):
            currentState -= 2
        if ((currentState & 2) == 0) and (mounted):
            currentState += 2
        
        if currentState != oldState:
            self.log.debug("statechange=%s->%s" % (oldState,currentState))
            self.state.set(currentState)
        return currentState    
    
        
    def mount(self):
        if not self._hasAtribs():
            self.logger.debug( 'no atribs' )
            return False
        currentState = self.state.get()
        #print "mount:", currentState
        if ((currentState & 2) == 2):
            self.logger.info( 'mounted %s' % (self.target))
            return True
        self._loadpartitions()
        if self.HostRootSpace == None:
            self.logger.info( 'HostRootSpace %s' % (self.HostRootSpace))
            return False
        if not os.path.exists(self.HostRootSpace):
            self.logger.error('exists:%s' % (self.HostRootSpace))
        if not os.path.isdir(self.target):
            os.makedirs(self.target)
            self.logger.info( 'Made Directory %s' % (self.target))

        cmd="mount %s %s" % (self.HostRootSpace,self.target)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.debug( 'self=%s,self.HostRootSpace=%s,self.target=%s' % (self,self.HostRootSpace,self.target))
            self.logger.error('Command "%s" Failed' % (cmd))
            self.logger.error( 'rc=%s,output=%s' % (rc,cmdoutput))
            return False
        return True
    def release(self):
        if not self._hasAtribs():
            self.logger.debug("does not have required atribs.")
            return False
        
        self._loadpartitions()
        if self.HostRootSpace == None:
            self.logger.info( 'HostRootSpace is None')
            return False
        if not os.path.exists(self.HostRootSpace):
            self.logger.error( 'HostRootSpace does not exist %s' % (self.HostRootSpace))
            return False
        if not os.path.isdir(self.target):
            os.makedirs(self.target)
            self.logger.info( 'Made Directory %s' % (self.target))
        
        cmd="umount %s" % (self.HostRootSpace)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Command "%s" Failed' % (cmd))
            self.logger.error('rc=%s,output=%s' % (rc,cmdoutput))
            self.logger.error('shoudl set statue unknown')
            return True
        self.logger.debug('umount Ok')
        return
    def _clearImplRm(self):
        if hasattr(self, 'formatstring'):
            return self.format()
        mountedOk = self.mount()
        if not mountedOk:
            self.logger.error('Could not Mount the fiel system to clear it.')
            return False
        
        cmd = "rm -rf %s/*" % (self.target)
        self.logger.debug('cmd=%s' % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.debug( 'self=%s,self.HostRootSpace=%s,self.target=%s' % (self,self.HostRootSpace,self.target))
            self.logger.error('Command "%s" Failed' % (cmd))
            self.logger.error( 'rc=%s,output=%s' % (rc,cmdoutput))
            return False
        
        self.logger.debug('rm Ok')
        return True
    def clear(self):
        if hasattr(self, 'formatString'):
            return self.format()
        return self._clearImplRm()






