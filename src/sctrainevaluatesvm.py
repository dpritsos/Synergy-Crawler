"""

"""

from scvectorhandlingtools import *
from svm import *

def train_svm(training_vectors, class_tags=None):
    if class_tags == None:
        class_tags = map( lambda x:1, range(len(training_vectors)) )
    print(len(class_tags)) 
    prob = svm_problem(class_tags, training_vectors)
    model_params = svm_parameter(svm_type=ONE_CLASS, kernel_type=LINEAR, C=1)
    svm_m = svm_model(prob, model_params)
    print("Done!")
    return svm_m

print("START")

#File path where to find files 
filepath = "/home/dimitrios/Documents/Synergy-Crawler/web_page_vectors/"

#Merge Data Collected by the Crawler
##Define Site Dictionary Files list
site_dicts_filelist = ['3-www.ted.com_CORPUS_DICTIONARY',\
                       '4-edition.cnn.com_CORPUS_DICTIONARY',\
                       '11-www.bloomberg.com_CORPUS_DICTIONARY',\
                       '15-www.nationalgeographic.com_CORPUS_DICTIONARY',\
                       '19-www.drdobbs.com_CORPUS_DICTIONARY',\
                       '38-www.bbc.co.uk_CORPUS_DICTIONARY',\
                       '28-www.time.com_CORPUS_DICTIONARY',\
                       '37-www.bbcfocusmagazine.com_CORPUS_DICTIONARY',\
                       #'46-news.google.com_CORPUS_DICTIONARY',\
                       '153-www.foxnews.com_CORPUS_DICTIONARY',\
                       '204-www.pcmag.com_CORPUS_DICTIONARY'
                       ]

##Define Site TF-Vectors of pages
vector_lists_filelist = ['3-www.ted.com_CORPUS_VECTORS',\
                         '4-edition.cnn.com_CORPUS_VECTORS',\
                         '11-www.bloomberg.com_CORPUS_VECTORS',\
                         '15-www.nationalgeographic.com_CORPUS_VECTORS',\
                         '19-www.drdobbs.com_CORPUS_VECTORS',\
                         '38-www.bbc.co.uk_CORPUS_VECTORS',\
                         '28-www.time.com_CORPUS_VECTORS',\
                         '37-www.bbcfocusmagazine.com_CORPUS_VECTORS',\
                         #'46-news.google.com_CORPUS_VECTORS',\
                         '153-www.foxnews.com_CORPUS_VECTORS',\
                         '204-www.pcmag.com_CORPUS_VECTORS'
                         ]

global_vect = merge_to_global_dict(site_dicts_filelist, filepath, force_lower_case=True)
print(global_vect.popitem())
filename = "globa_vect"
if save_dct(filename, global_vect ):
    print("global_vect: SAVED!")

#Create the Rank Index
gterm_index = dict()
global_term_l = global_vect.keys()
for i in range(len(global_term_l)):
    gterm_index[ global_term_l[i] ] = i + 1

############################################MAKE THE FORE LOOP AND THEN TRAIN IT

global_wps_l = list()
global_vect_l = list()
for filename in vector_lists_filelist:
    wps_l, vect_l = load_dict_l(filepath, filename, gterm_index, force_lower_case=True)
    global_wps_l.extend( wps_l )
    global_vect_l.extend( vect_l )

print(wps_l[0])
print(vect_l[0])
if save_dct_lst('dict_list',  global_vect_l[0], global_wps_l[0]):
    print('dict_list: Saved')
    
#Binary form
for line in global_vect_l:
    dkeys = line.keys()
    for key in dkeys:
        if line[key] > 10:
            line[key] = 1
        else:
            line[key] = 0 

            
for term in global_term_l:
    if global_vect[ term ] > 5:
        print(term, " : ", global_vect[ term ])
 
print("Sample %s" % global_vect_l[0])

#Train SVM
svm_m = train_svm( global_vect_l[0:199] )

#print("Labels %s" % svm_m.get_labels()) Not working for one-class SVM


#Evaluate SVM
c1 = 0
c2 = 0
for i in range(len(global_vect_l[200:])):
    d = svm_m.predict_values( global_vect_l[(199+i)] )
    if i == 0:
        value0 = d
    #print(d)
    if d > 0:
        c1 += 1
    else:
        c2 += 1
print("Value0 %s" % value0)
print("+ %s, - %s" % (c1, c2))







