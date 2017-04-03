#!/usr/bin/python

import logging
from xml.etree.ElementTree import Element, SubElement, tostring
import cvirthost


log = logging.getLogger(__name__)

class virtualhostKvm(cvirthost.virtualhost):


    def genXmlShouldExist(self):
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
        SubElement(features, "acpi")
        SubElement(features, "apic")
        SubElement(features, "pae")
        SubElement(domain, "clock",offset="utc")
        on_power_off  = SubElement(domain, "on_poweroff")
        on_power_off.text = "destroy"
        on_reboot = SubElement(domain, "on_reboot")
        on_reboot.text = "destroy"
        on_crash = SubElement(domain, "on_crash")
        on_crash.text = "destroy"
        devices = SubElement(domain, "devices")
        emulator = SubElement(devices, "emulator")
        emulator.text = "/usr/bin/kvm"
        
        self.RealiseDevice()
        self.DiskSubsystem.LibVirtXmlTreeGenerate(devices)
        self.logger.debug("DiskSubsystem %s" %(self.DiskSubsystem))
        if hasattr(self,"Bridge") and hasattr(self,"HostMacAddress"):
             log.debug("bridge=%s" % (self.Bridge))
             interface = SubElement(devices, "interface")
             interface.set('type', "bridge")
             SubElement(interface, "mac",address='%s' % (self.HostMacAddress))
             SubElement(interface, "source",bridge='%s' % (self.Bridge))
             SubElement(interface, "target",dev='vnet1')
        else:
            self.logger.debug("Has no mac address")
        serial = SubElement(devices, "serial")
        serial.set('type', "pty")
        SubElement(serial, "target",port="0")
        text = tostring(domain)
        self.logger.debug(text)
        return text
