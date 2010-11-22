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
    model_params = svm_parameter('-s 2 -t 0 -n 0.5') #svm_type=ONE_CLASS, kernel_type=LINEAR, nu=0.7)
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
        for key in dkeys:
            if line[key] > tf_threshold:
                line[key] = 1
            else:
                line[key] = 0
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

#File path where to find files
##Define paths for NEWs Corpus
filepath1 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/news/"
filepath11 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/news/corpus_dictionaries/" 
filepath12 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/news/corpus_webpage_vectors/"
filepath111 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/news/ngrams_corpus_dictionaries/" 
filepath122 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/news/ngrams_corpus_webpage_vectors/"
##Define paths for BLOGs Corpus
filepath2 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/product_companies/"
filepath21 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/product_companies/corpus_dictionaries/"
filepath22 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/product_companies/corpus_webpage_vectors/"
filepath211 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/product_companies/ngrams_corpus_dictionaries/"
filepath222 = "/home/dimitrios/Documents/Synergy-Crawler/saved_pages/product_companies/ngrams_corpus_webpage_vectors/"

TFREQ = 1
lower_case = True

##################### CREAT GLOBAL INDEX FOR BOTH CORPUSSES ##################
###LOAD DICTIONARY OF NEWS CORPUS
site_dicts_filelist = [files for path, dirs, files in os.walk(filepath11)]
site_dicts_filelist = site_dicts_filelist[0]
corpus_dict = merge_to_global_dict(site_dicts_filelist, filepath11, force_lower_case=lower_case)
#filename = "globa_vect"
#if save_dct(filename, corpus_dict, filepath1):
#    print("global_vect: SAVED!")
###LOAD DICTIONARY OF BLOGS CORPUS
site_dicts_filelist = [files for path, dirs, files in os.walk(filepath21)]
site_dicts_filelist = site_dicts_filelist[0]   
corpus_dict2 = merge_to_global_dict(site_dicts_filelist, filepath21, force_lower_case=lower_case)
###LOAD DICTIONARY OF NEWS CORPUS (NGRAMS)
site_dicts_filelist = [files for path, dirs, files in os.walk(filepath111)]
site_dicts_filelist = site_dicts_filelist[0]
corpus_dict3 = merge_to_global_dict(site_dicts_filelist, filepath111, force_lower_case=lower_case)
###LOAD DICTIONARY OF BLOGS CORPUS (NGRAMS)
site_dicts_filelist = [files for path, dirs, files in os.walk(filepath211)]
site_dicts_filelist = site_dicts_filelist[0]   
corpus_dict4 = merge_to_global_dict(site_dicts_filelist, filepath211, force_lower_case=lower_case)
###Create the Global Term Rank Index
gterm_index = merge_global_dicts(corpus_dict, corpus_dict2) #, corpus_dict3, corpus_dict4)

##################### NEWS #############################
vector_lists_filelist = [files for path, dirs, files in os.walk(filepath12)]
vector_lists_filelist = vector_lists_filelist[0] 
global_wps_l = list()
global_vect_l = list()
for filename in vector_lists_filelist:
    wps_l, vect_l = load_dict_l(filepath12, filename, gterm_index, force_lower_case=lower_case)
    global_wps_l.extend( wps_l )
    global_vect_l.extend( vect_l )
#print(wps_l[0])
#if save_dct_lst('dict_list',  global_vect_l, global_wps_l, filepath1):
#    print('dict_list: Saved')
temp = list()
for line in global_vect_l:
    if len(line) > 9:
        temp.append(line)
    else:
        print(line)
