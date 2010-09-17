"""
"""
import re
import numpy
import scipy
import multiprocessing
from multiprocessing import Pool, Process, Value
#from eventlet.green import urllib2
from threading import Thread
import eventlet 
import lxml.etree 
import lxml.html
import lxml.html.soupparser as soup
from StringIO import StringIO
from collections import deque
from urlparse import urlparse 
import hashlib

from lxml.html.clean import Cleaner

import time


class SCVectGen(Process): 
    """SCVectGen:"""    
    Num = 0    
    
    def __init__(self, *sc_xtrees, **kwargs): 
        Process.__init__(self)
        SCVectGen.Num += 1
        self.pnum = SCVectGen.Num 
        self.sc_xtrees = sc_xtrees 
        self.kill_evt = kwargs.pop("kill_evt", multiprocessing.Event().clear()) 
    
    def run(self):
        """SCVectGen's main function"""
        reg_obj = re.compile(r'[^\s]')
        htmlparser_r = lxml.etree.HTMLParser(recover=True, no_network=False)
        while True:
            #print("Running")
            #Checking for termination signal
            if self.kill_evt.is_set():
                print("SCVectGen Process (PID = %s - PCN = %s): Terminated" % (self.pid, self.pnum))
                SCVectGen.Num -= 1
                return
            #Extract the attributes of every XHTML create the Proper Vector(s) and save them 
            #for sc_xtr in self.sc_xtrees:
            try:
                xhtml_d = self.sc_xtrees[0].get_nowait()
            except:
                continue
            continue
            #if the SCVectGen process manages to get an xhtml_d from the Queue then process the xhtml source
            #xhtml_d = sc_xtr.get()
            xhtml_s = xhtml_d['xtree']
            f = open("/home/dimitrios/Desktop/PhD_papers/genre_archive/00/00/10/10/sc8003.doc.htm", "r")
            xhtml_t = lxml.etree.parse(f, parser=htmlparser_r)
            cleaner = Cleaner( scripts=True, javascript=True, comments=True, style=True,\
                           links=True, meta=True, page_structure=False, processing_instructions=True,\
                           embedded=True, annoying_tags=True, remove_unknown_tags=True )#meta=False becasue we need MetaInfo
            xhtml_s = cleaner.clean_html(lxml.etree.tostring(xhtml_t))
            xhtml_t = lxml.etree.fromstring(xhtml_s, parser=htmlparser_r)
            xhtml_text_l = xhtml_t.xpath("//text()") 
            xhtml_text_l.sort()
            xhtml_TF = dict()
            for terms_s in xhtml_text_l:
                terms_l = terms_s.split(" ")
                for term in terms_l:
                    term_chr_l = reg_obj.findall(term)
                    term = "".join(term_chr_l) 
                    if term in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                        xhtml_TF[term.decode("utf8")] += 1
                    elif term != "":
                        xhtml_TF[term.decode("utf8")] = 1 
            print("HTML STRING: %s" % xhtml_TF)
                        
            
            
            
            
        
        
        
        
        
        
        
        