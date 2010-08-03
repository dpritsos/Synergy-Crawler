#synmother_client_manager

from multiprocessing.managers import BaseManager
from multiprocessing import Process, Pool, current_process
import HTMLParser
import urlparse
import hashlib

class ExtractLinks(HTMLParser.HTMLParser):
    def __init__(self, urldata):
        HTMLParser.HTMLParser.__init__(self)
        self.urldata = urldata
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.urldata.append(value)
    def handle_startendtag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    self.urldata.append(value)
       
class SynCScanner(Process):
    """SynCScanner Process:"""
    PROCESSNUM = 0
    def __init__(self, myPendingScanQ, urlLQ):
        Process.__init__(self)
        SynCScanner.PROCESSNUM += 1
        self.myPendingScanQ = myPendingScanQ
        self.urlLQ = urlLQ 
        self.htmlSrcTuple = None               
    def run(self):
        #print "SynCScanner Process with PID:%s and PCN:%s - Engaged" % (current_process().pid, SynCScanner.PROCESSNUM)
        while True:
            self.htmlSrcTuple = self.myPendingScanQ.get()
            if self.htmlSrcTuple == None:
                print "SynCScanner Process with PID:%s and PCN:%s - Terminated (None...to do)" % (current_process().pid, SynCScanner.PROCESSNUM)
                SynCScanner.PROCESSNUM -= 1
                return
            listURLs = self._extracturls()
            digestedURLsLL = self._url_hash(listURLs)
            self.urlLQ.put(digestedURLsLL)
            #self.urlLQ.put(self.listURLs)
            #print self.urlLQ.qsize()
            #print "Extract URLs - END"                   
    def _extracturls(self):
        #print "Extract URLs"
        urls = []
        htmlsrc, charset, parenturl = self.htmlSrcTuple
        if htmlsrc != None: 
            resulturls = []
            urlExtractor = ExtractLinks(resulturls)
            try:
                if charset == None:
                    urlExtractor.feed(htmlsrc)
                else:
                    urlExtractor.feed(htmlsrc.decode(charset))                  
            except HTMLParser.HTMLParseError:
                pass
            try:
                urlExtractor.reset() # I think close needs special treatment .close()
            except HTMLParser.HTMLParseError:
                urlExtractor.reset()
            #this piece of code forms the URIs to full URLs by joining the 
            #parenturl with the network location free URLs extracted          
            for i in xrange(len(resulturls)): #replacing range() for performance reasons
                urlres = urlparse.urlparse(resulturls[i], "http")
                if urlres.netloc == "":
                    resulturls[i] = urlparse.urljoin(parenturl, resulturls[i])
                urls.extend(resulturls)        
        return urls
    def _url_hash(self, listURLs):
        digestedURLsLL = list()
        for i in xrange(len(listURLs)):#replacing range() for performance reasons 
            hash = hashlib.md5()
            hash.update(listURLs[i])
            digestedURLsLL.append( [hash.digest(), listURLs[i]] )
        return digestedURLsLL
            
            
            
            
                   
