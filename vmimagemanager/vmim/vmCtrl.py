import logging, logging.config
# I shoudl make my own GenKeyFunction Later
from observable import GenKey, Observable, ObservableDict
import ConfigParser, os

import ConfigParser

import sys

if float(sys.version[:3]) >= 2.6:
    import json
else:
    # python 2.4 or 2.5 can also import simplejson
    # as working alternative to the json included.
    import simplejson as json

class jsonConfigParser(ConfigParser.SafeConfigParser):
    def __init__(self):
        self.log = logging.getLogger("vmCtrl.jsonConfigParser")
        ConfigParser.SafeConfigParser.__init__(self)
    def getJson(self,section,option):
        value = self.get(section,option)
        try:
            return json.loads(value)
        except ValueError:
            self.log.warning("Could not parse value from section '%s' and key '%s'" % (SectionVm,option))
            return None


class vmModel(object):
    def __init__(self):
        self.CfgHostName = Observable(None)
        self.CfgRoot = Observable(None)
        self.CfgSwap = Observable(None)
        self.CfgMountPoint = Observable(None)
        self.CfgMac = Observable(None)
        self.CfgDiskImage = Observable(None)
        self.CfgDiskImagePartition = Observable(None)

class mainModel(object):
    def __init__(self):
        self.callbackKey = GenKey()
        self.libvirtConStr = Observable(None)
        self.libvirtConStr.addCallback(self.callbackKey,self._onlibvirtConStr)

        self.defaultPathExtracts = Observable(None)
        self.defaultPathImages = Observable(None)
        self.defaultPathMount = Observable(None)
        self.vmbyName = ObservableDict()
        
    def _onlibvirtConStr(self):
        print "onlibvirtConStr"






