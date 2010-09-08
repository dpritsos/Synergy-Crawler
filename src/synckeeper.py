#synmother_client_manager

from multiprocessing import Process, current_process 
import urlparse
import random 


class SynCKeeper(Process):
    """SynCFetcherProcess:"""
    PROCESSNUM = 0
    
    def __init__(self, keepersQ):
        Process.__init__(self)
        SynCKeeper.PROCESSNUM += 1
        self.keepersQ = keepersQ 
        self.htmlSrcTuple = None 
                      
    def run(self):
        #print "SynCKeeper Process with PID:%s and PCN:%s - Engaged" % (current_process().pid, SynCKeeper.PROCESSNUM)
        while True:
            self.htmlSrcTuple = self.keepersQ.get()
            if self.htmlSrcTuple == None:
                print( "SynCKeeper Process with PID:%s and PCN:%s - Terminated (None...to do)" % (current_process().pid, SynCKeeper.PROCESSNUM) )
                SynCKeeper.PROCESSNUM -= 1
                return
            self._save_html_src()
            
    def _save_html_src(self):
        #print "In Save"
        gblcounter = random.randint(1, 99999999) 
        htmlsrc, charset, url = self.htmlSrcTuple
        if htmlsrc == None:
            return
        gblcounter += 1 
        urlres = urlparse.urlparse(url, "http")
        directory = urlres.netloc + urlres.path
        filename = urlres.netloc + "-" + str(gblcounter) + ".html"
        filepn = "/home/dimitrios/Documents/Synergy-Crawler/" + filename
        #print "Save:" + str(filepn)
        try:
            # This will create a new file or **overwrite an existing file**.
            f = open( filepn, "w" ) #fix the nameing thing
            try:
                #print "WRITING..."
                f.write(htmlsrc) # Write a string to a file
                #f.writelines(lines) # Write a sequence of strings to a file
            finally:
                f.close()
        except IOError:
            pass
    
