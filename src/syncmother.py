"""
Synmather: Synergy Web Crawling Mother Programm

<!-- Write a summary here -->


Author: Dimitrios Pritsos

Last update: 03.05.2010
            01.06.2010 --

"""
from multiprocessing.managers import BaseManager
from multiprocessing import Process
import threading 
from Queue import Queue
import hashlib
import random
import urlparse

class DUEUnit(object):
    """DUE: 
        Summary: The base class structure used by Duplicate URL Eliminator(s) (DUE)
        Desription:
    """ 
    def __init__(self, path=None):
        self.id = None
        self.base = dict() #Keeps the hash and the Base URL 
        self.seen = dict() #Keeps the URLs with or without the Base part
        if path:
            self.filespath = path
        else:
            self.filespath = "/home/dimitrios/Documents/Synergy-Crawler/seen_urls/" 
        self.filelist = list()
        self.conditonal_var = threading.Condition() 
    def ust(self, urls=None):
        """DUEUnit.ust(): URL Seen Test (UST) function 
             Function returns True if a URL seen before and False if not seen before.
             If a List of URLs is given returns a List with True and False if URLs seen before respectively
             If None has given Returns None        
        """
        if isinstance(urls, str):
            url_hash = self.__url_hash(urls)
            if self.seen.has_key(url_hash):
                return True
            else:
                url_is_in_files = self.__ustf(url_hash)
                if url_is_in_files: 
                    return True
                elif url_is_in_files == None:
                    return None #Maybe this should be changed by raising an exception
            #if the function hasn't return until here then the URL have not been seen before
            #So store in in the Dictionary it and return False        
            self.seen[url_hash] = urls
            return False
        elif isinstance(urls, list):
            urls_hash_l = [self.__url_hash(url) for url in urls]
            ret_l = list()
            for i in xrange(len(urls_hash_l)):
                if not self.seen.has_key( urls_hash_l[i] ):
                    url_is_in_files = self.__ustf( urls_hash_l[i] )
                    if url_is_in_files == None:
                        return None #Maybe this should be changed by raising an exception
                    elif not url_is_in_files:
                        #Store the URL as seen 
                        self.seen[ urls_hash_l[i] ] = urls[i]
                        ret_l.append(False) 
                    else:
                        ret_l.append(True)
                else:
                    ret_l.append(True)
            #Return the list of True or false
            return ret_l
        else:
            return None #Maybe this should be changed by raising an exception
    def savetofile(self, filename=None):
        """savetofile(): Stores the whole hash-url dictionary on hard disk. 
            This function is recommended to be used externally from a process monitoring and handles the DUEUnit when 
            the crawler lacks of main memory. Currently the number of dictionary records are recommended to be used as criterion"""
        if not filename:
            filename = str( self.base['url'] ) + "." + str( len(self.filelist) ) + ".seenurls"
        try:
            f = open( self.filespath + filename, "w" ) 
            try:
                header = "BASE URL: " + str( self.base['hashkey'] ) + " => " + str( self.base['protocol'] ) + "://" + str( self.base['url'] ) + "/\n"
                print header
                f.write(header.encode())
                print header
                lines = [ str(hash) + " => " + str(url) + "\n" for hash, url in self.seen.items()] 
                for line in lines:
                    f.write(line.encode()) # Write a string to a file
            finally:
                f.close()
        except IOError:
            return None
        #Adding the new file name in the file list
        self.filelist.append([f,filename])
        #Clears the seen dictionary
        self.seen.clear()       
    def setBase(self, hash, protocol, url):
        """This is required for Manager() object in multiprocessing in case is need to be used... I think!"""
        self.base = {'hashkey' : hash,
                     'protocol' : protocol,
                     'url'     : url }
    def seen_len(self):
        return len(self.seen)
    def acquire(self):
        self.conditonal_var.acquire()
    def release(self):
        self.conditonal_var.release()
    def wait(self, timeout=None):
        if timeout == None:
            self.conditonal_var.wait()
        else:
            self.conditonal_var.wait(timeout)
    def notify_all(self):
        self.conditonal_var.notify_all()
    def __url_hash(self, url):
        """DUEUnit__url_hash(): 
            Hash function for digesting the URL and URI to fixed size codes for very fast comparison. 
            In addition it offers a level of transparency in case the code/hash function will be changed.
            Currently Hash function used is MD5.  
        """
        if url:
            hash = hashlib.md5()
            hash.update(url)
            #using hexdigest() and not digest() because we have to write the hash codes on utf8 files
            return hash.hexdigest() 
        return None  
    def __isRelevant_url(self, url):
        """This should be checked externally if needed in case a URL should be passed to an other DUEUnit (or frontier)"""
        pass
    def __ustf(self, url_hash=None):
        """DUEUnit.__ustf: is performing URL Seen Test using history(URL seen) files"""
        #print("IN FILE UST")
        if not self.filelist:
            print("OUT FILE UST: NO FILES")
            return False
        for i in xrange(len(self.filelist)):
            if self.filelist[i][0].closed: ### HUGE BAG THIS IS A STRING NOT A FILENO SO FIX IT
                try:
                    f = open( self.filespath + self.filelist[i][1], "r" )
                except IOError:
                    print("OUT FILE UST: ERROR")
                    return None #Return None to indicate a problem 
            #The following for loop is an alternative approach to reading lines instead of using f.readline() or f.readlines()
            for fileline in f:
                line = fileline.split(" => ") #BE CAREFULL with SPACES
                if hash == line[0]:
                    print("OUT FILE UST: FOUND")
                    #Let the File Open for next Search if needed
                    return True
            #In case the URL has not been found in the file close it
            f.close()
        #In case there are no files keeping history of seen/scanned urls just return that this url has not been seen before
        #print("OUT FILE UST: NOT FOUND")
        return False            

 
