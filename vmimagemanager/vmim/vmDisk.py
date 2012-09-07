from observable import Observable
from vmDiskAbstract import diskMounterBaseClass
from vmDiskKpartx import diskMounterKpartX
from vmDiskLvm import diskMounterLvm
import types

import logging



def Property(func):
    return property(**func())





class diskFacade(object):
    """Facade class for mulitple implementations of diskhandling,
    Should be robust for setting the impleemntation or attributes
    in any order."""
    def __init__(self):
        self._target = None
        self._path = None
        
    @Property
    def disk():
        doc = "diskFacade type"

        def fget(self):
            return self._diskName

        def fset(self, name):
            self._diskName = name
            if name == "kpartx":
                self._uploaderImp = diskMounterKpartX()
            elif name == "lvm":
                self._uploaderImp = diskMounterLvm()
            else:
	    	if hasattr(self, '_uploaderImp'):
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

    @Property
    def lvmVolume():
        doc = "The LvmRaw on the file system to be mounted"
        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'lvmVolume'):
                        return self._uploaderImp.lvmVolume
                    else:
                        return None
            return self._lvmVolume

        def fset(self, lvmVolume):
            self._lvmVolume = lvmVolume
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.lvmVolume = lvmVolume
        def fdel(self):
            del self._lvmVolume
        return locals()
    
    @Property
    def lvmSnapShot():
        doc = "The lvmSnapShot on the file system to be mounted"
        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'lvmSnapShot'):
                        return self._uploaderImp.lvmSnapShot
                    else:
                        return None
            return self._lvmSnapShot

        def fset(self, lvmSnapShot):
            self._lvmSnapShot = lvmSnapShot
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.lvmSnapShot = lvmSnapShot
        def fdel(self):
            del self._lvmSnapShot
        return locals()
        
    @Property
    def lvmVolumeGroup():
        doc = "The LVM Volume Group that we are using."
        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'lvmVolumeGroup'):
                        return self._uploaderImp.lvmVolumeGroup
                    else:
                        return None
            return self._lvmVolumeGroup

        def fset(self, lvmVolumeGroup):
            self._lvmVolumeGroup = lvmVolumeGroup
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.lvmVolumeGroup = lvmVolumeGroup
        def fdel(self):
            del self._lvmVolumeGroup
        return locals()

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
    #df.disk = 'kpartx'
    #df.path = '/var/lib/libvirt/images/lenny.img'
    #df.target = "/tmp/foo"
    #df.partitionNo = 1
    
    #print df.partitionNo
    df = diskFacade()
    df.disk = 'lvm'
    df.lvmVolumeGroup = 'fusion'
    df.lvmVolume = 'first'
    df.target = "/mnt/first"
    
    df.mount()
    # Backgroun processes occure in the kernel, to make linux more useable,
    # Unfortunatly this means that 
    time.sleep(1) 
    df.release()
