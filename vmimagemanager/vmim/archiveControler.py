
import logging


from archiveModel import archiveStore,archiveCollection,archive

from vmstorefacard import vmStoreFacade
import magic
import os

class StorageView(object):
    def __init__(self,archiveStore):
        self.store = archiveStore
        self.log = logging.getLogger("Events")
    def returnFiileType(self,magicStr):
        cleanstring = str.strip(magicStr)
        splitString = dir(magicStr)
        splitLine = cleanstring.split(', ')
        if splitLine[0] == 'gzip compressed data':
            return "tgz"
        return None
    
    
    
    
    def getSetOfFiles(self,directory):
        output = set([])
        foundPaths = self.getSetOfPaths()
        if not directory in foundPaths:
            return output
        
        for item in self.store.collection[directory].archives.keys():
            output.add(item.Name)
        return output
    
    def getSetOfPaths(self):
        foundPaths = set([])
        for item in self.store.collection.keys():
            path = self.store.collection[item].path.get()
            foundPaths.add(path)
        return foundPaths
        
    def directoryUpdate(self,directory):
        
        setOfPaths = self.getSetOfPaths()
        if not directory in setOfPaths:
            return
        known = self.getSetOfFiles(directory)
        filelist = set([])
        if os.path.isdir(directory):
            filelist = set(os.listdir(directory))
        files2make = filelist.difference(known)
        for fileName in files2make:
            ms = magic.open(magic.MAGIC_NONE)
            ms.load()
            fullpath = "%s/%s" %(directory,fileName)
            NewArchive = archive()
            NewArchive.Name.update(fileName)
            NewArchive.Name.update(fileName)
            NewArchive.FullPath.update(fullpath)
            magicout = ms.file(fullpath)
            print magicout
            NewArchive.Magic.update(magicout)
            self.store.collection[directory].addArchive(NewArchive)
        
        self.log.error("no directoryListing=%s" % (directory))
    def addDirectory(self,directory):
        if not os.path.isdir(directory):
            return
        setOfPaths = self.getSetOfPaths()
        if directory in setOfPaths:
            return self.store.collection[directory]
        output = archiveCollection()
        output.path.update(directory)
        self.store.addCollection(output)
        return output

    def directoryDel(self,directory):
        self.log.error("no implemented")
        
    def updateCfg(self,Cfg):
        hostpathmapping = {}
        pathhostmapping = {}
        output = {}
        cfgPaths = set()
        pthInfo = {}
        wooblebird = set()
        allHosts = Cfg.vmbyName.keys()
        if len(allHosts) == 0:
            cfgPaths = set(Cfg.defaultPathImages.get())
        for host in allHosts:
            path = Cfg.vmbyName[host].CfgPathImages.get()
            cfgPaths.add(path)
            hostpathmapping[host] = path
           
        #
        currentKeys = self.getSetOfPaths()
        keys2make = cfgPaths.difference(currentKeys)
        print "keys2make=%s" % (keys2make)
        
        for direct in keys2make:
            self.addDirectory(direct)
            self.directoryUpdate(direct)
        keys2del = currentKeys.difference(cfgPaths)
        #print "keys2del=%s" % (keys2del)
        for direct in keys2del:
            self.directoryDel(direct)
        
        
        pathImages = {}
        StoreFacade = vmStoreFacade()
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        
        for path in pthInfo.keys():
            if not os.path.isdir(path):
                continue
            for fileName in os.listdir(path):
                fileDetails = { 'Name' : fileName, 'Path' : path}
                fullPath = os.path.join(path,fileName)
                fileDetails['fullPath'] = fullPath
                if os.path.isdir(fullPath):
                    fileDetails["type"] = "rsync"
                elif os.path.isfile(fullPath):
                    magicout = ms.file(fullPath)
                    fileType = self.returnFiileType(magicout)
                    if fileType != None:
                        fileDetails["type"] = fileType
                output[fullPath] = fileDetails
        ms.close()
        return output
        

class StorageControler(object):
    def __init__(self):
        self.model = archiveStore()
        self.view = StorageView(self.model)


    def updateFromCfgMdel(self,cfgModel):
        self.view.updateCfg(cfgModel)



if __name__ == "__main__" :
    import time
    import sys
    from ConfigModel import vmModel , CfgModel
    from ConfigFileView import ConfigFile1
    logging.basicConfig(level=logging.INFO)
    thisCfgModel = CfgModel()
    config = ConfigFile1(thisCfgModel)
    config.upDateModel("/etc/vmimagemanager/vmimagemanager.cfg")
    sc = StorageControler()
    sc.updateFromCfgMdel(thisCfgModel)
