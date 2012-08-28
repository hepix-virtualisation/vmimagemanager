




# I shoudl make my own GenKeyFunction Later
from observable import GenKey, Observable, ObservableDict

formatMap = { "directory" : "rsync" ,
    'gzip compressed data': "tgz"}


class archiveInstance(object):
    
    def __init__(self):
        self.Name = Observable(None)
        self.FullPath = Observable(None)
        self.Magic = Observable(None)
        self.Format = Observable(None)
        self.Directory = Observable(None)
        self.Magic.addCallback(self,self.OnMagic)
        
    def update(self,source):
        self.Name.update(source.Name.get())
        self.FullPath.update(source.FullPath.get())
        self.Magic.update(source.Magic.get())
        self.Format.update(source.Format.get())
        self.Directory.update(source.Directory.get())
    
    def OnMagic(self):
        format = None
        
        magicString = self.Magic.get()
        cleanstring = str.strip(magicString)
        splitLine = cleanstring.split(', ')
        
        if splitLine[0] in formatMap.keys():
            format = formatMap[splitLine[0]]
        self.Format.update(format)

class archiveCollection(object):
    def __init__(self):
        self.path = Observable(None)
        self.archives = ObservableDict()
    def addArchive(self,archiveAdd):
        if not isinstance(archiveAdd,archiveInstance):
            return
        CollectionKeys = set(self.archives.keys())
        newCollection = archiveInstance()
        newName = archiveAdd.Name.get()
        if newName in CollectionKeys:
            return self.archives[newName]
        newCollection.update(archiveAdd)
        newCollection.Directory.update(self.path.get())
        self.archives[newName] = newCollection
        return self.archives[newName]


class archiveStore(object):
    def __init__(self):
        self.collection = ObservableDict()
        self.collection.addCbPost(self,self.onachiveColection)
    
    def addCollection(self,archive):
        if not isinstance(archive,archiveCollection):
            return
        CollectionKeys = set(self.collection.keys())
        newCollection = archiveCollection()
        newCollectionPath = archive.path.get()
        if newCollectionPath in CollectionKeys:
            return self.collection[newCollectionPath]
        newCollection.path.update(newCollectionPath)
        self.collection[newCollectionPath] = newCollection
        return self.collection[newCollectionPath]
        
        
    def onachiveColection(self):
        # cleans up structure
        for item in self.collection.keys():
            itemName = self.collection[item].path.get()
            if itemName != item:
                print "shoudl not happen"
