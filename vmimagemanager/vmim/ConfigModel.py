
# I shoudl make my own GenKeyFunction Later
from observable import GenKey, Observable, ObservableDict


class vmModel(object):
    def __init__(self):
        self.CfgHostName = Observable(None)
        self.CfgRoot = Observable(None)
        self.CfgSwap = Observable(None)
        self.CfgMountPoint = Observable(None)
        self.CfgMac = Observable(None)
        self.CfgDiskImage = Observable(None)
        self.CfgDiskImagePartition = Observable(None)
        self.CfgListed = Observable(None)




class mainModel(object):
    def __init__(self):
        self.libvirtConStr = Observable(None)        
        self.defaultPathExtracts = Observable(None)
        self.defaultPathImages = Observable(None)
        self.defaultPathMount = Observable(None)
        self.vmbyName = ObservableDict()
        
    


