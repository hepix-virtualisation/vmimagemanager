import logging, logging.config
from ConfigParserJson import jsonConfigParser

import os

from ConfigModel import vmModel , CfgModel

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
            DefaultPathImages = self.model.defaultPathImages.get()
            DefaultPathExtracts = self.model.defaultPathExtracts.get()
            DefaultPathInserts = self.model.defaultPathInserts.get()
            
            keyPreferances = ['hostname','HostName']
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
                    self.log.warning( "Configuration file does not have a section '%s', key '%s' is not an string, defaulting to %s."  % (SectionVm,key,DefnitionDiskImagePartition))
                else:
                    DefnitionDiskType = tmpDefaultPathMount
            
            
            keyPreferances = ['vmimages']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathImages = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathImages, unicode ):
                    self.log.debug( "Configuration file does not have a section '%s', key '%s' is not an string, defaulting to %s."  % (SectionVm,key,DefaultPathImages))
                else:
                    DefaultPathImages = tmpDefaultPathImages
            
            keyPreferances = ['vmextracts']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathExtracts = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathExtracts, unicode ):
                    self.log.debug( "Configuration file does not have a section '%s', key '%s' is not an string, defaulting to %s."  % (SectionVm,key,DefaultPathExtracts))
                else:
                    DefaultPathExtracts = tmpDefaultPathExtracts
            
            keyPreferances = ['vminserts']
            key = _selectBestKeyFor(keyPreferances,availableKeys)
            if key == None:
                self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
            else:
                tmpDefaultPathInserts = config.getJson(SectionVm,key)
                if not isinstance( tmpDefaultPathInserts, unicode ):
                    self.log.info( "Configuration file does not have a section '%s', key '%s' is not an string, defaulting to %s."  % (SectionVm,key,DefaultPathInserts))
                else:
                    DefaultPathInserts = tmpDefaultPathInserts
            
            
            
            
            
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
            self.model.vmbyName[DefaultHostName].CfgDiskType.update(DefnitionDiskType)
            self.model.vmbyName[DefaultHostName].CfgPathImages.update(DefaultPathImages)
            self.model.vmbyName[DefaultHostName].CfgPathExtracts.update(DefaultPathExtracts)
            self.model.vmbyName[DefaultHostName].CfgPathInserts.update(DefaultPathInserts)
            
            return DefaultHostName
            
            
            
            
        
        config = jsonConfigParser()
        config.readfp(open(configfile,'r'))
        configurationSections = config.sections()
        MainSection = 'vmim.local'
        ReadVmList = []
        libvirtConStr = 'qemu:///system'
        defaultPathExtracts = None
        defaultPathInserts = None
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
            tmpDefaultPathMount = config.getJson(MainSection,key)
            if not isinstance( tmpDefaultPathMount, unicode ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (MainSection,key,defaultPathMount))
            else:
                defaultPathMount = tmpDefaultPathMount
        self.model.defaultPathMount.update(defaultPathMount)
        keyPreferances = ['vmimages']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.info( "Configuration file does not have a section '%s', key '%s' setiong the default Path Mount when mounting VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpDefaultPathMount = config.getJson(MainSection,key)
            if not isinstance( tmpDefaultPathMount, unicode ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (MainSection,key,defaultPathImages))
            else:
                defaultPathImages = tmpDefaultPathMount
        self.model.defaultPathImages.update(defaultPathImages)
        keyPreferances = ['vmextracts']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.info( "Configuration file does not have a section '%s', key '%s' setiong the default Path Mount when mounting VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpDefaultPathExtracts = config.getJson(MainSection,key)
            if not isinstance( tmpDefaultPathMount, unicode ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (MainSection,key,defaultPathExtracts))
            else:
                defaultPathExtracts = tmpDefaultPathExtracts
        
        self.model.defaultPathExtracts.update(defaultPathExtracts)
        
        keyPreferances = ['vmextracts']
        key = _selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.info( "Configuration file does not have a section '%s', key '%s' setiong the default Path Mount when mounting VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpDefaultPathMount = config.getJson(MainSection,key)
            if not isinstance( tmpDefaultPathMount, unicode ):
                self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (MainSection,key,defaultPathImages))
            else:
                defaultPathInserts = tmpDefaultPathMount
        self.model.defaultPathInserts.update(defaultPathInserts)
        
        
        if defaultPathExtracts != None and defaultPathInserts == None:
            self.log.info( "Defaiulting section '%s' inserts path to '%s'."  % (SectionVm,defaultPathInserts))
            defaultPathInserts = defaultPathExtracts
            self.model.defaultPathExtracts.update(defaultPathExtracts)
        if defaultPathExtracts == None and defaultPathInserts != None:
            self.log.info( "Defaiulting section '%s' extracts path to '%s'."  % (SectionVm,defaultPathInserts))
            defaultPathExtracts = defaultPathInserts
        
        
         # Now process the vms 
        ReadVmSet = set(ReadVmList)
        
        vmSections = []
        # Get a list of vm's sections must have this prefix
        for section in configurationSections:
            if section[:8] == u'vmim.vm.':
                vmSections.append(section)
        
        CfgVmList = []
        for sectrion in vmSections:
            enabled = sectrion in ReadVmSet
            result = _upDateModelVm(self,sectrion,config)
            if result != None:
                self.model.vmbyName[result].CfgListed.update(enabled)
                CfgVmList.append(result)
        CfgVmSet = set(CfgVmList)
            
            
            
