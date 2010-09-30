"""

"""

import eventlet
import codecs
from multiprocessing import Process

from scgenrelerner_svmbased import *

Gset_terms = list()
vect_l_chnk = Queue()   
    
def load_dict(filepath, filename):
    try:
        f = open( filepath + str(filename), "r" )
    except IOError, e:
        print("FILE %s ERROR: %s" % (filename,e))
        return None
    #The following for loop is an alternative approach to reading lines instead of using f.readline() or f.readlines()
    vect_dict = dict()
    try:
        for fileline in f:
            line = fileline.split(" => ") #BE CAREFULL with SPACES
            vect_dict[ line[0] ] = line[1]
    except:
        f.close()
        return None
    f.close()
    #Return the TF Vector    
    return vect_dict  

def merge_to_global_dict(filelist, filepath=None):
    if not isinstance(filelist, (list, tuple)) :
        return False
    gpool = eventlet.GreenPool(10)
    filepaths= map( lambda x: filepath, range(len(filelist)) )
    #Start Merging the Dictionaries - or Vector of Term Frequencies
    global_vect = load_dict(filepath, filelist[0])
    for vect_d in gpool.imap(load_dict, filepaths, filelist[1:]):
        for d_trm in vect_d:
            if d_trm in global_vect: 
                global_vect[d_trm] += vect_d[d_trm]
            else:
                global_vect[d_trm] = vect_d[d_trm]
    return global_vect
    
def load_dict_l(filepath, filename, g_terms_l=None):
    try:
        f = open( filepath + str(filename), "r" )
    except IOError, e:
        print("FILE %s ERROR: %s" % (filename,e))
        return None
    #The following for loop is an alternative approach to reading lines instead of using f.readline() or f.readlines()
    wps_l = list()
    vect_l = list()
    try:
        for fileline in f:
            line = fileline.split(" => ") #BE CAREFULL with SPACES
            wps_l.append( line[0] )
            composed_terms = line[1].split("\t")
            vect_dict = dict()  
            for comp_term in composed_terms:
                decomp_term = comp_term.split(":")
                if g_terms_l == None:
                    vect_dict[ decomp_term[0] ] = decomp_term[1]
                else:
                    #if Globals Term list has been given then find the proper index value for creating the numerically tagged dictionary 
                    vect_dict[ g_terms_l.index(decomp_term[0]) ] = decomp_term[1]
            vect_l.append( vect_dict )
    except:
        f.close()
        return None
    f.close()
    #Return tuple of WebPages Vectors and     
    return (wps_l, vect_l)

def label_numerically(webpg_vect_l, Gset_terms):
    new_webpg_vect_l = list()
    for pg_vect in webpg_vect_l:
        #enc_pg_vect = pg_vect.keys()
        #for i in range(len(enc_pg_vect)):
        #    enc_pg_vect[i] = enc_pg_vect[i].encode("utf-8")
        libsvm_pg_vect = dict()
        for pg_term in pg_vect:
            libsvm_pg_vect[ Gset_terms.index(pg_term) ] = pg_vect[pg_term]
        new_webpg_vect_l.append( libsvm_pg_vect )
    return new_webpg_vect_l
    
################################################ Not in USE for a While    
def make_libsvm_sparse_vect(self, webpg_vect_l):
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
    ##    labeling_ps.append( Process(target=label_properly, args=(chunck_wp_l[i],vect_l_chnk)) ) 
        pass
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
    print("make_libsvm_sparse_vect: Second Part Done")
    return (new_webpg_vect_l)
################################################

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





if __name__ == "__main__":
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    