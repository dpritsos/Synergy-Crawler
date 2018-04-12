"""
Synmather: Synergy Web Crawling Mother Programm

<!-- Write a summary here -->


Author: Dimitrios Pritsos

Last update: 03.05.2010
            01.06.2010 --

"""
from multiprocessing.managers import BaseManager
from multiprocessing import Process
import threading
import urllib
import HTMLParser
from Queue import Queue
import hashlib
import time

class SynCMotherHandler(Process):
    """SynCMotherHandler:"""
    def __init__(self, SynCMother):
        Process.__init__(self)
        self.synCMom = SynCMother
        self.pDUECounter = 0

    def run(self):
        DUEliminatorsL = list()
        pDUE = Process( target=self._DUEliminator )
        DUEliminatorsL.append( pDUE )
        DUEliminatorsL[self.pDUECounter].start()
        print "pDUECounter:" + str( self.pDUECounter + 1 )
        while True:
            if self.synCMom.rawUrlsQ_qsize() > 2 and self.pDUECounter < 2:
                pDUE = Process( target=self._DUEliminator )
                DUEliminatorsL.append( pDUE )
                self.pDUECounter += 1
                DUEliminatorsL[self.pDUECounter].start()
                print "pDUECounter:" + str( self.pDUECounter + 1 )

    def _DUEliminator(self):
        print "RawQueueSize:" + str( self.synCMom.rawUrlsQ_qsize() )
        while True:
            #time.sleep(10)
            urlsLL = self.synCMom.rawUrlsQ_get()
            self.synCMom.acquire()
            self.synCMom.DUEliminate(urlsLL)
            self.synCMom.notify_all()
            self.synCMom.release()


class SynCMother:
    """symmother Class is handling two internal dictionaries one for web Sites that pending to
        be scanned and downloaded and one for the ready web sites, i.e. the ones that already been
        given to a process Pool to scan and download them"""

    def __init__(self):
        self.rawUrlsQ = Queue(100)
        hash = hashlib.md5()
        hash.update("http://www.blogs.com/")
        self.pending_urls = [[hash.digest(), "http://www.blogs.com/"]] # None
        self.scanned_urls = None
        self.ready_urls = threading.Condition()
        # The conditional variable notify the synworkers that some URL pending for handling

    def get_scanned(self):
        return self.scanned_urls

    def urls_pending(self):

        if self.pending_urls == None:
            return False

        else:
            return True

    def get_urls(self):

        urls = self.pending_urls

        if urls is not None:
            if self.scanned_urls is None:
                self.scanned_urls = [hashcode for hashcode, url in self.pending_urls]
            else:
                self.scanned_urls.extend([hashcode for hashcode, url in self.pending_urls])

        self.pending_urls = None
        return [url for hashcode, url in urls]

    def DUEliminate(self, urlsLL):

        # print "Mother DUEliminate..."
        if self.scanned_urls is None:

            self.pending_urls = urlsLL

        else:

            self.pending_urls = list()

            for i in range(len(urlsLL)):
                if not urlsLL[i][0] in self.scanned_urls:
                    self.pending_urls.append(urlsLL[i])

            if len(self.pending_urls) == 0:
                self.pending_urls = None

        # print "Mother DUEliminate - END"

    def send_urls(self, urls):
        self.rawUrlsQ.put(urls)

    def acquire(self):
        self.ready_urls.acquire()

    def release(self):
        self.ready_urls.release()

    def wait(self, timeout=None):
        if timeout is None:
            self.ready_urls.wait()
        else:
            self.ready_urls.wait(timeout)

    def notify_all(self):
        self.ready_urls.notify_all()

    def rawUrlsQ_qsize(self):
        return self.rawUrlsQ.qsize()

    def rawUrlsQ_get(self):
        return self.rawUrlsQ.get()


# Define the Manager Process for managing proxies to the the 'synmother' objects
class SynCMotherManager(BaseManager): pass
# SynCMotherManager.register('SynCMother', SynCMother)


if __name__ == "__main__":

    synmother_localhost = SynCMother()
    print "Mother is running"

    # Start a Manager for synmother_localfsdafsfsahos
    SynCMotherManager.register('SynCMother', callable=lambda: synmother_localhost)
    syncmm = SynCMotherManager(address=('', 15000), authkey='123456')
    synm = syncmm  # .get_server()
    synm.start()  # serve_forever()

    synCMotherHandler = SynCMotherHandler(synm.SynCMother())
    synCMotherHandler.start()
    synCMotherHandler.join()

    print "End of Programme"
