"""

"""
import os
from scvectorhandlingtools import *
from svm import *
import decimal

def train_svm(training_vectors, class_tags=None):
    if class_tags == None:
        class_tags = map( lambda x:1, range(len(training_vectors)) )
    print(len(class_tags)) 
    prob = svm_problem(class_tags, training_vectors)
    model_params = svm_parameter(svm_type=ONE_CLASS, kernel_type=LINEAR, nu=0.4)
    svm_m = svm_model(prob, model_params)
    print("Done!")
    return svm_m

print("START")

#File path where to find files
##Define paths for NEWs Corpus
filepath1 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/news/"
#filepath11 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/news/ngrams_corpus_dictionaries/" 
#filepath12 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/news/ngrams_corpus_webpage_vectors/"
filepath11 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/news/corpus_dictionaries/" 
filepath12 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/news/corpus_webpage_vectors/"
##Define paths for BLOGs Corpus
filepath2 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/blogs/"
#filepath21 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/blogs/ngrams_corpus_dictionaries/"
#filepath22 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/blogs/ngrams_corpus_webpage_vectors/"
filepath21 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/blogs/corpus_dictionaries/"
filepath22 = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/blogs/corpus_webpage_vectors/"

TFREQ = 1
lower_case = True
##################### CREAT GLOBAL INDEX FOR BOTH CORPUSSES ##################
###LOAD DICTIONARY OF NEWS CORPUS
site_dicts_filelist = [files for path, dirs, files in os.walk(filepath11)]
site_dicts_filelist = site_dicts_filelist[0]
print(site_dicts_filelist)
corpus_dict = merge_to_global_dict(site_dicts_filelist, filepath11, force_lower_case=lower_case)
filename = "globa_vect"
if save_dct(filename, corpus_dict, filepath1):
    print("global_vect: SAVED!")
    
###LOAD DICTIONARY OF BLOGS CORPUS
site_dicts_filelist2 = [files for path, dirs, files in os.walk(filepath21)]
site_dicts_filelist2 = site_dicts_filelist2[0]   
corpus_dict2 = merge_to_global_dict(site_dicts_filelist2, filepath21, force_lower_case=lower_case)
filename = "globa_vect2"
if save_dct(filename, corpus_dict2, filepath2):
    print("global_vect: SAVED!")
    
###Create the Global Term Rank Index
gterm_index = dict()
corpus_term_l = corpus_dict.keys()
for i in range(len(corpus_dict)):
    gterm_index[ corpus_term_l[i] ] = i + 1
#####Add the missing terms
corpus_term_l = corpus_dict2.keys()
gterm_index_len = len(gterm_index)
print("gterm_index_len %s" % gterm_index_len)
print("coprus_term 2nd set: %s" % len(corpus_dict2))
for i in range(len(corpus_dict2)):
    if not corpus_term_l[i] in gterm_index:
        gterm_index[ corpus_term_l[i] ] = gterm_index_len + i
print("gterm_index_len %s" % len(gterm_index))  

##################### NEWS #############################
vector_lists_filelist = [files for path, dirs, files in os.walk(filepath12)]
vector_lists_filelist = vector_lists_filelist[0] 
global_wps_l = list()
global_vect_l = list()
for filename in vector_lists_filelist:
    wps_l, vect_l = load_dict_l(filepath12, filename, gterm_index, force_lower_case=lower_case)
    global_wps_l.extend( wps_l )
    global_vect_l.extend( vect_l )
print(wps_l[0])
print(vect_l[0])
if save_dct_lst('dict_list',  global_vect_l, global_wps_l, filepath1):
    print('dict_list: Saved')
#Binary form
#for line in global_vect_l:
#    dkeys = line.keys()
#    for key in dkeys:
#        if line[key] > TFREQ:
#            line[key] = 1
#        else:
#            line[key] = 0

for line in global_vect_l:
    dkeys = line.keys()
    max = float( 0 )
    for key in dkeys:
        if line[key] > max:
            max = line[key]
    for key in dkeys:
        line[key] = (line[key]/max)

#for line in global_vect_l:
#    dkeys = line.keys()
#    sum = float( 0 )
#    for key in dkeys:
#            sum += line[key]
#            #print("MAX %s" % max)
#    for key in dkeys:
#            line[key] = line[key]/sum
                
     
            
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
print(wps_l2[0])
print(vect_l2[0])
if save_dct_lst('dict_list2',  global_vect_l2, global_wps_l2, filepath2):
    print('dict_list: Saved')
#Binary form
#for line in global_vect_l2:
#    dkeys = line.keys()
#    for key in dkeys:
#        if line[key] > TFREQ:
#            line[key] = 1
#        else:
#            line[key] = 0 

for line in global_vect_l2:
    dkeys = line.keys()
    max = float( 0 )
    for key in dkeys:
        if line[key] > max:
            max = line[key]
            #print("MAX %s" % max)
    for key in dkeys:
            line[key] = (line[key]/max)
            #if line[key] == 1:
            #    print("Key %s" % key)
#print("DiV Run %s" % line[key])

#for line in global_vect_l2:
#    dkeys = line.keys()
#    sum = float( 0 )
#    for key in dkeys:
#            sum += line[key]
#            #print("MAX %s" % max)
#    for key in dkeys:
#            line[key] = (line[key]/sum)

print("global_vect_l2 %s" % global_vect_l2[0])

print( "global_vect_l2 len %s" % len(global_vect_l2) )

"""
for term in global_term_l:
    if global_vect[ term ] > 5:
        print(term, " : ", global_vect[ term ])
        
"""
 
#print("Sample %s" % global_vect_l[0])

#Train SVM
svm_m = train_svm( global_vect_l[0:199] ) #256

#print("Labels %s" % svm_m.get_labels()) Not working for one-class SVM

#Evaluate SVM
c1 = decimal.Decimal('0')
c2 = decimal.Decimal('0')
tp = decimal.Decimal('0') 
tn = decimal.Decimal('0')
fp = decimal.Decimal('0')
fn = decimal.Decimal('0')
total_global_vect_l = global_vect_l[200:] #257
total_global_vect_l.extend(global_vect_l2) 
for i in range( len(total_global_vect_l) ):
    d = svm_m.predict( total_global_vect_l[i] )
    if i == 0:
        value0 = d
    #print("ValueD %s" % d)
    if d > 0:
        if i > 356: #299
            fp += 1
        else:
            tp += 1   
        c1 += 1
    else:
        if i > 356:
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





