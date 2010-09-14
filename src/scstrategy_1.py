""" 
    Crawling strategy 1

"""

from multiprocessing import Manager
from multiprocessing.managers import BaseManager

#Import Web Crawlers element modules
from scspider import SCSpider
from scspidermom import SCSpidermom, SCSmartQueue
from scseedtree import SCSeedTree, SCSeedTreeHandler

import time #Maybe for later


def monitor_all():
    
    ################### REDEFINE ###################
    
    while True:
        #print("*****Monitoring Report*****")
        #print("keepersQ len:" + str( self.keepersQ.qsize() ) ) 
        #print("scannersQL len:" + str( len(self.scannersQL) ) )
        #print("scannersQ[0] size:" + str( self.scannersQL[0].qsize() ) )
        #print("urlLQ len:" + str( self.urlLQ.qsize() ) )
        #print("fetchersQL len:" + str( len(self.fetchersQL) ) )
        #print("fetchersQ[0] size:" + str( self.fetchersQL[0].qsize() ) )
        #print("genreIdentQ len:" + str( self.genreidentQ.qsize() ) )
        #print("pGenreIdentL Count:" + str( self.pGcount.value ) )
        #print("pfetchersL Count:" + str( self.pFcount.value ) ) #len(self.pfetchersL) )
        #print("pscannersL Countc:" + str( self.pScount.value ) ) #len(self.pscannersL) )
        #print("pkeepersL Count:" + str( self.pKcount.value ) )
        #print("\n\n\n" )
        time.sleep(10)       

if __name__ == '__main__':

    #Initialise Global DUE, SCSeedTree
    scst_localhost = SCSeedTree()
    #Define and start a Manager process of an SCSeedTree instance 
    class SCSeedTreeManager(BaseManager): pass
    SCSeedTreeManager.register('SCSeedTree', callable=lambda: scst_localhost) 
    scst_m = SCSeedTreeManager() #scst_m = SCSeedTreeManager(address=('', 15000), authkey='123456')
    scst_m.start()
    #In case a Global DUE Unit (i.e. SCSeedTree) is running to an other machine skip the above code and replace it with the following
    ##Connect to the Manager Process of the Global DUE Unit that is running to an other machine
    ##class SCSeedTreeProxyManager(BaseManager): pass       
    ##SCSeedTreeProxyManager.register('SCSeedTree')
    ##scst_m = SCSeedTreeProxyManager(address=('  REMOTE HOST   ', 15000), authkey='123456')
    ##scst_m.connect()  
    
    #Initialise a SCSmartQueue Instance 
    scsq_localhost = SCSmartQueue()
    #Define and start a Manager process of an SCSmartQueue instance
    class SCSmartQueueManager(BaseManager): pass
    SCSmartQueueManager.register('SCSmartQueue', callable=lambda: scsq_localhost)
    scsq_m = SCSmartQueueManager()
    scsq_m.start()
    
    # ~~~~ Bellow this line begins the WebCrawling strategy ~~~~
    
    #Get a Proxy to the SCSmartQueue instance to handle it through a Manager() Process (for the sake of InterProcess Communication)
    scsmart_q = scsq_m.SCSmartQueue()
    #Define the User-Agent HTTP header for bypassing Search Engines or other Sites prohibition
    user_agent = 'Mozilla/5.0 (X11; U; Linux 2.6.34.1-SquidSheep; en-US; rv:1.9.2.3) Gecko/20100402 Iceweasel/3.6.3 (like Firefox/3.6.3)'
    #Gseed = "http://www.alpamayopro.gr"
    Gseed = "http://www.insomnia.gr"
    #Gseed = "http://www.blogy.com"
    #Gseed = "http://www.yahoo.com" 
    #Gseed ="http://www.google.gr/search?q=google&hl=el&client=firefox-a&hs=ksj&rls=com.ubuntu:en-GB:official&prmd=n&source=lnms&tbs=nws:1&ei=hhUuTPeRJML58Aa-_-C7Aw&sa=X&oi=mode_link&ct=mode&ved=0CBIQ_AU"
    
    #Manger process for InterProcess Event() and Simple Queue()
    m = Manager()
    #m.start() no need for this for a default manager
    #Define a Global Process Termination Event which will start Manager Process and will return a proxy to the Event() 
    killall_evt = m.Event()
    #Define an xhtmltree Queue for farther analysis of the pages from other Processes
    xhtmltree_q = m.Queue()
    
    #Start the Handler Process that manipulates the Global DUE i.e. the SCSeedTree defined above
    scseed_t = scst_m.SCSeedTree()
    scst_h = SCSeedTreeHandler(scseed_t, killall_evt)
    scst_h.start()
    
    #Start SCSpidermom Process
    scspidermom_p = SCSpidermom(scsmart_q, scseed_t, kill_evt=killall_evt)
    scspidermom_p.start()
    
    #Create the first Queue for the very first SCSpider Process
    scsmart_q.put(Gseed)
    
    #~~~~~~~~~~~~~~~Start the very first SCSpider
    scspider_ps = list()
    #scspider_ps.append( SCSpider(seed=Gseed, kill_evt=killall_evt, ext_due_q=scsmart_q, spider_spoof_id=user_agent) )
    #scspider_ps[0].start()
    
    terminate = False #Temporarily Here !!!
    
    new_seed = scsmart_q.popegg()
    while True:
        if terminate:
            killall_evt.set()
            break
        for scspider in scspider_ps:
            #if scspider.is_alive():
            #    pass
                #line = "SPIDER %d : IS_ALIVE\n" % (scspider_ps.index(scspider) + 1)
                #print(line)
            if not scspider.is_alive():
                scspider.join()
                line = "SPIDER %d : DEAD - JOIN\n" % (scspider_ps.index(scspider) + 1)
                scspider_ps.remove(scspider)
                print(line)
            #if not scspider.is_alive():
            #    scspider.terminate()
            #    scspider_ps.remove(scspider)
            #    line = "SPIDER %d : DEAD - TERMINATE\n" % (scspider_ps.index(scspider) + 1)
            #    print(line)
        if len(scspider_ps) > 200 or killall_evt.is_set():
            #Just Kill Some Eggs - SORRY ABOUT THAT
            for i in xrange(1000):
                scsmart_q.popegg(kill_eggs=True)
            continue
        if new_seed and not killall_evt.is_set():
            print("NEW SPIDER %d with BASE_URL: %s" % ((len(scspider_ps) + 1), new_seed))
            scspider_ps.append( SCSpider(seed=new_seed, kill_evt=killall_evt, ext_due_q=scsmart_q, spider_spoof_id=user_agent) )
            scsp_i = len(scspider_ps) - 1
            scspider_ps[scsp_i].start()
        new_seed = scsmart_q.popegg()
    
    #Try to end properly this Process and its SubProcesses   
    for scspider in scspider_ps:
        scspider.join()
    scspidermom_p.join(5)
    #m.join(10)
    scst_h.join(5)
    scsq_m.join(5)
    scst_m.join(5)
    #In case some Process is still alive Just Kill them all 
    for scspider in scspider_ps:
        if scspider.is_alive():
            scspider.terminate()
    if scspidermom_p.is_alive():
        scspidermom_p.terminate()
    #if m.is_alive():
    #    m.terminate()
    if scst_h.is_alive():
        scst_h.terminate()
    if scsq_m.is_alive():
        scsq_m.terminate()
    if scst_m.is_alive():
        scst_m.terminate()
        
    print("Thank you and Goodbye!")
    
    
    
    
    