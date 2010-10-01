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
    #user_agent = 'Mozilla/5.0 (X11; U; Linux 2.6.34.1-SquidSheep; en-US; rv:1.9.2.3) Gecko/20100402 Iceweasel/3.6.3 (like Firefox/3.6.3)'
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ro-RO; rv:1.7.6) Gecko/20050318 Firefox/1.0.2 '
    
    #SEEDS FOR NEWS
    Seeds = list()
    #Seeds.append( "http://www.bbc.co.uk" )
    #Seeds.append( "http://edition.cnn.com/" )
    #Seeds.append( "http://www.bloomberg.com" )
    #Seeds.append( "http://www.ted.com/talks/tags" )
    #Seeds.append( "http://www.foxnews.com" )
    #Seeds.append( "http://www.time.com/time" )
    #Seeds.append( "http://www.nationalgeographic.com" )
    #Seeds.append( "http://www.bbcfocusmagazine.com" )
    #Seeds.append( "http://www.pcmag.com" )
    #Seeds.append( "http://www.drdobbs.com" )
    #Seeds.append( "http://news.google.com" )
    Seeds.append( "http://www.insomnia.gr" )
    
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
    for Seed in Seeds:
        #NOTICE: "kill_evt=m.Event()," for having different termination signal for each Spider since for this Strategy (2) they do not collaborate
        scspider_ps.append( SCSpider(seed=Seed, base_url_drop_none=False, urls_number_stop=10, webpg_vect_tu=vects_q,kill_evt=m.Event(), spider_spoof_id=user_agent) )
    for scspider_p in scspider_ps:    
        scspider_p.start()
    
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
        
    print("Thank you and Goodbye!")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    