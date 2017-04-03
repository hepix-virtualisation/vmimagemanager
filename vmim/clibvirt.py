#!/usr/bin/python

import logging
import time
import libvirt
from vmLibVirtMdl import vmMdl 


log = logging.getLogger(__name__)


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
        self.log = logging.getLogger("clibvirt.LibVirtCnt")
    def updateModel(self):
        RunningDomains = self.connection.listDomainsID()
        for LibVirtRunningDomainId in RunningDomains:
            try:
                hostPtr = self.connection.lookupByID(LibVirtRunningDomainId)
            except libvirt.libvirtError as expt:
                self.log.warning("Exception thrown %s" % expt)
                continue
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
            ptr = self.connection.lookupByID(ID)
            if ptr != None:
                return ptr
        Name = match.vmsbyName.get()
        if Name in self.model.vmsbyName.keys():
            #print 'found Name',Name
            ptr = self.connection.lookupByName(Name)
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
            self.log.warning("No matching Vm found:%s"  % (vm))
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
                except libvirt.libvirtError as Expt:
                    currentState = match.libvirtState.get()
                    self.log.error("exception thrown" + str(Expt))
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
        return match
                
    def DefineHost(self,generatorXml):
        try:
            libvirtObj = self.conection.defineXML(generatorXml)
        except libvirt.libvirtError as expt:
            self.logger.error("generatorXml=%s" % (generatorXml))
            self.logger.debug(expt)
            return
        self.updateModel()
        
def tester(conection,model):
    vmModel = vmMdl()
    vmModel.libvirtName.set(Name)
    model.vmsbyName[Name] = vmModel



def debugModel(model):
    for item in model.vmsByUuid.keys():
        log.debug("By UUID %s?%s=%s,%s" % (item,model.vmsByUuid[item].libvirtName.get(),
            model.vmsByUuid[item].libvirtUuid.get(),
            model.vmsByUuid[item]))
    for item in model.vmsbyName.keys():
        log.debug("By Name %s?%s=%s" % (item,model.vmsbyName[item].libvirtName.get(),
            model.vmsbyName[item].libvirtUuid.get()))
    for item in model.vmsbyId.keys():
        log.debug("By Id %s?%s=%s" % (item,model.vmsbyId[item].libvirtName.get(),
            model.vmsbyId[item].libvirtId.get()))
