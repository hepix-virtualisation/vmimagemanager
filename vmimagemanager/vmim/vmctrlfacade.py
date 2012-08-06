from observable import Observable
from diskMounterAbstract import diskMounterBaseClass
from vmctrlfacadeKpartx import diskMounterKpartX
import types

import logging



def Property(func):
    return property(**func())






class diskFacade(object):
    """Facade class for mulitple implementations of diskhandling,
    Should be robust for setting the impleemntation or attributes
    in any order."""
    def __init__(self):
        self._uploaderImp = None

    @Property
    def disk():
        doc = "diskFacade type"

        def fget(self):
            return self._diskName

        def fset(self, name):
            self._diskName = name
            if name == "kpartx":
                self._uploaderImp = diskMounterKpartX()
            else:
                del(self._uploaderImp)
            if hasattr(self, '_uploaderImp'):
                self._uploaderImp.path = self.path
                self._uploaderImp.partition = self.partition
        def fdel(self):
            del self._diskName
        return locals()
    @Property
    def target():
        doc = "The target where the file system is to be mounted"

        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'target'):
                        return self._uploaderImp.target
                    else:
                        return None
                
            return self._target

        def fset(self, target):
            self._target = target
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.target = target
        def fdel(self):
            del self._target
        return locals()

    @Property
    def path():
        doc = "The path on the local file system of the diskImage"

        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'path'):
                        return self._uploaderImp.path
                    else:
                        return None
                
            return self._path

        def fset(self, path):
            self._path = path
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.path = path
        def fdel(self):
            del self._path
        return locals()

    @Property
    def partition():
        doc = "The shared partition to be mounted"
        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'partition'):
                        return self._uploaderImp.partition
                    else:
                        return None
                
            return self._partition

        def fset(self, partition):
            self._partition = partition
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.partition = partition
        def fdel(self):
            del self._partition
        return locals()
    
    @Property
    def partitionNo():
        doc = "The partitionNo on the file system to be mounted"

        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'partitionNo'):
                        return self._uploaderImp.partitionNo
                    else:
                        return None
                
            return self._partitionNo

        def fset(self, partitionNo):
            self._partitionNo = partitionNo
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.partitionNo = partitionNo
        def fdel(self):
            del self._partitionNo
        return locals()
    

    def __init__(self) :
        pass
    
    def mount(self):
        self.readMtab()
        if hasattr(self, '_uploaderImp'):
            rc = self._uploaderImp.mount()
            self.readMtab()
            return rc

    def release(self):
        self.readMtab()
        if hasattr(self, '_uploaderImp'):
            rc = self._uploaderImp.release()
            self.readMtab()
            return rc

    def clear(self):
        self.readMtab()
        if hasattr(self, '_uploaderImp'):
            rc = self._uploaderImp.clear()
            self.readMtab()
            return rc
    
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
        if hasattr(self, '_uploaderImp'):
            self._uploaderImp.updateFromMtab(ByTarget,BySource)
if __name__ == "__main__" :
    import time
    logging.basicConfig(level=logging.DEBUG)
    df = diskFacade()
    df.disk = 'kpartx'
    df.path = '/var/lib/libvirt/images/lenny.img'
    df.target = "/tmp/foo"
    df.partitionNo = 1
    #print df.partitionNo
    
    df.mount()
    # Backgroun processes occure in the kernel, to make linux more useable,
    # Unfortunatly this means that 
    time.sleep(1) 
    df.release()