class ConfigFile1(object):
    def __init__(self,model):
        self.model = model
        self.log = logging.getLogger("vmCtrl.ConfigFile1")
    
    

    def upDateModel(self,configfile):
        def _selectBestKeyFor(selections,availableKeys):
            for item in selections:
                if item in availableKeys:
                    return item
            return None
        def _upDateModelVm(self,SectionVm,config):
            items = config.items(SectionVm)
            availableKeys = set()
            for (key,value) in items:
                availableKeys.add(key)
            DefaultHostName = None
            DefnitionDiskType = None
            DefinitionRoot = None
            DefinitionSwap = None
            DefnitionDiskMount = None
            DefnitionMac = None
            DefnitionDiskImage = None
            DefnitionDiskImagePartition = None
            
            
            keyPreferances = ['hostname']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.info( "Section '%s', no key '%s' Ignoring Section."  % (keyPreferances[0]))
                return
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, unicode ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,defaultPathImages))
                else:
                    DefaultHostName = tmpDefaultPathMount
            
            # Set up default MountPath
            
            if isinstance(self.model.defaultPathMount.get(),str):
                DefnitionDiskMount = os.path.join(self.model.defaultPathMount.get(),DefaultHostName)

            keyPreferances = ['root']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, unicode ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefinitionRoot))
                else:
                    DefinitionRoot = tmpDefaultPathMount
            
            keyPreferances = ['swap']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, unicode ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefinitionSwap))
                else:
                    DefinitionSwap = tmpDefaultPathMount
            
            keyPreferances = ['mount']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, unicode ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefnitionDiskMount))
                else:
                    DefnitionDiskMount = tmpDefaultPathMount
            
            
            keyPreferances = ['mac']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, unicode ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefnitionMac))
                else:
                    DefnitionMac = tmpDefaultPathMount
            
            keyPreferances = ['hostdisk']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, unicode ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefnitionDiskImage))
                else:
                    DefnitionDiskImage = tmpDefaultPathMount
            
            
            keyPreferances = ['partition']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, int ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not an integer, defaulting to %s."  % (SectionVm,key,DefnitionDiskImagePartition))
                else:
                    DefnitionDiskImagePartition = tmpDefaultPathMount
            
            keyPreferances = ['diskType']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathMount = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathMount, unicode ):
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not an integer, defaulting to %s."  % (SectionVm,key,DefnitionDiskImagePartition))
                else:
                    DefnitionDiskType = tmpDefaultPathMount
            
            if (DefnitionDiskType == None) and (DefnitionDiskImage != None) and (DefnitionDiskImagePartition != None):
                self.log.info( "section '%s', defaulting image format to 'kpartx'"  % (SectionVm))
                DefnitionDiskType = "kpartx"
            if (DefnitionDiskType == None) and (DefinitionRoot != None):
                self.log.info( "section '%s', defaulting image format to 'lvm'" % (SectionVm))
                DefnitionDiskType = "lvm"
            
            if DefnitionDiskType == None:
                self.log.info( "Section '%s', no key '%s' Ignoring Section."  % (SectionVm,DefnitionDiskType))
                return
            
            
            
            if not DefaultHostName in self.model.vmbyName.keys():
                self.model.vmbyName[DefaultHostName] = vmModel()
            
            self.model.vmbyName[DefaultHostName].CfgHostName.update(DefaultHostName)
            self.model.vmbyName[DefaultHostName].CfgRoot.update(DefinitionRoot)
            self.model.vmbyName[DefaultHostName].CfgSwap.update(DefinitionSwap)
            self.model.vmbyName[DefaultHostName].CfgMountPoint.update(DefnitionDiskMount)
            self.model.vmbyName[DefaultHostName].CfgMac.update(DefnitionMac)
            self.model.vmbyName[DefaultHostName].CfgDiskImage.update(DefnitionDiskImage)
            self.model.vmbyName[DefaultHostName].CfgDiskImagePartition.update(DefnitionDiskImagePartition)
            return DefaultHostName
            
            
            
            
        
        config = jsonConfigParser()
        config.readfp(open(configfile,'r'))
        configurationSections = config.sections()
        MainSection = 'vmim.local'
        ReadVmList = []
        libvirtConStr = 'qemu:///system'
        defaultPathExtracts = None
        defaultPathImages = None
        defaultPathMount = None
        if not MainSection in configurationSections:
            self.log.fatal( "Configuration file does not have a section '%s'"  % (MainSection))
            return False
        
        
        
        
        
        
        
        
        items = config.items(MainSection)
        availableKeys = set()
        for (key,value) in items:
            availableKeys.add(key)
        keyPreferances = ['vmemulator']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.warning( "Configuration file does not have a section '%s', key '%s' on how to connect to libvirt."  % (MainSection,key))
        else:
            libvirtConStr = config.getJson(MainSection,key)
        self.model.libvirtConStr.update(libvirtConStr)
        
        keyPreferances = ['vmlist']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.warning( "Configuration file does not have a section '%s', key '%s' listing active VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpReadVmList = config.getJson(MainSection,key)
            if not isinstance( tmpReadVmList, list ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a list, defaulting to %s."  % (MainSection,key,json.dumps(ReadVmList)))
            else:
                unprocessed = []
                for item in tmpReadVmList:
                    if isinstance( item, unicode ):
                        ReadVmList.append(item)
                    else:
                        unprocessed.append(item)
                if len(unprocessed) > 0:
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' list, ignoed %s."  % (MainSection,key,unprocessed))
        keyPreferances = ['mount']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.info( "Configuration file does not have a section '%s', key '%s' setiong the default Path Mount when mounting VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpDefaultPathMount = config.get(MainSection,key)
            if not isinstance( tmpDefaultPathMount, str ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (MainSection,key,defaultPathMount))
            else:
                defaultPathMount = tmpDefaultPathMount
        self.model.defaultPathMount.update(defaultPathMount)
        keyPreferances = ['vmimages']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.info( "Configuration file does not have a section '%s', key '%s' setiong the default Path Mount when mounting VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpDefaultPathMount = config.get(MainSection,key)
            if not isinstance( tmpDefaultPathMount, str ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (MainSection,key,defaultPathImages))
            else:
                defaultPathImages = tmpDefaultPathMount
        self.model.defaultPathImages.update(defaultPathImages)
        keyPreferances = ['vmextracts']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.info( "Configuration file does not have a section '%s', key '%s' setiong the default Path Mount when mounting VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpDefaultPathMount = config.get(MainSection,key)
            if not isinstance( tmpDefaultPathMount, str ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (MainSection,key,defaultPathImages))
            else:
                defaultPathExtracts = tmpDefaultPathMount
        
        self.model.defaultPathExtracts.update(defaultPathExtracts)
        
        
        
        
        
         # Now process the vms 
        ReadVmSet = set(ReadVmList)
       
        vmSections = []
        
        for section in configurationSections:
            if section[:8] == u'vmim.vm.':
                vmSections.append(section)
        for sectrion in vmSections:
            enabled = sectrion in ReadVmSet
            result = _upDateModelVm(self,sectrion,config)
            print result
            
            
            
            
            
            

class vmControl(object):
    def __init__(self):
        self.log = logging.getLogger("vmStoreRsync.vmStoreRsync") 
        self.mainModel = mainModel()
        
    
    def setConectionString(self):
        libvirtCon = LibVirtCnt(conectionStr,mytestmodel)
        libvirtCon.updateModel()


    def LoadConfigCfg(self,configfile):
        config = ConfigFile1(self.mainModel)
        return config.upDateModel(configfile)
    
    
                

if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    Control = vmControl()
    Control.LoadConfigCfg('vmimagemanager.cfg')
    
