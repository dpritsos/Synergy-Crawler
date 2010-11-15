

import Queue
import lxml.etree as etree
import lxml.html
from lxml.html.clean import Cleaner as html_clr
import lxml.html.soupparser as soup
from StringIO import StringIO

#Import the custom thread-pool
from threadpool import ThreadPool 

class LinkExtractor(object):
    
    def __init__(self, **kwargs):
        #Thread pool
        self.__tpool = ThreadPool(100)
        #ETREE queue for the parsed xhtml(s) to be stored
        self.__etree_q = Queue.Queue()
        self.__site_links_q = Queue.Queue()
        self.__media_links_q = Queue.Queue()
        self.__scripts_links_q = Queue.Queue()
        self.__undefined_links_q = Queue.Queue()
        #A callable for iterators to return the content of Queues   
        self.__ret_q = lambda q: q.empty() or q.get()
        #XPath objects for extracting the URL Types
        self.__extract_site_urls = etree.XPath("/body/a/href")
        self.__extract_media_urls = etree.XPath("//src")
        self.__extract_scripts_urls = etree.XPath("//src")
        
    def __inter__(self):
        """Be careful when use the LinkExtractor as iterator"""
        return self
    
    def next(self):
        """Be careful as iterotr this class returns etree(s) not URLs links"""
        if self.__etree_q.empty():
            raise StopIteration
        else:
            return self.__etree_q.get()
    
    def feed(self, xhtml):
        self.__tpool.dispatch(self.__parseto_xtree, xhtml, self.__callback_chain)
        
    def l_feed(self, xhtml_l):
        self.__tpool.map(self.__parseto_xtree,  self.__callback_chain, xhtml_l)
    
    def __callback_chain(self, etree):
        #Put the etree to the etree-queue for getting all the URLs available
        self.__etree_q.put(etree)
        #Find Links to other site and put them in the queue 
        site_links = self.__site_links(etree)
        if site_links: 
            self.__site_links_q.put(site_links)
        #Find Links of media and put them in the queue
        media_links = self.__media__links(etree)
        if media_links:
            self.__media_links_q.put(media_links)
        #Find Links of scripts and put them in the queue
        script_links = self.__media_links(etree)
        if script_links:
            self.__scripts_links_q.put(script_links)
        undefined_links = self.__undefined_links()
        if undefined_links:
            self.__undefined_links_q.put(undefined_links)
    
    def all_links(self, etree):
        links = list()
        for link in etree.iterlinks():
            links.append(link)
            
    def site_links(self, etree):
        pass
    
    def media_links(self, etree):
        pass
    
    def scripts_links(self, etree):
        pass
    
    def undefined_links(self, etree):
        pass
    
    def __site_links(self, etree):
        pass
    
    def __media_links(self, etree):
        pass
    
    def __scripts_links(self, etree):
        pass
    
    def __undefined_links(self, etree):
        pass
    
    def all_links_iter(self):
        try:
            etree = self.__etree_q.get(2)
        except Queue.Empty:
            return StopIteration
        else:    
            return etree.iterlinks()
    
    def site_links_iter(self):
        return iter( self.__ret_q(self.__site_links_q), True)
    
    def media_links_iter(self):  
        return iter( self.__ret_q(self.__media_links_q), True)
    
    def scripts_links_iter(self):
        return iter( self.__ret_q(self.__scripts_links_q), True)
    
    def undefined_links_iter(self):
        return iter( self.__ret_q(self.__undefined_links_q), True)
    
    def __parseto_xtree(self, xhtml_s):
        if isinstance(xhtml_s, dict):
            base_url = xhtml_s.pop("base_url", None)
            resolve_base = xhtml_s.pop("resolve_base", True)
            clean_xhtml = xhtml_s.pop("clean_xhtml", False)
        elif isinstance(xhtml_s, str):
            clean_xhtml = False
            base_url = None
        else:
            raise Exception("LinkExtractor.__parseto_xtree(): string or dictionary instance expected")
        if clean_xhtml:
            xhtml_clr = html_clr( scripts=True, javascript=True, comments=True, style=True,\
                                  links=True, meta=True, page_structure=False, processing_instructions=True,\
                                  embedded=True, annoying_tags=True, remove_unknown_tags=True )#meta=False because we need MetaInfo
            xhtml_s = xhtml_clr.clean_html(xhtml_s) 
        #The HTMLParser(s) should be defined in the thread (or process) when lxml.html.parser is dispatched into it 
        htmlparser = lxml.html.HTMLParser(recover=True, no_network=False) #recover mode and download DTD enabled    
        #Now parse the XHTML source    
        try:           
            etree = lxml.html.parse( StringIO(xhtml_s), parser=htmlparser, base_url=(self.due.base_url['scheme'] + "://" +self.due.base_url['netloc']) )
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
        