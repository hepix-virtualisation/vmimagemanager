import logging, logging.config
from observable import GenKey, Observable, ObservableDict


import ConfigParser

from clibvirt import vmMdl, vhostMdl, LibVirtCnt, LibVirtConnection

from ConfigModel import vmModel , CfgModel

from ConfigFileView import ConfigFile1

import os

from vmStoreControl import StorageControler

from archiveControler import archControler

class vmState(object):
    actionsReqBoxes = set(['up','down','store','restore','extract','insert','kill','mount','release'])
    actionsReqStats = set(['list_images','list_boxes'])
    def __init__(self,libVirtControler,cfgModel,StorageCntl,archiveStore):
        self.libVirtControler = libVirtControler
        self.cfgModel = cfgModel
        self.StorageCntl = StorageCntl
        self.diskModelByHostName = {}
        self.archiveStore = archiveStore
        self.log = logging.getLogger("vmCtrl.vmState") 
    def _processAction(self,instructions,hostInfo,action):
        self.updateDiskModelByHostName()
        inputs = vmMdl()
        keys = hostInfo.keys()
        #print action
        if len(keys) != 1:
            print "oooo noooo"
            return
        hostName = keys.pop()
        inputs.libvirtName.set(hostName)
        
        if action in ["kill"]:
            self.libVirtControler.Kill(inputs)
        if action in ["extract","insert","store","restore","down","mount"]:
            self.libVirtControler.vmStop(inputs)
        if action in ["extract","insert","store","restore","mount"]:
            self.StorageCntl.mount(hostName)
        if action in ["extract"]:
            for item in hostInfo[hostName]['storeExtract']:
                self.StorageCntl.extract(hostName,item['name'],item['directory'],hostInfo[hostName]['storeFormat'])
        if action in ["store"]:
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            self.StorageCntl.store(hostName,hostInfo[hostName]['storeName'])
            
        if action in ["restore"]:
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            self.StorageCntl.restore(hostName,hostInfo[hostName]['restoreName'])
            
        if action in ["insert"]:
            for item in hostInfo[hostName]['storeInsert']:
                self.StorageCntl.insert(hostName,item["name"],hostInfo[hostName]['storeFormat'])
        
        if action in ["release","up"]:
            self.StorageCntl.release(hostName)
        if action in ["up"]:
            self.libVirtControler.vmStart(inputs)
    def _processBoxesList(self):
        cfgBoxes = set(self.cfgModel.vmbyName.keys())
        livirtBoxes = set(self.libVirtControler.model.vmsbyName.keys())
        BoxesUnion = cfgBoxes.union(livirtBoxes)
        boxesOutput = {}
        for item in BoxesUnion:
            newBox = {'name': str(item)}
            if item in livirtBoxes:
                newBox['libvirt'] = 1
            else:
                newBox['libvirt'] = 0
            if item in cfgBoxes:
                newBox['disk'] = 1
            else:
                newBox['disk'] = 0
            boxesOutput[item] = newBox
        return {'listBox' : boxesOutput }
    def _processImageList(self):
        output = {'listImages' : self.archiveStore.catImagesOldFormat()}
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
        self.archiveStore = archControler(self.cfgModel)
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
        self.archiveStore.updateImages()
        self.ProcessState = vmState(self.libVirtControler,self.cfgModel,ting,self.archiveStore)
        output = {'vmControl' : self.ProcessState.process(instructions)}
        return output
        
    def ListBoxes(self):
        cfgBoxes = set(self.cfgModel.vmbyName.keys())
        livirtBoxes = set(self.libVirtModel.vmsbyName.keys())
        BoxesUnion = cfgBoxes.union(livirtBoxes)
        boxesOutput = {}
        for item in BoxesUnion:
            newBox = {'name': str(item)}
            if item in livirtBoxes:
                newBox['libvirt'] = 1
            else:
                newBox['libvirt'] = 0
            if item in cfgBoxes:
                newBox['disk'] = 1
            else:
                newBox['disk'] = 0
            boxesOutput[item] = newBox
        return boxesOutput
    
        
        
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
