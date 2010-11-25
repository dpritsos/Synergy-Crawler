""" 
    Crawling strategy 1

"""

from multiprocessing import Manager
from multiprocessing.managers import BaseManager

#Import Web Crawlers element modules
from scspider import SCSpider

from Queue import Queue


import time #Maybe for later
 

if __name__ == '__main__':
    
    # ~~~~ Bellow this line begins the WebCrawling strategy ~~~~

    #Define the User-Agent HTTP header for bypassing Search Engines or other Sites prohibition
    user_agent = 'Mozilla/5.0 (X11; U; Linux 2.6.34.1-SquidSheep; en-US; rv:1.9.2.3) Gecko/20100402 Iceweasel/3.6.3 (like Firefox/3.6.3)'
    #user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.2.10) Gecko/20100914 Firefox/3.6.10 InRed'
    
    testpath = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/test/"
    
    #SEEDS FOR NEWS
    filepath1 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/news/" 
    News1 = ["http://www.bbc.co.uk",
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
    
    News2 = ["http://www.eweek.com",
             "http://www.sfgate.com",
             "http://www.pcmag.com",
             "http://www.informationweek.com",
             "http://www.technewsworld.com",
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
             "http://sports.yahoo.com" ]
    
    News3 = ["http://www.philly.com",
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
             "http://www.forbes.com" ]
    
    
    #Seeds.append( "http://www.insomnia.gr/" )
    
    
    #SEEDS FOR BLOGS
    filepath2 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/blogs/"
    Blogs1 = ["http://blogs.skype.com",
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
    
    Blogs2 = ["http://blogs.ft.com",
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
    
    Blogs3 = ["http://ormsbycinemainsane.blogspot.com",
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
    
    #SEEDS FOR BLOGS
    filepath3 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/product_companies/"
    Product_comp1 = ["http://www.thenorthface.com",
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
    
    Product_comp2 = ["http://www.olang.it",
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
    
    Product_comp3 = ["http://www.dixons.co.uk/gbuk/index.html",
                     "http://secure.comet.co.uk/h/Kitchen-Home/1671",
                     "http://www.radioshack.com",
                     "http://www.futureshop.ca/en-CA/home.aspx",
                     "http://www.kmart.com/",
                     "http://oemsofttech.net",
                     "http://www.actinic.co.uk/eshop-estore-software",
                     "http://www.oemstoredigital.com",
                     "http://www.furniturevillage.co.uk",
                     "http://www.thefurnitureshopdfw.com",
                     "http://www.homebase.co.uk",
                     "http://www.harveysfurniture.co.uk",
                     "http://www.tesco.com",
                     "http://www.spar.co.uk/",
                     "http://www.intersport.com/products",
                     "http://www.vans.com/",
                     "http://www.eastpak.com/shop/catalog/control/openCategory?subcategory_id=BAGS_BACKPACKS&category_id=ROOT_BAGS",
                     "http://www.shopstyle.com/browse/womens-clothes" ]
    
    Product_comp4 = ["http://www.7forallmankind.com",
                     "http://www.johnvarvatos.com",
                     "http://www.ellamoss.com/store/pg_type.aspx?id=1",
                     "http://www.splendid.com",
                     "http://www.lucy.com",
                     "http://www.toyota.com/",
                     "http://www.volvocars.com/en-ca/Pages/default.aspx" ]
    
    #Academic Sites
    filepath4 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/academic/"
    Academ1 = ["http://www.ucas.ac.uk",
               "http://www.ox.ac.uk",
               "http://www.cam.ac.uk",
               "http://www.gla.ac.uk",
               "http://www.kent.ac.uk",
               "http://www.ed.ac.uk",
               "http://www.essex.ac.uk",
               "http://www.leeds.ac.uk",
               "http://www.nottingham.ac.uk",
               "http://www.liv.ac.uk",
               "http://www.dur.ac.uk",
               "http://www.anglia.ac.uk",
               "http://www.strath.ac.uk",
               "http://www.kingston.ac.uk",
               "http://www.shef.ac.uk",
               "http://www.glam.ac.uk",
               "http://www.jiscmail.ac.uk",
               "http://www.ebi.ac.uk" ]
    
    Academ2 = ["http://www.ucl.ac.uk",
               "http://www3.imperial.ac.uk",
               "http://www.le.ac.uk",
               "http://www.bath.ac.uk",
               "http://www.soton.ac.uk",
               "http://www.kcl.ac.uk",
               "http://www.manchester.ac.uk",
               "http://www.bris.ac.uk",
               "http://www.nottingham.ac.uk",
               "http://www.brunel.ac.uk",
               "http://www.abdn.ac.uk",
               "http://www.exeter.ac.uk",
               "http://www.city.ac.uk",
               "http://www.reading.ac.uk",
               "http://www.qub.ac.uk",
               "http://www.cardiff.ac.uk",
               "http://www.herts.ac.uk",
               "http://www.ulster.ac.uk" ]
    
    Academ3 = ["http://www.stanford.edu",
               "http://www.harvard.edu",
               "http://www.yale.edu",
               "http://www.umich.edu",
               "http://www.utexas.edu",
               "http://www.umd.edu",
               "http://www.wisc.edu",
               "http://www.wisconsin.edu ",
               "http://www.washington.edu",
               "http://www.uwlax.edu",
               "http://www.uwsp.edu",
               "http://www.umich.edu",
               "http://illinois.edu",
               "http://matcmadison.edu",
               "http://www.uwrf.edu",
               "http://www.uwec.edu" ]
    
    filepath5 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/wiki_pages/"
    WikiPages = ["http://en.wikipedia.org/wiki/Main_Page",
                 "http://www.njc.edu.sg",
                 "http://wiki.mobileread.com/wiki/Main_Page"]
                
    filepath6 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/forum/"
    Forum1 = ["http://www.sbrforum.com",
              "http://www.forumw.org",
              "http://forum.joomla.org",
              "http://www.kde-forum.org",
              "http://ubuntuforums.org",
              "http://www.ruby-forum.com",
              "http://www.python-forum.org/pythonforum/index.php",
              "http://forums.onlinebookclub.org",
              "http://www.bookclubforum.co.uk",
              "http://www.fanforum.com",
              "http://www.dance-forums.com",
              "http://www.digitalspy.co.uk",
              "http://www.dance.net",
              "http://www.danceforums.net",
              "http://www.uk-dance.co.uk",
              "http://forums.televisionwithoutpity.com",
              "http://www.theinternetforum.co.uk",
              "http://forums.jokersupdates.com/ubbthreads" ]
    
    Forum2 = ["http://www.satelliteguys.us",
              "http://dancingmood.net",
              "http://www.liondancing.org",
              "http://www.geekstogo.com",
              "http://www.forumforgeeks.com",
              "http://www.ppcgeeks.com",
              "http://www.theoutdoorsforum.com",
              "http://forums.outdoorsdirectory.com",
              "http://www.outdoorsmenforum.ca",
              "http://christianoutdoorsman.com",
              "http://www.jimsbeerkit.co.uk/forum/index.php",
              "http://www.thebrewingnetwork.com/forum",
              "http://forums.morebeer.com",
              "http://www.mrbeerfans.com/ubbthreads",
              "http://www.mycarforum.com",
              "http://www.carsforums.com",
              "http://www.carforums.net",
              "http://www.autocar.co.uk/Forums/default.aspx" ]
    
    Forum3 = ["http://sportscarforums.com",
              "http://www.britishcarforum.com",
              "http://www.caraudioforum.com",
              "http://modifiedcarforums.com",
              "http://www.ecocarforum.com",
              "http://www.slotforum.com",
              "http://www.autocareforum.com",
              "http://www.apteraforum.com",
              "http://www.chinacarforums.com" ]
    #(News1,filepath1, 200), (News2, filepath1, 200), (News3, filepath1, 200), (Blogs1, filepath2, 200), (Blogs2, filepath2, 200),  
    AllGenres = [ (Blogs3, filepath2, 200),
                  (Product_comp1, filepath3, 170), (Product_comp2, filepath3, 170), (Product_comp3, filepath3, 170), (Product_comp4, filepath3, 170),
                  (Academ1,filepath4, 200), (Academ2, filepath4, 200), (Academ3, filepath4, 200),
                  (Forum1, filepath6, 210), (Forum2, filepath6, 210), (Forum3, filepath6, 210),
                  (WikiPages, filepath5, 3500) ]
    
    #Manger process for InterProcess Event() and Simple Queue()
    m = Manager()
    #m.start() no need for this for a default manager
    #Define a Global Process Termination Event which will start Manager Process and will return a proxy to the Event() 
    killall_evt = m.Event()
    #Define an xhtmltree Queue for farther analysis of the pages from other Processes
    #xhtmltree_q = Queue() # Only for interprocess communication
    
    #Define a variable that will use get the primitive analysis output of the SCSpider(s)   
    vects_q = Queue()  
    
    for Genre, filepath, sites_no in AllGenres:
        #Start the SCSpider restricted to scan the pages of one WebSite
        scspider_ps = list()
        for Seed in Genre:
            #NOTICE: "kill_evt=m.Event()," for having different termination signal for each Spider since for this Strategy (2) they do not collaborate
            scspider_ps.append( SCSpider(seed=str(Seed), base_url_drop_none=False, urls_number_stop=sites_no, kill_evt=m.Event(), spider_spoof_id=user_agent, save_path=str(filepath) ) )
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
                scspider.join(1)
        #In case some Process is still alive Just Kill them all
        for scspider in scspider_ps:
            if scspider.is_alive():
                scspider.terminate()
        
    print("Thank you and Goodbye!")     
    
    