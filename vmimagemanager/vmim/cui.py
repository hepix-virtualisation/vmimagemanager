

                 
#!/usr/bin/python

import logging, logging.config


import os
import os.path
import sys
import getopt
import commands
import time
import re
import ConfigParser, os


import cinterface 

import cvirthost


#for line in file('vmimagemanager.dict'):
#    cfg = eval(line)

# Add lines to import a namespace and add it to the list of namespaces used


#config = ConfigParser.ConfigParser()
#config.read(['vmimagemanager.cfg', os.path.expanduser('~/.vmimagemanager.cfg'),InstallPrefix + '/etc/vmimagemanager.cfg'])
def usage():
    print ' -h, --help                        Display help information'
    print ' -v, --version                     Version'
    print ' -c, --config                      Set config file'
    print ' -p, --print-config                Print config'
    print ' -b, --box       [host]            Set Virtual Box'
    print ' -s, --store     [image]           Store Virtual Box as parameter'
    print ' -r, --restore   [image]           Restore Virtual Box as parameter'
    print ' -i, --insert    [component]:[dir] insert component to a Virtual Box'
    print ' -e, --extract   [component]:[dir] extract component from a Virtual Box'
    print ' -D, --debug     [Level]           Set the debug  level'
    print ' -u, --up                          Start Virtual Box'
    print ' -d, --down                        Stop Virtual Box'
    print ' -l, --list-boxes                  List Virtual Boxes'
    print ' -L, --list-images                 List Virtual Box Images'
    print ' -k, --kill                        Kill Virtual Box'
    print ' -z, --tgz                         tar.gz Virtual Box Image'
    print ' -m, --locked                      List Locked slots'
    print ' -f, --free                        List Free slots.'
    print ' -U, --used                        List Used slots'
    print ' -y, --rsync                       rsync Virtual Box Image [Default]'
    print " -C, --cpu                         CPU cores"


