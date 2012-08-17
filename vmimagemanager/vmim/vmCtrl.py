import logging, logging.config
from observable import GenKey, Observable, ObservableDict



import ConfigParser

from clibvirt import vmMdl, vhostMdl, LibVirtCnt, LibVirtConnection

from ConfigModel import vmModel , mainModel

from ConfigFileView import ConfigFile1
            

class vmState(object):
    def __init__(self,libVirtControler,cfgModel):
        self.libVirtControler = libVirtControler
        self.cfgModel = cfgModel
    def wibble(self):
        print 'dddd'

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
        ProcessState = vmState(self.libVirtControler,self.cfgModel)
        return True


if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    Control = vmControl()
    Control.LoadConfigCfg('vmimagemanager.cfg')
    print Control.cfgModel.vmbyName[u'hudson-slave-vm01.desy.de'].CfgMountPoint.get()
    instructions = { 'vmControl' : { 'actions' : ['release','up'],
        'hosts' : ['vmname'],
     }
    }
    Control.Process(instructions)
