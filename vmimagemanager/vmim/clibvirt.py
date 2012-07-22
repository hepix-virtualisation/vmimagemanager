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
        #print libvirtName
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
        if Name in self.vmsbyName:
            return self.vmsbyName[Name]
        debugVm(vmModel)
        return None

    def addVM(self,vmModel):
        debugVm(vmModel)
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
        print "_onUuidPost" ,identifier
        if identifier == None:
            return
        if not identifier in self.vmsbyId.keys():        
            self.vmsbyId[identifier] = NewItem
        NewItem.update(self.vmsbyId[identifier])
        return self.vmsbyId[identifier]
    
    
        identifier = NewItem.libvirtId.get()
        if identifier == -1:
            return
        print "_onIdPost" ,identifier
        
        match = self.getVmMatch(NewItem)
        if match != None:
            NewItem.update(match)
            return

        self.vmsbyId[identifier] = NewItem
        return
        
            
    def _onUuidPost(self,NewItem):
        Uuid = NewItem.libvirtUuid.get()
        print "_onUuidPost" ,Uuid
        if Uuid == None:
            return
        if not Uuid in self.vmsByUuid.keys():        
            self.vmsByUuid[Uuid] = NewItem
        NewItem.update(self.vmsByUuid[Uuid])
        return self.vmsByUuid[Uuid]
         

        
    def _onNamePost(self,NewItem):
        Name = NewItem.libvirtName.get()
        print "_onNamePost" ,Name
        if Name == None:
            return
        if not Name in self.vmsbyName.keys():
            print 'ddd' , Name  
            self.vmsbyName[Name] = NewItem
        NewItem.update(self.vmsbyName[Name])
        return self.vmsbyName[Name]
        
        

class LibVirtConnection:
    def __init__(self,connectionstring):
        self.connectionstring = str(connectionstring)
        self.connection = libvirt.open(self.connectionstring)
        



class LibVirtCnt(object):
    def __init__(self,connection,model):
        self.connection  = libvirt.open(str(connection))
        self.model = model
    def updateModel(self):
        RunningDomains = self.connection.listDomainsID()
        for LibVirtRunningDomainId in RunningDomains:
            hostPtr = self.connection.lookupByID(LibVirtRunningDomainId)
            Name = hostPtr.name()
            Uuid = hostPtr.UUIDString()
            ID = hostPtr.ID()
            vmModel = vmMdl()
            vmModel.libvirtName.set(Name)
            vmModel.libvirtUuid.set(Uuid)
            vmModel.libvirtId.set(ID)
            self.model.addVM(vmModel)
            
        #debugModel(self.model)
        DefinedDomains = set(self.connection.listDefinedDomains())
        for Name in DefinedDomains.difference(self.model.vmsbyName.keys()):
            vmModel = vmMdl()
            vmModel.libvirtName.set(Name)
            self.model.addVM(vmModel)
        for name in self.model.vmsbyName.keys():
            hostPtr = self.connection.lookupByName(name)
            Uuid = hostPtr.UUIDString()
            print 'ssssssssss',Uuid
            vmModel = vmMdl()
            ID = hostPtr.ID()
            vmModel.libvirtName.update(Name)
            vmModel.libvirtUuid.update(Uuid)
            vmModel.libvirtId.update(ID)
            (state,maxMem,memory,nrVirtCpu,cpuTime) =  hostPtr.info()
            vmModel.libvirtState.update(state)
            vmModel.libvirtMaxMem.update(maxMem)
            vmModel.libvirtMem.update(memory)
            vmModel.libvirtNrVirtCpu.update(nrVirtCpu)
            vmModel.libvirtCpuTime.update(cpuTime)
            self.model.addVM(vmModel)
        
    def getLibVrtPtr(self,vm):
        debugModel(self.model)
        #print vm.libvirtName.get()
        #print "getLibVrtPtr",vm.libvirtName.get()
        vmDetails = self.model.getVmMatch(vm)
        if vmDetails != None:
            return vmDetails
        libvirtId = vm.libvirtId.get()
        if libvirtId != None:
            return libvirtId
        #print 'tong',vm
        libvirtUuid = vm.libvirtUuid.get()
        if libvirtUuid != None:
            return libvirtUuid
        libvirtName = vm.libvirtName.get()
        if libvirtName != None:
            return self.model.vmsbyName[libvirtName]
        self.conection.updateModel()
        return None
    
    def vmStart(self,vm):
        vmDetails = self.getLibVrtPtr(vm)
       
        if vmDetails == None:
            return
        print "here",vmDetails
        
        


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


def debugVm(Vm):
    message = "debugVm.Name:%s" % Vm.libvirtName.get()
    Uuid = Vm.libvirtUuid.get()
    if Uuid != None:
        message += "\nUuid:%s" % ( Uuid)
    ID = Vm.libvirtId.get()
    if ID != None:
        message += "\nID:%s" % ( Uuid)
    print message


def debugModel(model):
    for item in model.vmsByUuid.keys():
        print "By UUID %s?%s=%s,%s" % (item,model.vmsByUuid[item].libvirtName.get(),
            model.vmsByUuid[item].libvirtUuid.get(),
            model.vmsByUuid[item])
    for item in model.vmsbyName.keys():
        print "By Name %s?%s=%s" % (item,model.vmsbyName[item].libvirtName.get(),
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
                        
    def libvirtImport(self,conection):
       
        print "libvirtImport",str(conection)
        self.conection = libvirt.open(str(conection))
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
