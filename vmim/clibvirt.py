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
                #print "errot=%s" %(e)
                if (e.get_error_code() == 42):
                    #print "sdfDSF"
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
        #print "libvirtImport" + str(dir(self.conection))
        #print self.conection.listDevices()
        #print self.conection.listDomainsID()
        self.KnownHosts = []
        libVirtNames = self.conection.listDefinedDomains()
        #print "libVirtNames=%s"  % (libVirtNames)
        TmpHostNames = []
        for libVritId in self.hostlist:
            TmpHostNames.append(libVritId.HostName)
        #print "TmpHostNames" + str(TmpHostNames)
         
        for Name in libVirtNames:
            if not Name in TmpHostNames:
                cfgDict = {}
                cfgDict["Connection"] = self.conection
                #if has(libVritId
                #sif not libVritId
                libvirtdConnection = self.conection.lookupByName(Name)
                cfgDict["HostName"]  = Name
                fred =  self.virtualHostGenerator(cfgDict)
                #print fred
                #Host.libvirtObj = libvirt.open(self.VmHostServer)
                #print "sdfsfhjkf"
                #self.hostlist.append(Host)
            #print len(self.hostlist)
        return True
