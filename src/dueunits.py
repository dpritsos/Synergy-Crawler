"""

"""
from multiprocessing import Process, Pool
import threading
from threading import Thread 
from eventlet import GreenPool
from eventlet.green import os
import hashlib
from urlparse import urlparse
import codecs
import stat

class DUEUnit(object):
    """DUE: 
        Summary: The base class structure used by Duplicate URL Eliminator(s) (DUE)
        Desription:
    """ 

    def __init__(self, path=None):
        self.id = None
        self.base_url = dict() #Keeps the hash and the Base URL 
        self.seen = dict() #Keeps the URLs with or without the Base part
        self.filelist = list()
        self.conditonal_var = threading.Condition()
        self.green_pool = GreenPool(100)
        if path:
            self.filespath = path
        else:
            self.filespath = "/home/dimitrios/Documents/Synergy-Crawler/seen_urls/"
        if self.filespath and not os.path.isdir(self.filespath):
            os.mkdir(self.filespath)  
        
    def ust(self, urls=None):
        """DUEUnit.ust(): URL Seen Test (UST) function 
             Function returns True if a URL seen before and False if not seen before.
             If a List of URLs is given returns a List with True and False if URLs seen before respectively
             If None has given Returns None 
        """
        if isinstance(urls, str):
            url = urls
            if not url in self.seen:
                #if not in memory Check into files
                url_is_in_files = self.__ustf(url)
                if url_is_in_files: 
                    return True
                elif url_is_in_files == None:
                    raise IOError ("UST in files returned None")
                else:
                    #if the function hasn't return until here then the URL have not been seen before
                    #So store in in the Dictionary it and return False
                    self.seen[ url ] = True
                    return False
            else:
                return True
        elif isinstance(urls, list):
            ret_l = list()
            for url in urls:
                if not url in self.seen:
                    url_is_in_files = self.__ustf( url )
                    if url_is_in_files == None:
                        raise IOError ("UST in files returned None")
                    elif not url_is_in_files:
                        #Store the URL as seen 
                        self.seen[ url ] = True
                        ret_l.append(False) 
                    else:
                        ret_l.append(True)
                else:
                    ret_l.append(True)
            #Return the list of True or false
            return ret_l
        else:
            raise IOError ("Invalid URL or URL list for UST")
        
    def savetofile(self, filename=None, file_headers=True):
        """savetofile(): Stores the whole hash-url dictionary on hard disk. 
            This function is recommended to be used externally from a process monitoring and handles the DUEUnit when 
            the crawler lacks of main memory. Currently the number of dictionary records are recommended to be used as criterion"""
        if not filename:
            filename =  str( self.base_url['netloc'] ) + "." + str( len(self.filelist) ) + ".seenurls"
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
            if file_headers:
                header = "BASE URL: " + str( self.base_url['netloc'] ) + "/\n"
                #print header
                fenc.write(header) #heaser.encode()
                #print header
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
               
    def setBase(self, url=None):
        """SetBase: It decompose the URL into its components and ignores every term in 'url' after net-locator"""
        if url:
            url = urlparse(url)
            netloc_terms = url.netloc.split('.')
            self.base_url = {'scheme' : url.scheme, 
                             'netloc' : url.netloc,
                             'base' : netloc_terms[-2] + "." + netloc_terms[-1], 
                             'domain' : netloc_terms[-1]} 
        else:
            self.base_url = {'scheme' : None,
                             'netloc' : None,
                             'base' : None,
                             'domain' : None}
            
    def __url_hash(self, url):
        """DUEUnit__url_hash():
            Hash function for digesting the URL and URI to fixed size codes for very fast comparison.
            In addition it offers a level of transparency in case the code/hash function will be changed.
            Currently Hash function used is MD5.
                
                     !!! Depricated !!!
                
        if url:
            hash = hashlib.md5()
            hash.update(url)
            #using hexdigest() and not digest() because we have to write the hash codes on utf8 files
            hashkey = hash.hexdigest()
            return hashkey
        return None
        """
        pass
        
    def __ustf(self, url=None):
        """DUEUnit.__ustf: is performing URL Seen Test using history(URL seen) files"""
        if not self.filelist:
            #print("OUT FILE UST: NO FILES")
            return False
        #Make url_hash key to an iteratable [ url_hash, url_hash, url_hash,...]
        for seen_dict in self.green_pool.imap(self.__load_dict, self.filelist):
            if url in seen_dict:
                return True
        #If For loop finishes with no 'seen' variable equals to True then return False (i.e. UST in files returns None) 
        return False
    
    def __load_dict(self, filename=None):
        #Create a temp dictionary of the seen URLs in 'file'
        seen_dict = dict()  
        try:
            try:
                f = os.open( self.filespath + filename, os.O_RDONLY)
            except Exception as e:
                print("DUE Unit: Error while Opening file - Error: %s" % e)
                #Return None instead of Dictionary
                seen_dict = None                 
            #Place a file-object wrapper around the file Descriptor
            fobj = os.fdopen(f, "r", 1)       
            #Place an Encoding Wrapper to assure the file Writing to be performed with UTF-8 encoding
            fenc = codecs.EncodedFile(fobj,'utf-8')
            for fileline in fenc:
                #Remove Whitespace characters before giving it as key value into seen_dict
                url = fileline.rstrip()
                seen_dict[ url ] = True
        except Exception as e:
            print("DUE Unit: Exception occurred while loading file - Error: %s" % e)
            #Notify Spider that Something went wrong - Return None instead of Dictionary 
            seen_dict = None
        finally:
            #close file in any case
            fenc.close()
        #return the Dictionary   
        return seen_dict
    
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


if __name__ == "__main__":
    
    due = DUEUnit()

    due.setBase("http://www.unit-test.org")

    News_Seeds = ["http://www.bbc.co.uk",
                  "http://edition.cnn.com",
                  "http://www.bloomberg.com",
                  "http://www.ted.com/talks/tags",
                  "http://www.foxnews.com",
                  "http://www.time.com/time",
                  "http://www.nationalgeographic.com",
                  "http://www.bbcfocusmagazine.com",
                  "http://www.pcmag.com",
                  "http://www.drdobbs.com",
                  "http://news.google.com",
                  "http://www.channelnewsasia.com",
                  "http://health.usnews.com",
                  "http://www.zdnet.co.uk",
                  "http://soccernet.espn.go.com",
                  "http://mlb.mlb.com",
                  "http://www.dallasnews.com",
                  "http://www.theaustralian.com.au",
                  "http://www.nydailynews.com" ]

    due.ust(News_Seeds)

    #Seed = "http://www.bbc.co.uk"
    #if due.ust(Seed):
    #    print True

    for seen in due.ust(News_Seeds):
        print seen

    due.savetofile()

    for seen in due.ust(News_Seeds):
        print seen
