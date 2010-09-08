

"""
FROM EVENLET DEMOS:
This is a simple web "crawler" that fetches a bunch of urls using a pool to 
control the number of outbound connections. It has as many simultaneously open
connections as coroutines in the pool.

The prints in the body of the fetch function are there to demonstrate that the
requests are truly made in parallel.

FROM DIMITRIOS:
In order to see if the GreenPool class can use a method of the Class that it first time is declared
I made a Process Class that opens a GreenPool (Greenlets, known as MicroThreads too) and used one of the
methods defined in the Class. Some of the input data are given to the GreenThreads from the Class' 
Globals and some as argument. 

On the contrary Calling a Class method from a multiprocessin.Pool() class is impossible because of some Pickling
restrictions. In addition to this lost of Processes case great memory overhead just for declaring them. Moreover, 
big number of Processes with small chuncks of data is extremely slow. So Pool is best for BIG chuncks of Data, with 
small amount of ProcessWorkes say no more of two times you CPU Cores. The main reason for the delay is Pickling in 
order to distribute the data (by value) to the Processes. In complex cases like this one just use multhreading.Process(Func, args)
with some For loop. In case the procedure is CPU bound. In case you need Async I/O (Thousands of files or Internet connection just
use Async I/O with GreenThreads known as MircoThread) this is what WebServers do :) 

IT FUCKING WORKS!

"""

############ DON'T FORGET:  sudo easy_install Eventlet ############

#Fortunately 
urls = [[0,"http://www.google.com/intl/en_ALL/images/logo.gif"],
     [1,"https://wiki.secondlife.com/w/images/secondlife.jpg"],
     [2,"http://us.i1.yimg.com/us.yimg.com/i/ww/beta/y3.gif"]]

import eventlet
from eventlet.green import urllib2  
from multiprocessing import Process

class test(Process):
    
    def __init__(self, URLs):
        Process.__init__(self)
        self.urls = URLs
        self.timer = 10
        
    def run(self):
        pool = eventlet.GreenPool(2000000) #you can open as many GreenThreads as you want
        while self.timer:
            #imap will return an iterator of results, so as long as the URL is download (or the file is read)
            #you get the results Asynchronouly  
            #something = str(1232131) # TRY THIS TO SEE THE DIFF 
            something = map( lambda x:32132131, range(len(urls)) ) #Every argument mast be iteratable
            for url, body in pool.imap(self.fetch, something, urls):  
                print "got body from", url, "of length", len(body)
            self.timer -= 1
            
    def fetch(self, something, url):
        #NOTE: the sequence of the prints (there is no order) to understand the Concurrency and the 
        #Asynchronous printing depending on the I/O sequence of events
        print("Something", something)
        print("Passing arguments as a Class Globals:", self.urls)
        print "opening", url[1] 
        body = urllib2.urlopen(url[1]).read() #Connects to url -> returns a file-like object -> reads the page from server
        print "done with", url[1] #Note: is like you get each list sequentially (however you get it Async) even if you give a
                                  #list(list()) as an input       
        return url[1], body



if __name__ == '__main__':
    t = test(urls)
    t.start()
    t.join() #Join the main process i.e. this file running
    
    
    
