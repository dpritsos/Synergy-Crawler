


from Queue import Queue
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
        self.__etree_q = Queue()
        self.__extract_txt = etree.XPath("//text()")
        
    def __inter__(self):
        return self
    
    def next(self):
        if :
            raise StopIteration
        else:
    
    def feed(self, xhtml):
        self.__tpool.map(func, callback, iterable)
        self.__tpool.dispatch()
        
        t_list[ t_list.count() ].start()
        
        pass
        
    
    def of_sites(self, xhtml):
        pass
    
    def of_media(self, xhtml):
        pass
    
    def of_scripts(self, xhtml):
        pass
    
    def undefined_links(self):
        pass
    
    def of_sites_iter(self):
        pass
    
    def of_media_iter(self):
        pass
    
    def of_scripts_iter(self):
        pass
    
    def undefined_iter(self):
        pass
    
    def __parseto_xtree(self, xhtml_s, etree_q, clean_xhtml=False):
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
        etree_q.put( etree )
        
        
        
            
            
        xhtml_troot = xhtml_t.getroot()
        try:
            xhtml_troot.make_links_absolute(self.due.base_url['url'], resolve_base_href=True)
                except:
                    return {'xtree' : None, 'parsing_errors' : parsing_errors}
                for i in xhtml_t.iterlinks():
                    pass
        return {'xtree' : xhtml_t, 'parsing_errors' : parsing_errors}
