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
 

if __name__ == '__main__':
    
    # ~~~~ Bellow this line begins the WebCrawling strategy ~~~~

    #Define the User-Agent HTTP header for bypassing Search Engines or other Sites prohibition
    user_agent = 'Mozilla/5.0 (X11; U; Linux 2.6.34.1-SquidSheep; en-US; rv:1.9.2.3) Gecko/20100402 Iceweasel/3.6.3 (like Firefox/3.6.3)'
    #user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.2.10) Gecko/20100914 Firefox/3.6.10 InRed'
    
    News_Seeds = list()
    #SEEDS FOR NEWS
    filepath1 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/news/" 
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
                  "http://www.nydailynews.com"]
    
    #Seeds.append( "http://www.insomnia.gr/" )
    
    Blogs_Seeds = list()
    #SEEDS FOR BLOGS
    filepath2 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/blogs/"
    Blogs_Seeds = ["http://blogs.skype.com",
                   "http://blogs.technet.com",
                   "http://blogs.reuters.com",
                   "http://blogs.nfl.com",
                   "http://blog.cagle.com",
                   "http://blogs.abcnews.com",
                   "http://blogs.computerworld.com",
                   "http://blogs.adobe.com",
                   "http://blogs.howstuffworks.com",
                   "http://blogs.baltimoreravens.com",
                   "http://blogs.telegraph.co.uk",
                   "http://blogs.abcnews.com",
                   "http://kevin.lexblog.com",
                   "http://segullah.org",
                   "http://blogs.oxfam.org",
                   "http://blogs.standard.net",
                   "http://pagingdrgupta.blogs.cnn.com",
                   "http://a2zhomeschool.com" ]
    
    Blogs_Seeds2 = ["http://blogs.ft.com",
                   "http://www.mnprblog.com",
                   "http://blogs.babycenter.com",
                   "http://searchengineland.com",
                   "http://elementary-school.blogspot.com",
                   "http://blog.newsok.com/",
                   "http://blogs.mybandra.com/",
                   "http://blogs.adobe.com",
                   "http://blogs.cornellcollege.edu",
                   "http://weblogs.sun-sentinel.com",
                   "http://nabbschoolblogs.net",
                   "http://blogs.columbian.gwu.edu",
                   "http://www.wi-ski.com",
                   "http://www.virtualfilmclub.org.uk",
                   "http://westseattleblog.com",
                   "http://blog.doostang.com",
                   "http://blog.mapquest.com",
                   "http://blogpreston.co.uk" ]
    
    
    ProdCompany_Seeds = list()
    #SEEDS FOR BLOGS
    filepath3 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/product_companies/"
    PCmp_Seeds = ["http://www.thenorthface.com ",
                  "http://marmot.com",
                  "http://www.salomon.com",
                  "http://www.columbia.com",
                  "http://www.nike.com/nikeos/p/nikegolf/en_US",
                  "http://www.puma.com",
                  "http://www.apple.com",
                  "http://www.htc.com",
                  "http://www.htc.com/europe/",
                  "http://www.nokiausa.com",
                  "http://h40059.www4.hp.com/uk/homelaptops",
                  "http://www.usa.canon.com",
                  "http://www.toshiba.co.uk",
                  "http://www.compaq.com" ]
    
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
    #for Seed in News_Seeds:
        #NOTICE: "kill_evt=m.Event()," for having different termination signal for each Spider since for this Strategy (2) they do not collaborate
    #    scspider_ps.append( SCSpider(seed=Seed, base_url_drop_none=False, urls_number_stop=100, webpg_vect_tu=vects_q, kill_evt=m.Event(), spider_spoof_id=user_agent, save_path=filepath1) )
    for Seed in Blogs_Seeds2:
        #NOTICE: "kill_evt=m.Event()," for having different termination signal for each Spider since for this Strategy (2) they do not collaborate
        scspider_ps.append( SCSpider(seed=Seed, base_url_drop_none=False, urls_number_stop=600, kill_evt=m.Event(), spider_spoof_id=user_agent, save_path=filepath2) ) # webpg_vect_tu=vects_q,
    #for Seed in ProdCompany_Seeds:
    #    #NOTICE: "kill_evt=m.Event()," for having different termination signal for each Spider since for this Strategy (2) they do not collaborate
    #    scspider_ps.append( SCSpider(seed=Seed, base_url_drop_none=False, urls_number_stop=600, webpg_vect_tu=vects_q, kill_evt=m.Event(), spider_spoof_id=user_agent, save_path=filepath3) )
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
    
    