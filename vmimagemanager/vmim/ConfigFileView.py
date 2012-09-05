import logging, logging.config
from ConfigParserJson import jsonConfigParser

import os

from ConfigModel import vmModel , CfgModel


def selectBestKeyFor(selections,availableKeys):
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
    key = selectBestKeyFor(keyPreferances,availableKeys)
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
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathMount = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathMount, unicode ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefinitionRoot))
        else:
            DefinitionRoot = tmpDefaultPathMount

    keyPreferances = ['swap']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathMount = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathMount, unicode ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefinitionSwap))
        else:
            DefinitionSwap = tmpDefaultPathMount

    keyPreferances = ['mount']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathMount = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathMount, unicode ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefnitionDiskMount))
        else:
            DefnitionDiskMount = tmpDefaultPathMount


    keyPreferances = ['mac']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathMount = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathMount, unicode ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefnitionMac))
        else:
            DefnitionMac = tmpDefaultPathMount

    keyPreferances = ['hostdisk']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathMount = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathMount, unicode ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (SectionVm,key,DefnitionDiskImage))
        else:
            DefnitionDiskImage = tmpDefaultPathMount


    keyPreferances = ['partition']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathMount = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathMount, int ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not an integer, defaulting to %s."  % (SectionVm,key,DefnitionDiskImagePartition))
        else:
            DefnitionDiskImagePartition = tmpDefaultPathMount

    keyPreferances = ['diskType']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathMount = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathMount, unicode ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not an string, defaulting to %s."  % (SectionVm,key,DefnitionDiskImagePartition))
        else:
            DefnitionDiskType = tmpDefaultPathMount


    keyPreferances = ['vmimages']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathImages = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathImages, unicode ):
            self.log.debug( "Configuration file does not have a section '%s', key '%s' is not an string, defaulting to %s."  % (SectionVm,key,DefaultPathImages))
        else:
            DefaultPathImages = tmpDefaultPathImages

    keyPreferances = ['vmextracts']
    key = selectBestKeyFor(keyPreferances,availableKeys)
    if key == None:
        self.log.debug( "Section '%s', no key '%s'."  % (SectionVm,keyPreferances[0]))
    else:
        tmpDefaultPathExtracts = config.getJson(SectionVm,key)
        if not isinstance( tmpDefaultPathExtracts, unicode ):
            self.log.debug( "Configuration file does not have a section '%s', key '%s' is not an string, defaulting to %s."  % (SectionVm,key,DefaultPathExtracts))
        else:
            DefaultPathExtracts = tmpDefaultPathExtracts

    keyPreferances = ['vminserts']
    key = selectBestKeyFor(keyPreferances,availableKeys)
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



    

