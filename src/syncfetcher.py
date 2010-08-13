"""SynCFetcher: is the piece of code to build a concurrent HTML source fetching mechanism"""
from multiprocessing import Process
#importing urllib2 because urllib has been deprecated  
import urllib2
                
class SynCFetcher(Process):
    """SynCFetcherProcess:"""
    PROCESSNUM = 0
    def __init__(self, myPendingFetchQ, scannersQ, keepersQ, genreidentQ):
        Process.__init__(self)
        SynCFetcher.PROCESSNUM += 1
        self.myPendingFetchQ = myPendingFetchQ
        self.scannersQ = scannersQ 
        self.keepersQ = keepersQ
        self.gidentQ = genreidentQ #Added for enabling Genre Identification
        self.url = None
        self.headers = {
                        'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9)' 
                            }              
    def run(self):
        #print "SynCFetcher Process with PID:%s and PCN:%s - Engaged" % (current_process().pid, SynCFetcher.PROCESSNUM)
        while True:
            self.url = self.myPendingFetchQ.get()
            #print "SynCFetcher Process with PID:%s and PCN:%s - Terminated (None...to do)" % (self.pid, SynCFetcher.PROCESSNUM)    
            if self.url == None:
                print( "SynCFetcher Process with PID:%s and PCN:%s - Terminated (None...to do)" % (self.pid, SynCFetcher.PROCESSNUM) )
                SynCFetcher.PROCESSNUM -= 1
                return
            htmlTuple = self.__fetchsrc()
            #tmphtmlTuple = htmlTuple.next()
            self.scannersQ.put(htmlTuple)
            self.keepersQ.put(htmlTuple)
            self.gidentQ.put(htmlTuple) #Added for enabling Genre Identification       
    def __fetchsrc(self):
        htmlsrc = None
        socket = None
        charset = None
        try:
            rq = urllib2.Request(self.url, headers=self.headers)
            socket = urllib2.urlopen(rq)
            #while not socket:
            #    yield    
            htmlsrc = socket.read()
            charset = socket.info().getparam('charset')
            socket.close()
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
            rq = urllib2.Request(url, headers=self.headers)
            socket = urllib2.urlopen(rq)
            htmlsrc = socket.read()
            charset = socket.info().getparam('charset')
            socket.close()
        except:
            pass
        #Return a tuple of the HTML source, the character encoding of this source, and its URL 
        return (htmlsrc, charset, url) 
