from observable import Observable, ObservableDict
import logging, logging.config
import os.path

class mountedModel(object):
    def __init__(self):
        
        self.ByTarget = ObservableDict()
        self.BySource = ObservableDict()
        
    def _readMtabLine(self,line):
        stripedLine = line.strip()
        splitLine = stripedLine.split(' ')
        lenSplitLine = len (splitLine)
        if lenSplitLine < 3:
            return None
        Source = splitLine[0]
        Target = splitLine[1]
        FileSystem = splitLine[2]
        info = { 'Source' : Source,
            'Target' : Target,
            'FileSystem' : FileSystem}
        return info
        
        
    def readMtab(self):
        fp = open('/etc/mtab')
        ByTarget = {}
        BySource = {}
        for line in fp:
            result = self._readMtabLine(line)
            if result == None:
                continue
            ByTarget[result['Target']] = result
            BySource[result['Source']] = result
        # Shoudl handle updating here
        self.ByTarget.update(ByTarget)
        self.BySource.update(BySource)
        
    def mounted(self,HostRootSpace,target):
        self.readMtab()
        targetKeys = set(self.ByTarget.keys())
        sourceKeys = set(self.BySource.keys())
        if not target in self.ByTarget.keys():
            return False
        if not HostRootSpace in self.BySource.keys():
            return False
        return True
        
class diskMounterBaseClass(object):
    mounted = mountedModel()
    def __init__(self):
        self.log = logging.getLogger("vmDiskAbstract.diskMounterBaseClass") 
        # 1 Unknown
        # 2 Mounted (is it mounted)
        # 4 Released
        # 8 Can be mounted
        # 16 and higher are implementation specific
        self.state = Observable(0)
        
    def updateFromMtab(self,ByTarget,BySource):
        #self.log.debug("ByTarget=%s" % (ByTarget))
        #self.log.debug("BySource=%s" % (BySource))
        mounted =  True
        if not hasattr(self, 'target'):
            mounted = False
        if not self.target in ByTarget.keys():
            self.debug('no match',ByTarget.keys(),self.target)
            mounted = False
        oldState = self.state.get()
        currentState = oldState
        #self.log.info("statechange=%s->%s" % (oldState,currentState))
        if ((currentState & 2) == 2) and (not mounted):
            currentState -= 2
        if ((currentState & 2) == 0) and (mounted):
            currentState += 2
        
        if currentState != oldState:
            #self.log.info("statechange=%s->%s" % (oldState,currentState))
            self.state.set(currentState)
        return currentState
        
        
    def mount(self):
        currentState = self.state.get()
        if ((currentState & 2) == 2):
            return currentState
        if ((currentState & 2) == 0):
            currentState += 2
            self.state.set(currentState)
        return currentState
    def release(self):
        currentState = self.state.get()
        if ((currentState & 2) == 0):
            return currentState
        if ((currentState & 2) == 2):
            currentState -= 2
            self.state.set(currentState)
        return currentState
