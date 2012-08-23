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
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        hostDetails.release()

    def insert(self,hostname,storename,storeformat):
        self.UpdateFromModel()
        foundHost = self.findByHostName(hostname)
        #print (hostname,storename,storeformat,self.cfgModel.vmbyName[hostname].CfgPathInserts.get())
        hostDetails = diskFacade()
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        self.Storage.storeFormat = storeformat
        self.Storage.storePath = self.cfgModel.vmbyName[hostname].CfgPathInserts.get()
        self.Storage.insertRestore(hostDetails,storename)
    def extract(self,hostname,storename,directory,storeformat):
        
        self.UpdateFromModel()
        foundHost = self.findByHostName(hostname)
        #print (hostname,storename,storeformat,self.cfgModel.vmbyName[hostname].CfgPathInserts.get())
        hostDetails = diskFacade()
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        self.Storage.storeFormat = storeformat
        self.Storage.storePath = self.cfgModel.vmbyName[hostname].CfgPathInserts.get()
        self.Storage.insertStore(hostDetails,storename,directory)


    def listImages(self):
        output = {}
        availablepaths = set()
        pthInfo = {}
        allHosts = self.cfgModel.vmbyName.keys()
        if len(allHosts) == 0:
            availablepaths.add(self.cfgModel.defaultPathImages.get())
            pthInfo[self.cfgModel.defaultPathImages.get()] = []
        for host in allHosts:
            availablepaths.add(self.cfgModel.vmbyName[host].CfgPathImages.get())
            pth = self.cfgModel.vmbyName[host].CfgPathImages.get()
            if not pth in pthInfo.keys():
                pthInfo[pth] = { 'hosts' : [], 'images' : {}}
            pthInfo[pth]['hosts'].append(host)
        pathImages = {}
        StoreFacade = vmStoreFacade()
        for path in pthInfo.keys():
            StoreFacade.storePath = path
            for format in ["rsync",'cpio.bz2',"tgz"]:
                StoreFacade.storeFormat = format
                foundImages = StoreFacade.imageList()
                pthInfo[pth]['images'][format] = foundImages
        return pthInfo


class vmState(object):
    actionsReqBoxes = set(['up','down','store','restore','extract','insert','kill'])
    actionsReqStats = set(['list_images','list_boxes'])
    def __init__(self,libVirtControler,cfgModel,StorageCntl):
        self.libVirtControler = libVirtControler
        self.cfgModel = cfgModel
        self.StorageCntl = StorageCntl
        self.diskModelByHostName = {}
        self.log = logging.getLogger("vmCtrl.vmState") 
    def _processAction(self,instructions,hostInfo,action):
        self.updateDiskModelByHostName()
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
            for item in hostInfo[hostName]['storeExtract']:
                self.StorageCntl.extract(hostName,item['name'],item['directory'],hostInfo[hostName]['storeFormat'])
        if action in ["store"]:
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            self.StorageCntl.store(hostName,hostInfo[hostName]['storeName'])
            
        if action in ["restore"]:
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            self.StorageCntl.restore(hostName,hostInfo[hostName]['storeName'])
            
        if action in ["insert"]:
            self.StorageCntl.insert(hostName,hostInfo[hostName]['storeInsert'],hostInfo[hostName]['storeFormat'])
        if action in ["up"]:
            self.StorageCntl.release(hostName)
            self.libVirtControler.vmStart(inputs)
    def _processBoxesList(self):
        output = {}
        for item in self.libVirtControler.model.vmsbyName.keys():
            output[item] = {'libVirtName' : item}
        return {'listBox' : output }
    def _processImageList(self):
        output = {'listImages' : self.StorageCntl.listImages()}
        
        return output
        
        
    def process(self,instructions):
        #print instructions
        reqStats = self.actionsReqStats.intersection(instructions['vmControl']['actions'])
        lenReqStats = len(reqStats)
        if lenReqStats > 0:
            #print "reqStats",reqStats
            if 'list_boxes' in reqStats:
                return self._processBoxesList()
            if 'list_images' in reqStats:
                return self._processImageList()
        reqBoxes = self.actionsReqBoxes.intersection(instructions['vmControl']['actions'])
        lenReqBoxes = len(reqBoxes)
        #print "ssss",reqBoxes,instructions
        if lenReqBoxes > 0:
            output = {}
            instructionsKeys = instructions.keys()
            if not  'hostdetails' in instructionsKeys:
                self.log.info("No hostdetails")
                return 
            
            for host in instructions['hostdetails'].keys():
                for action in instructions['vmControl']['actions']:
                    self._processAction(instructions,{ host :instructions['hostdetails'][host]},action)
        return True
    def updateDiskModelByHostName(self):
        self.libVirtControler.updateModel()
        self.HostsSetlibvirt = set(self.libVirtControler.model.vmsbyName.keys())
        self.HostsSetGfg = set(self.cfgModel.vmbyName.keys())
        
        
        chgSet = set(self.cfgModel.vmbyName.keys())
        setToAdded = set(self.cfgModel.vmbyName.keys())
        
        #print "chgSet",        chgSet
       

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
        if not isinstance( instructions, dict ):
            return None
        if not 'vmControl' in instructions.keys():
            return None
        ting = StorageControler(self.cfgModel)
        self.ProcessState = vmState(self.libVirtControler,self.cfgModel,ting)
        return {'vmControl' : self.ProcessState.process(instructions)}
        


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
                'storeFormat' : 'cpio.bz2',}
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
    instructions = {'vmControl': {'actions': ['list_images'],
        'hostdetails': {},
        }
    }
    instructions = {'vmControl': {'actions': ['list_boxes'],
        'hostdetails': {},
        }
    }
    print Control.Process(instructions)
