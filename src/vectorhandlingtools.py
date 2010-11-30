"""

"""

import eventlet
import codecs
from multiprocessing import Process
#from scgenrelerner_svmbased import *

def merge_global_dicts(*gdicts):
    gterm_index = dict()
    gterm_list = list()
    for gdict in gdicts:
        print("Corpus index len: %s" % len(gdict.keys()) )
        gterm_list.extend( gdict.keys() )
    gterm_list.sort() #Remove it if it is too slow
    idx_no = 0
    for i in range(len(gterm_list)):
        if not gterm_list[i] in gterm_index:
            idx_no += 1
            gterm_index[ gterm_list[i] ] = [ idx_no, gdict[ gterm_list[i] ] ]  
    print("Global Term index len: %s" % len(gterm_index) ) 
    return gterm_index

def gterm_d_gen(webpg_vect_l):
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
    
def load_dict(filepath, filename, force_lower_case=False):
    try:
        f = codecs.open( filepath + str(filename), "r")
    except IOError, e:
        print("FILE %s ERROR: %s" % (filename,e))
        return None
    #The following for loop is an alternative approach to reading lines instead of using f.readline() or f.readlines()
    vect_dict = dict()
    try:
        for fileline in f:
            line = fileline.replace('\n', '')
            line = line.split(" => ") #BE CAREFULL with SPACES
            if force_lower_case: 
                vect_dict[ line[0].lower() ] = float( line[1] )
            else:
                vect_dict[ line[0] ] = float( line[1] )
    except:
        f.close()
        return None
    f.close()
    #Return the TF Vector    
    return vect_dict  

def merge_to_global_dict(filelist, filepath=None, force_lower_case=False):
    assert isinstance(filelist, (list, tuple))
    gpool = eventlet.GreenPool(10)
    filepaths= map( lambda x: filepath, range(len(filelist)) )
    force_lower= map( lambda x: force_lower_case, range(len(filelist)) )
    #Start Merging the Dictionaries - or Vector of Term Frequencies
    global_vect = load_dict(filepath, filelist[0], force_lower_case)
    for vect_d in gpool.imap(load_dict, filepaths, filelist[1:], force_lower):
        for d_trm in vect_d:
            if d_trm in global_vect: 
                global_vect[d_trm] += vect_d[d_trm] 
            else:
                global_vect[d_trm] = vect_d[d_trm]
    return global_vect
    
def load_dict_l(filepath, filename, g_terms_d=None, force_lower_case=False, page_num=0):
    try:
        f = codecs.open( filepath + str(filename), "r")
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
            composed_terms = line[1].split('\t')
            vect_dict = dict()  
            for comp_term in composed_terms:
                if comp_term == '\n': # or comp_term == ' ':
                    continue
                decomp_term = comp_term.split(' : ')
                if g_terms_d == None:
                    if force_lower_case:
                        vect_dict[ decomp_term[0].lower() ][1] = decomp_term[1]
                    else:    
                        vect_dict[ decomp_term[0] ][1] = decomp_term[1]
                elif isinstance(g_terms_d, dict):
                    #if Globals Term list has been given then find the proper index value for creating the numerically tagged dictionary
                    try:
                        if force_lower_case:
                            vect_dict[ g_terms_d[ decomp_term[0].lower() ][1] ] = float( decomp_term[1] )
                        else:
                            vect_dict[ g_terms_d[ decomp_term[0] ][1] ] = float( decomp_term[1] )
                    except:
                        #if you cannot find the term in the global dictionary just drop the term
                        #print("Term \" %s \"not found in the Global Dictionary/Index - Dropped!" % decomp_term[0])
                        pass
            vect_l.append( vect_dict )
            #If a limited number of HTML page vector is needed then stop loading when this number is reached
            vect_l_len = len(vect_l) 
            if vect_l_len == page_num:
                break
            if vect_l_len == 0:
                print("Page Vector has Zero terms common to the Training-Genre-Dictionary!!!")
    except:
        f.close()
        return None
    finally:
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
            libsvm_pg_vect[ Gset_terms[pg_term] ] = pg_vect[pg_term]
        new_webpg_vect_l.append( libsvm_pg_vect )
    return new_webpg_vect_l

def save_dct(filename, records, filepath=None):
    """save_dct():"""
    try:
        #Codecs needed for saving string that are encoded in UTF8, but I do not need it because strings are already the Proper Encoding form
        f = codecs.open( filepath + filename, "w", "utf-8") #change "utf-8" to xcharset
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
    
def save_dct_lst(filename, records, index, filepath=None):
    try:
        #Codecs needed for saving string that are encoded in UTF8, but I do not need it because strings are already the Proper Encoding form
        f = codecs.open( filepath + filename, "w", "utf-8") #change "utf-8" to xcharset
    except IOError:
        return None 
    try: 
        for i in range(len(index)):
            f.write(index[i] + " => ")
            for rec in records[i]:
                f.write( str(rec) + " : "  + str(records[i][rec]) + "\t") 
            f.write("\n") 
    except:
        print("ERROR WRITTING FILE: %s" % filename)
        f.close()
    return True           


#Testing Tools
if __name__ == "__main__":
    
    d1 = {'jim':1, 'fsdf':2, 'kol':3}
    d2 = {'fasdfsd':1, 'fsdf':2, 'kol':3, 'jim': 4}
    
    print d1
    print d2
    
    print merge_global_dicts(d1, d2)
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    