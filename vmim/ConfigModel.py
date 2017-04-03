
# I shoudl make my own GenKeyFunction Later
from observable import Observable, ObservableDict


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
        self.CfgDiskType = Observable(None)
        self.CfgPathImages = Observable(None)
        self.CfgPathExtracts = Observable(None)
        self.CfgPathInserts = Observable(None)

class CfgModel(object):
    def __init__(self):
        self.libvirtConStr = Observable(None)        
        self.defaultPathExtracts = Observable(None)
        self.defaultPathImages = Observable(None)
        self.defaultPathExtracts = Observable(None)
        self.defaultPathInserts = Observable(None)
        self.defaultPathMount = Observable(None)
        self.vmbyName = ObservableDict()
        
    


