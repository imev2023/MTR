# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 10:00 2023
"""

from Data import Data,Log_transformer,Standard_tranformer, Oversample
import pickle as pk
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, balanced_accuracy_score,roc_auc_score, fbeta_score, auc, roc_curve
from sklearn.linear_model import LogisticRegression
from torch.optim.lr_scheduler import ReduceLROnPlateau
from joblib import Parallel, delayed
import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import itertools

#generate data ST3

seed = 1235711
fold = os.getcwd()
fold

# # ### GENERATE DATA FOR CELL CNN ###
# data = Data()
# data.load(fold + "/data/ST2/ST2_train_scale")
# data.save(fold + "/data/ST2/ST2_cell/ST2_train_scale")
# data.load(fold + "/data/ST2/ST2_cell/ST2_train_scale")
# over = Oversample(seed)
# over.fit_transform(fold + "/data/ST2/ST2_cell/ST2_train_scale")
# # data.augmentation(factor=20, seed=seed)

# data.load(fold + "/data/ST2/ST2_cell/ST2_train_scale")
# data.save(fold + "/data/ST2/ST2_cell/ST2_cell_train_scale")
# data.load(fold + "/data/ST2/ST2_cell/ST2_cell_train_scale")
# data.sample_all_cells(numcells=10000,seed=seed+1)

# data.load(fold + "/data/ST2/ST2_val_scale")
# data.save(fold + "/data/ST2/ST2_cell/ST2_cell_val_scale")
# data.load(fold + "/data/ST2/ST2_cell/ST2_cell_val_scale")
# over.fit_transform(fold + "/data/ST2/ST2_cell/ST2_cell_val_scale")
# data.load(fold + "/data/ST2/ST2_cell/ST2_cell_val_scale")
# data.sample_all_cells(numcells=10000,seed=seed+2)

# data.load(fold + "/data/ST2/ST2_test_scale")
# data.save(fold + "/data/ST2/ST2_cell/ST2_cell_test_scale")
# data.load(fold + "/data/ST2/ST2_cell/ST2_cell_test_scale")
# data.sample_all_cells(numcells=10000,seed=seed+3)

# # save train and valalidation dataset
# dataset = data.get_dataload(fold_train=fold + "/data/ST2/ST2_cell/ST2_cell_train_scale", fold_test=fold + "/data/ST2/ST2_cell/ST2_cell_val_scale")
# file = open(fold +"/data/ST2/dataset_cell_cnn_scale_noaug.dat","wb")
# pk.dump(dataset,file)
# file.close()

### Load and contruct dataset ###
data = Data()
data.load(fold + "/data/ST3/ST3_logscale/ST3_train_logscale")
data.save(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_train_logscale")
data.load(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_train_logscale")
over = Oversample(seed)
over.fit_transform(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_train_logscale")
# data.augmentation(factor=20, seed=seed)

data.load(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_train_logscale")
data.save(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_train_logscale")
data.load(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_train_logscale")
data.sample_all_cells(numcells=10000,seed=seed+1)

data.load(fold + "/data/ST3/ST3_logscale/ST3_val_logscale")
data.save(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_val_logscale")
data.load(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_val_logscale")
over.fit_transform(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_val_logscale")
data.load(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_val_logscale")
data.sample_all_cells(numcells=10000,seed=seed+2)

data.load(fold + "/data/ST3/ST3_logscale/ST3_test_logscale")
data.save(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_test_logscale")
data.load(fold + "/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_cell_test_logscale")
data.sample_all_cells(numcells=10000,seed=seed+3)

# save train and valalidation dataset
dataset = data.get_dataload(fold_train=fold + "/data/ST3/ST3_cell_logscale/ST3_cell_train_scale", fold_test=fold + "/data/ST3/ST3_cell_logscale/ST3_cell_val_scale")
file = open(fold +"/data/ST3/ST3_logscale/dataset_cell_cnn_scale_noaug.dat","wb")
pk.dump(dataset,file)
file.close()

### Load and contruct dataset ###
data = Data()
data.load(fold+"/data/ST3/ST3_base")
tam = len(data.pheno)
pos = sum(data.pheno)
pos_weight = (tam-pos)/pos

# EQUIVALENT BELOW train_cell_data, val_cell_data = data.get_dataload(fold +"/data/ST3/ST3_cell_logscale/ST3_cell_train_scale",fold +"/data/ST3/ST3_cell_logscale/ST3_cell_val_scale")
file = open(fold +"/data/ST3/ST3_logscale/dataset_cell_cnn_logscale_noaug.dat","rb")
train_data, val_data  = pk.load(file)
file.close()

# Input shape is determined by the number of cells sampled from each sample and the number of markers (30 = ST3)
imput_shape = train_data.__getitem__(0)[0].size()
imput_size = 1
for v in imput_shape:
    imput_size*=v
    
### defining model ###
class Model_CV2(torch.nn.Module):
    def __init__(self,imput_size, num_markers):
        super().__init__()
        torch.set_default_dtype(torch.float64)
        self.flatten = torch.flatten
        self.cov1 = torch.nn.Conv2d(in_channels=1, out_channels=3, kernel_size=(1,num_markers))
        self.cov2 = torch.nn.Conv2d(in_channels=3, out_channels=3, kernel_size=(1,1))
        self.fc1 = torch.nn.Linear(in_features=3, out_features=1)
        self.avPoll=torch.nn.AvgPool2d(kernel_size=(10000,1),stride =1)
        self.sigmoid = torch.nn.Sigmoid()
        self.relu = torch.nn.ReLU()
        # self.do = torch.nn.Dropout1d(p=0.2)
        # self.bn = torch.nn.BatchNorm1d(1000)
        self.optimizer=None
    def forward(self, x):
        x = self.relu(self.cov1(x))
        print(x.shape)
        x = self.relu(self.cov2(x))
        print(x.shape)
        x = self.avPoll(x)
        print(x.shape)
        x = self.flatten(x, start_dim=1)
        print(x.shape)
        x = self.relu(self.fc1(x))
        print(x.shape)


        return x
    
# class Model_CV1(torch.nn.Module):
#     def __init__(self,imput_size, num_markers):
#         super().__init__()
#         torch.set_default_dtype(torch.float64)
#         self.flatten = torch.flatten
#         self.cov1 = torch.nn.Conv2d(in_channels=1, out_channels=3, kernel_size=(1,num_markers))
#         self.fc1 = torch.nn.Linear(in_features=3, out_features=1)
#         # self.sigmoid = torch.nn.Sigmoid()
#         self.relu = torch.nn.ReLU()
#         self.avPoll=torch.nn.AvgPool2d(kernel_size=(1000, 1),stride =1)
#         # self.do = torch.nn.Dropout1d(p=0.2)
#         self.optimizer=None
#     def forward(self, x):
#         x = self.relu(self.cov1(x))
#         x = self.fc1(x)
#         x = self.avPoll(x)
#         x = self.flatten(x)
#         return x

class Model_CV1(torch.nn.Module):
    def __init__(self,imput_size, num_markers):
        super().__init__()
        torch.set_default_dtype(torch.float64)
        self.flatten = torch.flatten
        self.cov1 = torch.nn.Conv2d(in_channels=1, out_channels=1, kernel_size=(1,num_markers))
        self.avPoll=torch.nn.AvgPool2d(kernel_size=(10000,1),stride =1)
        self.relu = torch.nn.ReLU()
        # self.do = torch.nn.Dropout1d(p=0.2)
        # self.bn = torch.nn.BatchNorm1d(1000)
        self.optimizer=None
    def forward(self, x):
        x = self.relu(self.cov1(x))
        x = self.avPoll(x)
        return x
    
### construct Neural_network ### 
class Neural:
    def __init__(self,train_dataset,val_dataset,model,optimizer,loss_f, device,sumary_lab=False,bach_size=16):
        self.train_loader = DataLoader(dataset=train_data, batch_size=bach_size, shuffle=True)
        self.bach_size = bach_size
        self.val_loader = DataLoader(dataset=val_data, batch_size=bach_size, shuffle=True)
        self.model = model
        self.optimizer = optimizer
        self.loss_f = loss_f
        self.device = device
        self.sumary_lab = sumary_lab
        self.model.to(device)
        if(sumary_lab!=False):
            self.writer= SummaryWriter(fold+"/data/ST3/ST3/logscale/ST3_cell_logscale/ST3_runs/"+self.sumary_lab)
        else:
            self.writer=None
        
    def trainning(self,num_epochs,file_out,test_dataset=None):
        for epoch in range(num_epochs):
            ###TRAINING###
            tloss = []
            vloss = []
            # si=0
            t_y = []
            v_y = []
            t_yp = []
            v_yp = []
            for batch_x,batch_y in self.train_loader:
                self.model.train()
                batch_x.to(self.device)
                batch_y.to(self.device)
                y_pred = self.model(batch_x) 
                ### Add loss ###
                loss = self.loss_f(torch.flatten(y_pred), batch_y)
                loss.backward()
                self.optimizer.step()
                self.optimizer.zero_grad()
                tloss.append(loss.detach().item())
                # True y in batch
                t_y = t_y + batch_y.detach().tolist()
                # Pred y in batch
                t_yp = t_yp + torch.flatten(y_pred.detach()).tolist()
                
            fpr, tpr, thresholds = roc_curve(t_y,t_yp, pos_label=1)
            b_acuracy = auc(fpr, tpr)       
            # accuracy = accuracy_score(t_y, t_yp)
            # bas = balanced_accuracy_score(t_y, t_yp)
            # f1 = fbeta_score(t_y, t_yp,beta = 1, pos_label=1)
            # f2 = fbeta_score(t_y, t_yp,beta = 2, pos_label=1)
            ### Average validation loss and score for all batches ###
            # print(si)
            tloss = np.mean(np.array(tloss))
            # sfscore = sfscore/si
            # sscore = sscore/si
            print("------------------")
            print("Epoch: ", str(epoch))
            print("training loss: ", str(tloss), "training auc: "+str(b_acuracy))
            # print("training accuracy: ", str(accuracy), "training bas: ", str(bas))
            # print("f1 score: ", str(f1), "f2 score: ", str(f2))
            # print("------------------")

            ###VALIDATION###
            self.model.eval()
            ### Add accuracy ###  
            with torch.no_grad():
                for batch_x,batch_y in self.val_loader:
                    self.model.train()
                    batch_x.to(self.device)
                    batch_y.to(self.device)
                    y_pred = self.model(batch_x) 
                    ### Add loss ###
                    loss = self.loss_f(torch.flatten(y_pred), batch_y)
                    vloss.append(loss.detach().item())
                    v_y = v_y + batch_y.detach().tolist()
                    v_yp = v_yp + torch.flatten(y_pred.detach()).tolist()
                        
                ### Average validation loss and score for all batches ###
                # print(si)
                fpr, tpr, thresholds =roc_curve(v_y,v_yp, pos_label=1)
                vb_acuracy = auc(fpr, tpr)
                vloss = np.mean(np.array(vloss))
                    # print("------------------")
                print("val loss: ", str(vloss), "val accuracy: "+str(vb_acuracy)) #, " fscore: ", str(sfscore))
                # print("learning rate: ", self.optimizer["lr"])
                print("------------------")
                if(epoch%20==0):
                    self._save(fold+"/data/ST3/ST3_logscale/ST3_cell_logscale/ST3_models/"+self.sumary_lab +".dat", epoch, num_epochs)
            if(self.sumary_lab!=False):
                self.writer.add_scalars(main_tag=self.sumary_lab, 
                                        tag_scalar_dict={"Loss/train":tloss,
                                                          "Loss/validation":vloss, 
                                                          "B_Accuracy/train":b_acuracy, 
                                                          "b_Accuracy/validation":vb_acuracy},
                                        global_step=epoch)
        self.save_res(file_out,test_dataset)
        if(self.sumary_lab!=False):
            self._writer_close()
        
    def _save(self,file,epoch,num_epochs):
        mod = {"model":self.model.state_dict(),"epoch":epoch,"opt":self.optimizer.state_dict(),"train_loader":self.train_loader,
                "val_loader":self.val_loader,"num_epochs":num_epochs,"loss_f":self.loss_f,"sumary_lab":self.sumary_lab,
                "device":self.device}
        torch.save(mod, file)
        
    def _writer_close(self):
        self.writer.close()
        
    def save_res(self,file,test_dataset=None):
        self.model.eval()
        with torch.no_grad():
            ytrain_true=[]
            ytrain_pred=[]
            for bx,by in self.train_loader:
                bx.to(self.device)
                ytrain_true.append(by) 
                ytrain_pred.append(self.model(bx))
            yval_true=[]
            yval_pred=[]
            for bx,by in self.val_loader:
                bx.to(self.device)
                yval_true.append(by) 
                yval_pred.append(self.model(bx))
            if(test_dataset!=None):
                tes_loader = DataLoader(dataset=test_dataset, batch_size=16, shuffle=False)
                ytest_true=[]
                ytest_pred=[]
                for bx,by in tes_loader:
                    bx.to(self.device)
                    ytest_true.append(by) 
                    ytest_pred.append(self.model(bx))
                ytrain_true=[]
                ytrain_pred=[]
                
                mod = {"model":self.model.state_dict(),"train_loader":self.train_loader,
                        "val_loader":self.val_loader,"test_loader":tes_loader,"sumary_lab":self.sumary_lab,
                        "ytrain_true":ytrain_true,"ytrain_pred":ytrain_pred, 
                        "yval_true":yval_true,"yval_pred":yval_pred, 
                        "ytest_true":ytest_true,"ytest_pred":ytest_pred}
            
            else:
                mod = {"model":self.model.state_dict(),"train_loader":self.train_loader,
                        "val_loader":self.val_loader,"sumary_lab":self.sumary_lab,
                        "ytrain_true":ytrain_true,"ytrain_pred":ytrain_pred, 
                        "yval_true":yval_true,"yval_pred":yval_pred}
            file = open(file,"wb")
            pk.dump(mod, file)
            file.close()
# #####################################################################################################

### Define the hyperparameter values to explore ###
batch_size=16
lr = 0.0001

device = "cpu"
torch.set_num_threads(16)
loss_f = torch.nn.BCEWithLogitsLoss(reduction="mean",pos_weight=torch.as_tensor(pos_weight))
print("run model")

model = Model_CV1(imput_size, num_markers=30)
optimizer=torch.optim.Adam(model.parameters(), lr=lr)
net = Neural(train_data,val_data,model=model, loss_f=loss_f,optimizer=optimizer,device=device,sumary_lab="scale_modelCV1_2307_1900",bach_size=batch_size)                  
net.trainning(num_epochs=5000, file_out=fold+"/data/ST3/ST3_cell/Results/scale_modelCV1_2307_1900.dat", test_dataset=None)


model = Model_CV2(imput_size, num_markers=30)
optimizer=torch.optim.Adam(model.parameters(), lr=lr)
net = Neural(train_data,val_data,model=model, loss_f=loss_f,optimizer=optimizer,device=device,sumary_lab="scale_modelCV2_2307_1900",bach_size=batch_size)                  
net.trainning(num_epochs=5000, file_out=fold+"/data/ST3/ST3_cell/Results/scale_modelCV2_2307_1900.dat", test_dataset=None)
