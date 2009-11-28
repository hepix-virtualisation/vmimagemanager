#!/usr/bin/python

import logging, logging.config


import os
import os.path
import string
import sys
import getopt
import time
import re
      
import cvirthost


class virtualHostContainer:
    
    def __init__(self):
        self.hostlist = []
        self.cfgDefault = {}
        
        self.logger = logging.getLogger("vmimagemanager.virtualHostContainer") 
        
    def createVirtualhost(self,cfg):
        return cvirthost.virtualhost(cfg)
	
	
    def PropertyVmSlotVarDirSet(self, value):
        for aHost in self.hostlist:
            aHost.VmSlotVarDir = value
            self.logger.error("aHost.VmSlotVarDir=%s" % (aHost.VmSlotVarDir))
            aHost.PropertyVmSlotVarDirSet(value)
        self.__VmSlotVarDir = value
        
    def virtualHostGenerator(self,cfg):
        hostName = str(cfg["HostName"])
        index = -1
        for x in range (0 , len(self.hostlist)):
           
            if str(self.hostlist[x].HostName) == hostName:
               index= x
               break
            #print self.hostlist[x].HostName
        if index == -1:
            #self.logger.debug("creating %s as index= %s" % (self.hostlist,index))
            #self.logger.debug("cfg=%s" % (cfg))
	    
            newhost = self.createVirtualhost(cfg)
            #newhost.loadCfg(self.cfgDefault)
            newhost.Container = self
            newhost.HostName = hostName
            self.hostlist.append(newhost)
            return newhost
        else:
            self.hostlist[x].loadCfg(cfg)
            return self.hostlist[x]
                    
    def cfgHostsLoad(self):
        
        for cfgSection in self.cfgHosts:
                #print cfgSection
                isanImage = 0
                VmMountsBaseDir = "/tmp/vmimagemanager"
                if (self.config.has_option(cfgSection, "vm_slot_enabled")):
                    isanImageStr = self.config.get(cfgSection,"vm_slot_enabled")
                    if (isanImageStr in (["Yes","YES","yes","y","On","on","ON","1"])):
                        isanImage = 1
                if isanImage > 0:
                    cfgDict = {}
                    cfgDict["Connection"] = self.conection
                    #ThisVirtualHost =  virtualhost()
                    
                    if (self.config.has_option(cfgSection, "HostName")):
                        cfgDict["HostName"]  = self.config.get(cfgSection,"HostName")
                    if (self.config.has_option(cfgSection, "mac")):
                        cfgDict["HostMacAddress"]  = self.config.get(cfgSection,"mac")
                    if (self.config.has_option(cfgSection, "ip")):
                        cfgDict["HostIp4Address"]  = self.config.get(cfgSection,"ip")
                
                    if (self.config.has_option(cfgSection, "root")):
                        cfgDict["HostRootSpace"]  = self.config.get(cfgSection,"root")
                    if (self.config.has_option(cfgSection, "swap")):
                        cfgDict["HostSwapSpace"]  = self.config.get(cfgSection,"swap")
                    if (self.config.has_option(cfgSection, "hostdisk")):
                        cfgDict["HostDisk"]  = self.config.get(cfgSection,"hostdisk")
                    if (self.config.has_option(cfgSection, "partition")):
                        cfgDict["HostPartition"]  = self.config.get(cfgSection,"partition")
                        #print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxXX %s,%s" %(cfgDict["HostName"],cfgDict["HostPartition"] )
                    if (self.config.has_option(cfgSection, "vmimages")):
                        cfgDict["ImageStoreDir"]  = self.config.get(cfgSection,"vmimages")                
                    else:
                        if self.sharedImageStoreDir:
                            cfgDict["ImageStoreDir"] = self.XenImageDir
                        else:
                            #"XenImageDir"):
                            cfgDict["ImageStoreDir"] = os.path.join(self.XenImageDir , cfgDict["HostName"])
                        
                    if (self.config.has_option(cfgSection, "mount")):
                        cfgDict["MountPoint"]  = self.config.get(cfgSection,"mount")
                    else:
                        cfgDict["MountPoint"]  = os.path.join(VmMountsBaseDir ,cfgDict["HostName"])
                    
                    if (self.config.has_option(cfgSection, "hosttransform")):
                        cfgDict["hosttransform"]  = self.config.get(cfgSection,"hosttransform")
                    else:
                        cfgDict["hosttransform"]  = self.cfgDefault["hosttransform"]
                    
                    
                    if (self.config.has_option(cfgSection, "memory")):
                        cfgDict["memory"]  = self.config.get(cfgSection,"memory")
                    else:
                        cfgDict["memory"]  = self.cfgDefault["memory"]
                    
                   
                    if (self.config.has_option(cfgSection, "currentMemory")):
                        cfgDict["currentMemory"]  = self.config.get(cfgSection,"currentMemory")
                    else:
                        cfgDict["currentMemory"]  = self.cfgDefault["currentMemory"]
                    #print "tskjdfhksjldf=%s" % (cfgDict["Mount)
                    cfgDict["VmSlotVarDir"] = os.path.join(self.newvmconfdir , cfgDict["HostName"])
                    
                    cfgDict["XenCfgFile"]  =  os.path.join(cfgDict["VmSlotVarDir"] , "xen")
                    if (self.config.has_option(cfgSection, "vmcfg")):
                        cfgDict["XenCfgFile"]  = self.config.get(cfgSection,"vmcfg")
                    
                    cfgDict["LockFile"]  = os.path.join( self.newvmconfdir , cfgDict["HostName"] ,"lock")
                    #print cfgDict["LockFile
                    if (self.config.has_option(cfgSection, "vmlock")):
                       
                        cfgDict["LockFile"]  = self.config.get(cfgSection,"vmlock")
                    
                    if (self.config.has_option(cfgSection, "vmextracts")):
                       
                        cfgDict["VmExtractsDir"]  = self.config.get(cfgSection,"vmextracts")
                    else:
                        cfgDict["VmExtractsDir"] = self.VmExtractsDir
                    
                    
                    
                    if (self.config.has_option(cfgSection, "formatFilter")):
                        cfgDict["FormatFilter"]  = self.config.get(cfgSection,"formatFilter")
                    else:
                        pass
                        #cfgDict["FormatFilter"] = self.cmdFormatFilter
                    
                    if (self.config.has_option(cfgSection, "ConfTemplateXen")):
                        cfgDict["ConfTemplateXen"]  = self.config.get(cfgSection,"ConfTemplateXen")
                    else:
                        cfgDict["ConfTemplateXen"] = self.ConfTemplateXen
                    
                    
                    
                    try:      
                        newhost = self.virtualHostGenerator(cfgDict)
                        
                    except InputError, (instance):
                        print "Input Error %s"  % (repr(instance.Message))
        
