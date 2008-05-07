#!/usr/bin/python
#import ConfigParser

import os
import os.path
import string
import sys
import getopt
import commands
import time
import re
import ConfigParser, os
#for line in file('vmimagemanager.dict'):
#    cfg = eval(line)
InstallPrefix="/"

ConfigFile = ""

Fillocations = ['vmimagemanager.cfg', os.path.expanduser('~/.vmimagemanager.cfg'),InstallPrefix + '/etc/vmimagemanager/vmimagemanager.cfg']

for fileName in Fillocations:
    if True == os.path.isfile(fileName):
        ConfigFile = fileName
        break

if len(ConfigFile) == 0:
    ConfigFile = '/etc/vmimagemanager/vmimagemanager.cfg'
    

# Add lines to import a namespace and add it to the list of namespaces used
import logging, logging.handlers

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
    print ' -u, --up                          Start Virtual Box'
    print ' -d, --down                        Stop Virtual Box'
    print ' -l, --list-boxes                  List Virtual Boxes'
    print ' -L, --list-images                 List Virtual Box Images'
    print ' -k, --kill                        Kill Virtual Box'
    print ' -z, --tgz                         tar.gz Virtual Box Image'
    print ' -y, --rsync                       rsync Virtual Box Image [Default]'
    
def VitualHostsList():
    cmd="xm list | sed -e 's/  */ /g'"
    (rc,cmdoutput) = commands.getstatusoutput(cmd)
    output = {}
    counter = 0
    for line in cmdoutput.split('\n'):
        if counter > 0:
            section = line.split(' ')
	    if len(section) > 5:
	        #output[section[0]] = [section[1],section[2],section[3],section[4],section[5],section[6]]
		output[section[0]] = [section[1],section[2],section[3],section[4],section[5]]
        counter += 1
    return output

