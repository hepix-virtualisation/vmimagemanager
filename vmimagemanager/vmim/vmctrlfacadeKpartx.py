from diskMounterAbstract import diskMounterBaseClass
import os
import logging, logging.config
import commands
import sys

import string

def Property(func):
    return property(**func())



class diskMounterKpartX(diskMounterBaseClass):
    def __init__(self):
        diskMounterBaseClass.__init__(self)
        self.requireAtribs = set(['_target','_partitionNo','_path'])
        self.logger = logging.getLogger("vmimagemanager.diskMounterKpartX") 
        self.HostRootSpace = None
        
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
    def partitionNo():
        doc = "The partitionNo on the local file system of the diskImage"
        def fget(self):
            return self._partitionNo

        def fset(self, partitionNo):
            #print 'ssssssssssssssssssssssssssssssssssssssss',partitionNo
            self._partitionNo = partitionNo
            if self._hasAtribs():
               self._loadpartitions()
        
        def fdel(self):
            del self._partitionNo
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
    def _parseKpartxOutput(self,output):
        if "" == output:
            self.logger.warning(' Cant mount The Disk "%s" has no partitons' % (self.path))
            return False
        
        rootStripLen = None
        DiskPartitionD = []
        
        for PartitionLine in output.split("\n"):
            
            
                
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
                parsedInfo = PartitionLineSplit[0][(rootStripLen):]
                #self.logger.debug("parsedInfo=%s,%s,%s" % (parsedInfo,rootStripLen,PartitionLineSplit[0]))
                try:
                    Partition['Number'] = int(parsedInfo)
                except:
                    continue
                
                #self.logger.debug("Partition=%s" % (Partition))
                DiskPartitionD.append(Partition)
        
        correct = None
        #self.logger.debug("DiskPartitionD=%s" % (DiskPartitionD))
        for item in DiskPartitionD:
            if int(item['Number']) == self.partitionNo:    
                correct = item
        if correct == None:
            partitionList = []
            self.logger.error('Partiton  "%s" does not exist.' % (self.partitionNo))
            for item in DiskPartitionD:
                self.logger.info( "Partion %s exists" % (item['Number']))
            self.logger.debug("")
            return False
        
        self.HostRootSpace = os.path.join("/dev/mapper",correct['Path'])
        return True
    def _loadpartitions(self):
        if not self._hasAtribs():
            return False
        cmd = 'kpartx -p vmim -lv %s' % (self.path)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Failed "%s"' % (cmd))
            self.logger.error(cmdoutput)
            self.logger.error('Return Code=%s' % (rc))
            sys.exit(1)
        rc = self._parseKpartxOutput(cmdoutput)
        self.mounted.mounted(self.HostRootSpace,self.target)
        return rc
    
    
    def _partitionsOpen(self):
        if not self._hasAtribs():
            return False
        cmd = 'kpartx -p vmim -av %s' % (self.path)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Failed "%s"' % (cmd))
            self.logger.error(cmdoutput)
            self.logger.error('Return Code=%s' % (rc))
            sys.exit(1)
            
        return self._loadpartitions()
                    
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
            return False
        currentState = self.state.get()
        #print "mount:", currentState
        if ((currentState & 2) == 2):
            return True
            
        if self.HostRootSpace == None:
            self._loadpartitions()
        
        if self.HostRootSpace == None:
            return False
        if not os.path.exists(self.HostRootSpace):
            print 'danger',self.HostRootSpace
        if not os.path.isdir(self.target):
            os.makedirs(self.target)
            self.logger.info( 'Made Directory %s' % (self.target))
        
        self._partitionsOpen()
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
        currentState = self.state.get()
        if ((currentState & 2) == 0):
            return True
        cmd="umount %s" % (self.HostRootSpace)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Command "%s" Failed' % (cmd))
            self.logger.error('rc=%s,output=%s' % (rc,cmdoutput))
            self.logger.error('shoudl set statue unknown')
            return True
        self.logger.debug('umount Ok')
        
        
        cmd = 'kpartx -p vmim -d %s' % ( self.HostRootSpace)
        self.logger.debug("Running command %s" % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.logger.error('Failed "%s"' % (cmd))
            self.logger.error(cmdoutput)
            self.logger.error('Return Code=%s' % (rc))
            self.logger.error('shoudl set statue unknown')
            return
        self.logger.debug('kpartx Ok')
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
