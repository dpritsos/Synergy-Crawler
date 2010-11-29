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
import os

import codecs

from lxml.html.clean import Cleaner

import time

import unicodedata
    
class VectGen(object): 

    def __init__(self):
        #For appending the URL of the xtree to the list of Web Pages that the TF (or other) vector has been Generated 
        self.webpg_l = list()
        #For appending the Term Vector of the xtree to the list of Web Pages' Vectors
        self.webpg_vect_l = list()
        #For appending the Ngram Vector of the xtree ot the list of Web Pages' Vectors
        self.ngram_vect_l = list()
        #Defin XPath objects to extract (X)HTML attributes
        ##Extract Text
        self.extract_txt = lxml.etree.XPath("/html/body//text()")
        #Define Regular Expression to extract textual attributes
        ##Whitepace characters [<space>\t\n\r\f\v] matching, for splitting the raw text to terms
        self.white_spliter = re.compile(r'\s+')
        ##Export Ngrams => 3Grams
        self.tri_grams = re.compile(r'.{3}')
        ##Find URL String. Probably anchor text
        self.url_str = re.compile(r'(((ftp://|FTP://|http://|HTTP://|https://|HTTPS://)?(www|[^\s()<>.?]+))?([.]?[^\s()<>.?]+)+?(?=.org|.edu|.tv|.com|.gr|.gov|.uk)(.org|.edu|.tv|.com|.gr|.gov|.uk){1}([/]\S+)*[/]?)')
        #######################The above regular expression needs some more work for not incorrectly catching e.g. ".gr/dd/fdfd" or just ".com"
        ##Comma decomposer
        self.comma_decomp = re.compile(r'[^,]+|[,]+')
        self.comma_str = re.compile(r'[,]+')
        ##Find dot or sequence of dots
        self.dot_str = re.compile(r'[.]+')
        self.dot_decomp = re.compile(r'[^.]+|[.]+')
        ##Symbol term decomposer 
        self.fredsb_clean = re.compile(r'^[^\w]+|[^\w%]+$', re.U) #front-end-symbol-cleaning => fredsb_clean
        ##Find proper number
        self.proper_num = re.compile(r'(^[0-9]+$)|(^[0-9]+[,][0-9]+$)|(^[0-9]+[.][0-9]+$)|(^[0-9]{1,3}(?:[.][0-9]{3})+[,][0-9]+$)|(^[0-9]{1,3}(?:[,][0-9]{3})+[.][0-9]+$)') 
        
    
    def gen_vect(self, xhtml_d):
        #From here it starts the analysis of the page
        xhtml_t = lxml.html.parse( open(xhtml_d['filepath'] + xhtml_d['filename'], "r") )
        print "etree"
        if xhtml_t.getroot() == None:
            print "NONE"
            return [None, None, None]
        #print xhtml_t
        #xcharset = xhtml_d['charset']
        #if not xcharset:
        xcharset = "utf8"
        #Get the Text of the XHTML in a list of document lines
        try: 
            xhtml_text_l = self.extract_txt(xhtml_t)
        except:
            print "None"
            return [None, None, None]
        #Normalise Unicode String for consistency in text attributes extraction among all corpus' web pages 
        for i in range(len(xhtml_text_l)):
            xhtml_text_l[i] = unicodedata.normalize('NFKC', xhtml_text_l[i].decode()) 
        #Create the Word Term Frequency Vectors 
        xhtml_TF = dict()
        #Create the Trigramms Frequency Vectors
        xhtml_NgF = dict()
        #Define the term list that will be used for putting the Terms before we start counting them
        terms_l = list()
        for text_line in xhtml_text_l:
            #Initially split the text to terms separated by whitespaces [ \t\n\r\f\v] 
            terms_l.extend( self.white_spliter.split(text_line) )
        #Find and Count NGrams
        #for term in terms_l:
        #    for i in range(len(term)):
        #        Ngrms_l = self.tri_grams.findall(term[i:])
        #        for tri_g in Ngrms_l:
        #            if tri_g in xhtml_NgF: #if the dictionary of terms has the 'terms' as a key 
        #                xhtml_NgF[tri_g] += 1
        #            elif tri_g: #None empty strings are accepted 
        #                xhtml_NgF[tri_g] = 1
        #Count and remove the Numbers form the terms_l
        num_free_tl = list()
        for term in terms_l:
            num_term_l = self.proper_num.findall(term)
            if num_term_l: #if a number found the the term should be the number so we keep it as it is
                #for i in range(len(num_term_l[0])):
                #    use this for-loop in case you want tho know the exact form of the number.
                #    Each from has a position with the following order 1)xxxxxx 2)xxxx,xxxx 3)xxxx.xxxx 4)333.333.333...333,xxxxxx 5)333,333,333,333,,,333.xxxxxx
                if term in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                    xhtml_TF[term] += 1
                else:    
                    xhtml_TF[term] = 1
            else:
                #Keep only Non-Number terms or Non-proper-numbers
                num_free_tl.append(term)
        terms_l = num_free_tl
        #Decompose the terms to sub-terms of any symbol but comma (,) and comma sub-term(s)
        comma_free_tl = list()
        for term in terms_l:
            #Decompose the terms that in their char set include comma symbol to a list of comma separated terms and the comma(s) 
            decomp_term_l = self.comma_decomp.findall(term)
            if len(decomp_term_l) > 1:
                for subterm in decomp_term_l:
                    if self.comma_str.findall(subterm):
                        if subterm in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                            xhtml_TF[subterm] += 1
                        else:    
                            xhtml_TF[subterm] = 1
                    else: #if the substring is not a comma string then forward for farther analysis 
                        comma_free_tl.append(subterm)
            else:
                #Keep only the terms that are already free of commas because the other have been already decomposed and counted
                comma_free_tl.append(term)
        #use the comma_free terms list as the terms list to continue processing
        terms_l = comma_free_tl
        #Split term to words upon dot (.) and dot needs special treatment because we have the case of . or ... and so on
        dot_free_tl = list()
        for term in terms_l:
            decomp_term = self.dot_decomp.findall(term)
            dec_trm_len = len(decomp_term)
            if dec_trm_len > 1 and dec_trm_len <= 3: 
                #Here we have the cases of ...CCC or .CC or CC.... or CCC. or CC.CCC or CCCC....CCCC so keep each sub-term
                for sub_term in decomp_term:
                    if self.dot_str.findall(sub_term):
                        if sub_term in xhtml_TF: 
                            xhtml_TF[sub_term] += 1
                        else:
                            xhtml_TF[sub_term] = 1
                    else: #give the new terms for farther analysis
                        dot_free_tl.append(sub_term)
            elif dec_trm_len > 3: #i.e. Greater thatn 3
                #Remove the first and the last dot sub-string and let the rest of the term as it was (but the prefix and suffix of dot(s))
                sub_term_l = list()
                #Extract dot-sequence prefix if any 
                if self.dot_str.findall(decomp_term[0]):
                    sub_term_l.append( decomp_term.pop(0) )
                #Extract dot-sequence suffix if any
                l_end = len(decomp_term) - 1
                if self.dot_str.findall(decomp_term[l_end]):
                    sub_term_l.append( decomp_term.pop(l_end) )
                #Count dot-sequence terms 
                for sub_term in sub_term_l:                  
                    if sub_term in xhtml_TF: 
                        xhtml_TF[sub_term] += 1
                    else:
                        xhtml_TF[sub_term] = 1
                #Re-compose the term without suffix/prefix dot-sequence and give it for further analysis 
                dot_free_tl.append( "".join(decomp_term) )
            else:
                if self.dot_str.findall(term): #in case of one element in the list check if it is a dot-sequence
                    if term in xhtml_TF: 
                        xhtml_TF[term] += 1
                    else:
                        xhtml_TF[term] = 1
                else: #keep already the dot-free terms    
                    dot_free_tl.append(term) 
        terms_l = dot_free_tl
        #Count and clean-up the non-alphanumeric symbols ONLY from the Beginning and the End of the terms
        ##except dot (.) and percentage % at the end for the term)
        clean_term_tl = list()
        for term in terms_l:
            #Get the 
            symb_term_l = self.fredsb_clean.findall(term)
            if symb_term_l:
                #Keep and count the symbols found 
                for symb in symb_term_l:
                    if symb in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                        xhtml_TF[symb] += 1
                    else: 
                        xhtml_TF[symb] = 1
                clean_trm = self.fredsb_clean.sub('', term)
                if clean_trm in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                    xhtml_TF[clean_trm] += 1
                elif clean_trm: #if not empty string (Just in case)
                    xhtml_TF[clean_trm] = 1
            else:
                #Keep only the terms that are already free of commas because the other have been already decomposed and counted
                clean_term_tl.append(term)
        #use the comma_free terms list as the terms list to continue processing
        terms_l = clean_term_tl
        #Finally! count the term frequencies (with any Noise unfortunately remains)    
        for term in terms_l:            
            if term in xhtml_TF: #if the dictionary of terms has the 'terms' as a key 
                xhtml_TF[term] += 1
            elif term:
                xhtml_TF[term] = 1                    
        #Append the URL of the xtree to the list of Web Pages that the TF (or other) vector has been Generated 
        #self.webpg_l.append( xhtml_d['filename'] )
        print "etree : Filters Done!"
        del xhtml_t
        return [ xhtml_d['filename'], xhtml_TF, xhtml_NgF ] 
        #Append the Term Vector of the xtree to the list of Web Pages' Vectors
        #self.webpg_vect_l.append(xhtml_TF)
        #return xhtml_TF
        #Append the Ngram Vector of the xtree ot the list of Web Pages' Vectors
        #self.ngram_vect_l.append(xhtml_NgF)
        #return xhtml_NgF
        
    def get_vects(self):
        return (self.webpg_l, self.webpg_vect_l, self.ngram_vect_l)
            
    








     