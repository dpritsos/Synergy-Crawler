
import Queue
import lxml.etree as etree
import lxml.html
from lxml.html.clean import Cleaner as html_clr
import lxml.html.soupparser as soup
from StringIO import StringIO
from urlparse import urlparse
import re
from multiprocessing import Pool, Process, Manager
from multiprocessing import Queue as pQueue

#Import the custom thread-pool
from threadpool import ThreadPool 


class XLinkExtractor(object):
    """                                    TO BE FIXED                         """
    def __init__(self, feed=True):
        #Thread pool
        self.__etree_q = Queue.Queue()
        self.__call_q = self.__etree_q 
        #XPath objects for extracting the URL Types
        self.__extract_site_urls = etree.XPath("/html/body//a/@href")
        self.__extract_media_urls = etree.XPath("//text()")
        self.__extract_scripts_urls = etree.XPath("//text()")
        
    def __iter__(self):
        """Be careful when use the XLinkExtractor as iterator"""
        return self
    
    def next(self):
        """Be careful: class as 'Iterator' returns etrees queue, by default, 
        or the one defined but the proper function bellow"""
        try:
            print "GET ITER"
            return self.__call_q.get(timeout=1) #timeout maybe should be trimmed 
        except Queue.Empty:
            print "EMPTY ITER" 
            raise StopIteration 
              
    def feed(self, xhtml):
        self.__tpool.dispatch(self.__parseto_xtree, xhtml, self.__callback_chain)
        
    def l_feed(self, xhtml_l):
        if isinstance(xhtml_l, list):
            self.__tpool.map(self.__parseto_xtree,  self.__callback_chain, xhtml_l)
        else:
            raise Exception("LinkExtractor.l_feed() Error: List() argument was expected")
               
    def all_links(self, etree):
        links = list()
        for link in etree.iterlinks():
            links.append(link)
            
    def sites_links(self, xhtml): 
        url_l = self._url_href.findall(xhtml['xhtml_s'])
        for i, url in enumerate(url_l):
            prsd_url = urlparse(url)
            if not prsd_url.netloc:
                url_l[i] = xhtml['base_url'] + url
        return url_l
    
    def media_links(self, xhtml):
        return None #to be Fixed
    
    def scripts_links(self, xhtml):
        return None #to be Fixed
    
    def undefined_links(self, xhtml):
        return None #to be fixed
    
    def __site_links(self, etree):
        return self.__extract_site_urls(etree)
    
    def __media_links(self, etree):
        return None #to be Fixed
    
    def __scripts_links(self, etree):
        return None #to be Fixed
    
    def __undefined_links(self, etree):
        return None #to be Fixed
       
    def __ret_q(self, q):
        """A callable for iterators to return the content of Queues"""
        if q.empty():
            return True 
        else:
            return q.get()
    
    def all_links_iter(self):
        try:
            etree = self.__etree_q.get(2)
        except Queue.Empty:
            return StopIteration
        else:    
            return etree.iterlinks()
       
    def __parseto_xtree(self, xhtml_s):
        #print "IN"
        if isinstance(xhtml_s, dict):
            base_url = xhtml_s.pop("base_url", None)
            #print "IN"
            print base_url
            resolve_base = xhtml_s.pop("resolve_base", True)
            clean_xhtml = xhtml_s.pop("clean_xhtml", False)
            xhtml_s = xhtml_s.pop("xhtml_s", None)
            assert xhtml_s, "LinkExtractor.__parseto_xtree() Error: Dictionary with <None> xhtml source"
        elif isinstance(xhtml_s, str):
            clean_xhtml = False
            base_url = None
        else:
            raise Exception("LinkExtractor.__parseto_xtree() Error: string or dictionary instance expected")
        if clean_xhtml:
            xhtml_clr = html_clr( scripts=True, javascript=True, comments=True, style=True,\
                                  links=True, meta=True, page_structure=False, processing_instructions=True,\
                                  embedded=True, annoying_tags=True, remove_unknown_tags=True )#meta=False because we need MetaInfo
            xhtml_s = xhtml_clr.clean_html(xhtml_s) 
        #The HTMLParser(s) should be defined in the thread (or process) when lxml.html.parser is dispatched into it 
        htmlparser = lxml.html.HTMLParser(recover=True, no_network=False) #recover mode and download DTD enabled    
        #Now parse the XHTML source    
        try:           
            etree = lxml.html.parse( StringIO(xhtml_s), parser=htmlparser)
        except Exception as e:
            print("LinkExtractor Error: %s" % e)
            print("LinkExtractor: Now Trying with the SOUP parser")
            try:
                etree = soup.parse(xhtml_s) 
            except Exception as e:
                raise Exception("LinkExtractor Error: %s" % e)
        if base_url:
            eroot = etree.getroot()
            try:
                eroot.make_links_absolute(base_url, resolve_base_href=resolve_base)
            except Exception as e:
                raise Exception("LinkExtractor.__parseto_xtree() while making links absolute Error: " % e)
        #Return the etree just created
        return etree
    

