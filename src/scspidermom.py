"""


"""
from multiprocessing import Process, Manager, Value
from multiprocessing.managers import BaseManager
import multiprocessing
from threading import Thread
import threading 
from collections import deque
from Queue import Queue
import hashlib
from urlparse import urlparse

                                   
class SCSmartQueue(object):
    
    def __init__(self):
        self.dict_qs = dict()
        self.prospective_seeds = Queue(1000) 
        self.eggs_q = deque()
        ############################ MAYBE I SHOULD MOVE LOCKS ANYWAY!!!
        self.dict_con_var = threading.Condition()
    
    def get(self, base_hash, wait_time):
        #if self.dict_con_var.acquire(False):        
        q = self.dict_qs.get(base_hash, None)
        #    self.dict_con_var.notify_all()
        #    self.dict_con_var.release()
        #else:
        #    return None
        if q == None:
            return None
        try: # check if it is empty or times out 
            return q.get(timeout=wait_time)
        except:
            return None
    
    def put(self, ext_url):
        parshed_u = urlparse(ext_url)
        hash = hashlib.md5()
        base_url = parshed_u.scheme + "://" + parshed_u.netloc
        hash.update(base_url)  
        ext_baseurl_hash = hash.hexdigest()
        #self.dict_con_var.acquire() 
        if self.dict_qs.has_key(ext_baseurl_hash):
            #print(" FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND  FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND ")
            #self.dict_qs[ext_baseurl_hash] = Queue()
            try:
                self.dict_qs[ext_baseurl_hash].put_nowait(ext_url)
            except:
                pass
        else:
            try:
                self.prospective_seeds.put_nowait(ext_url)
            except:
                pass
        #self.dict_con_var.notify_all()
        #self.dict_con_var.release()
    
    def getpseed(self):
        #print("PROSP: %s" % self.prospective_seeds.qsize())
        try:
            return self.prospective_seeds.get_nowait()
        except:
            return None
    
    def putegg(self, url_seed):
        #Update the eggs Queue for a new spider to emerge
        self.eggs_q.appendleft(url_seed)
        
    def popegg(self, kill_eggs=False):
        #print("#Eggs %s" % (len(self.eggs_q)))
        try:
            #print("QUEUES: %s" % len(self.dict_qs))
            egg = self.eggs_q.pop()
            if not kill_eggs:
                parshed_u = urlparse(egg)
                hash = hashlib.md5()
                hash.update(parshed_u.scheme + "://" + parshed_u.netloc)  
                new_hashkey = hash.hexdigest() 
                #Create a new Queue to the Queues Dictionary for the forthcoming Spider
                #self.dict_con_var.acquire()
                self.dict_qs[new_hashkey] = Queue(5)
                #self.dict_con_var.notify_all()
                #self.dict_con_var.release()
                return egg
            else:
                return None 
        except IndexError:
            return None
        
    def full(self, base_hash):
        #if self.dict_con_var.acquire(False):        
        q = self.dict_qs.get(base_hash, None)
        #    self.dict_con_var.notify_all()
        #    self.dict_con_var.release()
        #else:
        #    return None
        if q == None:
            return None
        #try: # check if it is empty or times out 
        return q.full()
        #except:
        #    return None
            

