"""

"""
import os
from vectorhandlingtools import *
from termvectorgenerator import VectGen
from svmutil import *
import decimal
import multiprocessing

import multiprocessing 

def train_svm(fobj, training_vectors, nu, class_tags=None):
    if class_tags == None:
        class_tags = [0]*len(training_vectors)
    print(len(class_tags))
    fobj.write( "Amount of Vector for training= " + str(len(class_tags)) + "\n" ) 
    prob = svm_problem(class_tags, training_vectors)
    params_s = '-s 2 -t 0 -n ' + str(nu)
    print params_s
    model_params = svm_parameter( params_s )
    svm_m = svm_train(prob, model_params)
    print("Done!")
    return class_tags, svm_m

def evaluate_svm(fobj, svm_m, vectl_genre, trained_genre, genres):
    c1 = decimal.Decimal('0')
    c2 = decimal.Decimal('0')
    tp = decimal.Decimal('0') 
    tn = decimal.Decimal('0')
    fp = decimal.Decimal('0')
    fn = decimal.Decimal('0')
    total_global_vect_l = vectl_genre[trained_genre][0:1000]
    for g in genres:
        if g != trained_genre:
            total_global_vect_l.extend(vectl_genre[ g ][0:1000]) 
    #Prediction phase
    #print len(vectl_genre['news'][3000:4000]), len(vectl_genre['product_companies'][0:3000]), len(total_global_vect_l)
    print len(total_global_vect_l)
    print "Predicting"  
    p_labels, acc, val = svm_predict([0]*len(total_global_vect_l), total_global_vect_l, svm_m, '-b 0' )
    #print p_labels
    print "Evaluating"
    for i, d in enumerate(p_labels):
        if d > 0:
            if i > 999:
                fp += 1
            else:
                tp += 1   
            c1 += 1
        else:
            if i > 999:
                tn += 1
            else:
                fn += 1
            c2 += 1
    ##
    s = "+ %s, - %s\n" % (c1, c2)
    fobj.write(s)
    s = "tp=%s, fp=%s, tn=%s, fn=%s\n" % (tp,fp,tn,fn)
    fobj.write(s)
    try:
        ##
        precision = tp/(tp+fp)
        s = "Precision=%f\n" % precision 
        fobj.write(s)
        ##
        recall = tp/(tp+fn)
        s = "Recall=%f\n" % recall 
        fobj.write(s)
        ##
        f1 = (2*precision*recall)/(precision+recall)
        s = "F1=%s\n\n" % f1
        fobj.write(s)
    except Exception as e:
        fobj.write( str(e)+"\n" )

def tf_abv_thrld(global_vect_l, tf_threshold=0):
    for line in global_vect_l:
        dkeys = line.keys()
        for key in dkeys:
            if line[key] < tf_threshold:
                line[key] = float( 0 )
    return global_vect_l

def tf2tfnorm(global_vect_l, div_by_max=False):
    if div_by_max:
        for line in global_vect_l:
            dkeys = line.keys()
            max = float( 0 )
            for key in dkeys:
                if line[key] > max:
                    max = line[key]
            if max > 0:
                for key in dkeys:
                    line[key] = (line[key]/max)
            else:
                pass
                #print("tf2tnorm MAX<0 on list line => len %s :: line %s" % (len(line),line))
    else:
        for line in global_vect_l:
            dkeys = line.keys()
            sum = float( 0 )
            for key in dkeys:
                sum += line[key]
            if sum > 0:
                for key in dkeys:
                    line[key] = line[key]/sum
            else:
                pass
                print("tf2tnorm SUM<0 on list line => len %s :: line %s" % (len(line),line))
    return global_vect_l

def inv_tf(global_vect_l):
    for line in global_vect_l:
        dkeys = line.keys()
        for key in dkeys:
            line[key] = (1/line[key])
    return global_vect_l

def tf2bin(global_vect_l, freq_idx,tf_threshold=0):
    for line in global_vect_l:
        dkeys = line.keys()
        for key in dkeys:
            if freq_idx[ key ] > tf_threshold:
                line[key] = 1
            else:
                line[key] = 0
    return global_vect_l

def tf2hapax(global_vect_l, freq_idx,tf_threshold=2):
    for line in global_vect_l:
        dkeys = line.keys()
        for key in dkeys:
            if freq_idx[ key ] < tf_threshold:
                line[key] = 1
            else:
                line[key] = 0
    return global_vect_l

