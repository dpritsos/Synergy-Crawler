"""Synergy-Crawler Spider:"""

import multiprocessing
from multiprocessing import Process
#from eventlet.green import urllib2
#import urllib2 #use it only in MultiProcessing/Threading not in GreenThreading
from threading import Thread
import eventlet 
from eventlet.green import urllib2 #For GreenThreading not I don't know how it is behaving with MultiProcessing/Threading
#import urllib2
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
        self.urls_number = kwargs.pop("urls_number_stop", 10000)  
        self.webpg_vect_tu = kwargs.pop("webpg_vect_tu", None)
        self.save_path = kwargs.pop("save_path", None)
        
    def run(self):
        """SCSpider's main function"""
        #Use the netloc (network locator) of the seed url as the base URL that this spider is working on
        url = self.urls_l[0]       
        self.due.setBase(url)
        #Define a process 
        fetchers_p = eventlet.GreenPool(1000)
        green_save_p = eventlet.GreenPool(1000)
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
        #Counter for the URLS that have been Followed by the Crawler
        scanned_urls = 0
        #From this line and below the loop this Process is starting 
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
            #Terminate - Some User condition reached
            if scanned_urls > self.urls_number:
                print("SCSpider Process (PID = %s - PCN = %s): Terminated - User Condition: Stop On %d Pages (%d have been followed) "\
                      % (self.pid, self.pnum, self.urls_number, scanned_urls))
                SCSpider.Num -= 1
                self.due.savetofile()
                self.kill_evt.set()
                break
            else:
                print("SCANNED URLS: %d" % scanned_urls)
                scanned_urls += len(self.urls_l)
            #Get one of the URLs which an other SCSpider has left to the ext_due_p and append it to the urls_l
            if self.ext_url_q != None:
                ext_url = self.ext_url_q.get(self.due.base_url['hashkey'],2)
                if ext_url:
                    self.urls_l.append(ext_url)
            tmp_urls_l = list() #SHOULD BE HERE
            #Start Processing WebPages (in fact sockets to them) which a Pool of GreenThreads is harvesting Asynchronously  
            #for page_soc in fetchers_p.imap_unordered(ffetchsrc, self.urls_l):
            for xhtml in fetchers_p.imap(self.fetchsrc, self.urls_l):
                # ~~~~~~~~ Maybe the following code can be wrapped up from a few sub-Processes or Threads ~~~~~~~~
                if xhtml[0] == None:
                    print("SPIDER %d of %d BASE %s" % (self.pnum, SCSpider.Num, self.due.base_url['netloc']))
                    print("Empty Page : %s" % xhtml[1])
                    continue
                else:
                    xhtml_s = xhtml[0]
                #Find the proper Encoding of the byte_string that urlopen has returned and decoded to it before you pass it to the lxml.html parser  
                if xhtml[1]:
                    if xhtml[1] != 'UTF-8' and xhtml[1] != 'utf-8':
                        print(xhtml[1])
                    #decode to the proper string Encoding. The incoming from urlopen() is  string is raw_byte string
                    #xhtml_s = xhtml_s.decode(xhtml[1], 'ignore') #'ignore': error handling when invalid UTF (or other) encoding characters are occurring
                else:
                    #try to figure out weather or not the data are coming with utf-8 encoding.... 
                    #Maybe I don't need this because encoding is retrieved from urlopen() and not the lxml library
                    #OR maybe I do need it because the encoding information are derived from HTTP headers Response
                    #utf_s = UnicodeDammit(xhtml_s, isHTML=True)
                    #if utf_s.unicode:
                    #    xhtml_s = utf_s.unicode #Be Careful of what you get
                    pass
                #Parse the XHTML Source fetched by from the GreenThreads
                xhtml_t = self.parseto_xtree(xhtml_s, clean_xhtml=True)
                #Expand the xhtml tree dictionary with some date for later process      
                xhtml_t['charset'] = xhtml[1]
                xhtml_t['url_req'] = xhtml[2]
                xhtml_t['url_resp'] = xhtml[3]
                xhtml_t['base_url'] = self.due.base_url 
                
                
                green_save_p.spawn_n(self.save_xhtml, self.due.base_url['netloc'], xhtml_s, xhtml_t)
                
                #Get every URL Link by performing etree traversal evaluate them and perform UST and them put them either
                #to the proper DUEUnit (internal or external) or give them to the Green-Threaded (XHTML) Source Fetcher(s)
                xtree = xhtml_t['xtree']
                if xtree:
                    xhtml_troot = xtree.getroot()
                else:
                    continue
                
                #if xhtml_troot is None: 
                    #if there is not any html etree root skip the URL processing because there is None
                #    continue
                count = 0
                for link in xhtml_troot.iterlinks():
                    if link[1] == 'href':
                        if link[2].find(".css") == -1 or link[2].find(".jpg") == -1 or link[2].find(".gif") == -1 or link[2].find(".png") == -1 or link[2].find("javascript:0")\
                        or link[2].find(".ico") == -1:
                            parsed_u = urlparse(link[2])
                            prsd_url = str(parsed_u.scheme + "://" + parsed_u.netloc)
                            baseurl = str(self.due.base_url['scheme'] + "://" +  self.due.base_url['netloc'])
                            if  prsd_url == baseurl:
                                seen = self.ust(link[2])
                                if not seen:
                                    count += 1 
                                    tmp_urls_l.append(link[2])
                                #else: means discarding this previously seen URL links
                            else:
                                #If the Base_urls is not the one this SCSpider is working on 
                                #try to pass it the other SCSpider Processes
                                if self.ext_url_q != None:
                                    #print("Sendto EXTERNAL LINKS: %s" % link[2])
                                    #if self.ext_url_q.full(self.due.base_url['hashkey']) == True:
                                        #print("FULL Queue Botle neck\n")
                                    #elif self.ext_url_q.full(self.due.base_url['hashkey']) == None:
                                    #    pass #print("NONE\n")
                                    self.ext_url_q.put(link[2])
                                elif self.base_url_drop_none:
                                        seen = self.ust(link[2])
                                        if seen:
                                            tmp_urls_l.append(link[2])
            #Now give the new URLs List back to the Fetcher GreenThreads
            del self.urls_l #for Preventing Memory Leakage remove it if has no effect but delay of the inevitable 
            self.urls_l = tmp_urls_l
        #If this Process has to be terminated wait for the Disk_keeper Thread to finish its job and join
        self.due.acquire()
        #WAKE-UP disk_keeper thread in case still waiting
        self.due.notify_all()
        self.due.release()
        disk_keeper_thrd.join()
    
    def parseto_xtree(self, xhtml_s, clean_xhtml=False):
        if clean_xhtml:
            cleaner = Cleaner( scripts=True, javascript=True, comments=True, style=True,\
                               links=True, meta=True, page_structure=False, processing_instructions=True,\
                               embedded=True, annoying_tags=True, remove_unknown_tags=True )#meta=False because we need MetaInfo
            try:
                xhtml_s = cleaner.clean_html(xhtml_s)
            except:
                pass
        #The HTML Parsers with and without recover mode but the capability to download the Proper DTD always ON
        #In case the lxml.html.parser will dispatched to sub-processes or threads then 
        #the HTMLParser(s) should be defined within these sub-processes or threads
        htmlparser = lxml.html.HTMLParser(recover=False, no_network=False) 
        htmlparser_rcv = lxml.html.HTMLParser(recover=True, no_network=False)    
        #Parse the XHTML Source 
        parsing_errors = list()    
        try:           
            xhtml_t = lxml.html.parse( StringIO(xhtml_s), parser=htmlparser, base_url=(self.due.base_url['scheme'] + "://" +self.due.base_url['netloc']) )
        except:
        #except ValueError, error:
        #except lxml.etree.XMLSyntaxError, error:
            #print(xhtml_s)
            pass
            #print("PARSE ERROR (no recovery mode): %s" % error)
            #parsing_errors.append(error)
            try:
                xhtml_t = lxml.html.parse(StringIO(xhtml_s), parser=htmlparser_rcv, base_url=(self.due.base_url['scheme'] + "://" +self.due.base_url['netloc']) ) #StringIO(xhtml_s)
            except Exception as error:
                print("PARSE ERROR (recovery mode): %s" % error)
                parsing_errors.append(error)
                try:
                    print('DA ZOUP')
                    xhtml_t = soup.parse(xhtml_s) #StringIO(xhtml_s)
                except:
                    print("FUCKED-UP PAGE")
                    parsing_errors.append("BeautifullSoup Failed")
                    return {'xtree' : None, 'parsing_errors' : parsing_errors}
                #Get the root Element and make the links absolute
                xhtml_troot = xhtml_t.getroot()
                try:
                    xhtml_troot.make_links_absolute(self.due.base_url['url'], resolve_base_href=True)
                except:
                    return {'xtree' : None, 'parsing_errors' : parsing_errors}
                for i in xhtml_t.iterlinks():
                    pass
        return {'xtree' : xhtml_t, 'parsing_errors' : parsing_errors}
        
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
        except IOError as e:
            resp = e #.read()
            #resp = e.read()
            print("FETCH ERRORS(urllib2): %s" % resp)
            
        #Return a tuple of the HTML source, the character encoding of this source, and its URL 
        return (htmlsrc, charset, url_req, url_resp)
    
    def save_xhtml(self, root_path, xhtml_source, xhtml_t):
        assert os.path.isdir(root_path)
        
        
        if filespath and not os.path.isdir(self.filespath):
            os.mkdir(self.filespath)
        filename =  str( self.base_url['netloc'] ) + ".html" 
        try:
            try:
                f = os.open( self.filespath + filename, os.O_CREAT | os.O_WRONLY, stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            except Exception as e:
                print("DUE Unit: Error while Creating file - Error: %s" % e)
                ret_signal = None 
            #Place a file-object wrapper around the file Descriptor
            fobj = os.fdopen(f, "w", 1)       
            #Place an Encoding Wrapper to assure the file Writing to be performed with UTF-8 encoding
            fenc = codecs.EncodedFile(fobj,'utf-8')
        except Exception as e:
            print("DUE Unit: Error while Saving file - Error: %s" % e)
            #Return None for the Spider to know that some error occurred for deciding what to do with it 
            ret_signal = None 
        else:
            lines = [ url for url in self.seen.keys() ]
            for line in lines:
                #os.write(f, line)
                fenc.write( str(line) + "\n" ) # Write a string to a file #line.encode()
            #Adding the new file name in the file list
            self.filelist.append(str(filename))
            #Clears the seen dictionary
            self.seen.clear()
            #Return True for the Spider to know that everything went OK
            ret_signal = True
        finally:
            fenc.close()
            
        return ret_signal
    
    def savedue(self):
        while not self.kill_evt.is_set():
            self.due.acquire()
            while self.due.seen_len() < 100:
                #This will force the thread to stop in case a global stop signal is given
                if self.kill_evt.is_set():
                    return
                #In case Seen Dictionary is still small Wait (i.e. Sleep)
                self.due.wait()
            if not self.due.savetofile():
                print("SCSPIDER: FILE NOT SAVED - HALT")
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