global_vect_l = temp
"""
#EXTEND Page vectors(Dictionaries) with Ngrams
vector_lists_filelist = [files for path, dirs, files in os.walk(filepath122)]
vector_lists_filelist = vector_lists_filelist[0] 
temp_wps_l = list()
temp_vect_l = list()
for filename in vector_lists_filelist:
    wps_l, vect_l = load_dict_l(filepath122, filename, gterm_index, force_lower_case=lower_case)
    temp_vect_l.extend( vect_l )
#Merge Ngrams with Tokens
for i in range(len(global_vect_l)):
    page_dict = global_vect_l[i]
    page_dict.update( temp_vect_l[i] )
"""
#########Keep TF above Threshold
#global_vect_l = tf_abv_thrld(global_vect_l, tf_threshold=TFREQ)
#########Binary from
#global_vect_l = inv_tf2bin(global_vect_l, tf_threshold=TFREQ)
global_vect_l = tf2bin(global_vect_l, tf_threshold=TFREQ)
#########Normalised Frequency form 
#global_vect_l = tf2tfnorm(global_vect_l, div_by_max=True)
#########Invert TF
#global_vect_l = inv_tf(global_vect_l)
          
print("global_vect_l len %s" % len(global_vect_l))

##################### BLOGS ##########################
vector_lists_filelist2 = [files for path, dirs, files in os.walk(filepath22)]
vector_lists_filelist2 = vector_lists_filelist2[0]
global_wps_l2 = list()
global_vect_l2 = list()
for filename in vector_lists_filelist2:
    wps_l2, vect_l2 = load_dict_l(filepath22, filename, gterm_index, force_lower_case=lower_case)
    global_wps_l2.extend( wps_l2 )
    global_vect_l2.extend( vect_l2 )
temp = list()
for line in global_vect_l2:
    if len(line) > 9:
        temp.append(line)
    else:
        print(line)
global_vect_l2 = temp
"""
#EXTEND Page vectors(Dictionaries) with Ngrams
vector_lists_filelist = [files for path, dirs, files in os.walk(filepath222)]
vector_lists_filelist = vector_lists_filelist[0] 
temp_wps_l = list()
temp_vect_l = list()
for filename in vector_lists_filelist:
    wps_l, vect_l = load_dict_l(filepath222, filename, gterm_index, force_lower_case=lower_case)
    temp_vect_l.extend( vect_l )
#Merge Ngrams with Tokens
for i in range(len(global_vect_l2)):
    page_dict = global_vect_l2[i]
    page_dict.update( temp_vect_l[i] )
"""
#########Keep TF above Threshold
#global_vect_l2 = tf_abv_thrld(global_vect_l2, tf_threshold=TFREQ)
#########Binary From
#global_vect_l2 = inv_tf2bin(global_vect_l2, tf_threshold=TFREQ)
global_vect_l2 = tf2bin(global_vect_l2, tf_threshold=TFREQ)
#########Normalised Frequency form 
#global_vect_l2 = tf2tfnorm(global_vect_l2, div_by_max=True)
#########Invert TF
#global_vect_l2 = inv_tf(global_vect_l2)


#print("global_vect_l2 %s" % global_vect_l2[0])
print( "global_vect_l2 len %s" % len(global_vect_l2) )
#print("Sample %s" % global_vect_l[0])

############################################### Train SVM ###############################################
class_tags, svm_m = train_svm( global_vect_l[0:1000] ) #256
#print("Labels %s" % svm_m.get_labels()) Not working for one-class SVM

############################################### Evaluate SVM ##############################################
c1 = decimal.Decimal('0')
c2 = decimal.Decimal('0')
tp = decimal.Decimal('0') 
tn = decimal.Decimal('0')
fp = decimal.Decimal('0')
fn = decimal.Decimal('0')
total_global_vect_l = global_vect_l[1001:4001] #257
total_global_vect_l.extend(global_vect_l2[0:3000]) 
#Prediction phase
print len(global_vect_l[1001:4001]), len(global_vect_l2[0:3000]), len(total_global_vect_l)
print "Predicting"
p_labels, acc, val = svm_predict([0]*len(total_global_vect_l), total_global_vect_l, svm_m, '-b 0' )
#print p_labels
print "Evaluating"
for i, d in enumerate(p_labels):
    if d > 0:
        if i > 2999: #299
            fp += 1
        else:
            tp += 1   
        c1 += 1
    else:
        if i > 2999:
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




