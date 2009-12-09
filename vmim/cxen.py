#!/usr/bin/python

import logging, logging.config


import os
import os.path
import string
import sys
import getopt
import commands
import time
import re

from xml.etree.ElementTree import Element, SubElement, dump,tostring




class vmControlXen:
    def StartUp(self):
        self.DiskSubsystem.ImageUnMount()
        self.DiskSubsystem.UnLock()
        if not os.access(self.XenCfgFile,os.R_OK):
            d = dict(
                DomainRootDev=self.HostRootSpace,
                DomainIp4Address=self.HostIp4Address,
                DomainName=self.HostName,
                DomainSwapDev=self.HostSwapSpace,
                DomainMac=self.HostMacAddress
            )
            directory = os.path.dirname( self.XenCfgFile)
            if not os.path.isdir(directory):
                try:
                    os.makedirs(directory)
                except:
                    logging.error("could not create directory '%s'" %(directory))
                    sys.exit(1)
            fpxenconftemp = open(self.ConfTemplateXen,'r')
            newconfig = open(self.XenCfgFile,'w')
            for line in fpxenconftemp:
                subline = line
                #print line
                try:
                    newconfig.write(string.Template(line).safe_substitute(d))
                except:
                    for key in d.keys():
                        subline = subline.replace("${%s}" % (key), d[key])
                    newconfig.write(subline)
            newconfig.close()
            fpxenconftemp.close()
                                    
        domainList = VitualHostsList()
        if not domainList.has_key(self.HostName):
            cmd = "xm create %s  %s" % (self.HostName,self.XenCfgFile)
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error("Failed to start up '%s'" % self.HostName)
                logging.warning(cmdoutput)
            else:
                for n in range(60):
                    time.sleep(1)
                    domainList = VitualHostsList()
                    if domainList.has_key(self.HostName):
                        break
            domainList = VitualHostsList()
        if not domainList.has_key(self.HostName):
            return False
        return True
    def ShutDown(self):
        domainList = VitualHostsList()
        if domainList.has_key(self.HostName):
            cmd = "xm shutdown %s" % self.HostName
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error("Failed to shut down '%s'" % self.HostName)
            else:
                for n in range(60):
                    time.sleep(1)
                    domainList = VitualHostsList()
                    #print domainList
                    if not domainList.has_key(self.HostName):
                        break
            domainList = VitualHostsList()
        if domainList.has_key(self.HostName):
            return False
        self.DiskSubsystem.PartitionsOpen()
        self.DiskSubsystem.ImageMount()
        return True
        

    def Kill(self):
        self.ShutDown()
        if domainList.has_key(self.HostName):
            cmd = "xm destroy %s" % (self.HostName)
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                logging.error("Failed to shut down or kill '%s'" % self.HostName)
                self.logger.info(cmdoutput)
            return False
        return True

        
