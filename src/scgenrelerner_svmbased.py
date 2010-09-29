"""   
    Single Class SVM Learner for Web Site Genre Classification 

"""

from svm import *

def train_svm(class_tags, training_vectors):
    class_tags = map( lambda x:1, range(len(webpg_l)) )
     
    prob = svm_problem(class_tags, training_vectors)
    model_params = svm_parameter(svm_type=ONE_CLASS)
    svm_m = svm_model(prob, model_params)
    print("Done!")
    
