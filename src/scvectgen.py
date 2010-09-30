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

import unicodedata


def label_numerically(webpg_vect_l, Gset_terms):
    new_webpg_vect_l = list()
    for pg_vect in webpg_vect_l:
        #enc_pg_vect = pg_vect.keys()
        #for i in range(len(enc_pg_vect)):
        #    enc_pg_vect[i] = enc_pg_vect[i].encode("utf-8")
        libsvm_pg_vect = dict()
        for pg_term in pg_vect:
            libsvm_pg_vect[ Gset_terms[pg_term] ] = pg_vect[pg_term]
        new_webpg_vect_l.append( libsvm_pg_vect )
    return new_webpg_vect_l


    
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
        #reg_obj = re.compile(r'')
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
            #NFKC: normalised to composed Unicode form with transformation of special 
            #characters to composed from too, for consistent text processing
            for i in range(len(xhtml_text_l)):
                xhtml_text_l[i] = unicodedata.normalize('NFKC', xhtml_text_l[i].decode()) 
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
            webpg_l.append( xhtml_d['url_resp'] )
            #Append the Term Vector of the xtree to the list of Web Pages' Vectors
            webpg_vect_l.append(xhtml_TF)
        global_term_dict = self.gterm_d_gen(webpg_vect_l) 
        print(len(webpg_l), len(webpg_vect_l))
        base_url_str = xhtml_d['base_url'].replace("http://", "")
        filename = str( len(webpg_l) ) + "-" + base_url_str  + "_CORPUS_DICTIONARY"   
        if self.save_dct(filename, global_term_dict ):
            print( str( xhtml_d['base_url'] ) + "_GLOBAL_TERMS_DICTIONARY: SAVED!" )
        filename = str( len(webpg_l) ) + "-" + base_url_str + "_CORPUS_VECTORS"
        if self.save_dct_lst( filename, webpg_vect_l, webpg_l ):
            print( str( xhtml_d['base_url'] ) + "_CORPUS_VECTORS: SAVED!" )
        
        ################################################# NEEDS DEBUGGING ###########################################
        
        term_list = global_term_dict.keys()
        terms_num_dict = dict()
        for i in xrange(len(term_list)):
            terms_num_dict[ term_list[i] ] = i 
        print("Term List is Ready %s" % len(term_list))
        num_label_test = label_numerically(webpg_vect_l, terms_num_dict)
        print("New Numerical Dict ready %s" % len(num_label_test))
        print("Sample %s" % num_label_test[0])
        filename = str( len(webpg_l) ) + "-" + base_url_str + "_NUM_TEST"
        if self.save_dct_lst( filename, num_label_test, webpg_l ):
            print( str( xhtml_d['base_url'] ) + "_NUM_TEST: SAVED!" )
       
    def gterm_d_gen(self, webpg_vect_l):
        set_vect = dict()
        #Creat the Global Term Vector of Frequencies
        for pg_vect in webpg_vect_l:
            pg_trm_l = pg_vect.keys()
            for pg_trm in pg_trm_l:
                if pg_trm in set_vect: 
                    set_vect[pg_trm] += pg_vect[pg_trm]
                else:
                    set_vect[pg_trm] = pg_vect[pg_trm]
        #set_terms = set_vect.keys()
        print("Global Terms Dictionary: Ready!")
        return set_vect
  
     
    def save_dct(self, filename, records):
        """save_dct():"""
        try:
            #Codecs needed for saving string that are encoded in UTF8, but I do not need it because strings are already the Proper Encoding form
            f = codecs.open( "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/" + filename, "w", "utf-8") #change "utf-8" to xcharset
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
    
    def save_dct_lst(self, filename, records, index):
        try:
            #Codecs needed for saving string that are encoded in UTF8, but I do not need it because strings are already the Proper Encoding form
            f = codecs.open( "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/" + filename, "w", "utf-8") #change "utf-8" to xcharset
        except IOError:
            return None 
        try: 
            for i in range(len(index)):
                f.write(index[i] + " => ")
                for rec in records[i]:
                    f.write( str(rec) + ":"  + str(records[i][rec]) + "\t") 
                f.write("\n") 
        except:
            print("ERROR WRITTING FILE: %s" % filename)
            f.close()
        f.close()
        return True           
        
                
            
                        
            
            
            
            
        
        
        
        
        
        
        
        