"""

"""
import os
from vectorhandlingtools import *
from termvectorgenerator import VectGen
from svmutil import *
import decimal
import multiprocessing

import multiprocessing 

def train_svm(training_vectors, class_tags=None):
    if class_tags == None:
        class_tags = [0]*len(training_vectors)
    print(len(class_tags)) 
    prob = svm_problem(class_tags, training_vectors)
    model_params = svm_parameter('-s 2 -t 0 -n 0.2') #svm_type=ONE_CLASS, kernel_type=LINEAR, nu=0.7)
    svm_m = svm_train(prob, model_params)
    print("Done!")
    return class_tags, svm_m

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
            for key in dkeys:
                line[key] = line[key]/sum
    return global_vect_l

def inv_tf(global_vect_l):
    for line in global_vect_l:
        dkeys = line.keys()
        for key in dkeys:
            line[key] = (1/line[key])
    return global_vect_l

def tf2bin(global_vect_l, tf_threshold=0):
    for line in global_vect_l:
        dkeys = line.keys()
        #print line
        for key in dkeys:
            if line[key] > tf_threshold:
                line[key] = 1
            else:
                line[key] = 0
        #print line
        #0/0
    print global_vect_l[1]
    return global_vect_l

def inv_tf2bin(global_vect_l, tf_threshold=0):
    for line in global_vect_l:
        dkeys = line.keys()
        for key in dkeys:
            if line[key] < tf_threshold:
                line[key] = 1
            else:
                line[key] = 0
    return global_vect_l

print("START")

lower_case = True

##################### CREAT GLOBAL INDEX FOR BOTH CORPUSSES ##################
genres = [ "news" , "product_companies"] #, "forum", "blogs",  "academic", "wiki_pages"] 
base_filepath = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/"
corpus_d = "/corpus_dictionaries/"
gterm_index = dict()
for g in genres:
    filepath = base_filepath + g + corpus_d
    cdicts_flist = [files for path, dirs, files in os.walk(filepath)]
    cdicts_flist = cdicts_flist[0]
    corpus_dict = merge_to_global_dict(cdicts_flist, filepath, force_lower_case=lower_case)
    print("%s Dictionary has been loaded" % g )
    gterm_index = merge_global_dicts(gterm_index, corpus_dict)
    print("%s merged to Global Term Index" % g)
print( "Global Index Size: %s\n" % len(gterm_index))
#gterm_index = merge_global_dicts(corpus_dict, corpus_dict2) #, corpus_dict3, corpus_dict4)

#################### CREAT GLOBAL LIST OF WEBPAGE VECTORS OF ALL GENRES################
vectors_d = "/corpus_webpage_vectors/"
wpsl_genre = dict()
vectl_genre = dict()
for g in genres:
    filepath = base_filepath + g + vectors_d
    vect_flist = [files for path, dirs, files in os.walk(filepath)]
    vect_flist = vect_flist[0] 
    global_wps_l = list()
    global_vect_l = list()
    for filename in vect_flist:
        wps_l, vect_l = load_dict_l(filepath, filename, gterm_index, force_lower_case=lower_case)
        global_wps_l.extend( wps_l )
        global_vect_l.extend( vect_l )
        print("%s global_vect_l len: %s" % (g, len(global_vect_l)))
    #CLEAN VECTOR LIST
    temp = list()
    for line in global_vect_l:
        if len(line) > 300:
            temp.append(line)
        else:
            print(line)
    global_vect_l = temp
    wpsl_genre[ g ] = global_wps_l
    vectl_genre[ g ] = global_vect_l
        
TFREQ = 5
lower_case = True
#########Keep TF above Threshold
#global_vect_l = tf_abv_thrld(global_vect_l, tf_threshold=TFREQ)
#########Binary from
#global_vect_l = inv_tf2bin(global_vect_l, tf_threshold=TFREQ)
for g in genres:
    vectl_genre[ g ] = inv_tf2bin(vectl_genre[ g ], tf_threshold=TFREQ)
    #vectl_genre[ g ] = tf2bin(vectl_genre[ g ], tf_threshold=TFREQ)
#########Invert TF
#global_vect_l = inv_tf(global_vect_l) 
#########Normalised Frequency form
#global_vect_l = tf2tfnorm(global_vect_l, div_by_max=True)
          
############################################### Train SVM ###############################################
class_tags, svm_m = train_svm( vectl_genre['news'][0:3000] )
#print("Labels %s" % svm_m.get_labels()) Not working for one-class SVM

############################################### Evaluate SVM ##############################################
c1 = decimal.Decimal('0')
c2 = decimal.Decimal('0')
tp = decimal.Decimal('0') 
tn = decimal.Decimal('0')
fp = decimal.Decimal('0')
fn = decimal.Decimal('0')
total_global_vect_l = vectl_genre['news'][3000:4000]
for g in genres:
    if g != 'news':
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
#print("Value0 %s" % value0)
print("+ %s, - %s" % (c1, c2))
print("tp=%s, fp=%s, tn=%s, fn=%s" % (tp,fp,tn,fn))

precision = tp/(tp+fp) 
print("Precision=%f" % precision)

recall = tp/(tp+fn) 
print("Recall=%f" % recall)

f1 = (2*precision*recall)/(precision+recall)
print("F1=%s" % f1)