class LinkExtractor(object):
    
    def __init__(self, base_url=None, iterable=None):
        #Set self.base_url and choose the proper function to be used
        self.set_base(base_url)
        #iterable argument should ONLY be used when class instance is used as interator
        self.__iter = iterable.__iter__()  
        #Regular expression objects for extracting the URL/Link Types
        self.__url_a_href = re.compile('<a href="([^"]+)"')
        
    def __iter__(self):
        return self
    
    def next(self):
        try:
            return self.all_links( self.__iter.next() ) 
        except StopIteration: 
            raise StopIteration
    
    def set_base(self, base_url):
        #Define the proper functions to be used and define a class scope variable
        if base_url:
            self.base_url = base_url
            self.site_links = self.__site_links_base 
            self.media_links = self.__media_links_base 
            self.script_links = self.__script_links_base 
            self.undefined_links = self.__undefined_links_base  
        else: 
            self.site_links = self.__site_links 
            self.media_links = self.__media_links 
            self.script_links = self.__script_links 
            self.undefined_links = self.__undefined_links
        
    def all_links(self, xhtml):
        all_links = list()
        all_links.extend( self.site_links(xhtml) )
        all_links.extend( self.media_links(xhtml) )
        all_links.extend( self.scripts_links(xhtml) )
        all_links.extend( self.undefined_links(xhtml) )
        return all_links
    
    def __site_links(self, xhtml): 
        return self.__url_a_href.findall(xhtml)
            
    def __site_links_base(self, xhtml): 
        url_l = self.__url_a_href.findall(xhtml)
        for i, url in enumerate(url_l):
            prsd_url = urlparse(url)
            if not prsd_url.netloc:
                url_l[i] = self.base_url + url
        return url_l
    
    def __media_links(self, xhtml):
        return None #to be Fixed
    
    def __media_links_base(self, xhtml):
        return None #to be Fixed
    
    def __scripts_links(self, xhtml):
        return None #to be Fixed
    
    def __scripts_links_base(self, xhtml):
        return None #to be Fixed
    
    def __undefined_links(self, xhtml):
        return None #to be fixed
    
    def __undefined_links_base(self, xhtml):
        return None #to be fixed


class LinkExtractorTPool(object):
    """                                    TO BE FIXED                         """
    def __init__(self, feed=True):
        #Thread pool
        if feed:
            self.__tpool = ThreadPool(100)
            #ETREE queue for the parsed xhtml(s) to be stored
            self.__etree_q = Queue.Queue()
            self.__site_links_q = Queue.Queue()
            self.__media_links_q = Queue.Queue()
            self.__scripts_links_q = Queue.Queue()
            self.__undefined_links_q = Queue.Queue()
            #Define a default queue returned with the iterator or callable instance of this Class  
            self.__call_q = self.__etree_q 
        #XPath objects for extracting the URL Types
        self.__extract_site_urls = etree.XPath("/html/body//a/@href")
        self.__extract_media_urls = etree.XPath("//src")
        self.__extract_scripts_urls = etree.XPath("//src")
        self._url_href = re.compile('<a href="([^"]+)"')
        
        
    def __iter__(self):
        """Be careful when use the LinkExtractor as iterator"""
        return self
    
    def next(self):
        """Be careful: class as 'Iterator' returns etrees queue, by default, 
        or the one defined but the proper function bellow"""
        try:
            print "GET ITER"
            return self.__call_q.get(timeout=1) #timeout maybe should be trimmed 
        except Queue.Empty:
            print "EMPTY ITER" 
            raise StopIteration 
    
    def __call__(self):
        """Be careful: class as 'Callable' returns etrees queue, by default, 
        or the one defined but the proper function bellow"""
        try:
            return self.__call_q.get(timeout=1) #timeout maybe should be trimmed
        except Queue.Empty:
            return False 
    
    def feed(self, xhtml):
        self.__tpool.dispatch(self.__parseto_xtree, xhtml, self.__callback_chain)
        
    def l_feed(self, xhtml_l):
        if isinstance(xhtml_l, list):
            self.__tpool.map(self.__parseto_xtree,  self.__callback_chain, xhtml_l)
        else:
            raise Exception("LinkExtractor.l_feed() Error: List() argument was expected")
            
    
    def __callback_chain(self, etree):
        #Put the etree to the etree-queue for getting all the URLs available
        self.__etree_q.put(etree)
        #Find Links to other site and put them in the queue 
        site_links = self.__site_links(etree)
        if site_links: 
            self.__site_links_q.put(site_links)
        #Find Links of media and put them in the queue
        media_links = self.__media_links(etree)
        if media_links:
            self.__media_links_q.put(media_links)
        #Find Links of scripts and put them in the queue
        script_links = self.__media_links(etree)
        if script_links:
            self.__scripts_links_q.put(script_links)
        undefined_links = self.__undefined_links(etree)
        if undefined_links:
            self.__undefined_links_q.put(undefined_links)
    
    def all_links(self, etree):
        links = list()
        for link in etree.iterlinks():
            links.append(link)
            
    def sites_links(self, xhtml): 
        url_l = self._url_href.findall(xhtml['xhtml_s'])
        for i, url in enumerate(url_l):
            prsd_url = urlparse(url)
            if not prsd_url.netloc:
                url_l[i] = xhtml['base_url'] + url
        return url_l
    
    def media_links(self, xhtml):
        return None #to be Fixed
    
    def scripts_links(self, xhtml):
        return None #to be Fixed
    
    def undefined_links(self, xhtml):
        return None #to be fixed
    
    def __site_links(self, etree):
        return self.__extract_site_urls(etree)
    
    def __media_links(self, etree):
        return None #to be Fixed
    
    def __scripts_links(self, etree):
        return None #to be Fixed
    
    def __undefined_links(self, etree):
        return None #to be Fixed
       
    def __ret_q(self, q):
        """A callable for iterators to return the content of Queues"""
        if q.empty():
            return True 
        else:
            return q.get()
    
    def all_links_iter(self):
        try:
            etree = self.__etree_q.get(2)
        except Queue.Empty:
            return StopIteration
        else:    
            return etree.iterlinks()
    
    def sites_links_iter(self):
        self.__call_q = self.__site_links_q
        return self
    
    def media_links_iter(self):
        self.__call_q = self.__media_links_q
        return self  
    
    def scripts_links_iter(self):
        self.__call_q = self.__scripts_links_q
        return self
    
    def undefined_links_iter(self):
        self.__call_q = self.__undefined_links_q
        return self
    
    def close(self):
        self.__tpool.join_all()


