import logging, logging.config
from ConfigParserJson import jsonConfigParser

import os

from ConfigModel import vmModel , CfgModel


def selectBestKeyFor(selections,availableKeys):
    for item in selections:
        if item in availableKeys:
            return item
    return None


class ConfigInterpretVm(object):
    def __init__(self,model,config,ConfigSectionName):
        self.log = logging.getLogger("ConfigFileView.ConfigInterpretVm")
        self.model = model
        self.config = config
        self.ConfigSectionName = ConfigSectionName
        self.canUpdate = False
        self.hostname = None
        self.availableKeys = set([])
    def getConfigSectionKey(self,section,keyPreferances):
        
        return selectBestKeyFor(keyPreferances,self.availableKeys)
    
    def getConfigValue(self,section,key,valueType,Default):
        tmpDefaultPathMount = self.config.getJson(section,key)
        if not isinstance( tmpDefaultPathMount, valueType ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a '%s', defaulting to %s."  % (self.ConfigSectionName,key,valueType,Default))
            return None
        return tmpDefaultPathMount
    def updateAll(self):
        self.updateAvailableKeys()
        self.updateName()
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        self.updatePathSharedPartition()
        self.updatePathSharedSwap()
        self.updatePathMount()
        self.updatePathImages()
        self.updatePathOverlays()
        self.updatePathExtracts()
        self.updateDiskImagePartition()
        self.updateDiskImage()
        self.updateMac()
        self.updateStorageType()
    def updateAvailableKeys(self):
        foundKeys = []
        for (key,value) in self.config.items(self.ConfigSectionName):
            foundKeys.append(key)
        self.availableKeys = set(foundKeys)
        
    def updateName(self):
        defaultPathImages = None
        keyPreferances = ['hostname','HostName']
        key = selectBestKeyFor(keyPreferances,self.availableKeys)
        if key == None:
            self.log.info( "Section '%s', no key '%s' Ignoring Section."  % (keyPreferances[0]))
            return
        HostName = self.config.getJson(self.ConfigSectionName,key)
        if not isinstance( HostName, unicode ):
            self.log.warning( "Configuration file does not have a section '%s', key '%s' is not a string, defaulting to %s."  % (self.ConfigSectionName,key,defaultPathImages))
            return
        keys = self.model.vmbyName.keys()
        if not HostName in self.model.vmbyName.keys():
            self.model.vmbyName[HostName] = vmModel()
        self.model.vmbyName[HostName].CfgHostName.set(HostName)
        self.canUpdate = True
        self.hostname = HostName

    def updatePathSharedPartition(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        DefaultPathMountPrefix = None
        keyPreferances = ['root']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],DefaultPathMountPrefix))
            self.model.vmbyName[self.hostname].CfgRoot.update(DefaultPathMountPrefix)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,unicode,DefaultPathMountPrefix)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],DefaultPathMountPrefix))
            self.model.vmbyName[self.hostname].CfgRoot.update(defaultPathMount)
            return
        normPath = os.path.normpath(RawPathMount)
        
        self.model.vmbyName[self.hostname].CfgRoot.update(normPath)
        return 
        
    
    def updatePathMount(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        DefaultPathMountPrefix = self.model.defaultPathMount.get()
        defaultPathMount = "/mnt/vm/%s" % (self.hostname)
        if DefaultPathMountPrefix != None:
            defaultPathMount = os.path.join(DefaultPathMountPrefix,self.hostname)
        keyPreferances = ['mount']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPathMount))
            self.model.vmbyName[self.hostname].CfgMountPoint.update(defaultPathMount)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,unicode,defaultPathMount)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPathMount))
            self.model.vmbyName[self.hostname].CfgMountPoint.update(defaultPathMount)
            return
        normPath = os.path.normpath(RawPathMount)
        self.model.vmbyName[self.hostname].CfgMountPoint.update(normPath)
        return 
        
        
    
    def updatePathImages(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultPath = self.model.defaultPathImages.get()
        keyPreferances = ['mount']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgPathImages.update(defaultPath)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,unicode,defaultPath)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgPathImages.update(defaultPath)
            return
        normPath = os.path.normpath(RawPathMount)
        self.model.vmbyName[self.hostname].CfgPathImages.update(normPath)
        return 
        
    
    def updatePathOverlays(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultPath = self.model.defaultPathInserts.get()
        keyPreferances = ['overlay','vminserts']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgPathInserts.update(defaultPath)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,unicode,defaultPath)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgPathInserts.update(defaultPath)
            return
        normPath = os.path.normpath(RawPathMount)
        self.model.vmbyName[self.hostname].CfgPathInserts.update(normPath)
        return 

    def updatePathExtracts(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultPath = self.model.defaultPathExtracts.get()
        keyPreferances = ['vmextracts']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgPathExtracts.update(defaultPath)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,unicode,defaultPath)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgPathExtracts.update(defaultPath)
            return
        normPath = os.path.normpath(RawPathMount)
        self.model.vmbyName[self.hostname].CfgPathExtracts.update(normPath)
    
    
    def updateDiskImagePartition(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultPath = None
        keyPreferances = ['partition']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgDiskImagePartition.update(defaultPath)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,int,defaultPath)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgDiskImagePartition.update(defaultPath)
            return
        self.model.vmbyName[self.hostname].CfgDiskImagePartition.update(RawPathMount)
    def updateDiskImage(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultPath = None
        keyPreferances = ['hostdisk']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgDiskImage.update(defaultPath)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,unicode,defaultPath)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgDiskImage.update(defaultPath)
            return
        normPath = os.path.normpath(RawPathMount)
        self.model.vmbyName[self.hostname].CfgDiskImage.update(normPath)
    def updatePathSharedSwap(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultPath = None
        keyPreferances = ['swap']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgSwap.update(defaultPath)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,unicode,defaultPath)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgSwap.update(defaultPath)
            return
        normPath = os.path.normpath(RawPathMount)
        self.model.vmbyName[self.hostname].CfgSwap.update(normPath)
    
    def updateMac(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultPath = []
        keyPreferances = ['mac']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgMac.update(defaultPath)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,list,defaultPath)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultPath))
            self.model.vmbyName[self.hostname].CfgMac.update(defaultPath)
            return
        self.model.vmbyName[self.hostname].CfgMac.update(RawPathMount)
    
    def updateStorageType(self):
        if self.hostname == None:
            self.log.info("Ignoring Section '%s' as no 'name' defined"  % (self.ConfigSectionName))
            return
        defaultType = None
        if self.model.vmbyName[self.hostname].CfgDiskImage.get() != None and self.model.vmbyName[self.hostname].CfgDiskImagePartition.get() != None:
            defaultType = 'shared'
        
        if self.model.vmbyName[self.hostname].CfgDiskImage.get() != None and self.model.vmbyName[self.hostname].CfgDiskImagePartition.get() != None:
            defaultType = 'kpartx'
        keyPreferances = ['store_type']
        key = self.getConfigSectionKey(self.ConfigSectionName,keyPreferances)
        if key == None:
            self.log.info("Section '%s' key '%s' missing defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultType))
            self.model.vmbyName[self.hostname].CfgMac.update(defaultType)
            return
        RawPathMount = self.getConfigValue(self.ConfigSectionName,key,list,defaultType)
        if RawPathMount == None:
            self.log.info("Section '%s' key '%s' invalid defaulting to '%s'"  % (self.ConfigSectionName,keyPreferances[0],defaultType))
            self.model.vmbyName[self.hostname].CfgMac.update(defaultType)
            return
        normPath = os.path.normpath(RawPathMount)
        self.model.vmbyName[self.hostname].CfgMac.update(normPath)
    
    
    
    
    
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
        
    


    def setDefaultPathOverlayExtracts(self):
        self.setDefaultPathExtracts()
        self.setDefaultPathOverlay()
        defaultPathExtracts = self.model.defaultPathExtracts.get()
        defaultPathInserts = self.model.defaultPathInserts.get()
        if defaultPathExtracts != None and defaultPathInserts == None:
            self.log.info( "Defaiulting section '%s' inserts path to '%s'."  % (self.mainSection,defaultPathExtracts))
            self.model.defaultPathInserts.update(defaultPathExtracts)
        if defaultPathExtracts == None and defaultPathInserts != None:
            self.log.info( "Defaiulting section '%s' extracts path to '%s'."  % (self.mainSection,defaultPathInserts))
            self.model.defaultPathExtracts.update(defaultPathInserts)
        

    def processVmSections(self):
        vmSections = self.getVMSections()
        CfgVmList = []
        defaultPathImages = self.model.defaultPathImages.get()
        defaultPathExtracts = self.model.defaultPathExtracts.get()
        defaultPathInserts = self.model.defaultPathInserts.get()
        defaultPathMount = self.model.defaultPathMount.get()
        for sectrion in vmSections:
            processor = ConfigInterpretVm(self.model,self.config,sectrion)
            processor.updateAll()
        
        
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
        
            
            
