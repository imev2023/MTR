# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 10:00 2023

@author: nina working on RF
"""


import pickle as pk
import os
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from joblib import Parallel, delayed
from sklearn.model_selection import cross_val_score
#generate data ST1
seed = 1235711
fold = os.getcwd()
fold
v = []
files = []

train_path = "/data/ST2/pooled/ST2_train_logscale_pool"
lab = "logscaled_ST2"
file = pd.read_csv(fold+train_path)
file=file.iloc[:,1:]
x_train= file.iloc[:, :-1]
y_train = file.iloc[:, -1]

val_path = "/data/ST2/pooled/ST2_val_logscale_pool"
file = pd.read_csv(fold+train_path)
file=file.iloc[:,1:]
x_val= file.iloc[:, :-1]
y_val = file.iloc[:, -1]

# x_train, x_val, y_train, y_val = train_test_split(x, y,stratify=y, test_size=0.10, random_state=seed)
files.append((x_train.copy(), x_val.copy(), y_train.copy(), y_val.copy(),lab))


train_path = "/data/ST2/pooled/ST2_train_scale_pool"
lab = "scaled_ST2"
file = pd.read_csv(fold+train_path)
file=file.iloc[:,1:]
x_train= file.iloc[:, :-1]
y_train = file.iloc[:, -1]

val_path = "/data/ST2/pooled/ST2_val_scale_pool"
file = pd.read_csv(fold+train_path)
file=file.iloc[:,1:]
x_val= file.iloc[:, :-1]
y_val = file.iloc[:, -1]

# x_train, x_val, y_train, y_val = train_test_split(x, y,stratify=y, test_size=0.10, random_state=seed)
files.append((x_train.copy(), x_val.copy(), y_train.copy(), y_val.copy(),lab))

# train_path = "/data/ST3/ST3_logscale/ST3_train_logscale_pool"
# lab = "logscaled_ST3"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_train= file.iloc[:, :-1]
# y_train = file.iloc[:, -1]

# val_path = "/data/ST3/ST3_logscale/ST3_val_logscale_pool"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_val= file.iloc[:, :-1]
# y_val = file.iloc[:, -1]

# # x_train, x_val, y_train, y_val = train_test_split(x, y,stratify=y, test_size=0.10, random_state=seed)
# files.append((x_train.copy(), x_val.copy(), y_train.copy(), y_val.copy(),lab))


# train_path = "/data/ST3/ST3_scale/ST3_train_scale_pool"
# lab = "scaled_ST3"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_train= file.iloc[:, :-1]
# y_train = file.iloc[:, -1]

# val_path = "/data/ST3/ST3_scale/ST3_val_scale_pool"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_val= file.iloc[:, :-1]
# y_val = file.iloc[:, -1]

# # x_train, x_val, y_train, y_val = train_test_split(x, y,stratify=y, test_size=0.10, random_state=seed)
# files.append((x_train.copy(), x_val.copy(), y_train.copy(), y_val.copy(),lab))


v = []
for data in files:
    for model in ["RF","LR","SVM"]:
        
        if model=="RF":
            res_max_features = ["sqrt","log2"]
            res_max_depth = [10,15,20,30]
            for max_features in res_max_features:
                for max_depth in res_max_depth:
                    par= {}
                    par["max_features"]=max_features
                    par["max_depth"]=max_depth
                    v.append((data,model,par)) 
        if model=="LR":    
            c = 1
            lrs = ["l1", "l2"]
            for a in range(20):
                par = {}
                par["c"]=c
                c = c-c*1/5
                print(c)
                for l in lrs:
                    par['l']=l
                v.append((data,model,par)) 
        # if model=="SVM":
        #     res_c = [0.8]
        #     res_gamma = [0.1]
        #     #res_c = [1,0.9,0.8,0.5,0.1]
        #     #res_gamma = [1,0.5,0.1,0.01,0.001,0.0001]
        #     res_kernel = ["linear",'rbf', 'sigmoid']
        #     for c in res_c:
        #         for gamma in res_gamma:
        #             for kernel in res_kernel:
        #                 par = {}
        #                 par["c"]=c
        #                 par["kernel"]=kernel
        #                 par["gamma"]=gamma
        #                 v.append((data,model,par)) 
                    
def calcu(v):
    data,model,par = v
    x_train, x_val, y_train, y_val, lab=data
    if model=="RF":
        rf = RandomForestClassifier(n_estimators=2001,max_features=par["max_features"],max_depth=par["max_depth"],random_state=seed,oob_score=False)
        rf.fit(x_train, y_train)
        y_pred=rf.predict(x_val)
        return accuracy_score(y_true=y_val,y_pred=y_pred)
    if model=="LR":
        lr = LogisticRegression(random_state=seed,C=par["c"],penalty=par['l'],solver="liblinear",max_iter=100)
        lr.fit(x_train, y_train)
        y_pred=lr.predict(x_val)
        return accuracy_score(y_true=y_val,y_pred=y_pred)
    if model=="SVM":
        svc = SVC(C=par["c"],gamma=par["gamma"],kernel=par["kernel"],cache_size=3000)
        svc.fit(x_train, y_train)
        if svc.fit_status_==1:
            print("not fit")
            return 0
        y_pred=svc.predict(x_val)
        return accuracy_score(y_true=y_val,y_pred=y_pred)
    return None

print("start")
res = Parallel(n_jobs=15, verbose=10)(delayed(calcu)(p) for p in v)
print("stop")

# best_params = []
# # Extract the best parameters for each model
# for r, params in res:
#     best_params.append((r, params))
# # Sort the best parameters based on accuracy in descending order
# best_params.sort(reverse=True)
# # Select the top parameters for each model
# top_params = best_params[:3]  # Change the number as needed

# output = {"v": v, "res": res, "best_params": top_params}

lab =[]
par = []
model = []
for i in range(len(v)):
    data,m,p = v[i]
    lab.append(data[4])
    par.append(p)
    model.append(m)
data = pd.DataFrame({"data":lab,"model":model,"par":par,"acuracy":res})

data.to_csv(fold+"/data/RF_LR_parameters_ST3_2407.csv",index_label=False)

# ### BATCH ###
# train_path = "/data/ST3_wout801/pooled/ST3_train_val_batch_pool"
# file = pd.read_csv(fold+train_path)
# # file = file.sample(n=20000,random_state=seed)
# file=file.iloc[:,1:]
# x_train= file.iloc[:, :-1]
# y_train = file.iloc[:, -1]

# test_path = "/data/ST3_wout801/pooled/ST3_test_batch_pool_unbalanced"
# file = pd.read_csv(fold+test_path)
# file=file.iloc[:,1:]
# x_test= file.iloc[:, :-1]
# y_test = file.iloc[:, -1]

# rf = RandomForestClassifier(n_estimators=501,max_features="sqrt",max_depth=20,random_state=seed,oob_score=False,n_jobs=15, verbose=2)
# rf.fit(x_train, y_train)
# y_pred=rf.predict(x_test)
# y_prob=rf.predict_proba(x_test)
# print("RF Finished")
# comb = {"y_true":y_test, "RF_y_pred":y_pred, "RF_y_prob":y_prob}
# file = open(fold+"/data/ST3/batch_ST3_RF_test","wb")
# pk.dump(comb, file)
# file.close()

# lr = LogisticRegression(random_state=seed,C= 0.04398046511104001,penalty="l1",solver="liblinear", verbose=2)
# lr.fit(x_train, y_train)
# y_pred=lr.predict(x_test)
# y_prob=lr.predict_proba(x_test)
# print("LR Finished")
# comb = {"y_true":y_test, "LR_y_pred":y_pred, "LR_y_prob":y_prob}
# file = open(fold+"/data/ST3/batch_ST3_LR_test.dat","wb")
# pk.dump(comb, file)
# file.close()

# ### SCALED ###
# train_path = "/data/ST2/ST2_scale/ST2_train_scale_pool"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_t= file.iloc[:, :-1]
# y_t = file.iloc[:, -1]
# val_path = "/data/ST2/ST2_scale/ST2_val_scale_pool"
# file = pd.read_csv(fold+val_path)
# file=file.iloc[:,1:]
# x_v= file.iloc[:, :-1]
# y_v = file.iloc[:, -1]
# x_train = pd.concat([x_t, x_v], axis=0)
# y_train = pd.concat([y_t, y_v], axis=0)

# test_path = "/data/ST2/ST2_scale/ST2_train_scale_pool"
# file = pd.read_csv(fold+test_path)
# file=file.iloc[:,1:]
# x_test= file.iloc[:, :-1]
# y_test = file.iloc[:, -1]

# rf = RandomForestClassifier(n_estimators = 1001,max_features="log2",max_depth=10,random_state=seed,oob_score=False,n_jobs=15, verbose=2)
# rf.fit(x_train, y_train)
# rf_y_pred=rf.predict(x_test)
# rf_y_prob=rf.predict_proba(x_test)
# print("RF Finished")

# lr = LogisticRegression(random_state=seed,C=  0.10737418240000003,penalty="l1",solver="liblinear", verbose=2)
# lr.fit(x_train, y_train)
# y_pred=lr.predict(x_test)
# y_prob=lr.predict_proba(x_test)
# print("LR Finished")

# comb = {"y_true":y_test, "RF_y_pred":rf_y_pred, "RF_y_prob":rf_y_prob,"LR_y_pred":y_pred, "LR_y_prob":y_prob}
# file = open(fold+"/data/ST2/ST2_scale/scaled_ST2_LRRF_test.dat","wb")
# pk.dump(comb, file)
# file.close()

# ### LOG SCALED ###
# train_path = "/data/ST2/ST2_logscale/ST2_train_logscale_pool"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_t= file.iloc[:, :-1]
# y_t = file.iloc[:, -1]
# val_path = "/data/ST2/ST2_logscale/ST2_val_logscale_pool"
# file = pd.read_csv(fold+val_path)
# file=file.iloc[:,1:]
# x_v= file.iloc[:, :-1]
# y_v = file.iloc[:, -1]
# x_train = pd.concat([x_t, x_v], axis=0)
# y_train = pd.concat([y_t, y_v], axis=0)

# test_path = "/data/ST2/ST2_logscale/ST2_train_logscale_pool"
# file = pd.read_csv(fold+test_path)
# file=file.iloc[:,1:]
# x_test= file.iloc[:, :-1]
# y_test = file.iloc[:, -1]

# rf = RandomForestClassifier(n_estimators = 1001, max_features="log2",max_depth=10,random_state=seed,oob_score=False,n_jobs=15, verbose=2)
# rf.fit(x_train, y_train)
# rf_y_pred=rf.predict(x_test)
# rf_y_prob=rf.predict_proba(x_test)
# print("RF Finished")

# lr = LogisticRegression(random_state=seed,C=  0.10737418240000003,penalty="l1",solver="liblinear", verbose=2)
# lr.fit(x_train, y_train)
# y_pred=lr.predict(x_test)
# y_prob=lr.predict_proba(x_test)
# print("LR Finished")

# comb = {"y_true":y_test, "RF_y_pred":rf_y_pred, "RF_y_prob":rf_y_prob,"LR_y_pred":y_pred, "LR_y_prob":y_prob}
# file = open(fold+"/data/ST2/ST2_logscale/logscaled_ST2_LRRF_1001.dat","wb")
# pk.dump(comb, file)
# file.close()

# ### SCALED ###
# train_path = "/data/ST3/ST3_scale/ST3_train_scale_pool"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_t= file.iloc[:, :-1]
# y_t = file.iloc[:, -1]
# val_path = "/data/ST3/ST3_scale/ST3_val_scale_pool"
# file = pd.read_csv(fold+val_path)
# file=file.iloc[:,1:]
# x_v= file.iloc[:, :-1]
# y_v = file.iloc[:, -1]
# x_train = pd.concat([x_t, x_v], axis=0)
# y_train = pd.concat([y_t, y_v], axis=0)

# test_path = "/data/ST3/ST3_scale/ST3_train_scale_pool"
# file = pd.read_csv(fold+test_path)
# file=file.iloc[:,1:]
# x_test= file.iloc[:, :-1]
# y_test = file.iloc[:, -1]

# rf = RandomForestClassifier(n_estimators = 1001,max_features="log2",max_depth=10,random_state=seed,oob_score=False,n_jobs=15, verbose=2)
# rf.fit(x_train, y_train)
# rf_y_pred=rf.predict(x_test)
# rf_y_prob=rf.predict_proba(x_test)
# print("RF Finished")

# lr = LogisticRegression(random_state=seed,C=  0.10737418240000003,penalty="l1",solver="liblinear", verbose=2)
# lr.fit(x_train, y_train)
# y_pred=lr.predict(x_test)
# y_prob=lr.predict_proba(x_test)
# print("LR Finished")

# comb = {"y_true":y_test, "RF_y_pred":rf_y_pred, "RF_y_prob":rf_y_prob,"LR_y_pred":y_pred, "LR_y_prob":y_prob}
# file = open(fold+"/data/ST3/ST3_scale/scaled_ST3_LRRF_test.dat","wb")
# pk.dump(comb, file)
# file.close()

# ### LOG SCALED ###
# train_path = "/data/ST3/ST3_logscale/ST3_train_logscale_pool"
# file = pd.read_csv(fold+train_path)
# file=file.iloc[:,1:]
# x_t= file.iloc[:, :-1]
# y_t = file.iloc[:, -1]
# val_path = "/data/ST3/ST3_logscale/ST3_val_logscale_pool"
# file = pd.read_csv(fold+val_path)
# file=file.iloc[:,1:]
# x_v= file.iloc[:, :-1]
# y_v = file.iloc[:, -1]
# x_train = pd.concat([x_t, x_v], axis=0)
# y_train = pd.concat([y_t, y_v], axis=0)

# test_path = "/data/ST3/ST3_logscale/ST3_train_logscale_pool"
# file = pd.read_csv(fold+test_path)
# file=file.iloc[:,1:]
# x_test= file.iloc[:, :-1]
# y_test = file.iloc[:, -1]

# rf = RandomForestClassifier(n_estimators = 1001, max_features="log2",max_depth=10,random_state=seed,oob_score=False,n_jobs=15, verbose=2)
# rf.fit(x_train, y_train)
# rf_y_pred=rf.predict(x_test)
# rf_y_prob=rf.predict_proba(x_test)
# print("RF Finished")

# lr = LogisticRegression(random_state=seed,C=  0.10737418240000003,penalty="l1",solver="liblinear", verbose=2)
# lr.fit(x_train, y_train)
# y_pred=lr.predict(x_test)
# y_prob=lr.predict_proba(x_test)
# print("LR Finished")

# comb = {"y_true":y_test, "RF_y_pred":rf_y_pred, "RF_y_prob":rf_y_prob,"LR_y_pred":y_pred, "LR_y_prob":y_prob}
# file = open(fold+"/data/ST3/ST3_logscale/logscaled_ST3_LRRF_1001.dat","wb")
# pk.dump(comb, file)
# file.close()