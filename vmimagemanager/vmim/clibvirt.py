#!/usr/bin/python

import logging, logging.config


import os
import os.path
import sys
import getopt
import time
import re

import libvirt
import cinterface

import cxsl as cvirthost

# I shoudl make my own GenKeyFunction Later
from observable import GenKey, Observable, ObservableDict
import functools

class vmMdl:
    def __init__(self):
        # Three indexable ways
        self.libvirtName = Observable(None)
        self.libvirtId = Observable(None)
        self.libvirtUuid = Observable(None)
        
        #VIR_DOMAIN_NOSTATE= 0: no state
        #VIR_DOMAIN_RUNNING= 1: the domain is running
        #VIR_DOMAIN_BLOCKED= 2: the domain is blocked on resource
        #VIR_DOMAIN_PAUSED= 3: the domain is paused by user
        #VIR_DOMAIN_SHUTDOWN= 4: the domain is being shut down
        #VIR_DOMAIN_SHUTOFF= 5: the domain is shut off
        #VIR_DOMAIN_CRASHED= 6: the domain is crashed
        self.libvirtState = Observable(0)
        self.libvirtMem = Observable(None)
        self.libvirtMaxMem = Observable(None)
        self.libvirtNrVirtCpu = Observable(None)
        self.libvirtCpuTime = Observable(None)
        
    def assign(self,destination):
        destination.libvirtName.update(self.libvirtName.get())
        destination.libvirtId.update(self.libvirtId.get())
        destination.libvirtUuid.update(self.libvirtUuid.get())
        destination.libvirtState.update(self.libvirtState.get())
        destination.libvirtMem.update(self.libvirtMem.get())
        destination.libvirtMaxMem.update(self.libvirtMaxMem.get())
        destination.libvirtNrVirtCpu.update(self.libvirtNrVirtCpu.get())
        destination.libvirtCpuTime.update(self.libvirtCpuTime.get())
        
    def update(self,destination):
        libvirtName = self.libvirtName.get()
        if libvirtName != None:
            destination.libvirtName.update(libvirtName)
        libvirtId = self.libvirtId.get()
        if libvirtId != None:
            destination.libvirtId.update(libvirtId)
        libvirtUuid = self.libvirtUuid.get()
        if libvirtUuid != None:
            destination.libvirtUuid.update(libvirtUuid)
        libvirtState = self.libvirtState.get()
        if libvirtState != None:
            destination.libvirtState.update(libvirtState)
        libvirtMaxMem = self.libvirtId.get()
        if libvirtMaxMem != None:
            destination.libvirtMaxMem.update(libvirtMaxMem)
        libvirtNrVirtCpu = self.libvirtNrVirtCpu.get()
        if libvirtNrVirtCpu != None:
            destination.libvirtNrVirtCpu.update(libvirtNrVirtCpu)
        libvirtCpuTime = self.libvirtCpuTime.get()
        if libvirtCpuTime != None:
            destination.libvirtCpuTime.update(libvirtCpuTime)
        
       
class vhostMdl:
    def __init__(self):
        self.callbackKey = GenKey()
        self.vmsbyName = ObservableDict()
        self.vmsbyName.addCbPost(self.callbackKey,self._onNamePost)
        self.vmsbyId = ObservableDict()
        self.vmsByUuid = ObservableDict()
        self.vmsByUuid.addCbPost(self.callbackKey,self._onUuidPost)

    def getVmMatch(self,vmModel):
        Uuid = vmModel.libvirtUuid.get()
        if Uuid in self.vmsByUuid:
            return self.vmsByUuid[Uuid]
        ID = vmModel.libvirtId.get()
        if ID in self.vmsbyId:
            return self.vmsbyId[ID]
        Name = vmModel.libvirtName.get()
        return None

    def addVM(self,vmModel):
        match = self.getVmMatch(vmModel)
        if match != None:
            vmModel.update(match)
            return match
        newOne = vmMdl()
        newOne.libvirtUuid.addCallback(self.callbackKey,functools.partial(self._onUuidPost,newOne))
        newOne.libvirtId.addCallback(self.callbackKey,functools.partial(self._onIdPost,newOne))
        newOne.libvirtName.addCallback(self.callbackKey,functools.partial(self._onNamePost,newOne))
        vmModel.update(newOne)
        return newOne
        
        
    def _onIdPost(self,NewItem):
        identifier = NewItem.libvirtId.get()
        if identifier != None:
            match = self.getVmMatch(NewItem)
            if match != None:
                NewItem.update(match)
                return
            self.vmsbyId[identifier] = NewItem
            return
        for key in self.vmsbyId:
            if self.vmsbyId[key] == NewItem:
                del self.vmsbyId[key]
            
    def _onUuidPost(self,NewItem):
        Uuid = NewItem.libvirtUuid.get()
        if Uuid != None:
            match = self.getVmMatch(NewItem)
            if match != None:
                NewItem.update(match)
                return
            self.vmsByUuid[Uuid] = NewItem
        for key in self.vmsByUuid:
            if self.vmsByUuid[key] == NewItem:
                del self.vmsByUuid[key]
        
    def _onNamePost(self,NewItem):
        Name = NewItem.libvirtName.get()
        if Name != None:
            match = self.getVmMatch(NewItem)
            if match != None:
                NewItem.update(match)
                return
            self.vmsbyName[Name] = NewItem
        for key in self.vmsbyName:
            if self.vmsbyName[key] == NewItem:
                del self.vmsbyName[key]