class IP_DUEUnit(BaseManager): 
    """IP_DUEUnit: Make the DUEUnit accessible by Processes
            IP_ stands for Interprocess
    """
    pass
#BE AWARE it is registered an DUEUnit Class Object and not an Instance of the Class
IP_DUEUnit.register('DUEUnit', DUEUnit )  

#class DUEHandler(Process):
##    def __init__(self, DUEUnit):
#        Process.__init__(self)
#        self.du = DUEUnit
#    def run
        
class SynCMotherHandler(Process):
    """SynCMotherHandler:"""
    def __init__(self, SynCMother): 
        Process.__init__(self)
        self.synCMom = SynCMother
        self.pDUECounter = 0 
    def run(self):
        pSave = Process( target=self.__DUESavetofile )
        pSave.start()
        DUEliminatorsL = list()
        pDUE = Process( target=self.__DUEliminator ) 
        DUEliminatorsL.append( pDUE )
        DUEliminatorsL[self.pDUECounter].start()
        print "pDUECounter:" + str( self.pDUECounter + 1 )
        while True:
            if self.synCMom.rawUrlsQ_qsize() > 10 and self.pDUECounter < 3: 
                pDUE = Process( target=self.__DUEliminator ) 
                DUEliminatorsL.append( pDUE )
                self.pDUECounter += 1
                DUEliminatorsL[self.pDUECounter].start()
                print( "pDUECounter:" + str( self.pDUECounter + 1 ) )
    def __DUEliminator(self):
        print "RawQueueSize:" + str( self.synCMom.rawUrlsQ_qsize() )
        while True:
            urlsLL = self.synCMom.rawUrlsQ_get()
            if urlsLL: #if NOT empty List [] or None
                self.synCMom.acquire()
                self.synCMom.DUEliminate(urlsLL)
                self.synCMom.notify_all()
                self.synCMom.release()
    def __DUESavetofile(self):
        self.synCMom.acquire()
        self.synCMom.setBase('123', 'http', 'www.google.com')
        self.synCMom.notify_all()
        self.synCMom.release()
        while True:
            self.synCMom.acquire()
            while  self.synCMom.seen_len() <= 500:
                self.synCMom.wait()
            self.synCMom.savetofile()
            self.synCMom.notify_all()
            self.synCMom.release()

class SynCMother(DUEUnit):
    def __init__(self, seedURL=None):
        DUEUnit.__init__(self)
        self.rawUrlsQ = Queue(1000)
        if seedURL:
            hash = hashlib.md5()
            hash.update(seedURL)
            self.pending_urls = [[hash.digest(), seedURL]]
        else:
            self.pending_urls = None
    def get_scanned(self):
        return self.seen.keys()
    def urls_pending(self):
        if self.pending_urls == None:
            return False
        else:
            return True
    def send_urls(self, urls):
        self.rawUrlsQ.put(urls)
    def get_urls(self):
        return [url for hash, url in self.pending_urls]
    def DUEliminate(self, urlsLL):
        #print "Mother DUEliminate..."
        if not urlsLL: #This it suppose to be checked before this function is called
            return
        self.pending_urls = list()
        seen_list = self.ust( [url for hash, url in urlsLL] )
        for i in xrange(len(urlsLL)): #in Python 2.x range returns a list, xrange returns an "xrange object"
            if not seen_list[i]:
                self.pending_urls.append(urlsLL[i])
        if len(self.pending_urls) == 0:
                self.pending_urls = None
        #print "Mother DUEliminate - END"
    def rawUrlsQ_qsize(self):
        return self.rawUrlsQ.qsize()
    def rawUrlsQ_get(self):
        return self.rawUrlsQ.get()
    #Moved to DUEUnit
    #def acquire(self):
    #    self.ready_urls.acquire()
    #def release(self):
    #    self.ready_urls.release()
    #def wait(self, timeout=None):
    #    if timeout == None:
    #        self.ready_urls.wait()
    #    else:
    #        self.ready_urls.wait(timeout)
    #def notify_all(self):
    #    self.conditonal_var.notify_all()                            

class SynCMotherManager(BaseManager): pass #Define the Manager Process for managing proxies to the the 'synmother' objects   
#SynCMotherManager.register('SynCMother', SynCMother)
            
if __name__ == "__main__":
    
    Gseed = "http://www.google.gr/search?q=google&hl=el&client=firefox-a&hs=ksj&rls=com.ubuntu:en-GB:official&prmd=n&source=lnms&tbs=nws:1&ei=hhUuTPeRJML58Aa-_-C7Aw&sa=X&oi=mode_link&ct=mode&ved=0CBIQ_AU" 
    synmother_localhost = SynCMother(Gseed)
    print "Mother is running"
    
    #Start a Manager for synmother_localfsdafsfsahos
    SynCMotherManager.register('SynCMother', callable=lambda: synmother_localhost)
    syncmm = SynCMotherManager(address=('', 15000), authkey='123456')
    synm = syncmm #.get_server()
    synm.start() #serve_forever()
    
    synCMotherHandler = SynCMotherHandler(synm.SynCMother())
    synCMotherHandler.start()
    
    synCMotherHandler.join()
    #while True: pass 
        
    print("End of Programme")
  



