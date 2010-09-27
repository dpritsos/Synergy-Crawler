"""
"""
import re
import numpy
import scipy
import multiprocessing
from multiprocessing import Pool, Process, Value, Queue
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

import codecs

from lxml.html.clean import Cleaner

import time

from scgenrelerner_svmbased import *



def label_properly(webpg_vect_l, vect_l_chnk):
    #Thread or MultiProcess Bellow Part or it will NEVER-END####################################################################
    new_webpg_vect_l = list()
    print("in")
    for pg_vect in webpg_vect_l:
        #pg_vect = webpg_vect_l[i]
        #i = webpg_vect_l.index(pg_vect) # get the index here because it seems that 'in' operator prevent this... Not know why yet
        libsvm_pg_vect = dict() 
        for set_term in Gset_terms:
            if set_term in pg_vect: #Is the 'in' operator cases copy of the pg_vect?
                libsvm_pg_vect[ Gset_terms.index(set_term) ] = pg_vect[set_term]
        new_webpg_vect_l.append( libsvm_pg_vect )
    print("out")
    vect_l_chnk.put( new_webpg_vect_l )
    print("put DONE!")
    

Gset_terms = list()
vect_l_chnk = Queue()

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
                xcharset = "utf8"
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
                        xhtml_TF[term] += 1
                    elif term != "":
                        xhtml_TF[term] = 1
            #Append the URL of the xtree to the list of Web Pages that the TF (or other) vector has been Generated 
            webpg_l.append( xhtml_d['xtree'] )
            #Append the Term Vector of the xtree to the list of Web Pages' Vectors
            webpg_vect_l.append(xhtml_TF)
        webpg_vect_l, set_vect, set_terms_l = self.make_libsvm_sparse_vect(webpg_vect_l)
        print("SVM input Vectors pre-processing DONE!")
        print(set_terms_l[0])
        class_tags = map( lambda x:1, range(len(webpg_l)) ) 
        print(len(class_tags), len(webpg_l), len(webpg_vect_l))
        self.save("SET_TERMS", set_vect)
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
        Gset_terms.extend(set_terms) 
        print("make_libsvm_sparse_vect: First Part Done")
        print(len(set_vect))
        #set_terms.sort()
        new_webpg_vect_l = list()
        chunck_wp_l =list()
        webpg_vect_l_size = len(webpg_vect_l)
        chnk_size = webpg_vect_l_size/12
        chnk_remain = webpg_vect_l_size%12
        pre_i = 0
        for i in range(chnk_size, webpg_vect_l_size, chnk_size):
            chunck_wp_l.append( webpg_vect_l[ pre_i : i ] )
            pre_i = i
        if chnk_remain != 0 :
            chunck_wp_l[11].extend( webpg_vect_l[ len(chunck_wp_l) : (len(chunck_wp_l) + chnk_remain) ] ) 
        print("Chuncking Done!")
        labeling_ps = list()
        for i in xrange(len(chunck_wp_l)):  
            labeling_ps.append( Process(target=label_properly, args=(chunck_wp_l[i],vect_l_chnk)) )
        for lbl_p in labeling_ps:
            lbl_p.start()
        print("Starting Done!")
        for i in xrange(len(chunck_wp_l)):
            new_webpg_vect_l.extend(vect_l_chnk.get())
        print("concatenation Done!")
        for lbl_pp in labeling_ps:
            lbl_pp.join()
            print("Process End")
        print("Processing Done!")
        #Thread or MultiProcess Bellow Part or it will NEVER-END####################################################################
        #new_webpg_vect_l = list()
        #for pg_vect in webpg_vect_l:
            #pg_vect = webpg_vect_l[i]
            #i = webpg_vect_l.index(pg_vect) # get the index here because it seems that 'in' operator prevent this... Not know why yet
        #    libsvm_pg_vect = dict() 
        #    for set_term in set_terms: 
        #        if set_term in pg_vect: #Is the 'in' operator cases copy of the pg_vect? 
        #            libsvm_pg_vect[ set_terms.index(set_term) ] = pg_vect[set_term]
        #        new_webpg_vect_l.append( libsvm_pg_vect )
        
        print("make_libsvm_sparse_vect: Second Part Done")
        return (new_webpg_vect_l, set_vect, set_terms)
     
    def save(self, filename, records):
        """save():"""
        try:
            #Codecs needed for saving string that are encoded in UTF8  
            f = codecs.open( "/home/dimitrios/Documents/Synergy-Crawler/seen_urls/" + filename, "w", "utf-8" ) #Change "utf8" with xcharset (see above)
        except IOError:
            return None 
        try: 
            for rec in records:
                f.write(rec + " => "  + str(records[rec]) + "\n") # Write a string to a file
        except:
            print("ERROR WRITTING FILE: %s" % filename)
            f.close()
        f.close()
        return True           
                
            
                        
            
            
            
            
        
        
        
        
        
        
        
        