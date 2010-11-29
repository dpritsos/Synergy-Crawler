"""

"""
import os
from vectorhandlingtools import *
from termvectorgenerator import VectGen
from svm import *
import decimal
import multiprocessing


vgen = VectGen()
def gen_vect(xhtml_d):
    return vgen.gen_vect(xhtml_d)
    
########################## CREAT DICTIONARIES #################################
# "news", "blogs", "academic", "wiki_pages", "forum", "product_companies"  
genres = [ "forum" ]
base_filepath = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/"


for g in genres:
    ppool = multiprocessing.Pool(4)
    filepath = str( base_filepath + g + "/" )
    if filepath and not os.path.isdir((filepath + "corpus_dictionaries/")):
        os.mkdir((filepath + "corpus_dictionaries/"))
    if filepath and not os.path.isdir((filepath + "corpus_webpage_vectors/")):
        os.mkdir((filepath + "corpus_webpage_vectors/"))
    if filepath and not os.path.isdir((filepath + "ngrams_corpus_dictionaries/")):
        os.mkdir((filepath + "ngrams_corpus_dictionaries/"))
    if filepath and not os.path.isdir((filepath + "ngrams_corpus_webpage_vectors/")):
        os.mkdir((filepath + "ngrams_corpus_webpage_vectors/"))
    page_file_l = [files for path, dirs, files in os.walk(filepath)]
    page_file_l = page_file_l[0]
    print len(page_file_l)
    #vgen = VectGen()
    xhtmlfiles = dict()
    xhtmlfiles_l = list()
    for i, page in enumerate(page_file_l):
        xhtmlfiles_l.append( {"filename" : page, "filepath" : filepath} )
    ###  
    vect_ll = ppool.map(gen_vect, xhtmlfiles_l, 4)
    ###
    for vect_l in vect_ll:
        if vect_l == [None, None, None]:
            vect_ll.remove(vect_l)
    ###
    webpg_l = [ i for i, j, k in vect_ll] 
    webpg_vect_l = [ j for i, j, k in vect_ll]
    ngram_vect_l = [ k for i, j, k in vect_ll]
    ###
    idx_l = list()
    for i, wp_vect in enumerate(webpg_vect_l):
        if not wp_vect:
            idx_l.append( i )
    c = -1
    for i in idx_l:
        c += 1
        del webpg_vect_l[ (i - c) ]
        del webpg_l[ (i - c) ] 
    print(len(webpg_l), len(webpg_vect_l), len(ngram_vect_l))
    global_term_dict = gterm_d_gen(webpg_vect_l)
    #global_ngram_dict = gterm_d_gen(ngram_vect_l)  
    #Save Term Frequency Dictionaries 
    filename = g  + ".corpd"   
    if save_dct(filename, global_term_dict, (filepath + "corpus_dictionaries/") ):
        print( g + " CORPUS TERMS DICTIONARY: SAVED!" )
    filename = g + ".cvect"
    if save_dct_lst( filename, webpg_vect_l, webpg_l, (filepath + "corpus_webpage_vectors/") ):
        print( g + " CORPUS VECTORS: SAVED!" )
    #Save Ngram Frequency Dictionaries
    #filename = g  + ".ncorpd"   
    #if save_dct(filename, global_ngram_dict, (filepath + "ngrams_corpus_dictionaries/") ):
    #    print( g + " NGRAMS CORPUS TERMS DICTIONARY: SAVED!" )
    #filename = g + ".ncvect"
    #if save_dct_lst( filename, ngram_vect_l, webpg_l, (filepath + "ngrams_corpus_webpage_vectors/") ):
    #    print( g + " NGRAMS CORPUS VECTORS: SAVED!" )
    ppool.close()
    ppool.join()

print("Thank you and Goodbye!")
