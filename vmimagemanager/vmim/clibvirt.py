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
        self.vmsbyId = ObservableDict()
        self.vmsByUuid = ObservableDict()
        

    def getVmMatch(self,vmModel):
        Uuid = vmModel.libvirtUuid.get()
        candidateUuid = []
        
        candidates = []
        if Uuid != None:
            if Uuid in self.vmsByUuid:
                candidateUuid.append(self.vmsByUuid[Uuid])

        candidateId = []
        ID = vmModel.libvirtId.get()
        if ID != None and ID != -1:
            if ID in self.vmsbyId:
                candidateId.append(self.vmsbyId[ID])
        
        candidateName = []
        Name = vmModel.libvirtName.get()
        if Name != None:
            if Name in self.vmsbyName:
                candidateName.append(self.vmsbyName[Name])
        
        candidateUuidSet = set(candidateUuid)
        candidateUuidSetLen = len(candidateUuidSet)
        candidateIdSet =  set(candidateId)
        candidateIdSetLen = len(candidateIdSet)
        candidateNameSet =  set(candidateName)
        candidateNameSetLen = len(candidateNameSet)
        if ((candidateNameSetLen > 0) and (candidateIdSetLen > 0) and (candidateUuidSetLen > 0)):
            completeSet = candidateUuidSet.intersection(candidateNameSet).intersection(candidateIdSet)
            
            if len(completeSet) == 1:
                return completeSet.pop()
        if ((candidateNameSetLen > 0) and (candidateUuidSetLen > 0)):
            nameUuidSet = candidateUuidSet.intersection(candidateNameSet)
            if len(nameUuidSet) == 1:
                return nameUuidSet.pop()
        if ((candidateNameSetLen > 0) and (candidateIdSetLen > 0)):
            nameIdSet = candidateIdSet.intersection(candidateNameSet)
            if len(nameIdSet) == 1:
                return nameIdSet.pop()
        if (candidateUuidSetLen > 0):
            nameUuidSetLen = len(candidateUuidSet)
            #print "nameUuidSetLen",nameUuidSetLen
            if nameUuidSetLen == 1:
                return candidateUuidSet.pop()
        if (candidateNameSetLen > 0):
            nameIdSetLen = len(candidateNameSet)
            #print "nameIdSetLen",nameIdSetLen
            if nameIdSetLen == 1:
                return candidateNameSet.pop()
        if (candidateIdSetLen > 0):
            nameIdSetLen = len(candidateIdSet)
            #print "nameIdSetLen",nameIdSetLen
            if nameIdSetLen == 1:
                return candidateIdSet.pop()
        
        
        lenAllSets = candidateUuidSetLen + candidateIdSetLen + candidateNameSetLen
        #print lenAllSets
        if lenAllSets == 0:
            # If we have no results return
            return None
        
        
        if candidateUuidSetLen == 1:
            return candidateUuidSet.pop()
        # This code will never be exxecuted
        candidates = candidateUuid + candidateId + candidateName
        if len(candidates) > 0:
            return candidates[0]

        return None

    def addVM(self,vmModel):
        #debugVm(vmModel)
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
        validIdentifier = True
        if identifier == None:
            validIdentifier = False
        if identifier == -1:
            validIdentifier = False
        #print "_onIdPdddddddddddddost" ,identifier
        matches = self.getVmMatch(NewItem)
        if matches == None:
            #print "fddddddddddddddddddddxxssddddd"
            #debugVm(NewItem)   
            self.vmsbyId[identifier] = NewItem
            matches = self.vmsbyId[identifier]
        OldId = matches.libvirtId.get()
        
        if OldId != None:
            #print 'herere;',debugVm(matches)
            if OldId != identifier:
                if OldId in self.vmsbyId.keys():
                    if validIdentifier:
                        self.vmsbyId[identifier] = self.vmsbyId[OldId]
                    del self.vmsbyId[OldId]
        if not validIdentifier:
            return None
          
        if not identifier in self.vmsbyId.keys():
            self.vmsbyId[identifier] = matches
        
        #NewItem.update(self.vmsbyId[identifier])
        
        return self.vmsbyId[identifier]
    
        
            
    def _onUuidPost(self,NewItem):
        Uuid = NewItem.libvirtUuid.get()
        #print "_onUuidPost" ,Uuid
        validIdentifier = True
        if Uuid == None:
            validIdentifier = False
        matches = self.getVmMatch(NewItem)
        #print "matches", matches
        if matches == None:
            #debugVm(NewItem)
            if not validIdentifier:
                return None
            if not Uuid in self.vmsByUuid.keys():
                self.vmsByUuid[Uuid] = NewItem
            matches = self.getVmMatch(NewItem)
        
        for UuidNow in self.vmsByUuid.keys():
            CurrentUuId = self.vmsByUuid[UuidNow].libvirtUuid.get()
            if CurrentUuId != UuidNow:
                del self.vmsByUuid[UuidNow]
        if not Uuid in self.vmsByUuid.keys():
            self.vmsByUuid[Uuid] = matches
        #NewItem.update(self.vmsByUuid[Uuid])
        self.vmsByUuid[Uuid]
        return self.vmsByUuid[Uuid]
         

        
    def _onNamePost(self,NewItem):
        Name = NewItem.libvirtName.get()
        #print "_onNamePost" ,Name
        validIdentifier = True
        if Name == None:
            validIdentifier = False
        matches = self.getVmMatch(NewItem)
        if matches == None:
            vmModel = vmMdl()
            
            #vmModel.libvirtName.update(Name)
            Uuid = NewItem.libvirtUuid.get()
            if Uuid != None:
                vmModel.libvirtUuid.update(Uuid)
            ID = NewItem.libvirtId.get()
            if ID != None and ID != -1:
                vmModel.libvirtId.update(ID)
            #print "fddddddddddddddddddddddddd"
            #debugVm(NewItem)
            if validIdentifier:
                self.vmsbyName[Name] = NewItem
                matches = self.vmsbyName[Name]
            else:
                return None
        OldName = matches.libvirtName.get()
        if OldName != None:
            #print 'herere;',debugVm(matches)
            if OldName != Name:
                if OldName in self.vmsbyName.keys():
                    if validIdentifier:
                        self.vmsbyName[Name] = self.vmsbyName[OldName]
                    del self.vmsbyName[OldName]
        if not validIdentifier:
            return None
                
        #print "OldName",OldName,"Name",Name
        if not Name in self.vmsbyName.keys():
            self.vmsbyName[Name] = matches
        #NewItem.update(self.vmsbyName[Name])
        return self.vmsbyName[Name]
        

