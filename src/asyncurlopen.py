"""This is a Wrap Object for making the urllib (urllib2 in Python 2.x) GreenThreading and Asynchronous I/O enabled"""

from syncioscheduler import ReadWait, WriteWait

class AsyncUrlOpen:
    def __init__(self, usock):
        self.usock = usock
        
    def read(self, size=None):
        yield ReadWait(self.usock)
        yield self.usock.read(size)
        
    def readline(self, size=None):
        yield ReadWait(self.usock)
        yield self.usock.readline()
        
    def readlines(self, size=None):
        yield ReadWait(self.usock)
        yield self.usock.readlines()
        
    def info(self):
        yield ReadWait(self.usock)
        yield self.usock.info()
        
    def getcode(self):
        yield ReadWait(self.usock)
        yield self.usock.getcode()
        
    def geturl(self):
        yield ReadWait(self.usock)
        yield self.usock.geturl()
        
    def close(self):
        yield self.usock.close()
        
    def fileno(self):
        self.usock.fileno()
    

        

