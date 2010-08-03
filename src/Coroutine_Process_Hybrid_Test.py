
"""Testing a case of function to be a Process and coroutine at the same time"""

import urllib2   
import syncioscheduler

from asyncurlopen import AsyncUrlOpen

header = {
            'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9)' 
                }

def fetch(req):
    while True:
        resp = yield req.read()
        print ("Printing Response %s" % resp)         
       

if __name__ == "__main__":
    #rq = urllib2.Request(url="http://www.in.gr/", headers=header)
    sock1 = urllib2.urlopen("http://www.in.gr/")
    print (sock1.geturl())
    #sock = AsyncUrlOpen( urllib2.urlopen(rq) )   
    #sched = syncioscheduler.SynCIOScheduler()
    #sched.new( fetch(sock) )
    #sched.run()
     
    