def load_vects(genres, term_idx, lower_case, pg_num=None, wpsl_genre={}, vectl_genre={}):
    vectors_d = "/corpus_webpage_vectors/"
    base_filepath = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/"
    if pg_num == None:
        pg_num = 0
    for g in genres:
        filepath = base_filepath + g + vectors_d
        vect_flist = [files for path, dirs, files in os.walk(filepath)]
        vect_flist = vect_flist[0] 
        global_wps_l = list()
        global_vect_l = list()
        for filename in vect_flist:
            wps_l, vect_l = load_dict_l(filepath, filename, term_idx, force_lower_case=lower_case, page_num=pg_num)
            global_wps_l.extend( wps_l )
            global_vect_l.extend( vect_l )
            print("%s global_vect_l len: %s" % (g, len(global_vect_l)))
        #CLEAN VECTOR LIST
        for i, line in enumerate(global_vect_l):
            if line < 50:
                del global_vect_l[i]
                del global_wps_l[i]
        wpsl_genre[ g ] = global_wps_l
        vectl_genre[ g ] = global_vect_l

print("START")

lower_case = True

genres = [ "news" , "product_companies", "forum", "blogs", "wiki_pages"] # "academic", 
base_filepath = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/"
corpus_d = "/corpus_dictionaries/"
##################### CREAT GLOBAL INDEX FOR BOTH CORPUSSES ####################
#term_index = dict()
#for g in genres:
#    filepath = base_filepath + g + corpus_d
#    cdicts_flist = [files for path, dirs, files in os.walk(filepath)]
#    cdicts_flist = cdicts_flist[0]
#    corpus_dict = merge_to_global_dict(cdicts_flist, filepath, force_lower_case=lower_case)
#    print("%s Dictionary has been loaded" % g )
#    term_index = merge_global_dicts(term_index, corpus_dict)
#    print("%s merged to Global Term Index" % g)
#print( "Global Index Size: %s\n" % len(term_index))
#term_index = merge_global_dicts(corpus_dict, corpus_dict2) #, corpus_dict3, corpus_dict4)

genres = [ "news" , "product_companies", "forum", "blogs", "wiki_pages"] 
base_filepath = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/"
for g in genres:
    fobj = open( base_filepath + g + "_vs_all.eval", "w" )
    fobj.write("---- for Genre= " + g + " ----\n")
    #################### LOAD THE PROPER GLOBAL INDEX ##############################
    filepath = base_filepath + g + corpus_d
    cdicts_flist = [files for path, dirs, files in os.walk(filepath)]
    cdicts_flist = cdicts_flist[0]
    corpus_dict = load_n_merge_dcts(cdicts_flist, filepath, force_lower_case=lower_case)
    term_idx, freq_idx = get_indexs(corpus_dict) 
    print("%s Dictionary has been loaded" % g )
    print( "Global Index Size: %s\n" % len(term_idx))
    #################### CREAT GLOBAL LIST OF WEBPAGE VECTORS OF ALL GENRES################
    wpsl_genre = dict() 
    vectl_genre = dict()
    #Load all vectors of Genre for which One-Class SVM will be trained for 
    load_vects( [ g ] , term_idx, lower_case, None, wpsl_genre, vectl_genre)
    rest_genres = list()
    for rst_g in genres:
        if rst_g != g:
            rest_genres.append(rst_g)
    load_vects( rest_genres, term_idx, lower_case, 1000, wpsl_genre, vectl_genre)
    for i in [1,2,3]:
        ######
        TFREQ = 3
        lower_case = True
        #########Keep TF above Threshold
        #global_vect_l = tf_abv_thrld(global_vect_l, tf_threshold=TFREQ)
        #########Binary from
        if i == 1:
            fobj.write("**** Inverse Binary - Hapax Legomenon ****\n")
            for grn in genres:
                vectl_genre[ grn ] = tf2hapax(vectl_genre[ grn ], freq_idx,tf_threshold=TFREQ)
        elif i == 2:
            fobj.write("**** Binary ****\n")
            for grn in genres:
                vectl_genre[ grn ] = tf2bin(vectl_genre[ grn ], freq_idx,tf_threshold=TFREQ)
        elif i == 3:
            fobj.write("**** Normilised by Max Term ****\n")
            for grn in genres:
                vectl_genre[ grn ] = tf2tfnorm(vectl_genre[ grn ], div_by_max=True)
        elif i == 4:
            fobj.write("**** Normilised by Total Sum ****\n")
            for grn in genres:
                vectl_genre[ grn ] = tf2tfnorm(vectl_genre[ grn ], div_by_max=False)            
        #########Invert TF
        #global_vect_l = inv_tf(global_vect_l) 
        #########Normalised Frequency form
        for nu in [0.2, 0.3, 0.5, 0.7, 0.8]: # 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
            ############################################## Train SVM ###############################################
            fobj.write("++++ for nu= " + str(nu) + " ++++\n")
            for size in range(1500,9000,500):
                print "Training"
                class_tags, svm_m = train_svm(fobj, vectl_genre[ g ][1000:size], nu )
                #print("Labels %s" % svm_m.get_labels()) Not working for one-class SVM
                ############################################### Evaluate SVM ##############################################
                #fobj.write("---- for Genre= " + g + " ----\n")
                evaluate_svm(fobj, svm_m, vectl_genre, g, genres)
    fobj.close()


print "Thank you and Goodbye!"

