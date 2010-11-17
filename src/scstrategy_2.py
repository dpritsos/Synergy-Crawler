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
    
    
    #SEEDS FOR NEWS
    filepath1 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/news/" 
    News_Seeds1 = ["http://www.bbc.co.uk",
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
    
    News_Seeds2 = ["http://www.eweek.com",
                   "http://www.sfgate.com",
                   "http://www.pcmag.com",
                   "http://www.informationweek.com",
                   "http://www.technewsworld.com",
                   "http://news.softpedia.com",
                   "http://www.space-travel.com",
                   "http://www.upi.com",
                   "http://news.cnet.com",
                   "http://spectrum.ieee.org",
                   "http://www.digitaltrends.com",
                   "http://www.ynetnews.com",
                   "http://www.ndtv.com",
                   "http://www.mirror.co.uk",
                   "http://www.miamiherald.com",
                   "http://online.wsj.com",
                   "http://www.huffingtonpost.com",
                   "http://www.theglobeandmail.com",
                   "http://sports.yahoo.com"]
    
    News_Seeds3 = ["http://www.philly.com",
                   "http://www.freep.com",
                   "http://www.rotoworld.com",
                   "http://www.gilroydispatch.com",
                   "http://www.pasadenastarnews.com",
                   "http://www.statesman.com",
                   "http://www.nytimes.com",
                   "http://abclocal.go.com",
                   "http://www.themoneytimes.com",
                   "http://lacrossetribune.com",
                   "http://www.buckslocalnews.com",
                   "http://www.forbes.com",
                   "http://www.doctorslounge.com",
                   "http://www.latimes.com",
                   "http://www.product-reviews.net",
                   "http://www.businessweek.com",
                   "http://news.morningstar.com",
                   "http://www.ft.com",
                   "http://www.forbes.com"]
    
    
    #Seeds.append( "http://www.insomnia.gr/" )
    
    
    #SEEDS FOR BLOGS
    filepath2 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/blogs/"
    Blogs_Seeds1 = ["http://blogs.skype.com",
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
    
    Blogs_Seeds3 = ["http://ormsbycinemainsane.blogspot.com",
                    "http://blog.mapquest.com",
                    "http://www.blogcatalog.com ",
                    "http://blogs.forward.com",
                    "http://pauledie.blogspot.com",
                    "http://www.blogcatalog.com",
                    "http://gethiroshima.blogspot.com",
                    "http://www.mallublogs.com",
                    "http://blogs.bellinghamherald.com",
                    "http://diveintoyesterday.blogspot.com",
                    "http://thaddeushogarth.berkleemusicblogs.com",
                    "http://music.travelingluck.com",
                    "http://blogs.kcrw.com/musicnews",
                    "http://musicsquareone.blogspot.com",
                    "http://blogs.cetis.ac.uk" ]
    
    ProdCompany_Seeds = list()
    #SEEDS FOR BLOGS
    filepath3 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/product_companies/"
    PCmp_Seeds1 = ["http://www.thenorthface.com",
                   "http://marmot.com",
                   "http://www.salomon.com",
                   "http://www.columbia.com",
                   "http://www.nike.com/nikeos/p/nikegolf/en_US",
                   "http://www.puma.com",
                   "http://www.apple.com",
                   "http://www.htc.com",
                   "http://www.htc.com/europe",
                   "http://www.nokiausa.com",
                   "http://h40059.www4.hp.com/uk/homelaptops",
                   "http://www.usa.canon.com",
                   "http://www.toshiba.co.uk",
                   "http://www.compaq.com",
                   "http://www.cannondale.com/gbr/eng/",
                   "http://www.specialized.com/us/en/bc/home.jsp",
                   "http://www.scott-sports.com/",
                   "http://www.shopadidas.com" ]
    
    PCmp_Seeds2 = ["http://www.olang.it",
                   "http://www.odlo.com/en/#collection",
                   "http://www.mavic.com",
                   "http://www.idealindustries.com",
                   "http://www.ideal.com",
                   "http://www.bt.com",
                   "http://www.intel.com",
                   "http://www.amd.com",
                   "http://usa.asus.com",
                   "http://www.nvidia.com/page/home.html",
                   "http://www.microsoft.com/en/us/default.aspx",
                   "http://www.sandisk.com",
                   "http://www.kingston.com/default.asp",
                   "http://www.wdc.com/en/",
                   "http://www.cisco.com",
                   "http://www.maplin.co.uk",
                   "http://www.shoe-shop.com",
                   "http://www.aldoshoes.com/uk" ]
    
    PCmp_Seeds2 = ["",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "",
                   "" ]
    
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
    for Seed in PCmp_Seeds2:
        #NOTICE: "kill_evt=m.Event()," for having different termination signal for each Spider since for this Strategy (2) they do not collaborate
        scspider_ps.append( SCSpider(seed=Seed, base_url_drop_none=False, urls_number_stop=100, kill_evt=m.Event(), spider_spoof_id=user_agent, save_path=filepath3) )
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
    
    