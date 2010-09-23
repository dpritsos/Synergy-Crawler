"""   
    Single Class SVM Learner for Web Site Genre Classification 

"""

from svm import *

def train_svm(class_tags, training_vectors): 
    prob = svm_problem(class_tags, training_vectors)
    model_params = svm_parameter('-c 4')
    svm_model = svm_train(prob, model_params)
    print("Done!")
    
