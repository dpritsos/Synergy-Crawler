"""
SynCManater:

<!-- Write a summary here -->


Author: Dimitrios Pritsos

Last update: 25.05.2010

"""
from multiprocessing import Process, Pool, current_process, Manager, Value
from multiprocessing.managers import BaseManager
import HTMLParser
import threading
import urllib

# Import Web Crawlers element modules
from syncscanner import SynCScanner
from syncfetcher import SynCFetcher
from synckeeper import SynCKeeper
import time

QUEUESIZE = 200

#  # # #  WHATS UP WITH THE MANAGER OBJECT AND THE PROXIES


class SynCManager(Process):
    """SyncManagerProcess:"""

    PROCESSNUM = 0

    def __init__(self, syncmotherProxy, syncqueuesmanager):
        Process.__init__(self)
        self.syncmother = syncmotherProxy

    def run(self):

        # ###
        #    BUT THERE IS A PROBLEM WITH MANAGER PASSING VARIABLES NOT REALY GOOD
        #    IMPLEMETATION FOR MULTIPROCESSING
        # ###

        self.syncqueuesmanager = Manager() # syncqueues
        # Queue of tuples (HTML source, URL) to be saved
        self.keepersQ = self.syncqueuesmanager.Queue()
        # List of Queues of tuples (HTML sources, Encoding) to be scanned for URLS - Not Share-able able to other Processes
        self.scannersQL = list()
        # Global Queue of tuples (HTML sources, Encoding) to be scanned
        self.scannersQL.append(self.syncqueuesmanager.Queue(QUEUESIZE))
        # Queue of tuples (HTML sources, Encoding) to be scanned for the first SynCScanner Process
        self.scannersQL.append(self.syncqueuesmanager.Queue(QUEUESIZE))
        # Queue of lists of URLs to be sent to SynCMother for Storage and UST (URL-seen)
        # i.e. SynCMother works as DUE (Duplicate URL eliminator)
        self.urlLQ = self.syncqueuesmanager.Queue()
        # list of html queues - Not Share-able able to other Processes
        self.fetchersQL = list()
        # The Global Queue of URLs to be downloaded
        self.fetchersQL.append(self.syncqueuesmanager.Queue(QUEUESIZE))
        # The fist Queue for the first SynCFetcher Process with URLs to be downloaded
        self.fetchersQL.append(self.syncqueuesmanager.Queue(QUEUESIZE))
        # List of SynCFetcher Processes
        self.pfetchersL = list()
        # List of SynCScanner Processes
        self.pscannersL = list()
        # List of SynCKeeper Processes
        self.pkeepersL = list()
        # INITIALIZE AT LEAST ONE PROCESS of each PROCESS CLASS -- NOT FINALL STRATEGY
        # Start fetcher processes (at least one)
        self.pfetchersL.append(SynCFetcher(self.fetchersQL[0], self.scannersQL[0], self.keepersQ))
        self.pfetchersL[0].start()
        # Start scanner processes (at least one)
        self.pscannersL.append(SynCScanner(self.scannersQL[0], self.urlLQ))
        self.pscannersL[0].start()
        # Start keeper processes (at least one)
        self.pkeepersL.append(SynCKeeper(self.keepersQ))
        self.pkeepersL.append(SynCKeeper(self.keepersQ))
        self.pkeepersL[0].start()
        self.pkeepersL[1].start()
        # var = self.urlLQ
        self.pFcount = Value("i")
        self.pScount = Value("i")
        self.pKcount = Value("i")
        self.pFcount.value = 1
        self.pScount.value = 1
        self.pKcount.value = 2
        pSendtoMom = Process(target=self._sendto_mom) # , args=(self.syncmother,self.urlLQ))
        pSendtoMom.start()
        pMonitoring = Process(target=self._monitor_all) # args=(self.keepersQ, self.scannersQL, self.urlLQ, self.fetchersQL, self.pfetchersL, self.pscannersL, self.pkeepersL))
        pMonitoring.start()
        pGetnDispatch = Process(target=self._get_n_dispatch)
        pGetnDispatch.start()
        while True:
            if self.fetchersQL[0].qsize() > 50 and self.pFcount.value < 150:
                # Start fetcher processes (at least one)
                self.pfetchersL.append(SynCFetcher(self.fetchersQL[0], self.scannersQL[0], self.keepersQ))
                # self.pFcount.value += 1
                self.pfetchersL[self.pFcount.value].start()
                self.pFcount.value += 1
            if self.scannersQL[0].qsize() > 50 and self.pScount.value < 50:
                # Start scanner processes (at least one)
                self.pscannersL.append(SynCScanner(self.scannersQL[0], self.urlLQ))
                # self.pScount.value += 1
                self.pscannersL[self.pScount.value].start()
                self.pScount.value += 1
            if self.keepersQ.qsize() > 50 and self.pKcount.value < 50:
                self.pkeepersL.append(SynCKeeper(self.keepersQ))
                self.pkeepersL[self.pKcount.value].start()
                self.pKcount.value += 1
    def _get_n_dispatch(self):
        while True:
            # Get URLs list form SynCMother - Blocks until it gets the list
            # urlL = self._get_from_mom()
            self.syncmother.acquire()
            while self.syncmother.urls_pending() == False:
                self.syncmother.wait()
            urlL = self.syncmother.get_urls()
            self.syncmother.release()
            # _distributed_urls(): distributes URLs to fetchers lists
            # for now just use a for and the global fetchers list
            for i in range(len(urlL)):
                self.fetchersQL[0].put(urlL[i])
    def _get_from_mom(self):
        # print "GET FROM MOM"
        self.syncmother.acquire()
        while self.syncmother.urls_pending() == False:
            self.syncmother.wait()
        urlList = self.syncmother.get_urls()
        self.syncmother.release()
        return urlList
    def _sendto_mom(self):
        while True:
            if self.urlLQ.empty() == False:
                # self.syncmother.acquire()
                self.syncmother.send_urls(self.urlLQ.get())
                # self.syncmother.notify_all()
                # self.syncmother.release()
    def _send_to_mom(self, var):
        # print "SEND TO MOM"
        self.syncmother.acquire()
        var = self.urlLQ.get()
        self.syncmother.send_urls(var)
        self.syncmother.notify_all()
        self.syncmother.release()
    def _monitor_all(self): # , keepersQ, scannersQL, urlLQ, fetchersQL, pfetchersL, pscannersL, pkeepersL):
        while True:
            print "*****Monitoring Report*****"
            print "keepersQ len:" + str(self.keepersQ.qsize())
            print "scannersQL len:" + str(len(self.scannersQL))
            print "scannersQ[0] size:" + str(self.scannersQL[0].qsize())
            print "urlLQ len:" + str(self.urlLQ.qsize())
            print "fetchersQL len:" + str(len(self.fetchersQL))
            print "fetchersQ[0] size:" + str(self.fetchersQL[0].qsize())
            print "pfetchersL Count:" + str(self.pFcount.value) # len(self.pfetchersL))
            print "pscannersL Count:" + str(self.pScount.value) # len(self.pscannersL))
            print "pkeepersL Count:" + str(self.pKcount.value)
            print "\n\n\n"
            time.sleep(10)


if __name__ == "__main__":
    class SynCMotherProxyManager(BaseManager): pass # Define the Manager Process
    SynCMotherProxyManager.register('SynCMother')
    print "Manager is running..."
    syncmotherObject = SynCMotherProxyManager(address=('192.168.1.68', 15000), authkey='123456')
    syncmotherObject.connect() # scannerpool1
    syncmotherProxy = syncmotherObject.SynCMother()

    syncqueuesmanager = Manager()
    q = syncqueuesmanager.Queue()
    print q
    pmanager = SynCManager(syncmotherProxy, syncqueuesmanager)
    pmanager.start()
