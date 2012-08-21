import logging, logging.config
from observable import GenKey, Observable, ObservableDict

from vmDisk import diskFacade

import ConfigParser

from clibvirt import vmMdl, vhostMdl, LibVirtCnt, LibVirtConnection

from ConfigModel import vmModel , CfgModel

from ConfigFileView import ConfigFile1
            
from vmstorefacard import vmStoreFacade


class StorageControler(object):
    def __init__(self,cfgModel):
        self.cfgModel = cfgModel
        self.diskFacardDict = {}
        self.Storage = vmStoreFacade()
        self.UpdateFromModel()
        
    def UpdateFromModel(self):
        self.Storage.storePath = self.cfgModel.defaultPathImages.get()
        itemsByName = self.cfgModel.vmbyName.keys()
        for item in itemsByName:
            if not item in self.diskFacardDict.keys():
                self.diskFacardDict[item] = diskFacade()
            
    def findByHostName(self,hostname): 
        matchset = self.diskFacardDict.keys()
        if hostname in matchset:
            return self.diskFacardDict[hostname]
        return None
    def store(self,hostname,storename):
        self.UpdateFromModel()
        hostDetails = diskFacade()
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        self.Storage.imageStore(hostDetails,storename)
        
    def release(self,hostname):
        hostDetails = diskFacade()
        print self.cfgModel.vmbyName[hostname]
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        hostDetails.release()

class vmState(object):
    def __init__(self,libVirtControler,cfgModel,StorageCntl):
        self.libVirtControler = libVirtControler
        self.cfgModel = cfgModel
        self.StorageCntl = StorageCntl
        self.diskModelByHostName = {}
    def _processAction(self,hostInfo,action):
        self.updateDiskModelByHostName()
        #print (hostInfo,action)
        inputs = vmMdl()
        keys = hostInfo.keys()
        #print keys
        if len(keys) != 1:
            print "oooo noooo"
            return
        hostName = keys.pop()
        inputs.libvirtName.set(hostName)
        if action in ["kill"]:
            self.libVirtControler.Kill(inputs)
        if action in ["extract","insert","store","restore","down"]:
            self.libVirtControler.vmStop(inputs)
        if action in ["extract"]:
            self.diskModelByHostName.Extract(inputs)
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            
        if action in ["store"]:
            print 'here', hostName , hostInfo
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            
            
            self.StorageCntl.store(hostName,hostInfo[hostName]['storeName'])
            
        if action in ["restore"]:
            self.diskModelByHostName.RestoreHost(inputs)
        if action in ["insert"]:
            self.diskModelByHostName.Insert()
        if action in ["extract","insert","store","restore","up"]:
            self.StorageCntl.release(hostName)
            self.libVirtControler.vmStart(inputs)
        
    def process(self,instructions):
        
        for host in instructions['hostdetails'].keys():
            for action in instructions['actions']:
                
                    self._processAction({ host :instructions['hostdetails'][host]},action)

    def updateDiskModelByHostName(self):
        self.libVirtControler.updateModel()
        self.HostsSetlibvirt = set(self.libVirtControler.model.vmsbyName.keys())
        self.HostsSetGfg = set(self.cfgModel.vmbyName.keys())
        
        
        chgSet = set(self.cfgModel.vmbyName.keys())
        setToAdded = set(self.cfgModel.vmbyName.keys())
        
        print "chgSet",        chgSet
       

class vmControl(object):
    def __init__(self):
        self.callbackKey = GenKey()
        self.log = logging.getLogger("vmStoreRsync.vmStoreRsync") 
        self.cfgModel = CfgModel()
        self.cfgModel.libvirtConStr.addCallback(self.callbackKey,self._onlibvirtConStr)
        self.libVirtModel = vhostMdl()

    def LoadConfigCfg(self,configfile):
        config = ConfigFile1(self.cfgModel)
        return config.upDateModel(configfile)

    def _onlibvirtConStr(self):
        connectionStr = self.cfgModel.libvirtConStr.get()
        if not isinstance( connectionStr, unicode ):
            print "asdaSDASD"
        self.libVirtControler = LibVirtCnt(connectionStr,self.libVirtModel)
        self.libVirtControler.updateModel()

    def Process(self,instructions):
        if not 'vmControl' in instructions.keys():
            return False
        ting = StorageControler(self.cfgModel)
        self.ProcessState = vmState(self.libVirtControler,self.cfgModel,ting)
        self.ProcessState.process(instructions['vmControl'])
        return True


if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    Control = vmControl()
    Control.LoadConfigCfg('vmimagemanager.cfg')
    
    
    print Control.cfgModel.vmbyName[u'hudson-slave-vm01.desy.de'].CfgMountPoint.get()
    
    
    
    instructions = { 'vmControl' : { 'actions' : ['release','up'],
        'hostdetails' : {
            'vmname' : { 'storeName' : 'vmControlTest' }
            },
     }
    }
    #Control.Process(instructions)
    instructions = { 'vmControl' : { 'actions' : ['down','store'],
        'format' : ['rsync'],
        'hostdetails' : {
            'vmname' : { 'storeName' : 'vmControlTest.cpio.bz2' ,
                'libVirtName' : 'vmname',
                'storeFormat' : 'cpio.bz',}
            },
     }
    }
    #Control.Process(instructions)
    instructions = { 'vmControl' : { 'actions' : ['down','store'],
        'format' : ['rsync'],
        'hostdetails' : {
            'vmname' : { 'storeName' : 'vmControlTest.rsync' ,
                'libVirtName' : 'vmname',
                'storeFormat' : 'rsync',}
            },
     }
    }
    Control.Process(instructions)
    print 'dfsdfsdf'
    instructions = { 'vmControl' : { 'actions' : ['down'],
        'hostdetails' : {
            'vmname' : { 'storeName' : 'vmControlTest' }
            },
     }
    }
    Control.Process(instructions)
