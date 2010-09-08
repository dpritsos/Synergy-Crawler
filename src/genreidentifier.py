"""
"""
from multiprocessing import Process
import re
import numpy
import scipy
from lxml import etree
from StringIO import StringIO

class GenreIdentifier(Process):
    processnum = 0
    def __init__(self, WebPagesTouplesQ):
        Process.__init__(self)
        GenreIdentifier.processnum += 1
        self.webpages_q = WebPagesTouplesQ
        
    def run(self):
        file = open("/home/dimitrios/Documents/Synergy-Crawler/XHTMLParsingResulrs.txt", "a")
        while True: #not self.counter:
            (src, cod, url) = self.webpages_q.get()
            try:
                parser = etree.XMLParser(dtd_validation=True, load_dtd=True, no_network=False, recover=True) #recover=True, dtd_validation=True)
                elroot = etree.parse(StringIO(src), parser)
            except etree.XMLSyntaxError, e:
                print("Error: " + str(e))
                parser = etree.HTMLParser(recover=True)
                elroot = etree.parse(StringIO(src), parser)
            #elroot.write(file)
            #print(etree.tostring(elroot, pretty_print=True))
            #res = self.gIdent.get()
            #if res:
            #    print(res)
            #    self.counter += 1
    def __xml(self):
        pass
    
class GGGGGenreIdentifier(object):
    pass        