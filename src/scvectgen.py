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

from scvectorhandlingtools import *

    
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
        nonwhite_str = re.compile(r'\S')
        alphanum_str = re.compile(r'[^.(),!@#$%&*-_=+/\\?><"\':]')
        url_str = re.compile(r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/)))')
        date_str = re.compile(r'^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$')
        word_str = re.compile(r'\b\w+\b')
        #word_str = re.compile(r'\b(\w+)')
        ############################################ fix Regular expressions ###############################
        dot_chr = re.compile(r'[.]')
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
            xhtml_text_l = extract_txt(xhtml_t) #.xpath("//text()") 
            for i in range(len(xhtml_text_l)):
                xhtml_text_l[i] = unicodedata.normalize('NFKC', xhtml_text_l[i].decode()) 
            #xhtml_text_l.sort() #not really necessary 
            xhtml_TF = dict()
            for terms_s in xhtml_text_l:
                terms_l = terms_s.split(" ")
                for term in terms_l:
                    term_chr_l = nonwhite_str.findall(term)
                    term = "".join(term_chr_l)
                    url_term = url_str.findall(term)
                    if url_term:
                        term = url_term[0]
                    else:
                        date_term = date_str.findall(term)
                        if date_term:
                            term = date_term[0]
                        else:
                            word_term = word_str.findall(term)
                            term = word_term
                    #term = "".join(term_chr_l) 
                    if term in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                        xhtml_TF[term] += 1
                    elif term != "":
                        xhtml_TF[term] = 1
            #Append the URL of the xtree to the list of Web Pages that the TF (or other) vector has been Generated 
            webpg_l.append( xhtml_d['url_resp'] )
            #Append the Term Vector of the xtree to the list of Web Pages' Vectors
            webpg_vect_l.append(xhtml_TF)
        global_term_dict = gterm_d_gen(webpg_vect_l) 
        print(len(webpg_l), len(webpg_vect_l))
        base_url_str = xhtml_d['base_url'].replace("http://", "")
        filename = str( len(webpg_l) ) + "-" + base_url_str  + "_CORPUS_DICTIONARY"   
        if save_dct(filename, global_term_dict ):
            print( str( xhtml_d['base_url'] ) + "_GLOBAL_TERMS_DICTIONARY: SAVED!" )
        filename = str( len(webpg_l) ) + "-" + base_url_str + "_CORPUS_VECTORS"
        if save_dct_lst( filename, webpg_vect_l, webpg_l ):
            print( str( xhtml_d['base_url'] ) + "_CORPUS_VECTORS: SAVED!" )
        
        #################################################
        
        term_list = global_term_dict.keys()
        terms_num_dict = dict()
        for i in xrange(len(term_list)):
            terms_num_dict[ term_list[i] ] = i 
        print("Term List is Ready %s" % len(term_list))
        num_label_test = label_numerically(webpg_vect_l, terms_num_dict)
        print("New Numerical Dict ready %s" % len(num_label_test))
        print("Sample %s" % num_label_test[0])
        filename = str( len(webpg_l) ) + "-" + base_url_str + "_NUM_TEST"
        if save_dct_lst( filename, num_label_test, webpg_l ):
            print( str( xhtml_d['base_url'] ) + "_NUM_TEST: SAVED!" )
       









     