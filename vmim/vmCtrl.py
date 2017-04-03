import logging
from observable import GenKey
from clibvirt import vmMdl, vhostMdl, LibVirtCnt
from ConfigModel import CfgModel
from ConfigFileView import ConfigFile1
from vmStoreControl import StorageControler
from archiveControler import archControler

log = logging.getLogger(__name__)

class vmState(object):
    actionsReqBoxes = set(['up','down','store','restore','extract','insert','kill','mount','release'])
    actionsReqStats = set(['list_images','list_boxes','list_inserts'])
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
        #self.log.debug("input=%s" % (instructions))
        if len(keys) != 1:
            log.error("No key found")
            return
        hostName = keys.pop()
        inputs.libvirtName.set(hostName)
        if len(action.intersection(["kill"])) > 0:
            self.libVirtControler.Kill(inputs)
        if len(action.intersection(["extract","insert","store","restore","down","mount"])) > 0:
            self.libVirtControler.vmStop(inputs)
        if len(action.intersection(["extract","insert","store","restore","mount"])) > 0:
            self.StorageCntl.mount(hostName)
        if len(action.intersection(["extract"])) > 0:
            for item in hostInfo[hostName]['storeExtract']:
                self.StorageCntl.extract(hostName,item['name'],item['directory'],hostInfo[hostName]['storeFormat'])
        if len(action.intersection(["store"])) > 0:
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            self.StorageCntl.store(hostName,hostInfo[hostName]['storeName'])
            
        if len(action.intersection(["restore"])) > 0:
            self.StorageCntl.Storage.storeFormat = hostInfo[hostName]['storeFormat']
            self.archiveStore.updateImages()
            imagedetails = self.archiveStore.getImageMdl(hostName,hostInfo[hostName]['restoreName'])
            if imagedetails == None:
                self.log.error("Image not found")
                return
            else:
                fileFormat = imagedetails.Format.get()
                self.StorageCntl.restore(hostName,hostInfo[hostName]['restoreName'],fileFormat)
            
        if len(action.intersection(["insert"])) > 0:
            for item in hostInfo[hostName]['storeInsert']:
                self.archiveStore.updateImages()
                imagedetails = self.archiveStore.getInsertsMdl(hostName,item['name'])
                if imagedetails == None:
                    self.log.error("Image not found:%s",item['name'])
                    return
                else:
                    fileFormat = imagedetails.Format.get()
                    self.StorageCntl.insert(hostName,item['name'],fileFormat)
        
        if len(action.intersection(["release","up"])) > 0:
            self.StorageCntl.release(hostName)
        if len(action.intersection(["up"])) > 0:
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
       
        
    def process(self,instructions):
        reqStats = self.actionsReqStats.intersection(instructions['vmControl']['actions'])
        lenReqStats = len(reqStats)
        if lenReqStats > 0:
            #print "reqStats",reqStats
            if 'list_boxes' in reqStats:            
                return self._processBoxesList()
            if 'list_images' in reqStats:
                self.archiveStore.updateImages()
                return {'listImages' : self.archiveStore.catImages()}
            if 'list_inserts' in reqStats:
                self.archiveStore.updateOverlay()
                return {'listOverlays' : self.archiveStore.catInserts()}
            
        reqBoxes = self.actionsReqBoxes.intersection(instructions['vmControl']['actions'])
        lenReqBoxes = len(reqBoxes)
        if lenReqBoxes > 0:
            output = {}
            instructionsKeys = instructions.keys()
            if not  'hostdetails' in instructionsKeys:
                self.log.info("No hostdetails")
                return 
            
            for host in instructions['hostdetails'].keys():
                actions = set(instructions['vmControl']['actions'])
                if len(actions) > 0:
                    self._processAction(instructions,{ host :instructions['hostdetails'][host]},actions)
                else:
                    self.log.error("No actions specified.")
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
        self.config = ConfigFile1(self.cfgModel)
        return self.config.upDateModel(configfile)

    def _onlibvirtConStr(self):
        connectionStr = self.cfgModel.libvirtConStr.get()
        self.libVirtControler = LibVirtCnt(connectionStr,self.libVirtModel)
        self.libVirtControler.updateModel()

    def Process(self,instructions):
        if not isinstance( instructions, dict ):
            return None
        if not 'vmControl' in instructions.keys():
            return None
        ting = StorageControler(self.cfgModel)
        
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
    
    
    print (Control.cfgModel.vmbyName[u'hudson-slave-vm01.desy.de'].CfgMountPoint.get())
    
    
    
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
    print (Control.Process(instructions))
