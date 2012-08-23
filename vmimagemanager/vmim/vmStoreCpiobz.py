from diskMounterAbstract import diskMounterBaseClass
import os
import logging, logging.config
import commands
import sys

import string


class vmStoreCpiobz(object):
    def __init__(self):
        self.log = logging.getLogger("vmStoreCpiobz.vmStoreCpiobz") 
     
    def imageStore(self,diskFacade,storeName):
        if self.storePath == None:
            self.log.error("storePath not set")
            return False
        diskFacade.mount()
        
            
        targetPath = os.path.join(self.storePath,storeName)
        #cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/%s/" % (diskFacade.target,self.storePath,storeName)
        #cmd = "tar -zcspf %s/%s --exclude=lost+found -C %s ." % (self.storePath,storeName,diskFacade.target)
        cmd = "cd %s; find . -print |cpio -o -Hnewc |bzip2 -9 -z -q -f > %s" % (diskFacade.target,targetPath)
        self.log.debug("running command %s" % ( cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.log.debug("command='%s'" % (cmd))
            message = 'The command failed "%s"\n' % (cmd)
            message += cmdoutput + '\nReturn Code=%s' % (rc)
            self.log.error(message)
            return rc
        self.log.debug("ran command.")
        return True
    def imageRestore(self,diskFacade,storeName):
        foundImages = self.imageList()
        if not storeName in foundImages:
            self.log.error("Image '%s' not found" % (storeName))
            self.log.error("These images exist '%s'" % (foundImages))
            return
        diskFacade.clear()
        diskFacade.mount()
        targetPath = os.path.join(self.storePath,storeName)
        cmd = "cd %s; bzcat %s |cpio -i" % (diskFacade.target,targetPath)
        self.log.debug('cmd=%s' % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.log.error('Command "%s" Failed' % (cmd))
            self.log.error( 'rc=%s,output=%s' % (rc,cmdoutput))
            return False
        
        self.log.debug('rm Ok')
        return True
    def imageList(self):
        output = []
        if self.storePath == None:
            return output
        if not os.path.isdir(self.storePath):
            self.log.warning("Store Path '%s' does not exist",self.storePath)
        else:
            for filename in os.listdir(self.storePath):
                output.append(filename)
        return output
 
    def insertRestore(self,diskFacade,storeName):
        diskFacade.mount()
        InsertPath = os.path.join(self.storePath,storeName)
        if not os.path.isfile(InsertPath):
            self.log.error("Error: File %s is not found" % (InsertPath))
            return None
        cmd = "cd %s; bzcat %s |cpio -i" % (diskFacade.target,InsertPath)
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.log.error('Failed "%s"' % (cmd))
            self.log.error(cmdoutput)
            self.log.error('Return Code=%s' % (rc))
        return True
        
    def insertStore(self,diskFacade,storeName,directory):
        diskFacade.mount()
        insertPath = os.path.join(diskFacade.target,directory.lstrip('/'))
        if not os.path.isdir(insertPath):
            self.log.error("Error: Extract target dir %s is not found" % (insertPath))
            return None
        destArchive = os.path.join(self.storePath,storeName)
        cmd = "cd %s; find %s -print |cpio -o -Hnewc |bzip2 -9 -z -q -f > %s" % (diskFacade.target,directory,destArchive)
        print cmd
        return 0
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            logging.error('Failed "%s"' % (cmd))
            logging.error(cmdoutput)
            logging.error('Return Code=%s' % (rc))
        return 0
