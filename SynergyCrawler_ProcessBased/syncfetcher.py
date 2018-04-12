"""SynCFetcher: is the piece of code to build a concurrent HTML source fetching mechanism"""
from multiprocessing.managers import BaseManager
from multiprocessing import Process, Pool, current_process
import HTMLParser
import urllib

class SynCFetcher(Process):
    """SynCFetcherProcess:"""

    PROCESSNUM = 0

    def __init__(self, myPendingFetchQ, scannersQ, keepersQ):
        Process.__init__(self)
        SynCFetcher.PROCESSNUM += 1
        self.myPendingFetchQ = myPendingFetchQ
        self.scannersQ = scannersQ
        self.keepersQ = keepersQ
        self.url = None

    def run(self):
        #print "SynCFetcher Process with PID:%s and PCN:%s - Engaged" % (current_process().pid, SynCFetcher.PROCESSNUM)
        while True:
            self.url = self.myPendingFetchQ.get()
            #if self.url == None:
            #    print "SynCFetcher Process with PID:%s and PCN:%s - Terminated (None...to do)" % (current_process().pid, SynCFetcher.PROCESSNUM)
            #    break
            htmlTuple = self._fetchsrc()
            self.scannersQ.put(htmlTuple)
            self.keepersQ.put(htmlTuple)

    def _fetchsrc(self):
        htmlsrc = None
        socket = None
        charset = None
        try:
            socket = urllib.urlopen(self.url)
            htmlsrc = socket.read()
            socket.close()
            charset = socket.info().getparam('charset')
        except:
            pass
        #Return a tuple of the HTML source, the character encoding of this source, and its URL
        return (htmlsrc, charset, self.url)

    def fetchsrc(self, url):
        """This is for external use... MAYBE it is USELESS"""
        #print "In fetch"
        htmlsrc = None
        socket = None
        charset = None
        try:
            socket = urllib.urlopen(url)
            htmlsrc = socket.read()
            socket.close()
            charset = socket.info().getparam('charset')
        except:
            pass
        #Return a tuple of the HTML source, the character encoding of this source, and its URL
        return (htmlsrc, charset, url)