class virtualhost:
    def __init__(self):
        self.HostName = ""
        self.HostMacAddress = ""
        self.HostIp4Address = ""
        self.HostRootSpace = ""
        self.HostSwapSpace = ""
        self.ImageMode = ""
        self.PropertyInsertionsSet({})
        self.PropertyExtractionsSet({})
        self.PropertyImageRestoreNameSet("")
        self.PropertyImageStoreNameSet("")
        self.ImageStoreDir = ""
        self.ImageMode = "tgz"
    def PropertyHostNameSet(self, value):
        self.__HostName = value
        
    def PropertyHostNameGet(self):
        return self.__HostName
    def PropertyHostIdSet(self, value):
        self.__HostName = value
        
    def PropertyHostIdGet(self):
        return self.__HostName
        
    def PropertyHostIp4AddressSet(self, value):
        self.__HostIp4Address = value

    def PropertyHostIp4AddressGet(self):
        return self.__HostIp4Address

    def PropertyHostMacAddressSet(self, value):
        self.__HostMacAddress = value
        
    def PropertyHostMacAddressGet(self):
        return self.__HostMacAddress

    def PropertyHostSwapSpaceSet(self, value):
        self.__HostSwapSpace = value
    def PropertyHostSwapSpaceGet(self):
        return self.__HostSwapSpace

    def PropertyHostRootSpaceSet(self, value):
        self.__HostRootSpace = value
    def PropertyHostRootSpaceGet(self):
        return self.__HostRootSpace

    def PropertyMountSet(self, value):
        self.__Mount = value
    def PropertyMountGet(self):
        return self.Mount

    def PropertyImageModeSet(self, value):
        self.__ImageMode = value
        
    def PropertyImageModeGet(self):
        return self.__ImageMode

    def PropertyExtensionModeSet(self, value):
        self.__ExtensionMode = value
        
    def PropertyExtensionModeGet(self):
        return self.__ExtensionMode
    
    def PropertyExtractionsSet(self, value):
        self.__Extractions = value
        
    def PropertyExtractionsGet(self):
        return self.__Extractions
    
    def PropertyInsertionsSet(self, value):
        self.__Insertions = value
        
    def PropertyInsertionsGet(self):
        return self.__Insertions
     
    def PropertyImageRestoreNameSet(self, value):
        self.__ImageRestoreName = value
    def PropertyImageRestoreNameGet(self):
        return self.__ImageRestoreName
    
    def PropertyImageStoreNameSet(self, value):
        self.__ImageStoreName = value
    def PropertyImageStoreNameGet(self):
        return self.__ImageStoreName
    def PropertyImageStoreDirSet(self, value):
        print " got here"
        self.__ImageStoreDir = value
    def PropertyImageStoreDirGet(self):
        return self.__ImageStoreDir
    def delx(self): 
        del self.HostRootSpace
    HostName = property(PropertyHostNameGet, PropertyHostNameSet)
    HostId = property(PropertyHostIdGet, PropertyHostIdSet)
    HostIp4Address = property(PropertyHostIp4AddressGet, PropertyHostIp4AddressSet)
    HostMacAddress = property(PropertyHostMacAddressGet, PropertyHostMacAddressSet)
    HostSwapSpace = property(PropertyHostSwapSpaceGet, PropertyHostSwapSpaceSet)
    #HostRootSpace = property(PropertyHostRootSpaceGet, PropertyHostRootSpaceSet)
    HostRootSpace = property(PropertyHostRootSpaceGet, PropertyHostRootSpaceSet, delx, "I'm the HostRootSpace property.")
    ImageMode = property(PropertyImageModeGet, PropertyImageModeSet)
    ExtensionMode = property(PropertyExtensionModeGet, PropertyExtensionModeSet)
    Mount = property(PropertyMountGet, PropertyMountSet)
    Extractions = property(PropertyExtractionsGet, PropertyExtractionsSet)
    Insertions = property(PropertyInsertionsGet,PropertyInsertionsSet)
    ImageStoreName = property(PropertyImageStoreNameGet,PropertyImageStoreNameSet)
    ImageRestoreName = property(PropertyImageRestoreNameGet,PropertyImageRestoreNameSet)
    ImageStoreDir = property(PropertyImageStoreDirGet,PropertyImageStoreDirSet)
    
    def MountStatus(self):
        # Returns 0 for not mounted
        # Returns 1 for device mounted
        result = 0
        cmd="mount"
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            print 'mount "%s" Failed' % (Device)
            print 'rc=%s,output=%s' % (rc,cmdoutput)
            sys.exit(1)            
        #print "%s %s" % (self.PropertyHostRootSpaceGet(),self.PropertyMountGet())
        for mntline in cmdoutput.split("\n"):
            mntsplit = mntline.split(" ")
            if len(mntsplit) < 3:
                print "Error parsing mount command!"   
            #print mntsplit[2]    
            if mntsplit[0] == self.HostRootSpace or mntsplit[2] == self.Mount:
                # Assumes no VM host maps to same directory
                result = 1
        return result
    
    
    def MountImage(self):
        if self.MountStatus() == 1:
            return
        if not os.path.isdir(self.Mount):
            os.makedirs(self.Mount)
        cmd="mount %s %s" % (self.HostRootSpace,self.Mount)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            print 'Command "%s" Failed' % (cmd)
            print 'rc=%s,output=%s' % (rc,cmdoutput)
            sys.exit(1)            
        return

    def UnMount(self):
        if self.MountStatus() == 0:
            return
        if not os.path.isdir(self.Mount):
            os.makedirs(self.Mount)
        cmd="umount %s" % (self.HostRootSpace)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            print 'Command "%s" Failed' % (cmd)
            print 'rc=%s,output=%s' % (rc,cmdoutput)
            sys.exit(1)            
        return

    def MountTest(self):
        print "MountStatus %s" % (self.MountStatus())
        self.Mount()
        print "MountStatus %s" % (self.MountStatus())
        self.UnMount()
        print "MountStatus %s" % (self.MountStatus())
        sys.exit(0)    
    


        
    def ShutDown(self):
        domainList = VitualHostsList()
        if domainList.has_key(self.HostName):
            cmd = "xm shutdown %s" % self.HostName
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                print "Failed to shut down '%s'" % self.HostName
            else:
                for n in range(60):
                    time.sleep(1)
                    domainList = VitualHostsList()
                    if not domainList.has_key(self.HostName):
                        break
            domainList = VitualHostsList()
        if domainList.has_key(self.HostName):
            return False
        self.MountImage()
        return True
        

    def Kill(self):
        self.ShutDown()
        if domainList.has_key(self.HostName):
            cmd = "xm destroy %s" % (self.HostName)
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                print "Failed to shut down or kill '%s'" % self.HostName
                print cmdoutput
            return False
        return True
    
    def StorageDir(self):
        return self.ImageStoreDir
        
    def AvailableImage(self):
        restoreImage = self.PropertyImageRestoreNameGet()
        ImageName = "%s/%s" % (self.StorageDir(),restoreImage)
        if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
            return False
        return True
        
    def AvailableImageListGet(self):
        output = []
        for filename in os.listdir(self.ImageStoreDir):
            output.append(filename)
        return output


    
    def ExtractDir(self):
        return self.VmExtractsDir
        
    def AvailableExtract(self):
        if not os.path.isdir(self.ExtractDir()):
            return False
        for ext in self.PropertyInsertionsGet().keys():
            ImageName = "%s/%s" % (self.ExtractDir(),ext)
            if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
                return False
        return True        
    def AvailableExtractListGet(self):
        output = []
        for filename in os.listdir(self.ExtractDir()):
            output.append(filename)
        return output


    def StartUp(self):
        self.UnMount()
        domainList = VitualHostsList()
        if not domainList.has_key(self.HostName):
            cmd = "xm create %s  %s" % (self.HostName,self.vmcfgFile)
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                print "Failed to start up '%s'" % self.HostName
                print cmdoutput
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
    def Restart(self):
        self.ShutDown()
        self.StartUp()

    def StoreHost(self):
        ImageName = self.PropertyImageStoreNameGet()
        if not self.ShutDown():
            print 'Exiting cleanly'
            sys.exit(1)
        self.MountImage()
        cmd = ""
        storedir =  self.ImageStoreDir
        if not os.path.isdir(storedir):
            os.makedirs(storedir)
        if os.path.isdir('%s/%s' % (storedir,ImageName)):
            self.ImageMode = "rsync"
        if "tgz" == self.ImageMode:
            cmd = "tar -zcsf %s/%s --exclude=lost+found -C %s ." % (storedir,ImageName,self.Mount)
        if "rsync" == self.ImageMode:
            cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/%s/" % (self.PropertyMountGet(),storedir,ImageName)
        if cmd == "":
            print "Error: Failing to store images"
            sys.exit(1)
            
        #print "command='%s'" % (cmd)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            print 'The command failed "%s"' % (cmd)
            print cmdoutput
            print 'Return Code=%s' % (rc)
            
            return rc
        
        self.StartUp()
    def RestoreHost(self):
        restoreImage = self.PropertyImageRestoreNameGet()
        
        storedir =  self.ImageStoreDir
        ImageName = "%s/%s" % (storedir,restoreImage)
        
        if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
            print "Image '%s' not found these images where found in directory %s" % (restoreImage,storedir)
            for filename in os.listdir(storedir):
                print " %s" % (filename)
            sys.exit(1)
        
        if True == os.path.isfile(ImageName):
            self.PropertyImageModeSet("tgz")
        if True == os.path.isdir(ImageName):
            self.PropertyImageModeSet("rsync")
        if not self.ShutDown():
            print 'Exiting cleanly'
            sys.exit(1)
        if len(self.Mount) == 0 :
            print 'Failed to get mount point aborting "%s"' % (self.PropertyMountGet())
            sys.exit(1)
        
        if self.PropertyImageModeGet() == None:
            print "Warning: Could not find image type"
        else:
            cmd = ""
            if "tgz" == self.PropertyImageModeGet():
                self.UnMount()
                # Formatting is faster but we have a catch, 
                # With dcache must give it an option for XFS
                # cmdFormatFilter="mkfs.xfs %s"
                
                cmd=self.cmdFormatFilter % (self.HostRootSpace)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                if rc != 0:
                    print cmdoutput
                    print "command line failed running %s" % (cmd)
                    return -1
                self.MountImage()
                cmd = "rm -rf %s" % (self.Mount)
                (rc,cmdoutput) = commands.getstatusoutput(cmd)
                cmd = "tar -zxf %s --exclude=lost+found   -C %s" % (ImageName,self.Mount)
            if "rsync" == self.PropertyImageModeGet():
                cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/" % (ImageName,self.Mount)
            #print cmd
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                print 'Failed "%s"' % (cmd)
                print cmdoutput
                print 'Return Code=%s' % (rc)
                return rc
        filename="%s/sourceimage" % (self.Mount)
        fpvmconftemp = open(filename,'w+')
        fpvmconftemp.write("%s\n" % (ImageName))
        fpvmconftemp.close()
        
        

    def Extract(self):
        if not os.path.isdir(self.ExtractDir()):
            os.makedirs(self.ExtractDir())
        for ext in self.PropertyExtractionsGet().keys():
            target = "%s/%s" % (self.PropertyMountGet(),ext)
            if "tgz" == self.PropertyImageModeGet():
                selectedDir = self.PropertyExtractionsGet()[ext].strip('/')
                cmd = "tar -zcsf %s/%s --exclude=lost+found -C %s %s" % (self.ExtractDir(),ext,self.PropertyMountGet(),selectedDir)
            if "rsync" == self.PropertyImageModeGet():
                cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/%s %s/%s/" % (self.PropertyMountGet(),self.PropertyExtractionsGet()[ext],self.ExtractDir(),ext)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            print 'Failed "%s"' % (cmd)
            print cmdoutput
            print 'Return Code=%s' % (rc)
            
    def Insert(self):
        #print "Debug: PropertyInsertionsGet=%s" % (self.PropertyInsertionsGet())
        #print "Debug: ExtractDir=%s" % (self.ExtractDir())
        #print "Debug: MountDir=%s" % (self.PropertyMountGet())
        #print "Debug: PropertyImageModeGet=%s" % (self.PropertyImageModeGet())
        if not os.path.isdir(self.ExtractDir()):
            print "Error: Directory %s is not found" % (self.ExtractDir())
            sys.exit(1)
        for ext in self.PropertyInsertionsGet().keys():
            ImageName = "%s/%s" % (self.ExtractDir(),ext)
            if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
                print "Error: Insert '%s' is not found in '%s'" % (ext,self.ExtractDir())
                continue
            insertFormat = ""
            insertDone = False
            
            if True == os.path.isfile(ImageName):
                insertFormat = "tgz"
            if True == os.path.isdir(ImageName):
                insertFormat = "rsync"
            
            #print "insertFormat=%s" % (insertFormat)
            if "tgz" == insertFormat:
                cmd=  "tar -zxf %s --exclude=lost+found   -C %s" % (ImageName,self.PropertyMountGet())
            if "rsync" == insertFormat:
                cmd = "rsync -ra --numeric-ids --exclude=lost+found %s/ %s/%s" % (ImageName,self.PropertyMountGet(),self.PropertyInsertionsGet()[ext])
            #print cmd
            (rc,cmdoutput) = commands.getstatusoutput(cmd)
            if rc != 0:
                print 'Failed "%s"' % (cmd)
                print cmdoutput
                print 'Return Code=%s' % (rc)
        return 0        
            
    
