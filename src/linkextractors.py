

import Queue
import lxml.etree as etree
import lxml.html
from lxml.html.clean import Cleaner as html_clr
import lxml.html.soupparser as soup
from StringIO import StringIO

#Import the custom threadpool
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
        
    #def __inter__(self):
    #    return self
    
    #def next(self):
    #    if :
    #        raise StopIteration
    #    else:
    
    def feed(self, xhtml):
        self.__tpool.dispatch(self.__parseto_xtree, xhtml, self.__callback_chain)
        
    def l_feed(self, xhtml_l):
        self.__tpool.map(self.__parseto_xtree,  self.__callback_chain, xhtml_l)
    
    def __callback_chain(self, etree):
        #Find Links to other site and put them in the queue 
        site_links = self.site_links(etree)
        if site_links: 
            self.__site_links_q.put(site_links)
        #Find Links of media and put them in the queue
        media_links = self.media__links(etree)
        if media_links:
            self.__media_links_q.put(media_links)
        #Find Links of scripts and put them in the queue
        script_links = self.of_string()
        if script_links:
            self.__scripts_links_q.put(script_links)
        undefined_links = self.undefined_links()
        if undefined_links:
            self.__undefined_links_q.put(undefined_links)
    
    def all_links(self, etree):
        pass
            
    def site_links(self, etree):
        pass
    
    def media_links(self, etree):
        pass
    
    def scripts_links(self, etree):
        pass
    
    def undefined_links(self, etree):
        pass
    
    def all_links_iter(self):
        try:
            etree = self.__etree_q.get(2)
        except Queue.Empty:
            
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
    
    def __parseto_xtree(self, xhtml_s, clean_xhtml=False):
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
        #Return the etree just created
        return etree
        
        
        
            
            
        xhtml_troot = xhtml_t.getroot()
        try:
            xhtml_troot.make_links_absolute(self.due.base_url['url'], resolve_base_href=True)
                except:
                    return {'xtree' : None, 'parsing_errors' : parsing_errors}
                for i in xhtml_t.iterlinks():
                    pass
        return {'xtree' : xhtml_t, 'parsing_errors' : parsing_errors}
