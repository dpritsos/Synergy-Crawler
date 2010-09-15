"""

"""

import multiprocessing
from multiprocessing.managers import BaseManager
from multiprocessing import Process, Pool
import threading
from threading import Thread 
import eventlet
import hashlib
from urlparse import urlparse

class DUEUnit(object):
    """DUE: 
        Summary: The base class structure used by Duplicate URL Eliminator(s) (DUE)
        Desription:
    """ 

    def __init__(self, path=None):
        self.id = None
        self.base_url = dict() #Keeps the hash and the Base URL 
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
                #print("FOUND IN SEEN LIST: %s" % urls) ####################################### HERE????
                return True
            else:
                url_is_in_files = self.__ust_files(url_hash)
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
                    url_is_in_files = self.__ust_files( urls_hash_l[i] )
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
        
    def savetofile(self, filename=None, file_headers=True):
        """savetofile(): Stores the whole hash-url dictionary on hard disk. 
            This function is recommended to be used externally from a process monitoring and handles the DUEUnit when 
            the crawler lacks of main memory. Currently the number of dictionary records are recommended to be used as criterion"""
        if not filename:
            filename =  str( urlparse(self.base_url['url'] ).netloc ) + "." + str( len(self.filelist) ) + ".seenurls"
        try:
            f = open( self.filespath + filename, "w" )
        except IOError:
            return None 
        try:
            if file_headers:
                header = "BASE URL: " + str( self.base_url['hashkey'] ) + " => " + str( self.base_url['url'] ) + "/\n"
                #print header
                f.write(header.encode())
                #print header
            lines = [ str(hash) + " => " + str(url) + "\n" for hash, url in self.seen.items()] 
            for line in lines:
                f.write(line.encode()) # Write a string to a file
        except:
            print("ERROR WRITTING FILE: %s" % filename)
            f.close()
        #Maybe A finally statement could be used as in previous version but leave it like this to be sure
        f.close()
        #Adding the new file name in the file list
        #self.filelist.append([f,filename]) #Should I keep f too or it is too big?
        self.filelist.append(str(filename))
        #Clears the seen dictionary
        self.seen.clear()
        return True
               
    def setBase(self, url):
        """This is required for Manager() object in multiprocessing in case is need to be used... I think!"""
        self.base_url = {'hashkey' : self.__url_hash(url),
                         'url'     : url }
        
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
            hashkey = hash.hexdigest()
            return hashkey 
        return None
    
    def __ust_files(self, url_hash=None):
        """DUEUnit.__ust_files: is performing URL Seen Test using history(URL seen) files"""
        if not self.filelist:
            #print("OUT FILE UST: NO FILES")
            return False
        gpool = eventlet.GreenPool(2) ########### Check This because it is too small for but works for scstrategy_1
        #Make url_hash key to an iteratable [ url_hash, url_hash, url_hash,...]
        iter_url_hash = map( lambda x: url_hash, range(len(self.filelist)) )
        for seen in gpool.imap(self.__ustf, iter_url_hash, self.filelist):
            if seen:
                return seen
        return False
    
    def __ustf(self, url_hash, file=None):
        #print("URL_HASH: %s" % url_hash)
        #if file[0].closed: 
        try:
            f = open( self.filespath + str(file), "r" )
        except IOError, e:
            while e:
                try:
                    f = open( self.filespath + str(file), "r" )
                except IOError, e:
                    pass
                #print("OUT FILE UST: ERROR - file: %s" % file[1])
                #return None #Return None to indicate a problem 
        #The following for loop is an alternative approach to reading lines instead of using f.readline() or f.readlines()
        for fileline in f:
            line = fileline.split(" => ") #BE CAREFULL with SPACES
            if url_hash == line[0]:
                #print("OUT FILE UST: FOUND")
                f.close() #Is it OK to let the file open for next search
                return True
        #In case the URL has not been found in the file close it
        f.close()    
        return False  
    
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

"""
class IP_DUEUnit(BaseManager): 
    '''IP_DUEUnit: Make the DUEUnit accessible by Processes
            IP_ stands for Interprocess'''

    pass
#BE AWARE it is registered an DUEUnit Class Object and not an Instance of the Class
IP_DUEUnit.register('DUEUnit', DUEUnit )       

"""
