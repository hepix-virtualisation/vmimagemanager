import logging, logging.config
from observable import GenKey, Observable, ObservableDict

from vmDisk import diskFacade

import ConfigParser

from clibvirt import vmMdl, vhostMdl, LibVirtCnt, LibVirtConnection

from ConfigModel import vmModel , mainModel

from ConfigFileView import ConfigFile1
            
import vmstorefacard

class vmStoreManager(object):
    def __init__(self,cfgModel):
        self.cfgModel = cfgModel
        


class vmState(object):
    def __init__(self,libVirtControler,cfgModel):
        self.libVirtControler = libVirtControler
        self.cfgModel = cfgModel
        self.ActionMappings = {'release' : self.actionRelease}
        self.diskModelByHostName = {}
    def _processAction(self,host,action):
        self.updateDiskModelByHostName()
        print (host,action)
        inputs = vmMdl()
        inputs.libvirtName.set(host)
        if action in ["kill"]:
            self.libVirtControler.Kill(inputs)
        if action in ["extract","insert","store","restore","down"]:
            self.libVirtControler.vmStop(inputs)
        if action in ["extract"]:
            self.diskModelByHostName.Extract(inputs)
        if action in ["store"]:
            print 'here',self.cfgModel
            df = diskFacade()
            df.disk = 'kpartx'
            df.path = '/var/lib/libvirt/images/lenny.img'

            df.target = "/tmp/foo"
            df.partitionNo = 1
            df.readMtab()
            sf.imageStore(df,'fred.rsync')
            df.readMtab()
            sf = vmStoreFacade()
            #self.diskModelByHostName.StoreHost(inputs)
        if action in ["restore"]:
            self.diskModelByHostName.RestoreHost(inputs)
        if action in ["insert"]:
            self.diskModelByHostName.Insert()
        if action in ["extract","insert","store","restore","up"]:
            self.libVirtControler.vmStart(inputs)
        
    def process(self,instructions):
        
        for host in instructions['hostdetails']:
            for action in instructions['actions']:
                
                    self._processAction(instructions['hostdetails'][host],action)

    def updateDiskModelByHostName(self):
        self.libVirtControler.updateModel()
        self.HostsSetlibvirt = set(self.libVirtControler.model.vmsbyName.keys())
        self.HostsSetlibvirt = set(self.cfgModel.vmbyName.keys())
        
        
        chgSet = set(self.cfgModel.vmbyName.keys())
        setToAdded = set(self.cfgModel.vmbyName.keys())
        
        print "chgSet",        chgSet
    def actionRelease(self,host):
        self.updateDiskModelByHostName()
        print host
        print self.diskModelByHostName   
            

class vmControl(object):
    def __init__(self):
        self.callbackKey = GenKey()
        self.log = logging.getLogger("vmStoreRsync.vmStoreRsync") 
        self.cfgModel = mainModel()
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
        self.ProcessState = vmState(self.libVirtControler,self.cfgModel)
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
    Control.Process(instructions)
    instructions = { 'vmControl' : { 'actions' : ['down','store'],
        'format' : ['rsync'],
        'hostdetails' : {
            'vmname' : { 'storeName' : 'vmControlTest' }
            },
     }
    }
    Control.Process(instructions)