class LibVirtConnection:
    def __init__(self,connectionstring):
        self.connectionstring = str(connectionstring)
        self.connection = libvirt.open(self.connectionstring)
        



class LibVirtCnt(object):
    def __init__(self,connection,model):
        self.connection  = libvirt.open(str(connection))
        self.model = model
        # Default time to wait befor assuming Shutdown has failed.
        self.DefaultsShutdownTimeOut = 180
        
    def updateModel(self):
        RunningDomains = self.connection.listDomainsID()
        for LibVirtRunningDomainId in RunningDomains:
            hostPtr = self.connection.lookupByID(LibVirtRunningDomainId)
            Name = hostPtr.name()
            Uuid = hostPtr.UUIDString()
            ID = hostPtr.ID()
            vmModel = vmMdl()
            vmModel.libvirtName.update(Name)
            vmModel.libvirtUuid.update(Uuid)
            vmModel.libvirtId.update(ID)
            self.model.addVM(vmModel)
            
        #debugModel(self.model)
        DefinedDomains = set(self.connection.listDefinedDomains())
        for Name in DefinedDomains.difference(self.model.vmsbyName.keys()):
            vmModel = vmMdl()
            vmModel.libvirtName.set(Name)
            self.model.addVM(vmModel)
        for Name in self.model.vmsbyName.keys():
            hostPtr = self.connection.lookupByName(Name)
            Uuid = hostPtr.UUIDString()
            #print 'ssssssssss',Uuid
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
        
    def getLibVrtPtr(self,match):
        # Match is a VM from one of the lists
        Uuid = str(match.libvirtUuid.get())
        if Uuid in self.model.vmsByUuid.keys():
            #print 'found Uuid',Uuid
            ptr = self.connection.lookupByUUIDString(Uuid)
            if ptr != None:
                return ptr
        ID = match.libvirtId.get()
        if ID in self.model.lookupByID.keys():
            #print 'found ID',ID
            ptr = self.connection.lookupByID(LibVirtRunningDomainId)
            if ptr != None:
                return ptr
        Name = match.vmsbyName.get()
        if Name in self.model.vmsbyName.keys():
            #print 'found Name',Name
            ptr = self.connection.lookupByName(LibVirtRunningDomainId)
            if ptr != None:
                return ptr
        
    
    def vmStart(self,vm):
        #debugVm(vm)
        match = self.model.getVmMatch(vm)
        if match == None:
            return None
        #debugVm(match)
        self.updateModel()
        currentState = match.libvirtState.get()
        #VIR_DOMAIN_NOSTATE= 0: no state
        #VIR_DOMAIN_RUNNING= 1: the domain is running
        #VIR_DOMAIN_BLOCKED= 2: the domain is blocked on resource
        #VIR_DOMAIN_PAUSED= 3: the domain is paused by user
        #VIR_DOMAIN_SHUTDOWN= 4: the domain is being shut down
        #VIR_DOMAIN_SHUTOFF= 5: the domain is shut off
        #VIR_DOMAIN_CRASHED= 6: the domain is crashed
        if currentState in [1,2]:
            return match
        
        vmDetails = self.getLibVrtPtr(match)
        if vmDetails == None:
            return None
        MorToBeDone = True
        
        while MorToBeDone:
            
            rc = vmDetails.create()
            self.updateModel()
            currentState = match.libvirtState.get()
            if currentState in [1,2]:
                break
            time.sleep(1)
            if currentState in [1,2]:
                break


    def vmStop(self,vm):
        match = self.model.getVmMatch(vm)
        if match == None:
            return None
        self.updateModel()
        currentState = match.libvirtState.get()     
        #VIR_DOMAIN_NOSTATE= 0: no state
        #VIR_DOMAIN_RUNNING= 1: the domain is running
        #VIR_DOMAIN_BLOCKED= 2: the domain is blocked on resource
        #VIR_DOMAIN_PAUSED= 3: the domain is paused by user
        #VIR_DOMAIN_SHUTDOWN= 4: the domain is being shut down
        #VIR_DOMAIN_SHUTOFF= 5: the domain is shut off
        #VIR_DOMAIN_CRASHED= 6: the domain is crashed
        if not currentState in (1,2,3):
            return match
        counter = 0
        timeout = self.DefaultsShutdownTimeOut
        vmDetails = self.getLibVrtPtr(match)
        if vmDetails == None:
            return None
   
        while currentState in (1,2,3):
            counter += 1
            if counter < timeout:
                try:
                    rc = vmDetails.shutdown()
                    #print rc
                except libvirt.libvirtError, E:
                    currentState = match.libvirtState.get()
                    print "exception thrownddd" , E
                    vmDetails = self.getLibVrtPtr(match)
            else:
                self.logger.warning("Timed out shutting down domain")
                counter = 0
                #print "timed Out"
                rc = vmDetails.destroy()
                #print rc
            
            time.sleep(1)
            currentState = match.libvirtState.get()
            (currentState,maxMem,memory,nrVirtCpu,cpuTime) =  vmDetails.info()
            #print (currentState,maxMem,memory,nrVirtCpu,cpuTime) 
            match.libvirtState.update(currentState)
            match.libvirtMem.update(memory)
            match.libvirtMaxMem.update(maxMem)
            match.libvirtNrVirtCpu.update(nrVirtCpu)
            match.libvirtCpuTime.update(cpuTime)
                
        
