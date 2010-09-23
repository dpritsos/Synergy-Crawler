""" 
    Crawling strategy 1

"""

from multiprocessing import Manager
from multiprocessing.managers import BaseManager

#Import Web Crawlers element modules
from scspider import SCSpider
from scvectgen import SCVectGen

from Queue import Queue


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
    
    # ~~~~ Bellow this line begins the WebCrawling strategy ~~~~

    #Define the User-Agent HTTP header for bypassing Search Engines or other Sites prohibition
    user_agent = 'Mozilla/5.0 (X11; U; Linux 2.6.34.1-SquidSheep; en-US; rv:1.9.2.3) Gecko/20100402 Iceweasel/3.6.3 (like Firefox/3.6.3)'
    #Gseed = "http://www.alpamayopro.gr"
    Gseed = "http://www.insomnia.gr/forum/"
    #Gseed = "http://www.blogger.com"
    #Gseed = "http://www.yahoo.com" 
    #Gseed ="http://www.google.gr/search?q=google&hl=el&client=firefox-a&hs=ksj&rls=com.ubuntu:en-GB:official&prmd=n&source=lnms&tbs=nws:1&ei=hhUuTPeRJML58Aa-_-C7Aw&sa=X&oi=mode_link&ct=mode&ved=0CBIQ_AU"
    
    #Manger process for InterProcess Event() and Simple Queue()
    m = Manager()
    #m.start() no need for this for a default manager
    #Define a Global Process Termination Event which will start Manager Process and will return a proxy to the Event() 
    killall_evt = m.Event()
    #Define an xhtmltree Queue for farther analysis of the pages from other Processes
    #xhtmltree_q = Queue() # Only for interprocess communication
    
    #Define a variable that will use get the primitive analysis output of the SCSpider(s)   
    vects_q = Queue()  
    
    #Start the SCSpider restricted to scan the pages of one WebSite
    scspider_ps = list()
    scspider_ps.append( SCSpider(seed=Gseed, base_url_drop_none=False, urls_number_stop=10, webpg_vect_tu=vects_q,kill_evt=killall_evt, spider_spoof_id=user_agent) )
    scspider_ps[0].start()
    
    terminate = False #Temporarily Here !!!
    while True:
        if terminate:
            killall_evt.set()
            break
        for scspider in scspider_ps:
            if not scspider.is_alive():
                scspider.join()
                line = "SPIDER %d : DEAD - JOIN\n" % (scspider_ps.index(scspider) + 1)
                scspider_ps.remove(scspider)
                print(line)
            else:
                if not vects_q.empty():
                    vects_tu = vects_q.get()
        if len(scspider_ps) ==  0:
            terminate = True
            
    #Try to end properly this Process and its SubProcesses
    for scspider in scspider_ps:
        if scspider.is_alive():
            scspider.join(5)
    #In case some Process is still alive Just Kill them all
    for scspider in scspider_ps:
        if scspider.is_alive():
            scspider.terminate()
              
    #Train One-Class SVM model with the Training-Data Collected by the Spider Above 
    if not vects_q.empty():
        vects_tu = vects_q.get()
        print(vects_tu[0])
        print(vects_tu[1])
        print(vects_tu[2])
        print(vects_tu[3])
        
    print("Thank you and Goodbye!")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    