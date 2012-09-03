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

import ConfigFileViewLibVirtGen as cvirthost


from vmLibVirtMdl import vmMdl, vhostMdl 





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
        return match
                
        
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
