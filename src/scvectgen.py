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

from scgenrelerner_svmbased import *

class SCVectGen(Thread): 
    """SCVectGen:"""    
    Num = 0    

    def __init__(self, webpg_vect_tu, *sc_xtrees, **kwargs): 
        Thread.__init__(self)
        SCVectGen.Num += 1
        self.pnum = SCVectGen.Num 
        self.webpg_vect_tu = webpg_vect_tu
        self.sc_xtrees = sc_xtrees 
        self.kill_evt = kwargs.pop("kill_evt", multiprocessing.Event().clear()) 
    
    def run(self):
        """SCVectGen's main function"""
        reg_obj = re.compile(r'[^\s]')
        extract_txt = lxml.etree.XPath("//text()")
        webpg_l = list()
        webpg_vect_l = list()
        while True:
            #print("Running")
            #Checking for termination signal
            if self.kill_evt.is_set():
                print("SCVectGen (Thread or Process CN = %d): Terminated" % (self.pnum))
                SCVectGen.Num -= 1
                break
             #xhtml_d['xtree'] 
             #xhtml_d['parsing_errors']
             #xhtml_d['charset'] 
             #xhtml_d['url_req'] 
             #xhtml_d['url_resp']
            #Extract the attributes of every XHTML create the Proper Vector(s) and save them 
            #for sc_xtr in self.sc_xtrees:
            try:
                xhtml_d = self.sc_xtrees[0].get_nowait()
            except:
                continue
            xhtml_t = xhtml_d['xtree']
            if not xhtml_t:
                continue
            xcharset = xhtml_d['charset']
            if not xcharset:
                xcharset = "utif8"
            #print("DUE: %s => %s" % (isinstance(xhtml_t, lxml.html.HtmlElement), "") )
            #cleaner = Cleaner( scripts=True, javascript=True, comments=True, style=True,\
            #               links=True, meta=True, page_structure=False, processing_instructions=True,\
            #               embedded=True, annoying_tags=True, remove_unknown_tags=True )#meta=False because we need MetaInfo
            #xhtml_s = cleaner.clean_html(xhtml_s)
            #xhtml_t = lxml.etree.fromstring(xhtml_s, parser=htmlparser_r)
            xhtml_text_l = extract_txt(xhtml_t) #.xpath("//text()") 
            #xhtml_text_l.sort() #not really necessary 
            xhtml_TF = dict()
            for terms_s in xhtml_text_l:
                terms_l = terms_s.split(" ")
                for term in terms_l:
                    term_chr_l = reg_obj.findall(term)
                    term = "".join(term_chr_l) 
                    if term in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                        xhtml_TF[term.decode(xcharset)] += 1
                    elif term != "":
                        xhtml_TF[term.decode(xcharset)] = 1
            #Append the URL of the xtree to the list of Web Pages that the TF (or other) vector has been Generated 
            webpg_l.append( xhtml_d['xtree'] )
            #Append the Term Vector of the xtree to the list of Web Pages' Vectors
            webpg_vect_l.append(xhtml_TF)
        webpg_vect_l, set_vect, set_terms_l = self.make_libsvm_sparse_vect(webpg_vect_l)
        print("SVM input Vectors pre-processing DONE!")
        class_tags = map( lambda x:1, range(len(webpg_l)) )
        train_svm(class_tags, webpg_vect_l)
        #self.webpg_vect_tu.put( 1 ) #(webpg_l, webpg_vect_l, set_vect, set_terms_l)
       
    def make_libsvm_sparse_vect(self, webpg_vect_l):
        set_vect = dict()
        #Creat the Global Term Vector of Frequencies
        for pg_vect in webpg_vect_l:
            pg_trm_l = pg_vect.keys()
            for pg_trm in pg_trm_l:
                if pg_trm in set_vect: 
                    set_vect[pg_trm] += pg_vect[pg_trm]
                else:
                    set_vect[pg_trm] = pg_vect[pg_trm]
        set_terms = set_vect.keys()
        set_terms.sort()    
        for pg_vect in webpg_vect_l:
            libsvm_pg_vect = dict() 
            for set_term in set_terms: 
                if set_term in pg_vect:
                    libsvm_pg_vect[ set_terms.index(set_term) ] = pg_vect[set_term]
            pg_vect = libsvm_pg_vect
        return (webpg_vect_l, set_vect, set_terms)
                
                
            
                        
            
            
            
            
        
        
        
        
        
        
        
        