class SCSpidermom(Process):
    
    Num = 0
    
    def __init__(self, SCSmartQueue, SCSeedTree, **kwargs):
        Process.__init__(self)
        SCSpidermom.Num += 1
        self.pnum = SCSpidermom.Num 
        self.smart_q = SCSmartQueue
        self.seedtree = SCSeedTree
        self.kill_evt = kwargs.pop("kill_evt", multiprocessing.Event().clear())
        self.egg_fertillise_ps = list()
    
    def run(self):
        while True:
            #Checking for termination signal
            if self.kill_evt.is_set():
                print("SCSpidermom Process (PID = %s - PCN = %s): Terminated" % (self.pid, self.pnum))
                SCSpidermom.Num -= 1
                return
            #If the prespective_seed is big enough that SCSpidermom happens to find it non-Empty then a new egg_fertilizer will start
            if len(self.egg_fertillise_ps) < 4:
                prospective_seed = self.smart_q.getpseed()
            else:
                prospective_seed = None
            if prospective_seed:
                #print('PROSP_SEED: %s' % prospective_seed)
                up = urlparse(prospective_seed)
                bup = up.scheme + "://" + up.netloc
                if bup == "http://www.insomnia.gr":
                    print("FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND FOUND")  
                self.egg_fertillise_ps.append( Process(target=self.due, args=(prospective_seed,)) )
                ef_i = len(self.egg_fertillise_ps) - 1
                self.egg_fertillise_ps[ef_i].start()
            #Check if the "egg fertillisers" are still alive if not just Join() (terminate) them for good
            for egg_frtlz_p in self.egg_fertillise_ps:
                if not egg_frtlz_p.is_alive():
                    #print("FERTILIZER IS DEAD - JOIN\n")
                    egg_frtlz_p.join()
                    self.egg_fertillise_ps.remove(egg_frtlz_p)
        #In case this process is terminated then all the SubProcesses should terminate too
        for egg_frtlz_p in self.egg_fertillise_ps:
            egg_frtlz_p.join()
            self.egg_fertillise_ps.remove(egg_frtlz_p)
           
    def due(self, prospective_seed):
        """due: Duplicate URL Elimination"""
        while prospective_seed:
            parshed_url = urlparse(prospective_seed)
            base_url = parshed_url.scheme + "://" + parshed_url.netloc
            #self.seedtree.acquire()
            try:
                seen = self.seedtree.ust(base_url)
            except EOFError, e:
                print("%s - CONNECTION & EOF ERROR: %s" % (base_url, e))
                self.kill_evt.set()
                return #seen = None
            #self.seedtree.notify_all()
            #self.seedtree.release()
            if not seen:
                self.smart_q.putegg(prospective_seed)
            #Get next prospective seed to fertillise a SCSpider egg
            prospective_seed = self.smart_q.getpseed()
        
""" OLD VERSION OF SPIDER MOM
class SCSpidermom(Process):
    
    Num = 0
    
    def __init__(self, SCSmartQueue, SCSeedTree, **kwargs):
        SCSpidermom.Num += 1
        self.smart_q = SCSmartQueue
        self.seedtree = SCSeedTree
        self.kill_evt = kwargs.pop("kill_evt", multiprocessing.Event().clear())
        self.seeds_send_ps = list()
        self.egg_fertillise_ps = list()
    
    def run(self):
        while True:
            #Checking for termination signal
            if self.kill_evt.is_set():
                print("SCSpidermom Process (PID = %s - PCN = %s): Terminated" % (self.pid, SCSpidermom.Num))
                SCSpidermom.Num -= 1
                return
            #If the prespective_seed is big enough that SCSpidermom happens to find it non-Empty then a new some seed_send will start 
            prospective_seed = self.smart_q.getseed()
            if prospective_seed:
                self.seeds_sender_p.append( Process(target=self.sendseeds, prospective_seed) )
                sp_i = len(self.seed_sender_p) - 1
                self.seeds_sender_p[sp_i].start()
            #If the seedtree has lots of url Seeds waiting to became Spider eggs then open one more geteggdeed process to speed up things
            egg_seed = self.seedtree.get()
            if egg_seed:
                self.egg_fertillise_ps.append( Process(target=self.geteggseeds, egg_seed) )
                ef_i = len(self.egg_fertillise_ps) - 1
                self.egg_fertillise_ps[ef_i].start()
        #In case this process is terminated then all the SubProcesses should terminate too
        for seed_snt_p in self.seed_send_ps:
            seed_snt_p.join()
        for egg_frtlz_p in self.egg_fertillise_ps:
            egg_frtlz_p.join()
                
    def sendseeds(self, prosp_seed):
        while prosp_seed:
            self.seedtree.send_url( prosp_seed )
            prosp_seed = self.smart_q.getseed()
    
    def geteggseeds(self, egg_seed):
        while egg_seed:
            self.smart_q.putegg(egg_seed)
            egg_seed = self.seedtree.get_url()   
                                                      """