def tester(conection,model):
    vmModel = vmMdl()
    vmModel.libvirtName.set(Name)
    model.vmsbyName[Name] = vmModel


def debugVm(Vm):
    message = "debugVm.Name:%s" % Vm.libvirtName.get()
    Uuid = Vm.libvirtUuid.get()
    if Uuid != None:
        message += "\nUuid:%s" % ( Uuid)
    ID = Vm.libvirtId.get()
    if ID != None:
        message += "\nID:%s" % ( ID)
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
        print "By Id %s?%s=%s" % (item,model.vmsbyId[item].libvirtName.get(),
            model.vmsbyId[item].libvirtId.get())

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
                        
    def libvirtImport(self,conectionStr):
       
        #print "libvirtImport",str(conection)
        
        self.conection = libvirt.open(str(conectionStr))
        mytestmodel = vhostMdl()
        libvirtCon = LibVirtCnt(conectionStr,mytestmodel)
        libvirtCon.updateModel()
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
            model = vmMdl()
            model.libvirtName.update(Name)
            match = mytestmodel.getVmMatch(model)
            libvirtdConnection = libvirtCon.getLibVrtPtr(match)
            cfgDict["HostName"]  = Name
            fred =  self.virtualHostGenerator(cfgDict)
        
        
        return True