class ConfigFile1(object):
    def __init__(self,model):
        self.model = model
        self.log = logging.getLogger("vmCtrl.ConfigFile1")
        self.config = jsonConfigParser()
        self.mainSection = 'vmim.local'
    def getVMSections(self):
        configurationSections = self.config.sections()
        vmSections = []
        # Get a list of vm's sections must have this prefix
        for section in configurationSections:
            if section[:8] == u'vmim.vm.':
                vmSections.append(section)
        return vmSections
    def getAvailableKeys(self,MainSection):
        items = self.config.items(MainSection)
        availableKeys = set()
        for (key,value) in items:
            availableKeys.add(key)
        return availableKeys

    def getConfigSectionKey(self,section,keyPreferances):
        availbleKeys = self.getAvailableKeys(section)
        return selectBestKeyFor(keyPreferances,availbleKeys)
    
    def getConfigValue(self,section,key,valueType,Default):
        tmpDefaultPathMount = self.config.getJson(section,key)
        if not isinstance( tmpDefaultPathMount, valueType ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a '%s', defaulting to %s."  % (self.mainSection,key,valueType,Default))
            return None
        return tmpDefaultPathMount


    def setDefaultPathImages(self):
        defaultPathExtracts = None
        keyPreferances = ['images','vmimages']
        key = self.getConfigSectionKey(self.mainSection,keyPreferances)
        if key == None:
            self.log.info("Configuration file does not have a section '%s', key '%s' section the default VM image directory."  % (self.mainSection,keyPreferances[0]))
            return
        defaultPathExtracts = self.getConfigValue(self.mainSection,key,unicode,defaultPathExtracts)
        if defaultPathExtracts == None:
            return
        self.model.defaultPathImages.update(defaultPathExtracts)
    
    def setDefaultPathOverlay(self):
        defaultPathExtracts = None
        keyPreferances = ['overlay','inserts']
        key = self.getConfigSectionKey(self.mainSection,keyPreferances)
        if key == None:
            self.log.info("Configuration file does not have a section '%s', key '%s' section the default VM ovelay image directory."  % (self.mainSection,keyPreferances[0]))
            return
        defaultPathExtracts = self.getConfigValue(self.mainSection,key,unicode,defaultPathExtracts)
        if defaultPathExtracts == None:
            return
        self.model.defaultPathImages.update(defaultPathExtracts)
    
    def setDefaultPathExtracts(self):
        defaultPathExtracts = None
        keyPreferances = ['vmextracts']
        key = self.getConfigSectionKey(self.mainSection,keyPreferances)
        if key == None:
            self.log.info("Configuration file does not have a section '%s', key '%s' section the default VM extracts image directory."  % (self.mainSection,keyPreferances[0]))
            return
        defaultPathExtracts = self.getConfigValue(self.mainSection,key,unicode,defaultPathExtracts)
        if defaultPathExtracts == None:
            return
        self.model.defaultPathExtracts.update(defaultPathExtracts)
    

    def setDefaultPathMount(self):
        defaultPathExtracts = None
        keyPreferances = ['mount']
        key = self.getConfigSectionKey(self.mainSection,keyPreferances)
        if key == None:
            self.log.info("Configuration file does not have a section '%s', key '%s' section the default Path Mount when mounting VM's."  % (self.mainSection,keyPreferances[0]))
            return
        defaultPathExtracts = self.getConfigValue(self.mainSection,key,unicode,defaultPathExtracts)
        if defaultPathExtracts == None:
            return
        self.model.defaultPathExtracts.update(defaultPathExtracts)
    


    def setDefaultPathOverlayExtracts(self):
        self.setDefaultPathExtracts()
        self.setDefaultPathOverlay()
        defaultPathExtracts = self.model.defaultPathExtracts.get()
        defaultPathInserts = self.model.defaultPathInserts.get()
        if defaultPathExtracts != None and defaultPathInserts == None:
            self.log.info( "Defaiulting section '%s' inserts path to '%s'."  % (self.mainSection,defaultPathInserts))
            self.model.defaultPathExtracts.update(defaultPathExtracts)
        if defaultPathExtracts == None and defaultPathInserts != None:
            self.log.info( "Defaiulting section '%s' extracts path to '%s'."  % (self.mainSection,defaultPathInserts))
            self.model.defaultPathInserts.update(defaultPathInserts)
        
    def setVM(self,sectionName):
        print sectionName
        keyPreferances = ['hostname','HostName']
        key = self.getConfigSectionKey(sectionName,keyPreferances)
        if key == None:
            self.log.info("Ignoring section: no '%s' key in '%s' section."  % (keyPreferances[0],self.mainSection))
            return
        hostName = self.getConfigValue(sectionName,key,unicode,None)
        if hostName == None:
            self.log.info("Ignoring section: value for '%s' section '%s' key is invalid."  % (sectionName,defaultPathInserts))
            return
        if not hostName in self.model.vmbyName.keys():
            self.model.vmbyName[hostName] = vmModel()
        
        defaultPathImages = self.model.defaultPathImages.get()
        defaultPathInserts = self.model.defaultPathInserts.get()
        defaultPathExtracts = self.model.defaultPathExtracts.get()
        defaultPathInserts = self.model.defaultPathInserts.get()
        defaultPathMount = self.model.defaultPathMount.get()
        if defaultPathMount == None:
            defaultPathMount = '/mnt'
        defaultPathMount = os.path.join(defaultPathMount,hostName)
        keyPreferances = ['mount']
        key = self.getConfigSectionKey(sectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (sectionName,keyPreferances[0],defaultPathMount))
        else:
            tmp = self.getConfigValue(sectionName,key,unicode,defaultPathMount)
            if tmp != None:
                defaultPathMount = tmp
        keyPreferances = ['root']
        key = self.getConfigSectionKey(sectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (sectionName,keyPreferances[0],defaultPathMount))

    def processVmSections(self):
        vmSections = self.getVMSections()
        CfgVmList = []
        defaultPathImages = self.model.defaultPathImages.get()
        defaultPathExtracts = self.model.defaultPathExtracts.get()
        defaultPathInserts = self.model.defaultPathInserts.get()
        defaultPathMount = self.model.defaultPathMount.get()
        for sectrion in vmSections:
            self.setVM(sectrion)
        
        
    def upDateModel(self,configfile):
        self.config.readfp(open(configfile,'r'))
        configurationSections = self.config.sections()
        MainSection = 'vmim.local'
        ReadVmList = []
        libvirtConStr = 'qemu:///system'
        
        defaultPathImages = None
        defaultPathMount = None
        if not MainSection in configurationSections:
            self.log.fatal( "Configuration file does not have a section '%s'"  % (MainSection))
            return False
        
    
        items = self.config.items(MainSection)
        availableKeys = set()
        for (key,value) in items:
            availableKeys.add(key)
        keyPreferances = ['vmemulator']
        key = selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.warning( "Configuration file does not have a section '%s', key '%s' on how to connect to libvirt."  % (MainSection,key))
        else:
            libvirtConStr = self.config.getJson(MainSection,key)
        self.model.libvirtConStr.update(libvirtConStr)
        
        keyPreferances = ['vmlist']
        key = selectBestKeyFor(keyPreferances,availableKeys)
        if key == None:
            self.log.warning( "Configuration file does not have a section '%s', key '%s' listing active VM's."  % (MainSection,keyPreferances[0]))
        else:
            tmpReadVmList = self.config.getJson(MainSection,key)
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
        
        
        self.setDefaultPathImages()
           
        self.setDefaultPathMount()
        self.setDefaultPathOverlayExtracts()
        
        self.processVmSections()
        
        # Now process the vms 
        ReadVmSet = set(ReadVmList)
        
        vmSections = self.getVMSections()
        
        CfgVmList = []
        for sectrion in vmSections:
            enabled = sectrion in ReadVmSet
            result = _upDateModelVm(self,sectrion,self.config)
            if result != None:
                self.model.vmbyName[result].CfgListed.update(enabled)
                CfgVmList.append(result)
        CfgVmSet = set(CfgVmList)
            
            
            
