
from observable import Observable
import types

import logging

from vmstoreTgz import vmStoreTgz
from vmStoreRsync import vmStoreRsync
from vmStoreCpiobz import vmStoreCpiobz
def Property(func):
    return property(**func())


diskTypes = { "tgz" : vmStoreTgz ,
    'rsync' : vmStoreRsync,
    'cpio.bz2' : vmStoreCpiobz}



class vmStoreFacade(object):
    """Facade class for mulitple implementations of diskhandling,
    Should be robust for setting the impleemntation or attributes
    in any order."""
    def __init__(self):
        pass

    @Property
    def storeFormat():
        doc = "storeFormat type"

        def fget(self):
            return self._uploaderImp

        def fset(self, storeFormat):
            self._storeFormat = storeFormat
            if storeFormat in diskTypes.keys():
                self._uploaderImp = diskTypes[storeFormat]()
            else:
                if hasattr(self, '_uploaderImp'):
                    del(self._uploaderImp)
            if hasattr(self, '_uploaderImp'):
                self._uploaderImp.storePath = self._storePath
                
        def fdel(self):
            del self._uploaderImp
        return locals()
    @Property
    def storePath():
        doc = "The shared partition to be mounted"
        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'partition'):
                        return self._uploaderImp.storePath
                    else:
                        return None
                
            return self._storePath

        def fset(self, storePath):
            self._storePath = storePath
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.storePath = storePath
        def fdel(self):
            del self._storePath
        return locals()
    
    
    def imageStore(self,diskFacade,storeName):
        if hasattr(self, '_uploaderImp'):
            return self._uploaderImp.imageStore(diskFacade,storeName)

    def imageRestore(self,diskFacade,storeName):
        if hasattr(self, '_uploaderImp'):
            return self._uploaderImp.imageRestore(diskFacade,storeName)
    
    def insertRestore(self,diskFacade,storeName):
        if hasattr(self, '_uploaderImp'):        
            return self._uploaderImp.insertRestore(diskFacade,storeName)
        else:
            return None
            
    def imageList(self):
        if hasattr(self, '_uploaderImp'):
            return self._uploaderImp.imageList()
    
    
if __name__ == "__main__" :
    import time
    import sys
    from vmDisk import diskFacade
    logging.basicConfig(level=logging.DEBUG)
    
    df = diskFacade()
    
    
    df.disk = 'kpartx'
    df.path = '/var/lib/libvirt/images/lenny.img'
    
    df.target = "/tmp/foo"
    df.partitionNo = 1
    df.readMtab()
    
    sf = vmStoreFacade()
    
    sf.storeFormat = 'cpio.bz2'
    sf.storePath = '/server/store'
    sf.imageStore(df,'fred.cpio.bz2')
    df.readMtab()
    sf.imageRestore(df,'fred.cpio.bz2')
    df.readMtab()
    df.release()
    #sys.exit(1)
    
    
    sf.storeFormat = 'rsync'
    sf.storePath = '/server/store'
    print sf.imageList()
    df.mount()
    print sf.imageStore(df,'fred.rsync')
    df.readMtab()
    print sf.imageRestore(df,'fred.rsync')
    df.readMtab()
    df.release()
    
    sf.storeFormat = 'tgz'
    sf.storePath = '/server/store'
   
    
    print sf.imageList()
    df.mount()
    
    print sf.imageStore(df,'fred.tgz')
    df.readMtab()
    print sf.imageRestore(df,'fred.tgz')
    df.readMtab()
    df.release()