class virtualHostContainer:
    def __init__(self):
        self.hostlist = []
        

    def LoadConfigFile(self,fileName):
        
        GeneralSection = "VmImageManager"
        HostListSection = "AvailalableHosts"
        RequiredSections = [GeneralSection]
        #RequiredSections = [GeneralSection,HostListSection]
        self.hostlist = []
        config = ConfigParser.ConfigParser()
        cmdFormatFilter = "mkfs.ext3 %s"
        config.readfp(open(fileName,'r'))
        #print config.sections()
        configurationSections = config.sections()
        for ASection in RequiredSections:
            if not ASection in configurationSections:
                print "Configuration file does not have a section '%s'"  % (ASection)
                sys.exit(1)
        
        cfgHosts = config.sections()

        
        newvmconfdir = config.get(GeneralSection,'vmconfdir')
        if len(newvmconfdir) == 0:
            print "Configuration file does not have a section '%s' with a key in it 'vmconfdir'" % (GeneralSection)
            sys.exit(1)
        self.vmconfdir = newvmconfdir
        
        newxenconftemplate = config.get(GeneralSection,'xenconftemplate')
        if len(newxenconftemplate) == 0:
            print "Configuration file does not have a section '%s' with a key in it 'vmconfdir'" % (GeneralSection)
            sys.exit(1)
        self.xenconftemplate = newxenconftemplate
        
        newXenImageDir = config.get(GeneralSection,'vmimages')
        if len(newXenImageDir) == 0:
            print "Configuration file does not have a section '%s' with a key in it 'vmimages'" % (GeneralSection)
            sys.exit(1)
        self.XenImageDir = newXenImageDir
        self.VmExtractsDir = newXenImageDir
        
        newVmExtractsDir = config.get(GeneralSection,'vmextracts')
        if len(newVmExtractsDir) == 0:
            print "Configuration file does not have a section '%s' with a key in it 'vmextracts' defaulting to '%s'" % (GeneralSection,GeneralSection)
            print "You probably want to set this variable."
        else:            
            self.VmExtractsDir = newVmExtractsDir
        
        
        
        if (config.has_option(GeneralSection, "formatFilter")):
            cmdFormatFilter = config.get(GeneralSection,'formatFilter')
        
        for aHost in cfgHosts:
                #print aHost
                isanImage = 0
                if (config.has_option(aHost, "vm_slot_enabled")):
                    isanImageStr = config.get(aHost,"vm_slot_enabled")
                    if (isanImageStr in (["Yes","YES","yes","y","On","on","ON","1"])):
                        isanImage = 1
                if isanImage > 0:
                
                    ThisVirtualHost =  virtualhost()
                    
                    if (config.has_option(aHost, "HostName")):
                        ThisVirtualHost.HostName  = config.get(aHost,"HostName")
                    if (config.has_option(aHost, "mac")):
                        ThisVirtualHost.HostMacAddress  = config.get(aHost,"mac")
                    if (config.has_option(aHost, "ip")):
                        ThisVirtualHost.HostIp4Address  = config.get(aHost,"ip")
                
                    if (config.has_option(aHost, "root")):
                        ThisVirtualHost.HostRootSpace  = config.get(aHost,"root")
                    if (config.has_option(aHost, "swap")):
                        ThisVirtualHost.HostSwapSpace  = config.get(aHost,"swap")
                    if (config.has_option(aHost, "vmimages")):
                        ThisVirtualHost.ImageStoreDir  = config.get(aHost,"vmimages")
                    else:
                        ThisVirtualHost.ImageStoreDir = self.XenImageDir + "/" + ThisVirtualHost.HostName
                    if (config.has_option(aHost, "mount")):
                        ThisVirtualHost.Mount  = config.get(aHost,"mount")
                    if (config.has_option(aHost, "vmcfg")):
                       
                        ThisVirtualHost.vmcfgFile  = config.get(aHost,"vmcfg")
                    else:
                        ThisVirtualHost.vmcfgFile = self.vmconfdir + "/" + ThisVirtualHost.HostName
                    if (config.has_option(aHost, "vmextracts")):
                       
                        ThisVirtualHost.VmExtractsDir  = config.get(aHost,"vmextracts")
                    else:
                        ThisVirtualHost.VmExtractsDir = self.VmExtractsDir
                    
                    
                    
                    if (config.has_option(aHost, "formatFilter")):
                        ThisVirtualHost.cmdFormatFilter  = config.get(aHost,"formatFilter")
                    else:
                        ThisVirtualHost.cmdFormatFilter = cmdFormatFilter
                    if not os.access(ThisVirtualHost.vmcfgFile,os.R_OK):
                        d = dict(
                            DomainRootDev=ThisVirtualHost.HostRootSpace,
                            DomainIp4Address=ThisVirtualHost.HostIp4Address,
                            DomainName=ThisVirtualHost.HostName,
                            DomainSwapDev=ThisVirtualHost.HostSwapSpace,
                            DomainMac=ThisVirtualHost.HostMacAddress
                        )
                        self.xenconftemplate
                        fpxenconftemp = open(self.xenconftemplate,'r')
                        newconfig = open(ThisVirtualHost.vmcfgFile,'w')
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
                                    
                        
                    self.hostlist.append(ThisVirtualHost)


