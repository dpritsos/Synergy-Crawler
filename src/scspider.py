"""Synergy-Crawler Spider:"""
import multiprocessing
from multiprocessing import Pool, Process, Value
#from eventlet.green import urllib2
import urllib2
from threading import Thread
import eventlet 
import lxml.etree 
import lxml.html
import lxml.html.soupparser as soup
from StringIO import StringIO
from collections import deque
from urlparse import urlparse 
import hashlib

from scdueunit import DUEUnit

import time

#Use this function only in case you want to have a Process.Pool() instead of Green.Pool()
#This is because Process.Pool can not have a class member function as argument 
def ffetchsrc(url):
    htmlsrc = None
    socket = None
    charset = None
    try:
        rq = urllib2.Request(url, headers={ 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9)' })
        socket = urllib2.urlopen(rq)
        htmlsrc = socket.read()
        charset = socket.info().getparam('charset')
        socket.close()
    except:
        pass
    #Return a tuple of the HTML source, the character encoding of this source, and its URL 
    return (htmlsrc, charset, url)


class SCSpider(Process): 
    """SCSpider:"""    
    Num = 0    
    
    def __init__(self, *sc_queues, **kwargs): 
        Process.__init__(self)
        SCSpider.Num += 1
        self.pnum = SCSpider.Num 
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
        self.xtrees_q = kwargs.pop("xtrees_q", None)
        #ext_due_q is a Queue of URL Links for an External DUE-Unit 
        self.ext_url_q = kwargs.pop("ext_due_q", None) 
    
    def run(self):
        """SCSpider's main function"""
        #Use the netloc (network locator) of the seed url as the base URL that this spider is working on
        url = urlparse(self.urls_l[0])
        hash = hashlib.md5()
        hash.update(url.scheme + "://" + url.netloc)
        hashkey = hash.hexdigest()
        self.due.setBase(url.scheme + "://" +url.netloc) 
        #Define 10000 Green Threads for fetching and lets see how it goes
        #fetchers_p = Pool(10) #eventlet.GreenPool(10000)
        fetchers_p = eventlet.GreenPool(500)
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
            if self.kill_evt.is_set():
                print("SCSpider Process (PID = %s - PCN = %s): Terminated" % (self.pid, self.pnum))
                SCSpider.Num -= 1
                break
            #Get one of the URLs which an other SCSpider has left to the ext_due_p and append it to the urls_l
            if self.ext_url_q != None:
                ext_url = self.ext_url_q.get(self.due.base_url['hashkey'],2)
            if ext_url:
                self.urls_l.append(ext_url)
            if self.urls_l == []:
                disk_keeper_thrd.join()
                self.due.savetofile()
                break
            tmp_urls_l = list() #SHOULD BE HERE
            #Start Processing WebPages (in fact sockets to them) which a Pool of GreenThreads is harvesting Asynchronously  
            #for page_soc in fetchers_p.imap_unordered(ffetchsrc, self.urls_l):
            for xhtml in fetchers_p.imap(self.fetchetree, self.urls_l):
                # ~~~~~~~~ Maybe the following code can be wrapped up from a few sub-Processes or Threads ~~~~~~~~
                if xhtml[0] == None:
                    #print("SPIDER %d of %d BASE %s" % (self.pnum, SCSpider.Num, self.due.base_url['url']))
                    #print("Empty Page : %s" % xhtml[1])
                    continue
                else:
                    xhtml_t = xhtml[0]
                #print("BLOCKS HERE????")
                count = 0
                for link in xhtml_t.iterlinks(): #xhtml_t.iterlinks():
                    if link[1] == 'href':
                        if link[2].find(".css") == -1 or link[2].find(".jpg") == -1 or link[2].find(".gif") == -1 or link[2].find(".png") == -1 or link[2].find("javascript:0")\
                        or link[2].find(".ico") == -1:
                            parsed_u = urlparse(link[2])
                            prsd_url = str(parsed_u.scheme + "://" + parsed_u.netloc)
                            if  prsd_url == self.due.base_url['url']:
                                seen = self.ust(link[2])
                                if not seen:
                                    count += 1 
                                    if self.due.seen_len() < 30:
                                        pass #print("SPIDER %d APPEND_LINKS %s SEEN-LIST %s" % (self.pnum, count, self.due.seen_len()))
                                    tmp_urls_l.append(link[2])
                                #else: means discarding this previously seen URL links
                            else:
                                #If the Base_urls is not the one this SCSpider is working on 
                                #try to pass it the other SCSpider Processes
                                if self.ext_url_q != None:
                                    #print("Sendto EXTERNAL LINKS: %s" % link[2])
                                    #if self.ext_url_q.full(self.due.base_url['hashkey']) == True:
                                        #print("FFFFFFFFFFFFFFFFFFFFUUUUUUUUUUUUUUUUUUCCCCCCCCCCCCCCCCCKKKKKKKKKKKKKKK Queue Botle neck\n")
                                    #elif self.ext_url_q.full(self.due.base_url['hashkey']) == None:
                                    #    pass #print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNOOOOOOOOOONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN\n")
                                        
                                    self.ext_url_q.put(link[2])
                                else: #if no one is expecting it
                                    seen = self.ust(link[2])
                                    if seen:
                                        tmp_urls_l.append(link[2])
                    #else:
                        #print("SPIDER %d of %d BASE %s" % (self.pnum, SCSpider.Num, self.due.base_url['url']))
                        #print("No Proper href found: %s" % link[2])      
                #Put xhtml tree to other queue for "Intelligent" processing if any
                #No need to send the urls found above, because in case this will be needed  
                #lxml (i.e. libxml2 written in C/C++ ) will do the job quite fast. So, at least we same some memory
                #However we sent the Errors have occurred during parsing 
                #if self.xtrees_q != None:
                #    self.xtrees_q.put({'xtree' : xhtml_t,
                #                       'parsing_errors' : parsing_errors})
                #for sc_q in self.scqs:
                #    sc_q.put({'xtree' : xhtml_t,
                #              'parsing_errors' : parsing_errors})
            #Now give the new URLs List back to the Fetcher GreenThreads 
            self.urls_l = tmp_urls_l
        #If this Process has to be terminated wait for the Disk_keeper Thread to finish its job and join
        disk_keeper_thrd.join(2)
        
    def fetch(self, url):
        #print("IN FETCH: " + str(self.headers))
        #print(url)
        rq = urllib2.Request(url, headers=self.headers)
        socket = urllib2.urlopen(rq)
        return socket
    
    def fetchsrc(self, url):
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
    
    def fetchetree(self, url):
        xhtml_s = None
        socket = None
        charset = None
        try:
            rq = urllib2.Request(url, headers=self.headers)
            socket = urllib2.urlopen(rq)
            xhtml_s = socket.read()
            charset = socket.info().getparam('charset')
            socket.close()
        except:
            pass
        parsing_errors = list()
        #try:           
        #xhtml_t = 1 #lxml.html.parse(page_soc, parser=htmlparser, base_url=self.due.base_url['url'])
        #except lxml.etree.XMLSyntaxError, error:
        #    print("PARSE ERROR: %s" % error)
        #    parsing_errors.append(error)
        #    try:
        #        xhtml_t = 1 #lxml.html.parse(page_soc, parser=htmlparser_r, base_url=self.due.base_url['url'])
        #    except:
        #        print("PARSE ERROR: %s" % error)
        #        parsing_errors.append(error)
        #        try:
        #            print('DA ZOUP')
        #            xhtml_t = 1 #lxml.html.soupparser.parse(page_soc)
        #        except:
        #            print("FUCKED-UP PAGE")
        #            parsing_errors.append("BeautifullSoup Failed")
        #            xhtml_t = lxml.etree.ElementTree(element=None)

        if not xhtml_s:
            return (None, url)
        if charset:
            try:
                xhtml_t = lxml.html.document_fromstring( str(xhtml_s.decode(charset)), base_url=self.due.base_url['url'] )
            except:
                #print("SPIDER %d of %d BASE %s" % (self.pnum, SCSpider.Num, self.due.base_url['url']))
                #print("FAULTY URL (encoding) : %s" % url)
                return (None, url)
        else:
            try:
                xhtml_t = lxml.html.document_fromstring( str(xhtml_s), base_url=self.due.base_url['url'] )
            except:
                #print("SPIDER %d of %d BASE %s" % (self.pnum, SCSpider.Num, self.due.base_url['url']))
                #print("FAULTY URL : %s" % url)
                return (None, url)
                #try:
                #    xhtml_t = soup.fromstring(page_soc[0])
                #except:
                #    print("SPIDER %d BASE %s" % (self.pnum, self.due.base_url['url']))
                #    print("FAULTY URL :")
                #    #print("FAULTY URL : %s" % page_soc[2])
                #    return
                
        xhtml_t.make_links_absolute(self.due.base_url['url'], resolve_base_href=True)    
                
        #Return the xhtml_t
        return (xhtml_t, url)
    
    def savedue(self):
        while True:
            self.due.acquire()
            while self.due.seen_len() < 5:
                self.due.wait()
            if not self.due.savetofile():
                print("FILE NOT SAVED - HALT")
                self.kill_evt.set()
                return
            #self.due.notify_all()
            self.due.release()
            
    def ust(self, link):
        self.due.acquire()
        seen = self.due.ust(link)
        self.due.notify_all()
        self.due.release()
        return seen