def tester(conection,model):
    vmModel = vmMdl()
    vmModel.libvirtName.set(Name)
    model.vmsbyName[Name] = vmModel

    
def LibvirtUpdate(conection,model):
    
    RunningDomains = conection.listDomainsID()
    for LibVirtRunningDomainId in RunningDomains:
        hostPtr = conection.lookupByID(LibVirtRunningDomainId)
        Name = hostPtr.name()
        Uuid = hostPtr.UUIDString()
        ID = hostPtr.ID()
        vmModel = vmMdl()
        vmModel.libvirtName.set(Name)
        vmModel.libvirtUuid.set(Uuid)
        vmModel.libvirtId.set(ID)
        model.addVM(vmModel)
        
    DefinedDomains = set(conection.listDefinedDomains())
    for Name in DefinedDomains.difference(model.vmsbyName.keys()):
        vmModel = vmMdl()
        vmModel.libvirtName.set(Name)
        model.addVM(vmModel)
    for name in model.vmsbyName.keys():
        hostPtr = conection.lookupByName(name)
        Uuid = hostPtr.UUIDString()
        vmModel = vmMdl()
        ID = hostPtr.ID()
        ThisObj = model.vmsbyName[name]
        ThisObj.libvirtName.update(Name)
        ThisObj.libvirtUuid.update(Uuid)
        ThisObj.libvirtId.update(ID)
        (state,maxMem,memory,nrVirtCpu,cpuTime) =  hostPtr.info()
        ThisObj.libvirtState.update(state)
        ThisObj.libvirtMaxMem.update(maxMem)
        ThisObj.libvirtMem.update(memory)
        ThisObj.libvirtNrVirtCpu.update(nrVirtCpu)
        ThisObj.libvirtCpuTime.update(cpuTime)
        
def debugModel(model):
    for item in model.vmsByUuid.keys():
        print "By UUID %s=%s,%s" % (model.vmsByUuid[item].libvirtName.get(),
            model.vmsByUuid[item].libvirtUuid.get(),
            model.vmsByUuid[item])
    for item in model.vmsbyName.keys():
        print "By Name %s=%s" % (model.vmsbyName[item].libvirtName.get(),
            model.vmsbyName[item].libvirtUuid.get())
    for item in model.vmsbyId.keys():
        print "By Id %s=%s" % (model.vmsbyId[item].libvirtName.get(),
            model.vmsbyId[item].libvirtUuid.get())

class virtualHostContainerLibVirt(cinterface.virtualHostContainer):
    def __init__(self):
        cinterface.virtualHostContainer.__init__(self)
    def createVirtualhost(self,cfg):
        return cvirthost.virtualhostKvm(cfg)

    def libVirtExport(self):
        hostNames = []
        libVirtNames = self.conection.listDefinedDomains()
        for x in range (0 , len(self.hostlist)):
            try:
                if not hasattr(self.hostlist[x],"libvirtObj"):
                    self.hostlist[x].libvirtObj = self.conection.lookupByName(self.hostlist[x].HostName)
            except libvirt.libvirtError, e:
                if (e.get_error_code() == 42):
                    self.hostlist[x].cfgApply()
                    self.hostlist[x].RealiseDevice()
                    
                    generatorXml = self.hostlist[x].genXmlShouldExist()
                    if generatorXml != "":
                        try:
                            
                            self.hostlist[x].libvirtObj = self.conection.defineXML(generatorXml)
                        except libvirt.libvirtError, e:
                            #print KnownHosts
                            #print "Exception Generating " + self.hostlist[x].HostName
                            self.logger.error("generatorXml=%s" % (generatorXml))
                            self.logger.error("Exception Generating " + self.hostlist[x].HostName)
                            self.logger.debug(e)
                            #print dir(e)
                            #print e.get_error_level()
                            #print e
                            #raise e
                        
    def libvirtImport(self):
        self.VmHostServer
        self.conection = libvirt.open(str(self.VmHostServer))
        mytestmodel = vhostMdl()
        LibvirtUpdate(self.conection,mytestmodel)
        libvirtKnonVms = set(mytestmodel.vmsbyName.keys())
        #print libvirtKnonVms.difference(self.hostlist)
        #print len(self.hostlist)
        TmpHostNames = []
        for libVritId in self.hostlist:
            TmpHostNames.append(libVritId.HostName)
        
        
        for Name in libvirtKnonVms.difference(TmpHostNames):
            cfgDict = {}
            cfgDict["Connection"] = self.conection
            #if has(libVritId
            #sif not libVritId
            
            libvirtdConnection = self.conection.lookupByName(Name)
            cfgDict["HostName"]  = Name
            fred =  self.virtualHostGenerator(cfgDict)
        
        return True
