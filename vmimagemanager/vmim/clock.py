import logging, logging.config


import os
import os.path
import string
import sys
import getopt
import commands
import time
import re
import shutil

class DiscLocking:
    def __init__(self,LockFile):
        
        self.lockedByMeKnown = False
        self.lockedByOtherKnown = False
        self.LockFile = LockFile
    def __del__(self):
        self.Unlock()
    def IsLocked(self):
        if not os.path.isfile(self.LockFile):
            return False
        #print self.LockFile
        return True
    def LockOwners(self):
        if not self.IsLocked():
            return []
        fi  = open(self.LockFile, 'r')
        foundPids = []
        for line in fi:
            messgDict = {}
            splitline = line.split(" ")
            for split in splitline:
                keyval = split.split("=")
                value = int(keyval[1].strip(' "\n'))
                messgDict[keyval[0].strip()] = value
            foundPids.append(messgDict)
        fi.close()
        if (foundPids == []):
            os.remove(self.LockFile)
        self.logger.debug("DiscLocking foundPids=%s" % (foundPids))
        return foundPids
    def Lock(self):
        
        if (self.lockedByOtherKnown == True):
            return False
        
        if self.lockedByMeKnown:
            return True
        if self.IsLocked():
            if self.IsLockedByMe():
                return True
            #print "heher"
            return False
        #self.logger.error "can lock %s" % ( self.LockFile)
        lockfiledir = os.path.dirname(self.LockFile)
        if not os.path.isdir(lockfiledir):
            os.makedirs(lockfiledir)
        pid = os.getpid()
        newlockfileName = self.LockFile + ".new.%d5" % (pid)
        tmplockfileName = self.LockFile + ".tmp.%d5" % (pid)
        #print newlockfileName
        fi = open(newlockfileName, 'w')
        #msg = 'pid="%s" message="%s"\n' % (pid,self.message)
        msg = 'pid="%s"\n' % (pid)
        fi.write(msg)
        fi.close()
        if not os.path.isfile(self.LockFile):
            shutil.move(newlockfileName,self.LockFile)
            return self.IsLockedByMe()
        else:
            os.remove(newlockfileName)
            return False
        
    def IsLockedByMe(self):
        if self.lockedByOtherKnown:
            return False
        
        if self.lockedByMeKnown:
            return True
        pid = os.getpid()
        foundPids= self.LockOwners()
        if (len( foundPids ) == 0):
            #os.remove(self.LockFile)
            return False
        objdisc = foundPids[0]
        if objdisc["pid"] == pid:
            #print "wibble"
            self.lockedByMeKnown = True
            return True
        else:
            #print "processing results"
            self.lockedByOtherKnown = True
            self.lockedByMeKnown = False
            processlist = []
            output = commands.getoutput("ps -e")
            proginfo = string.split(output,"\n")
            for line in  proginfo:
                stripedLine = string.strip(line)
                FirstBit = string.split(stripedLine," ")
                ProcessNight = None
                try:
                    ProcessNight = int(FirstBit[0])
                    processlist.append(ProcessNight)
                except:
                    pass
            
            for owner in foundPids:
                #print ("owner=%s" % (owner['pid']))
                OwnerPid = owner["pid"]
                if OwnerPid in proginfo:
                    self.lockedByOtherKnown = True
            if not self.lockedByOtherKnown:
                os.remove(self.LockFile)
                return False
            return False
            
    def IsLockedStill(self):
        foundPids= self.LockOwners()
        if (len( foundPids ) == 0):
            return False
        pid = os.getpid()
        objdisc = foundPids[0]
        if objdisc["pid"] == pid:
            #print "wibble"
            self.lockedByMeKnown = True
            return True
        else:
            #print "processing results"
            self.lockedByOtherKnown = False
            self.lockedByMeKnown = False
            processlist = []
            output = commands.getoutput("ps -e")
            proginfo = string.split(output,"\n")
            for line in  proginfo:
                stripedLine = string.strip(line)
                FirstBit = string.split(stripedLine," ")
                ProcessNight = None
                try:
                    ProcessNight = int(FirstBit[0])
                    processlist.append(ProcessNight)
                except:
                    pass
            
            for owner in foundPids:
                #print ("owner=%s" % (owner['pid']))
                OwnerPid = owner["pid"]
                if OwnerPid in proginfo:
                    self.lockedByOtherKnown = True
            if self.lockedByOtherKnown:
                return True
            if os.path.isfile(self.LockFile):
                os.remove(self.LockFile)
            return False
            
    def Unlock(self):
        if self.lockedByOtherKnown:
            return False
        if self.lockedByMeKnown:
            if os.path.isfile(self.LockFile):
                os.remove(self.LockFile)
            self.lockedByMeKnown = False
            return True
        return False
