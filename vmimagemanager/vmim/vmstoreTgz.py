import os
import logging, logging.config
import commands

class vmStoreTgz(object):
    def __init__(self):
        self.log = logging.getLogger("vmStoreTgz.vmStoreTgz")
    
    def imageList(self):
        output = []
        if not os.path.isdir(self.storePath):
            self.log.warning("Store Path '%s' does not exist",self.storePath)
        else:
            for filename in os.listdir(self.storePath):
                output.append(filename)
        return output
    
    def imageStore(self,diskFacade,storeName):
        diskFacade.mount()
        cmd = "tar -zcspf %s/%s --exclude=lost+found -C %s ." % (self.storePath,storeName,diskFacade.target)
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
        ImageName = os.path.join(self.storePath,storeName)
        cmd = "tar -zxf %s --exclude=lost+found   -C %s" % (ImageName,diskFacade.target)   
        self.log.debug('cmd=%s' % (cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.log.error('Command "%s" Failed' % (cmd))
            self.log.error( 'rc=%s,output=%s' % (rc,cmdoutput))
            return False
        
        self.log.debug('rm Ok')
        return True

    def insertRestore(self,diskFacade,storeName):
        diskFacade.mount()
        InsertPath = os.path.join(self.storePath,storeName)
        if not os.path.isfile(InsertPath):
            self.log.error("Error: File %s is not found" % (InsertPath))
            return None
        cmd=  "tar -zxpsf %s --exclude=lost+found   -C %s" % (InsertPath,diskFacade.target)
        print cmd
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.log.error('Failed "%s"' % (cmd))
            self.log.error(cmdoutput)
            self.log.error('Return Code=%s' % (rc))
        return True