def HostContainerLoadConfigFile(virtualHostContainer,fileName):

    GeneralSection = "VmImageManager"
    HostListSection = "AvailalableHosts"
    RequiredSections = [GeneralSection]
    #RequiredSections = [GeneralSection,HostListSection]
    virtualHostContainer.config = ConfigParser.ConfigParser()
    cmdFormatFilter = "mkfs.ext3 -L / %s"
    virtualHostContainer.config.readfp(open(fileName,'r'))
    #virtualHostContainer.logger.warning( config.sections()
    configurationSections = virtualHostContainer.config.sections()
    for ASection in RequiredSections:
        if not ASection in configurationSections:
            virtualHostContainer.logger.fatal( "Configuration file does not have a section '%s'"  % (ASection))
            return False

    virtualHostContainer.cfgHosts = virtualHostContainer.config.sections()
    virtualHostContainer.sharedImageStoreDir = True
    newVmExtractsDir = virtualHostContainer.config.get(GeneralSection,'vmextracts')
    if len(newVmExtractsDir) == 0:
        virtualHostContainer.VmExtractsDir = newXenImageDir
        virtualHostContainer.logger.warning("Configuration file does not have a section '%s' with a key in it 'vmextracts' defaulting to '%s'" % (GeneralSection,GeneralSection))
    else:            
        virtualHostContainer.VmExtractsDir = newVmExtractsDir

    virtualHostContainer.newvmconfdir = virtualHostContainer.config.get(GeneralSection,'vmconfdir')
    if len(virtualHostContainer.newvmconfdir) == 0:
        virtualHostContainer.logger.fatal( "Configuration file does not have a section '%s' with a key in it 'vmconfdir'" % (GeneralSection))
        return False
    ##virtualHostContainer.VmSlotVarDir = newvmconfdir
    virtualHostContainer.PropertyVmSlotVarDirSet(virtualHostContainer.newvmconfdir)
    #logging.warning( virtualHostContainer.__VmSlotVarDir
    newConfTemplateXen = virtualHostContainer.config.get(GeneralSection,'xenconftemplate')
    if len(newConfTemplateXen) == 0:
        virtualHostContainer.logger.fatal( "Configuration file does not have a section '%s' with a key in it 'xenconftemplate'" % (GeneralSection))
        return False
    virtualHostContainer.ConfTemplateXen = newConfTemplateXen

    new_xsl_file = virtualHostContainer.config.get(GeneralSection,'hosttransform')
    if len(new_xsl_file) > 0:
    
        virtualHostContainer.cfgDefault["hosttransform"] = new_xsl_file
    else:
        virtualHostContainer.logger.fatal( "Configuration file does not have a section '%s' with a key in it 'hosttransform'" % (GeneralSection))
        return False



    newXenImageDir = virtualHostContainer.config.get(GeneralSection,'vmimages')
    if len(newXenImageDir) >= 0:
        virtualHostContainer.XenImageDir = newXenImageDir
    else:
        virtualHostContainer.logger.fatal( "Configuration file does not have a section '%s' with a key in it 'vmimages'" % (GeneralSection))


    newVmExtractsDir = virtualHostContainer.config.get(GeneralSection,'vmextracts')
    if len(newVmExtractsDir) == 0:
        virtualHostContainer.VmExtractsDir = newXenImageDir
        logging.warning("Configuration file does not have a section '%s' with a key in it 'vmextracts' defaulting to '%s'" % (GeneralSection,GeneralSection))
    else:
    	
	virtualHostContainer.cfgDefault["vmextracts"] = newVmExtractsDir
        virtualHostContainer.VmExtractsDir = newVmExtractsDir

    VmMountsBaseDir = virtualHostContainer.config.get(GeneralSection,'mount')

    ThisKey = 'virthost'
    if (virtualHostContainer.config.has_option(GeneralSection, ThisKey)):
        virtualHostContainer.VmHostServer = str(virtualHostContainer.config.get(GeneralSection,ThisKey))
    else:
        default = 'qemu:///system'
        logging.warning("Configuration file does not have a section '%s' with a key in it 'virthost' defaulting to '%s'" % (GeneralSection,default))
        virtualHostContainer.VmHostServer = default


    if (virtualHostContainer.config.has_option(GeneralSection, "formatFilter")):
        cmdFormatFilter = virtualHostContainer.config.get(GeneralSection,'formatFilter')

    if (virtualHostContainer.config.has_option(GeneralSection, "vAlocatedMemory")):
        virtualHostContainer.cfgDefault["memory"] = virtualHostContainer.config.get(GeneralSection,'vAlocatedMemory')
    else:
        default = 2097152
        virtualHostContainer.logger.warning("Configuration file does not have a section '%s' with a key in it 'vAlocatedMemory' defaulting to '%s'" % (GeneralSection,default))
        virtualHostContainer.cfgDefault["memory"] = default

    if (virtualHostContainer.config.has_option(GeneralSection, "cAlocatedMemory")):
        virtualHostContainer.cfgDefault["currentMemory"] = virtualHostContainer.config.get(GeneralSection,'cAlocatedMemory')
    else:
        default = 2097152
        virtualHostContainer.logger.warning("Configuration file does not have a section '%s' with a key in it 'cAlocatedMemory' defaulting to '%s'" % (GeneralSection,default))
        virtualHostContainer.cfgDefault["currentMemory"] = default
    if (virtualHostContainer.config.has_option(GeneralSection, "vcpu")):
        virtualHostContainer.cfgDefault["vcpu"] = int(virtualHostContainer.config.get(GeneralSection,'vcpu'))
    else:
        virtualHostContainer.cfgDefault["vcpu"] = int(1)

    if (virtualHostContainer.config.has_option(GeneralSection, "bridge")):
        virtualHostContainer.cfgDefault["bridge"] = str(virtualHostContainer.config.get(GeneralSection,'bridge'))
    else:
    	default = 'br0'
        virtualHostContainer.cfgDefault["bridge"] = default
	logging.warning("Configuration file does not have a section '%s' with a key in it 'bridge' defaulting to '%s'" % (GeneralSection,default))
        
    return True
