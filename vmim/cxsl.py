#!/usr/bin/python

import logging, logging.config



from os import path
from lxml import etree

try: from StringIO import StringIO
except ImportError:
    from io import BytesIO
    def StringIO(s):
        if isinstance(s, str): s = s.encode("UTF?8")
        return BytesIO(s)

import string
import sys
import getopt
import time
import re
try:
    from xml.etree.ElementTree import Element, SubElement, dump,tostring
except ImportError:
    from elementtree.ElementTree  import Element, SubElement, dump,tostring

import cvirthost

class virtualhostKvm(cvirthost.virtualhost):

    
    def XslSet(self,filename):
        pass

    def genXmlShouldExist(self):
    
    	defaultTransfrom = '''<xsl:stylesheet  version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
    <foo><xsl:value-of select="/domain/name" /></foo>
</xsl:template>
</xsl:stylesheet>'''
        
        domain = Element("domain")
        domain.set('type', "kvm")
        name = SubElement(domain, "name",)
        name.text = self.HostName
        memory = SubElement(domain, "memory")
        memory.text = str(self.DcgDict["memory"])
        cmemory = SubElement(domain, "currentMemory")
        cmemory.text = str(self.DcgDict["currentMemory"])
        vcpu = SubElement(domain, "vcpu")
        vcpu.text = str(self.DcgDict["vcpu"])
        os = SubElement(domain, "os")
        os_type = SubElement(os, "type",arch="x86_64",machine="pc")
        os_type.text = str("hvm")
        features = SubElement(domain, "features")
        acpi = SubElement(features, "acpi")
        apic = SubElement(features, "apic")
        pae = SubElement(features, "pae")
        
        clock = SubElement(domain, "clock",offset="utc")
        on_power_off  = SubElement(domain, "on_poweroff")
        on_power_off.text = "destroy"
        on_reboot = SubElement(domain, "on_reboot")
        on_reboot.text = "destroy"
        on_crash = SubElement(domain, "on_crash")
        on_crash.text = "destroy"
        devices = SubElement(domain, "devices")
        emulator = SubElement(devices, "emulator")
        emulator.text = "/usr/bin/kvm"
        emulator.text = "/usr/libexec/qemu-kvm"
        if "vmemulator" in  self.DcgDict.keys():
             emulator.text = self.DcgDict['vmemulator']
        self.RealiseDevice()
        self.DiskSubsystem.LibVirtXmlTreeGenerate(devices)
        self.logger.debug("DiskSubsystem %s" %(self.DiskSubsystem))
        self.Bridge = "br0"
        if hasattr(self,"Bridge") and hasattr(self,"HostMacAddress"):
             
             interface = SubElement(devices, "interface")
             interface.set('type', "bridge")
             mac_address = SubElement(interface, "mac",address='%s' % (self.HostMacAddress))
             source = SubElement(interface, "source",bridge='br0')
             target = SubElement(interface, "target",dev='vnet1')
        else:
            self.logger.debug("Has no mac address")
        
        #print "self.genXml=" + self.genXml()
        #print "genXmlShouldExist=" + text
        if "hosttransform" in  self.DcgDict.keys():
            libvirtxsltfile = str(self.DcgDict["hosttransform"])
            if path.isfile(libvirtxsltfile):
                defaultTransfrom = ""
                for line in open(libvirtxsltfile):
                    defaultTransfrom += line
                self.logger.debug( defaultTransfrom)
            else:
                self.logger.error("libvirtxslt file not found with path %s" % (libvirtxsltfile))
        else:
            self.logger.error("libvirtxslt file not defined.")
        xslt_tree   =  etree.XML(defaultTransfrom)
        transform = etree.XSLT(xslt_tree)
        f = StringIO(tostring(domain))
        doc = etree.parse(f)
        result = transform(doc)
        text = str(result)
        self.logger.debug(text)
        
        return text