class LinkExtractorPPool(LinkExtractor):
    
    def __init__(self, size=3, *args):
        LinkExtractor.__init__(*args)
        #Thread pool definition
        self.__pl_size = size
        self.__ppool = Pool(size)
        #ETREE queue for the parsed xhtml(s) to be stored
        self.__site_links_q = pQueue()
        self.__media_links_q = pQueue()
        self.__scripts_links_q = pQueue()
        self.__undefined_links_q = pQueue()
        #Define a default queue returned with the iterator or callable instance of this Class  
        self.__call_q = self.__etree_q 
    
    def __iter__(self):
        return self
           
    def next(self):
        try:
            print "GET ITER"
            return self.__call_q.get(timeout=1) #timeout maybe should be trimmed 
        except Queue.Empty:
            print "EMPTY ITER" 
            raise StopIteration 
    
    def __call__(self):
        """Be careful: class as 'Callable' returns etrees queue, by default, 
        or the one defined but the proper function bellow"""
        try:
            return self.__call_q.get(timeout=1) #timeout maybe should be trimmed
        except Queue.Empty:
            return False 
    
    def all_feed(self, xhtml):
        self.__all_links = self.__ppool.apply_async(self.all_links, xhtml)
    
    def url_feed(self, xhtml):
        self.__url_links = self.__ppool.apply_async(self.site_links, xhtml)
    
    def med_feed(self, xhtml):
        self.__media_links = self.__ppool.apply_async(self.media_links_links, xhtml)
    
    def scr_feed(self, xhtml):
        self.__script_links = self.__ppool.apply_async(self.script_links, xhtml)
    
    def und_feed(self, xhtml):
        self.__undif_links = self.__ppool.apply_async(self.undefined_links, xhtml)
    
    def get_all(self):
        return self.__all_links.get()
    
    def get_url(self):
        return self.__url_links.get()
    
    def get_med(self):
        return self.__med_links.get()
    
    def get_scr(self):
        return self.__scr_links.get()
    
    def get_und(self):
        return self.__und_links.get()
    
    def all_imap(self, xhtml_list):
        return self.__ppool.imap(self.all_links, xhtml_list, self.__pl_size)
    
    def url_imap(self, xhtml_list):
        return self.__ppool.imap(self.site_links, xhtml_list, self.__pl_size)
    
    def url_imap(self, xhtml_list):
        return self.__ppool.imap(self.site_links, xhtml_list, self.__pl_size)
    
    def url_imap(self, xhtml_list):
        return self.__ppool.imap(self.site_links, xhtml_list, self.__pl_size)
        
    def close(self):
        self.__ppool.close()
        self.__ppool.join()      

#Unit test    
if __name__ == "__main__":
    
    import urllib2
    
    rq = urllib2.Request("http://www.extremepro.gr", headers={ 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9)' })
    socket = urllib2.urlopen(rq)
    
    #URL to other Sites extraction
    link_extro = LinkExtractor(base_url="http://www.extremepro.gr/")
    
    src = socket.read()
    
    #String-Source as input
    #link_extro.feed( src )
    #List of Sources as input
    #link_extro.l_feed( [src] )
    #Dictionary of sources & metadata as input
    #link_extro.feed( {'xhtml_s' : src, 'base_url' : "http://www.extremepro.gr" } )
    #List of Dictionary of sources & metadata as input
    #link_extro.l_feed( [{'xhtml_s' : src, 'base_url' : "http://www.extremepro.gr" }] )
    
    #for links in link_extro.sites_links_iter():
    #    for link in links:
    #        print link
    
    #print("Iterations Done")
    
    #Media URL extraction
    
    #Script URL extraction
    
    #Undefined URL extraction
    
    #link_extro.close()
    
    print("Thank you and Goodbye!")
    
    
    
    
        