"""Synergy-Crawler Spider:"""

import multiprocessing
from multiprocessing import Process
from threading import Thread
import eventlet
#import urllib2 #use it only in MultiProcessing/Threading not in GreenThreading
#import os 
from eventlet.green import urllib2, os #For GreenThreading not I don't know how it is behaving with MultiProcessing/Threading
import stat
import codecs
import lxml.html
from lxml.html.clean import Cleaner
import lxml.html.soupparser as soup
from StringIO import StringIO
from urlparse import urlparse 
import hashlib

from Queue import Queue

from scvectgen import SCVectGen

from BeautifulSoup import UnicodeDammit

#Load custom modules containing the Unit variants that the SCSpider consist of
from dueunits import DUEUnit
from linkextractors import LinkExtractor

import time

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
        self.link_extro = LinkExtractor(feed=False)
        #The self.headers keeps the HTTP headers Agent information for Masking the Crawler
        self.headers = { 'User-Agent' : kwargs.pop("spider_spoof_id", None) }
        if self.headers['User-Agent'] == None: 
            self.headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9)' }
        self.kill_evt = kwargs.pop("kill_evt", multiprocessing.Event().clear())
        self.urls_l = [ kwargs.pop("seed", None) ] 
        self.xtrees_q = kwargs.pop("xtrees_q", Queue()) #Use external Queue only for Interprocess Communication if any
        #ext_due_q is a Queue of URL Links for an External DUE-Unit 
        self.ext_url_q = kwargs.pop("ext_due_q", None)
        self.base_url_drop_none = kwargs.pop("base_url_drop_none", True)
        #urls_number_stop : Stop in a Default Values (if none given from user) for Politeness and because there is no point to have more samples of this site (I think)
        self.urls_number = kwargs.pop("urls_number_stop", 1000)  
        self.webpg_vect_tu = kwargs.pop("webpg_vect_tu", None)
        self.save_path = kwargs.pop("save_path", None)
        if self.save_path and not os.path.isdir(self.save_path):
            os.mkdir(self.save_path)
        self.file_counter = 0
        
    def run(self):
        """SCSpider's main function"""
        #Use the netloc (network locator) of the seed url as the base URL that this spider is working on
        url = self.urls_l[0]       
        self.due.setBase(url)
        #Define a process 
        gpool = eventlet.GreenPool(1000)
        #green_save_p = eventlet.GreenPool(1000)
        #A thread is constantly checking the DUE seen dictionary is big enough to be saved on disk
        disk_keeper_thrd = Thread(target=self.savedue)
        disk_keeper_thrd.start()
        """
        #Start a thread that will Analyse the pages for further process. In case none process uses this Analysis the thread will just not start at all
        if self.webpg_vect_tu: 
            scvectgen_t = SCVectGen(self.webpg_vect_tu, self.xtrees_q, kill_evt=self.kill_evt, save_path=self.save_path)
            scvectgen_t.start()
                    DEPRICATED is should be OUTSIDE the process
        """
        #From this line and below the loop this Process is starting 
        scanned_urls = 0 #Counter for the URLS that have been Followed by the Crawler - SHOULD BE HERE
        while True:
            #Termination Condition of this spider: They can be external signal(s), user defined conditions or when spider didn't finds any URLs related to the Crawling target
            #Terminate - External Signal or Functional problems occur while crawling
            if self.kill_evt.is_set():
                print("SCSpider Process (PID = %s - PCN = %s): Terminated" % (self.pid, self.pnum))
                SCSpider.Num -= 1
                break
            #Terminate - No more Urls to follow
            if self.urls_l == []:
                print("SCSpider Process (PID = %s - PCN = %s): Terminated - No more URL links to follow" % (self.pid, self.pnum))
                SCSpider.Num -= 1
                self.due.savetofile()
                self.kill_evt.set()
                break
            #Get one of the URLs which an other SCSpider has left to the ext_due_p and append it to the urls_l
            if self.ext_url_q != None:
                ext_url = self.ext_url_q.get(self.due.base_url['hashkey'],2)
                if ext_url:
                    self.urls_l.append(ext_url)
            tmp_urls_l = list() #SHOULD BE HERE
            #Start Processing WebPages (in fact sockets to them) which a Pool of GreenThreads is harvesting Asynchronously  
            #for page_soc in fetchers_p.imap_unordered(ffetchsrc, self.urls_l):
            for xhtml in gpool.imap(self.fetchsrc, self.urls_l):
                #Feed the link Extractor with the new-coming XHTML(s) if not empty
                if xhtml[0]:
                    #Expand the xhtml tree dictionary with some date for later process
                    xhtml_d = dict()
                    xhtml_d['xhtml_s'] = xhtml[0]       
                    xhtml_d['charset'] = xhtml[1]
                    xhtml_d['url_req'] = xhtml[2]
                    xhtml_d['url_resp'] = xhtml[3]
                    prsd_url = urlparse(xhtml[2])
                    xhtml_d['netloc'] = prsd_url.netloc
                    xhtml_d['base_url'] = str(prsd_url.scheme + "://" + prsd_url.netloc)
                    #print xhtml_d['base_url']
                    #print xhtml_d
                    #count += 1
                    #print count
                    #Save fetched xhtml 
                    self.save_xhtml(xhtml_d)
                    #Terminate - Some User condition reached
                    if scanned_urls > self.urls_number:
                        print("SCSpider Process (PID = %s - PCN = %s): Terminated - User Condition: Stop On %d Pages (%d have been followed) "\
                              % (self.pid, self.pnum, self.urls_number, scanned_urls))
                        SCSpider.Num -= 1
                        self.due.savetofile()
                        self.kill_evt.set()
                        break
                    else:
                        print("SAVED URLS: %d" % scanned_urls)
                        scanned_urls += 1
                    #Extract URL for next Sites
                    ##Feed LinkExtractor now - get later    
                    #self.link_extro.feed(xhtml_d)
                    ##Force LinkExtractor to return immediately     
                    for link in self.link_extro.sites_links(xhtml_d):
                        parsed_u = urlparse(link)
                        prsd_url = str(parsed_u.scheme + "://" + parsed_u.netloc)
                        baseurl = str(self.due.base_url['scheme'] + "://" +  self.due.base_url['netloc'])
                        if  prsd_url == baseurl:
                            seen = self.ust(link)
                            if not seen:                   
                                tmp_urls_l.append(link)
                            #else: means discarding this previously seen URL links
                            else:
                                pass
                else:
                    print("SPIDER %d of %d BASE %s" % (self.pnum, SCSpider.Num, self.due.base_url['netloc']))
                    print("Empty Page : %s" % xhtml[1])
                    
            #Get the Link lists form linkextractor.sites_links_iter() iterator - In case feed() or l_feed() have been used
            #for links in self.link_extro.sites_links_iter():
            #    for link in links:
            #        parsed_u = urlparse(link)
            #        prsd_url = str(parsed_u.scheme + "://" + parsed_u.netloc)
            #        baseurl = str(self.due.base_url['scheme'] + "://" +  self.due.base_url['netloc'])
            #        if  prsd_url == baseurl:
            #            seen = self.ust(link)
            #            if not seen:
            #                print "Not SEEN!"                    
            #                tmp_urls_l.append(link)
                        #else: means discarding this previously seen URL links
            #            else:
            #                pass
                            #If the Base_urls is not the one this SCSpider is working on, try to pass it the other SCSpider Processes
                            #if self.ext_url_q != None:
            #                self.ext_url_q.put(link)
                            #elif self.base_url_drop_none:
                            #    seen = self.ust(link)
                            #    if seen:
                            #        tmp_urls_l.append(link)
                            
            #Now give the new URLs List back to the Fetcher GreenThreads
            del self.urls_l #for Preventing Memory Leakage remove it if has no effect but delay of the inevitable 
            self.urls_l = tmp_urls_l
        #If this Process has to be terminated wait for the Disk_keeper Thread to finish its job and join
        self.due.acquire()
        #WAKE-UP disk_keeper thread in case still waiting
        self.due.notify_all()
        self.due.release()
        #self.link_extro.close()
        disk_keeper_thrd.join()
        
    def fetch(self, url):
        #print("IN FETCH: " + str(self.headers))
        #print(url)
        rq = urllib2.Request(url, headers=self.headers)
        socket = urllib2.urlopen(rq)
        return socket
    
    def fetchsrc(self, url_req):
        htmlsrc = None
        socket = None
        charset = None
        url_resp = None
        try:
            rq = urllib2.Request(url_req, headers=self.headers)
            socket = urllib2.urlopen(rq)
            htmlsrc = socket.read()
            charset = socket.info().getparam('charset')
            url_resp = socket.geturl()
            socket.close()
        except Exception as e:
            print("FETCH ERROR(urllib2): %s - URL: %s" % (e, url_req))
        #Return a tuple of the HTML source, the character encoding of this source, and its URL 
        return (htmlsrc, charset, url_req, url_resp)
    
    def save_xhtml(self, xhtml_d):
        assert os.path.isdir(self.save_path)
        ret_signal = True 
        self.file_counter += 1
        try:
            try:
                file = self.save_path + str(xhtml_d['netloc']) + "." + str(self.file_counter) + ".html"
                print file
                f = os.open( file, os.O_CREAT | os.O_WRONLY, stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            except Exception as e:
                #Stop the Process First and then raise the Exception with some extra info
                self.kill_evt.set()
                raise Exception("SCSpider error while Creating file - Error: %s" % e)
            #Place a file-object wrapper around the file Descriptor
            fobj = os.fdopen(f, "w", 1)       
            #Place an Encoding Wrapper to assure the file Writing to be performed with UTF-8 encoding
            #if xhtml_d['charset']:
            #    fenc = codecs.EncodedFile(fobj, xhtml_d['charset'])
            #else:
            fenc = fobj
        except Exception as e:
            print("SCSpider error while Creating file - Error: %s" % e)
            #Return None for the Spider to know that some error occurred for deciding what to do with it 
            ret_signal = None 
        else:
            try:
                fenc.write( xhtml_d['xhtml_s'] ) # Write the source to file
            except Exception as e:
                print("SCSpider Error while Writing file - Error: %s" % e)
                ret_signal = None
        finally:
            fenc.close()
            
        return ret_signal
    
    def savedue(self):
        while not self.kill_evt.is_set():
            self.due.acquire()
            while self.due.seen_len() < 1000:
                #This will force the thread to stop in case a global stop signal is given
                if self.kill_evt.is_set():
                    return
                #In case Seen Dictionary is still small Wait (i.e. Sleep)
                self.due.wait()
            if not self.due.savetofile():
                print("SCSPIDER: DUE FILE NOT SAVED - HALT")
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

