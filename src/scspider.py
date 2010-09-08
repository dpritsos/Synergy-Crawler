"""Synergy-Crawler Spider:"""
import multiprocessing
from multiprocessing import Process
from eventlet.green import urllib2
from threading import Thread
import eventlet 
import lxml.etree 
import lxml.html
from StringIO import StringIO
from collections import deque
from urlparse import urlparse 
import hashlib

from scdueunit import DUEUnit

class SCSpider(Process): 
    """SCSpider:"""    
    Num = 0
    
    def __init__(self, *sc_queues, **kwargs): 
        Process.__init__(self)
        SCSpider.Num += 1
        if sc_queues:
            self.scqs = sc_queues
        else:
            self.scqs = list() 
        self.due = DUEUnit()
        #The self.headers keeps the HTTP headers Agent information for Masking the Crawler
        self.headers = { 'User-Agent' : kwargs.pop("spider_spoof_id", None) }
        if self.headers['User-Agent'] == None: 
            self.headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9)' }
        self.kill_evt = kwargs.pop("kill_evt", multiprocessing.Event().clear())
        self.urls_l = [ kwargs.pop("seed", None) ] 
        print(self.urls_l[0])
        self.xtrees_q = kwargs.pop("xtrees_q", None)
        #ext_due_q is a Queue of URL Links for an External DUE-Unit 
        self.ext_url_q = kwargs.pop("ext_due_q", None) 
    
    def run(self):
        """SCSpider's main function"""
        #Use the netloc (network locator) of the seed url as the base URL that this spider is working on
        url = urlparse(self.urls_l[0])
        hash = hashlib.md5()
        hash.update(url.scheme + url.netloc)
        hashkey = hash.hexdigest()
        self.due.setBase(url.scheme + url.netloc) 
        #Define 10000 Green Threads for fetching and lets see how it goes
        fetchers_p = eventlet.GreenPool(10000)
        #A thread is constantly checking the DUE seen dictionary is big enough to be saved on disk
        disk_keeper_thrd = Thread(target=self.savedue)
        disk_keeper_thrd.start()
        #The HTML Parsers with and without recover mode but the capability to download the Proper DTD always ON
        #In case the lxml.html.parser will dispatched to sub-processes or threads then 
        #the HTMLParser(s) should be defined within these sub-processes or threads
        htmlparser = lxml.etree.HTMLParser(recover=False, no_network=False) 
        htmlparser_r = lxml.etree.HTMLParser(recover=True, no_network=False)
        #From this line and below the loop this Process is starting 
        while True:
            #Checking for termination signal
            if self.kill_evt.is_set():
                print("SCSpider Process (PID = %s - PCN = %s): Terminated" % (self.pid, SCSpider.Num))
                SCSpider.Num -= 1
                break
            #Get one of the URLs which an other SCSpider has left to the ext_due_p and append it to the urls_l
            if self.ext_url_q != None:
                ext_url = self.ext_url_q.get(self.due.base_url['hashkey'],2)
            if ext_url:
                self.urls_l.append(ext_url)
            #Start Processing WebPages (in fact sockets to them) which a Pool of GreenThreads is harvesting Asynchronously  
            for page_soc in fetchers_p.imap(self.fetch, self.urls_l):
                # ~~~~~~~~ Maybe the following code can be wrapped up from a few sub-Processes or Threads ~~~~~~~~~
                parsing_errors = list()
                try:           
                    xhtml_t = 1 #lxml.html.parse(page_soc, parser=htmlparser, base_url=self.due.base_url['url'])
                except lxml.etree.XMLSyntaxError, error:
                    print("PARSE ERROR: %s" % error)
                    parsing_errors.append(error)
                    try:
                        xhtml_t = 1 #lxml.html.parse(page_soc, parser=htmlparser_r, base_url=self.due.base_url['url'])
                    except:
                        print("PARSE ERROR: %s" % error)
                        parsing_errors.append(error)
                        try:
                            print('DA ZOUP')
                            xhtml_t = 1 #lxml.html.soupparser.parse(page_soc)
                        except:
                            print("FUCKED-UP PAGE")
                            parsing_errors.append("BeautifullSoup Failed")
                            xhtml_t = lxml.etree.ElementTree(element=None)
                #xhtml_t.make_links_absolute(self.due.base_url, resolve_base_href=True) #Maybe I don't need this because base_url argument in .parse()
                tmp_urls_l = list()
                xhtml_s = page_soc.read() #lxml.html.tostring(xhtml_t.getroot()
                for link in lxml.html.document_fromstring( xhtml_s ).iterlinks(): #xhtml_t.iterlinks():
                    parsed_u = urlparse(link[2])
                    prsd_url = parsed_u.scheme + parsed_u.netloc
                    if  prsd_url == self.due.base_url['url']:
                        seen = self.ust(link[2])
                        if not seen:
                            tmp_urls_l.append(link[2])
                        #else: means discarding this previously seen URL links
                    else:
                        #If the Base_urls is not the one this SCSpider is working on 
                        #try to pass it the other SCSpider Processes
                        if self.ext_url_q != None:
                            self.ext_url_q.put(link[2])
                        else: #if no one is expecting it
                            seen = self.ust(link[2])
                            if seen:
                                tmp_urls_l.append(link[2])       
                #Put xhtml tree to other queue for "Intelligent" processing if any
                #No need to send the urls found above, because in case this will be needed  
                #lxml (i.e. libxml2 written in C/C++ ) will do the job quite fast. So, at least we same some memory
                #However we sent the Errors have occurred during parsing 
                if self.xtrees_q != None:
                    self.xtrees_q.put({'xtree' : xhtml_t,
                                       'parsing_errors' : parsing_errors})
                for sc_q in self.scqs:
                    sc_q.put({'xtree' : xhtml_t,
                              'parsing_errors' : parsing_errors})
            #Now give the new URLs List back to the Fetcher GreenThreads 
            del self.urls_l
            self.urls_l = tmp_urls_l
        #If this Process has to be terminated wait for the Disk_keeper Thread to finish its job and join
        disk_keeper_thrd.join()
        
    def fetch(self, url):
        print(self.headers)
        print(url)
        rq = urllib2.Request(url, headers=self.headers)
        socket = urllib2.urlopen(rq)
        return socket
    
    def fetchsrc(self):
        htmlsrc = None
        socket = None
        charset = None
        try:
            rq = urllib2.Request(self.url, headers=self.headers)
            socket = urllib2.urlopen(rq)
            htmlsrc = socket.read()
            charset = socket.info().getparam('charset')
            socket.close()
        except:
            pass
        #Return a tuple of the HTML source, the character encoding of this source, and its URL 
        return (htmlsrc, charset, self.url)
    
    def savedue(self):
        while True:
            self.due.acquire()
            while self.due.seen_len() <= 500:
                self.due.wait()
            self.due.savetofile()
            self.due.notify_all()
            self.due.release()
            
    def ust(self, link):
        self.due.acquire()
        self.due.ust(link)
        self.due.notify_all()
        self.due.release()

