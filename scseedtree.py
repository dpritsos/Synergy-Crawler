"""
SCSeedTree: 

<!-- Write a summary here -->


Author: Dimitrios Pritsos

Last update: 

"""
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from threading import Thread 
from Queue import Queue
import hashlib
import random
from urlparse import urlparse

from scdueunit import DUEUnit
        
class SCSeedTreeHandler(Process):
    """SCSeedTreeHandler:"""
    
    Num = 0
    
    def __init__(self, SCSeedTree, kill_evt ): 
        Process.__init__(self)
        SCSeedTreeHandler.Num += 1
        self.pnum = SCSeedTreeHandler.Num 
        self.seedtree = SCSeedTree
        self.kill_evt = kill_evt
         
    def run(self):
        #This Process is constantly checking the DUE seen dictionary is big enough to be saved on disk
        filenum = 0
        while True:
            #Checking for termination signal
            if self.kill_evt.is_set():
                print("SCSeedTreeHandler Process (PID = %s - PCN = %s): Terminated" % (self.pid, self.pnum))
                SCSeedTreeHandler.Num -= 1
                break
            #Get the SCSeedTree for a while and in case the the URL seen Dictionary 
            #has more than 500 elements save them to the local drive 
            #otherwise suspend (thanx to Conditional Variable defined in the DUEUnit Class object
            #self.seedtree.acquire()
            while self.seedtree.seen_len() < 400:
                pass #self.seedtree.wait() #pass
            else:
                print("SEED TREE SEEN LIST_LEN %s" % self.seedtree.seen_len())
                
            filenum += 1
            file_name = "Visited_WebSite_List." + str(filenum)
            if not self.seedtree.savetofile( file_name , file_headers=False):
                print("SEEDtREE: FILE NOT SAVED - HALT")
                self.kill_evt.set()
                return
            #self.seedtree.notify_all()
            #self.seedtree.release()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Future Work Buld the Site Graph-Tree while Crawling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    


class SCSeedTree(DUEUnit):
    
    def __init__(self):
        DUEUnit.__init__(self)
        #Set the Base_url Here will be used only as file_names
        #self.setBase("Visited_WebSite_List")
        #self.egg_seed_q = Queue()
        #if seed_url:
        #    parsed_u = urlparse(seed_url)
        #    seen = self.ust(parsed_u.netloc)
        #    if not seen: 
    
    #def send_url(self, seed_url):
    #    self.prospective_seeds_q.put(seed_url)
        
    #def get_url(self):
    #    try:
    #        return self.egg_seed_q.get_nowait()
    #    except:
    #        return None
        
    #def prosp_seed_q_qsize(self):
    #    return self.prosp_seed_q.qsize()
    
    #def prosp_seed_q_get(self):
    #    try:
    #        return self.prosp_seed_q.get_nowait()
    #    except:
    #       return None
        
    #def seen_dict_len(self):
    #    return len(self.seen)    

            
        
    
            
if __name__ == "__main__":
    
    Gseed = "http://www.yahoo.com" #"http://www.google.gr/search?q=google&hl=el&client=firefox-a&hs=ksj&rls=com.ubuntu:en-GB:official&prmd=n&source=lnms&tbs=nws:1&ei=hhUuTPeRJML58Aa-_-C7Aw&sa=X&oi=mode_link&ct=mode&ved=0CBIQ_AU" 
    scst_localhost = SCSeedTree(Gseed)
    print "Mother is running"
    
    class SCSeedTreeManager(BaseManager): pass
    #Start a Manager for synmother_localfsdafsfsahos
    SCSeedTreeManager.register('SCSeedTree', callable=lambda: scst_localhost)
    scst_m = SCSeedTreeManager(address=('', 15000), authkey='123456')
    #sc = scmm.get_server()
    scst_m.start() #serve_forever()
    
    scst_m.join()
    #while True: pass 
    print("End of Programme")
  



