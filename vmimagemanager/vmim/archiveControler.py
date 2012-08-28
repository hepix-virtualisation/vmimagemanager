
import logging


from archiveModel import archiveStore,archiveCollection,archiveInstance

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
        if len(files2make) > 0:
            ms = magic.open(magic.MAGIC_NONE)
            ms.load()
            for fileName in files2make:
                fullpath = "%s/%s" %(directory,fileName)
                NewArchive = archive()
                NewArchive.Name.update(fileName)
                NewArchive.Name.update(fileName)
                NewArchive.FullPath.update(fullpath)
                magicout = ms.file(fullpath)
                NewArchive.Magic.update(magicout)
                self.store.collection[directory].addArchive(NewArchive)
            ms.close()
        
        self.log.error("no directoryListing=%s" % (directory))
        
    def addDirectory(self,directory):
        if not os.path.isdir(directory):
            self.log.warning("Directory does not exist:%s" %(directory))
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
        cfgInserts = set()
        pthInfo = {}
        wooblebird = set()
        allHosts = Cfg.vmbyName.keys()
        if len(allHosts) == 0:
            cfgPaths = set(Cfg.defaultPathImages.get())
            cfgInserts = set(Cfg.defaultPathInserts.get())
        for host in allHosts:
            path = Cfg.vmbyName[host].CfgPathImages.get()
            cfgPaths.add(path)
            insert = Cfg.vmbyName[host].CfgPathInserts.get()
            cfgInserts.add(insert)
            hostpathmapping[host] = path
           
        #
        currentKeys = self.getSetOfPaths()
        keys2make = cfgPaths.difference(currentKeys)
        print "keys2make=%s" % (keys2make)
        
        for direct in keys2make:
            self.addDirectory(direct)
            self.directoryUpdate(direct)

    



class archiveCollectionView(object):
    def __init__(self,Collection):
        self.collection = Collection
        #print type(Collection)
        self.log = logging.getLogger("Events")
    
    def update(self):
        path = self.collection.path.get()
        if not os.path.isdir(path):
            self.log.warning("Invalid Directory:%s"  % (path))
            return None
        listDir = set(os.listdir(path))
        knownImageNames = set(self.collection.archives.keys())
        files2make = listDir.difference(knownImageNames)
        if len(files2make) > 0:
            ms = magic.open(magic.MAGIC_NONE)
            ms.load()
            for fileName in files2make:
                fullpath = "%s/%s" %(path,fileName)

                NewArchive = archiveInstance()
                NewArchive.Name.update(fileName)
                NewArchive.Name.update(fileName)
                NewArchive.FullPath.update(fullpath)
                magicout = ms.file(fullpath)
                NewArchive.Magic.update(magicout)
                self.collection.addArchive(NewArchive)
            ms.close()
        
            
    def imageInDirectory(self,ImageName):
        if ImageName == None:
            self.log.error("Image Names None")
            return None
        knownImageNames = self.collection.archives.keys()
        if not ImageName in knownImageNames:
            # Maybe the first time for cleared cache
            self.update()
            knownImageNames = self.collection.archives.keys()
        if not ImageName in knownImageNames:
            # Updated the directory and still not here:
            self.log.error("No model setsssssssssss")
            return None
        return self.collection.archives[ImageName]


class archiveStoreView(object):
    def __init__(self,store):
        self.store = store
        #print type(Collection)
        self.log = logging.getLogger("Events")

    def addDirectory(self,directory):
        if not os.path.isdir(directory):
            self.log.warning("Directory does not exist:%s" %(directory))
            return
        setOfPaths = self.store.collection.keys()
        if directory in setOfPaths:
            return self.store.collection[directory]
        output = archiveCollection()
        newinfo = self.store.addCollection(output)
        if newinfo == None:
            self.log.error("Failed to add:%s" %(output))
            return
        newinfo.path.update(directory)
        return newinfo

    def updateImagesCfg(self,config):
        self.log.warning("updateCfg not finished.") 
        hostNames = config.vmbyName.keys()
        hostMappingPathImages = {}
        for host in hostNames:
            path = config.vmbyName[host].CfgPathImages.get()
            if path == None:
                continue
            if not path in hostMappingPathImages.keys():
                hostMappingPathImages[path] = set([])
            hostMappingPathImages[path].add(host)
        known = set(self.store.collection.keys())
        found = set(hostMappingPathImages.keys())
        collections2make = found.difference(known)
        for collections in collections2make:
            self.addDirectory(collections)
        
        found = hostMappingPathImages
    def listImages(self):
        output = {}
        for item in self.store.collection.keys():
            print "listImages.item", item
            collectionstuff = archiveCollectionView( self.store.collection[item])
            collectionstuff.update()
            images = {}
            for image in self.store.collection[item].archives.keys():
                newArchive = self.store.collection[item].archives[image]
                fullPath = newArchive.FullPath.get()
                details = {'Path': newArchive.Directory.get(),
                    'fullPath': newArchive.FullPath.get(), 
                    'type': newArchive.Format.get(), 
                    'Name': newArchive.Name.get()}, 
                images[fullPath] = details
            output[item] = images
        return output
    
    def listImagesCompat(self):
        foundImages = set([])
        output = {}
        
        for item in self.store.collection.keys():
            collectionstuff = archiveCollectionView( self.store.collection[item])
            collectionstuff.update()
            images = {}
            for image in self.store.collection[item].archives.keys():
                newArchive = self.store.collection[item].archives[image]
                fullPath = newArchive.FullPath.get()
                details = {'Path': newArchive.Directory.get(),
                    'fullPath': newArchive.FullPath.get(), 
                    'type': newArchive.Format.get(), 
                    'Name': newArchive.Name.get()}
                images[fullPath] = details
            output = images
        return output
    

