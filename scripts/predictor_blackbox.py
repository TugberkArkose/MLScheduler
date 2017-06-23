
import sys
import json
from sklearn.neural_network import MLPRegressor
from sklearn.externals import joblib
import pickle
import os.path
import itertools
import time


params_to_use_per_thread = ['uopBR_Norm', 'uopFPtotal_Norm', 'uopGeneric_Norm', 'uopLD_Norm', 'DL1miss_Norm', 'L2miss_Norm','L3miss_Norm',
      'IL1ld_div_DL1ld_Norm', 'L2miss_div_DL1miss_Norm','L3miss_div_L2miss_Norm', 'L3miss_div_DL1miss_Norm'] # 11 in total

#try out different sizes
num_hdn_layers = 5
width_hdn_layers = 25



def loadModel(modelName):

    if os.path.exists(modelName):
        return pickle.load(open(modelName, 'rb'))
    else:
        clf = MLPRegressor(hidden_layer_sizes=(width_hdn_layers,num_hdn_layers),random_state=11)
        saveModel(clf, modelName)
        return clf

def saveModel(model, modelName):
    pickle.dump( model, open( modelName, 'wb'))


def continue_training(x,y,model,modelName):
    #input x is the thread stats for all 4 threads always consistent of ordering, and y is the system ipc observed during simulation
    model = model.partial_fit(x,y)
    saveModel(model, modelName)
    return model

def get_sysIPC_prediction(a, b, c, d, model):
    l = [a + b + c + d]
    predict_model = model
    return model.predict(l)

def get_model_accuracy(model,x,y):
    # y is the observed system IPC during simulation
    score = model.score(X=x, y=y, dtype="float")

def get_quantum_squareError(pred,y):
    #pred is the predicted system IPC value and y is the observed IPC value after quantum
    e = (pred-y)**2
    return e

def get_quantum_percentError(pred,y):
    #pred is the predicted system IPC value and y is the observed IPC value after quantum
    e = abs(pred-y)/y
    return e

def save_model(model,fname):
    #fname should be name of file including path and should end with the .pkl extension
    joblib.dump(model,fname)

def predict(a, b, c, d, model):
    
    prediction_stats = [a] + [b] + [c] + [d]
    permutations = []
    perm = list(itertools.permutations([0,1,2,3], 4))
    for i in perm:
        permutations.append(list(i))
    ipc = 0
    mapping = ""
    for i in perm:
        system_ipc = get_sysIPC_prediction(prediction_stats[int(i[0])], prediction_stats[int(i[1])], prediction_stats[int(i[2])], prediction_stats[int(i[3])], model)[0]
        # print system_ipc
        if system_ipc >= ipc:
            mapping = str(i[0]) + str(i[1]) + str(i[2]) + str(i[3])
            ipc = system_ipc
    return mapping + str(ipc)


if __name__ == '__main__':

    #if this fails try to change the os.popen paramater for this scripts location in demo.py, called path
    '''
    arg[0] is the script name
    arg[1] is the train or predict decision paramater
    arg[2] is the train stats in json format, last indexed list is system ipc's
    '''
    train_or_predict = int(sys.argv[1])
    model_name = str(sys.argv[2])
    model = loadModel(model_name)
    start = time.time()
    if train_or_predict == 0:
        data = json.loads(sys.argv[3])
        ipcs = json.loads(sys.argv[4])
        continue_training(data, ipcs, model, model_name)
        end = time.time()
        with open("/scratch/nas/1/dn/sniper-6.0/benchmarks/SimResults/paper2exec.txt", "a") as myfile:
            myfile.write("train time : " + str(start - end))
    else:
        a = json.loads(sys.argv[3])
        b = json.loads(sys.argv[4])
        c = json.loads(sys.argv[5])
        d = json.loads(sys.argv[6])
        prediction = predict(a, b, c, d, model)
        end = time.time()
        with open("~/paper2exec.txt", "a") as myfile:
            myfile.write("predict time : " + str(start - end))
        print prediction


################
