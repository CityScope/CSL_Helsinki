#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 15:28:06 2018

@author: doorleyr
"""
import numpy as np
import numpy.matlib
import matplotlib.pyplot as plt

# Resources
# resourceTimeTable from hour 0 to 12

locR=np.array([[1,1],
              [2,3],
              [-1,2],
              [2,0]])
maxDist=3


tR=np.array([[1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,1,1,1,1,1,1],
    [1,1,1,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,1,1,0,0,1,1]])

T=tR.shape[1]

# suitability of each resource for each use (3 possible)
aR=np.array([[1, 1, 0],
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1]])

# Demands
# demand for uses
locHub=[0,0]
D=[6,6,6]

#distances
c=[np.sqrt(np.power((locHub[0]-locR[i,0]),2)+ np.power((locHub[1]-locR[i,1]),2)) for i in range(locR.shape[0])]
cAll=[]

#suitability matrix
bounds=[]
delta=np.zeros([aR.shape[1], aR.shape[0], tR.shape[1]])
for i in range(aR.shape[1]):
    for j in range(aR.shape[0]):
        for t in range(tR.shape[1]):
            cAll.extend([c[j]])
            if aR[j,i]>0 and tR[j,t]>0 and c[j]<maxDist:
                delta[i,j,t]+=1
                bounds.append([0,1])
            else:
                bounds.append([0,0])

boundsMat=np.array(bounds)
cMat=np.array(cAll)
                
# Demand Constraints
constraints=[]
for i in range(len(D)):
    constraintMat=np.zeros([aR.shape[1], aR.shape[0], tR.shape[1]])
    constraintMat[i,:,:]=1
    cMFlat=constraintMat.flatten()
    constraints.extend([list(cMFlat)])
    
A_eq=np.mat(constraints)
b_eq=D
    

#Plot
plt.scatter(locR[:,0], locR[:,1], color='blue')
plt.scatter(locHub[0], locHub[1], color='red')


from scipy.optimize import linprog
res = linprog(cMat, A_eq=A_eq, b_eq=b_eq, bounds=boundsMat)

#flowsMat=np.empty([aR.shape[1], aR.shape[0], tR.shape[1]])
#count=0
#for i in range(aR.shape[1]):
#    for j in range(aR.shape[0]):
#        for t in range(tR.shape[1]):
#            flowsMat[i,j,t]=res['x'][count]
#            count+=1

flowsMat=np.array(res['x']).reshape(delta.shape)

f, ax = plt.subplots(3, 4)
for i in range(3):
    for j in range(4):        
        for l in range(locR.shape[0]):
            ax[i,j].scatter(locR[:,0], locR[:,1], color='blue')
            ax[i,j].scatter(locHub[0], locHub[1], color='red')
            if sum(flowsMat[:,l,4*i+j])>0:
                ax[i,j].plot([locHub[0],locR[l,0]], [locHub[1],locR[l,1]], color='green')
                ax[i,j].set_xlim([-1,4])
                ax[i,j].set_ylim([-1,4])