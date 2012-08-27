import logging, logging.config
from observable import GenKey, Observable, ObservableDict

from vmDisk import diskFacade

import ConfigParser

from clibvirt import vmMdl, vhostMdl, LibVirtCnt, LibVirtConnection

from ConfigModel import vmModel , CfgModel

from ConfigFileView import ConfigFile1
            
from vmstorefacard import vmStoreFacade

import magic
import os

class StorageControler(object):
    def __init__(self,cfgModel):
        self.cfgModel = cfgModel
        self.diskFacardDict = {}
        self.Storage = vmStoreFacade()
        self.UpdateFromModel()
        self.log = logging.getLogger("vmCtrl.StorageControler") 
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
    def restore(self,hostname,storename):
        if not hostname in self.cfgModel.vmbyName.keys():
            self.log.warning("No configuration for '%s'" % (hostname))
            return
        self.UpdateFromModel()
        insertDir = self.cfgModel.vmbyName[hostname].CfgPathImages.get()
        path = os.path.join(insertDir,storename)
        hostDetails = diskFacade()
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        self.Storage.imageRestore(hostDetails,storename)    
    def release(self,hostname):
        if not hostname in self.cfgModel.vmbyName.keys():
            self.log.warning("No configuration for '%s'" % (hostname))
            return
        hostDetails = diskFacade()
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        hostDetails.release()
    def mount(self,hostname):
        if not hostname in self.cfgModel.vmbyName.keys():
            self.log.warning("No configuration for '%s'" % (hostname))
            return
        hostDetails = diskFacade()
        hostDetails.disk = self.cfgModel.vmbyName[hostname].CfgDiskType.get()
        hostDetails.path = self.cfgModel.vmbyName[hostname].CfgDiskImage.get()
        hostDetails.target = self.cfgModel.vmbyName[hostname].CfgMountPoint.get()
        hostDetails.partitionNo = self.cfgModel.vmbyName[hostname].CfgDiskImagePartition.get()
        hostDetails.mount()
    def insert(self,hostname,storename,storeformat):
        insertDir = self.cfgModel.vmbyName[hostname].CfgPathInserts.get()
        insertPath = os.path.join(insertDir,storename)
        if not os.path.isfile(insertPath):
            self.log.error("No such file '%s'" % insertPath)
            return
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        magicout = ms.file(insertPath)
        fileType = self.returnFiileType(magicout)
        if fileType != None:
            storeformat = fileType
        if not hostname in self.cfgModel.vmbyName.keys():
            self.log.warning("No configuration for '%s'" % (hostname))
            return
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
        if not hostname in self.cfgModel.vmbyName.keys():
            self.log.warning("No configuration for '%s'" % (hostname))
            return
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
    
    
    def returnFiileType(self,magicStr):
        cleanstring = str.strip(magicStr)
        splitString = dir(magicStr)
        splitLine = cleanstring.split(', ')
        if splitLine[0] == 'gzip compressed data':
            return "tgz"
        return None

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
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        
        for path in pthInfo.keys():
            if not os.path.isdir(path):
                continue
            for fileName in os.listdir(path):
                fileDetails = { 'Name' : fileName, 'Path' : path}
                fullPath = os.path.join(path,fileName)
                fileDetails['fullPath'] = fullPath
                if os.path.isdir(fullPath):
                    fileDetails["type"] = "rsync"
                elif os.path.isfile(fullPath):
                    magicout = ms.file(fullPath)
                    fileType = self.returnFiileType(magicout)
                    if fileType != None:
                        fileDetails["type"] = fileType
                output[fullPath] = fileDetails
        ms.close()
        return output


class vmState(object):
    actionsReqBoxes = set(['up','down','store','restore','extract','insert','kill','mount','release'])
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