class archControler(object):
    def __init__(self,cfgModel):
        self.log = logging.getLogger("archControler")
        self.mdlImages = archiveStore()
        self.mdlExtracts = archiveStore()
        self.mdlInserts = archiveStore()
        
        self.viewImages = StorageView(self.mdlImages)
        self.viewExtracts = StorageView(self.mdlExtracts)
        self.viewInserts = StorageView(self.mdlInserts)
        self.mdlCfg = cfgModel
    
        
        

    def hasHost(self,hostname):
        keys = self.mdlCfg.vmbyName.keys()
        if not host in keys:
            self.log.error("Host not configured")
            return None
        return self.mdlCfg.vmbyName[hostname]
    
    def getImageMdl(self,host,image):
        
        keys = self.mdlCfg.vmbyName.keys()
        if not host in keys:
            self.log.error("Host not configured")
            return None
        ImagePath = self.mdlCfg.vmbyName[host].CfgPathImages.get()
        #self.mdlCfg.vmbyName[host].CfgPathExtracts.get()
        #self.mdlCfg.vmbyName[host].CfgPathInserts.get()
        if ImagePath == None:
            self.log.error("File Path for Image.")
            return None
        directoryDetails = self.viewImages.addDirectory(ImagePath)
        if directoryDetails == None:
            self.log.error("directoryDetails not found.")
            return None
        directoryView = archiveCollectionView(directoryDetails)
        return directoryView.imageInDirectory(image)
        
    def getExtractMdl(self,host,image):
        
        keys = self.mdlCfg.vmbyName.keys()
        if not host in keys:
            self.log.error("Host not configured")
            return None
        ImagePath = self.mdlCfg.vmbyName[host].CfgPathExtracts.get()
        #self.mdlCfg.vmbyName[host].CfgPathInserts.get()
        if ImagePath == None:
            self.log.error("File Path for Image.")
            return None
        directoryDetails = self.viewExtracts.addDirectory(ImagePath)
        if directoryDetails == None:
            self.log.error("directoryDetails not found.")
            return None
        directoryView = archiveCollectionView(directoryDetails)
        return directoryView.imageInDirectory(image)
        
    def getInsertsMdl(self,host,image):
        
        keys = self.mdlCfg.vmbyName.keys()
        
        if not host in keys:
            self.log.error("Host not configured")
            return None
        ImagePath = self.mdlCfg.vmbyName[host].CfgPathInserts.get()
        if ImagePath == None:
            self.log.error("File Path for Image.")
            return None
        directoryDetails = self.viewInserts.addDirectory(ImagePath)
        if directoryDetails == None:
            self.log.error("directoryDetails not found.")
            return None
        directoryView = archiveCollectionView(directoryDetails)
        return directoryView.imageInDirectory(image)
       
            
    
    def formatBtHostImage(self,host,image):
        if not hasattr(self,"mdlCfg"):
            self.log.error("No model set")
        
        self.mdlCfg.vmbyName.keys()
    def updateImages(self):
        # reads the models.
        outputer = archiveStoreView(self.mdlImages)
        outputer.updateImagesCfg(self.mdlCfg)
            
    def catImages2(self):
        outputer = archiveStoreView(self.mdlImages)
        output = outputer.listImages()
        return output

    def catImagesOldFormat(self):
        outputer = archiveStoreView(self.mdlImages)
        output = outputer.listImagesCompat()
        return output


    def catInserts(self):
        outputer = archiveStoreView(self.mdlImages)
        output = {'listImages': outputer.listImages()}
        return output
    def catExtracts(self):
        outputer = archiveStoreView(self.mdlImages)
        output = {'listImages': outputer.listImages()}
        return output


if __name__ == "__main__" :
    import time
    import sys
    from ConfigModel import vmModel , CfgModel
    from ConfigFileView import ConfigFile1
    logging.basicConfig(level=logging.INFO)
    thisCfgModel = CfgModel()
    config = ConfigFile1(thisCfgModel)
    config.upDateModel("/etc/vmimagemanager/vmimagemanager.cfg")
    sc = archControler(thisCfgModel)
    archive = sc.getImageMdl("vmname","fred.rsync")
    print "FullPath:%s" % (archive.FullPath.get())
    print "Magic:%s" % (archive.Magic.get())
    print "Format:%s" % (archive.Format.get())
    print "Directory:%s" % (archive.Directory.get())
    sc.updateImages()
    print "catImages", sc.catImages()
