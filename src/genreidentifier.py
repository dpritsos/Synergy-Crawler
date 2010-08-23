"""
"""
from multiprocessing import Process
import re
import numpy
import scipy
from lxml import etree

class GenreIdentifier(Process):
    processnum = 0
    def __init__(self, WebPagesTouplesQ):
        Process.__init__(self)
        GenreIdentifier.processnum += 1
        self.webpages_q = WebPagesTouplesQ
    def run(self):
        while True: #not self.counter:
            (src, cod, url) = self.webpages_q.get()
            eltree = etree.fromstring( src )
            raw_text = eltree.findtext()
            print(raw_text)
            #res = self.gIdent.get()
            #if res:
            #    print(res)
            #    self.counter += 1
    def __xml(self):
        pass
    
class GGGGGenreIdentifier(object):
    pass        