if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:s:r:e:i:c:udlLhvkzyp", ["box=", "store=","restore=","extract=","insert=","config=","up","down","list-boxes","list-images","help","version","kill","tgz","rsync","print-config"])
    except:
        pass
    hostName = None
    storeImage = None
    restoreImage = None
    restoreExtension = None
    insertions = []
    extractions = []
    start = False
    stop = False
    kill = False
    actionList = []
    boxlist = []
    ParsedImage = None
    ParsedConfigFile = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        if o in ("-v", "--version"):
            cvsTag = "$Name:  $"
            cvsTag = cvsTag[7:-2]
            if cvsTag == "": 
                cvsTag = "Development"
                print "vmimagemanager.py version: " + cvsTag
            sys.exit(0)
        if o in ("-b", "--box"):
            if a != None:
                boxlist.append(a)
        if o in ("-s", "--store"):
            actionList.append("store")
            storeImage = a
        if o in ("-r", "--restore"):
            actionList.append("restore")
            restoreImage = a
        if o in ("-e", "--extract"):
            actionList.append("extract")
            extractions.append(a)
        if o in ("-i", "--insert"):
            actionList.append("insert")
            insertions.append(a)
        
        if o in ("-c", "--config"):
            ParsedConfigFile = a
        if o in ("-u", "--up"):
            actionList.append("up")
            start = True
        if o in ("-d", "--down"):
            actionList.append("down")
            stop = True
        if o in ("-k", "--kill"):
            actionList.append("kill")
            kill = True
        if o in ("-l", "--list-boxes"):
            actionList.append("list-boxes")
        if o in ("-L", "--list-images"):
            actionList.append("list-images")
        if o in ("-z", "--tgz"):
            ParsedImage = "tgz"
        if o in ("-y", "--rsync"):
            ParsedImage = "rsync"
        if o in ("-p", "--print-config"):
            actionList.append("print-config")
        
            
    
    #print "foof",ParsedConfigFile,"fd"
    HostContainer = virtualHostContainer()
    #hostlist = makeConfig()
    if ParsedConfigFile != "":
        #print "foof"
        ConfigFile = ParsedConfigFile
    if os.path.isfile(ConfigFile):
        HostContainer.LoadConfigFile(ConfigFile)
    else:
        print "Error: Configuration File '%s' not found" % (ConfigFile)
        sys.exit(1)
    
    if ParsedImage != None:
        HostContainer.ImageMode = ParsedImage
    processingBoxes = []
    if len(boxlist) >0:       
        notfound = False
        for box in boxlist:
            found = False
            for ahost in HostContainer.hostlist:
                if ahost.HostName == box:
                    found = True
                    processingBoxes.append(ahost)
            if found == False:
               notfound = True 
        if (notfound):
            print "box slot '%s' not found! The following Host slots exist." % (box)
            for ahost in HostContainer.hostlist:
                print ahost.HostName
            sys.exit(1) 
    #print "dslkjsdljsdlkjsd"
    if "list-boxes" in actionList:
        #print  HostContainer.hostlist
        for ahost in HostContainer.hostlist:
            print ahost.HostName
        sys.exit(0)
    if "print-config" in actionList:
        if cfg.has_key("hosts"):
            hostlist = ""
            for host in cfg["hosts"]:
                hostlist += ":" + host 
            print "HOSTS=%s" % (hostlist[1:])
        if cfg.has_key("general"):
            if cfg["general"].has_key("vmimages"):
                print "vmimages=%s" % (cfg["general"]["vmimages"])
            if cfg["general"].has_key("vmextracts"):
                print "vmextracts=%s" % (cfg["general"]["vmextracts"])
        sys.exit(0)
    
    if len(processingBoxes) == 0:
        print "Error: No Valid 'boxes' not stated on command line."
        sys.exit(1)
    
    if len(actionList) == 0:
        print "Error: No task selected"
        usage()
        sys.exit(1)
        
    
    if "list-images" in actionList:
        for box in processingBoxes:
            #print dir(box)
            for image in box.AvailableImageListGet():
                print image
        sys.exit(0)



    extractionsDict = {}
    for component in extractions:
        compdecp = component.split(':')
        if len(compdecp) != 2:
            print "Error: Extraction '%s' is invalid it must conatain name:dir" % (compdecp)
            usage()
            sys.exit(1)
        extractionsDict[compdecp[0]] = compdecp[1]
    #print "extractionsDict=%s" % (extractionsDict)
    insertionsDict = {}
    for component in insertions:
        compdecp = component.split(':')
        if len(compdecp) != 2:
            print "Error: Insertion '%s' is invalid it must conatain name:dir" % (compdecp)
            usage()
            sys.exit(1)
        insertionsDict[compdecp[0]] = compdecp[1]
    for box in processingBoxes:
        box.PropertyExtractionsSet(extractionsDict)
        box.PropertyInsertionsSet(insertionsDict)        
    #print "avirtualHost.PropertyExtractionsGet=%s" % (avirtualHost.PropertyExtractionsGet())
        if ParsedImage != None:
            box.PropertyImageModeSet(ParsedImage)
    
        box.PropertyImageRestoreNameSet(restoreImage)
        box.PropertyImageStoreNameSet(storeImage)
        
        imageList = []
        if "restore" in actionList:
            if not box.AvailableImage():
                print "Error: Image '%s' not found in directory '%s'" % (restoreImage,box.ImageStoreDir)
                for item in box.AvailableImageListGet():
                    print item
                sys.exit(1)
            
        if "insert" in actionList:
            if not box.AvailableExtract():
                insertions = box.PropertyInsertionsGet()
                for ext in box.PropertyInsertionsGet().keys():
                    ImageName = "%s/%s" % (box.ExtractDir(),ext)
                    if False == os.path.isfile(ImageName) and False == os.path.isdir(ImageName):
                        print "Error: Insert '%s' not found in directory '%s'" % (ext,box.ExtractDir())
                sys.exit(1)
    for box in processingBoxes:       
        for comp in actionList:
            if comp in ["kill"]:
                box.Kill()
        for comp in actionList:
            if comp in ["extract","insert","store","restore","down"]:
                box.ShutDown()
        for comp in actionList:
            if comp in ["extract"]:
                box.Extract()
        for comp in actionList:
            if comp in ["store"]:
                box.StoreHost()
        for comp in actionList:
            if comp in ["restore"]:
                box.RestoreHost()
        for comp in actionList:
            if comp in ["insert"]:
                box.Insert()
        for comp in actionList:
            if comp in ["extract","insert","store","restore","up"]:
                box.StartUp()
        
    



