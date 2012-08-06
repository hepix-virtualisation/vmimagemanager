import os
import logging, logging.config
import commands

class vmStoreRsync(object):
    def __init__(self):
        self.log = logging.getLogger("vmStoreRsync.vmStoreRsync") 
    
    def imageStore(self,diskFacade,storeName):
        
        diskFacade.mount()
        cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/%s/" % (diskFacade.target,self.storePath,storeName)
        self.log.debug("running command %s" % ( cmd))
        (rc,cmdoutput) = commands.getstatusoutput(cmd)
        if rc != 0:
            self.log.debug("command='%s'" % (cmd))
            message = 'The command failed "%s"\n' % (cmd)
            message += cmdoutput + '\nReturn Code=%s' % (rc)
            self.log.error(message)
            return rc
        self.log.debug("ran command.")

    def imageRestore(self,diskFacade,storeName):
        foundImages = self.imageList()
        if not storeName in foundImages:
            self.log.error("Image '%s' not found" % (storeName))
            self.log.error("These images exist '%s'" % (foundImages))
            return
        diskFacade.clear()
        diskFacade.mount()
        ImageName = os.path.join(self.storePath,storeName)
        cmd = "rsync -ra --delete --numeric-ids --exclude=lost+found %s/ %s/" % (ImageName,diskFacade.target)
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
 
