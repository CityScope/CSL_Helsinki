#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 10:17:54 2018

@author: doorleyr
"""

import calendar
import json
import datetime
import time
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy.matlib
import random
from shapely.geometry import shape, Point
import pyproj

utm35N=pyproj.Proj("+init=EPSG:32635")
wgs84=pyproj.Proj("+init=EPSG:4326")

#function to find the centre lat and lon of the building(s) with a particular building code.
def getBldLL(bCode, bldJson):
    xs, ys=[], []
    for i in range(len(bldJson['features'])):
        if bldJson['features'][i]['properties']['buildingCo']==bCode:
            polygon = shape( bldJson['features'][i]['geometry'])
            xs.extend([polygon.centroid.x])
            ys.extend([polygon.centroid.y])
    if len(xs)>0:
        return [np.mean(xs), np.mean(ys)]
    else:
        return []
            
#get the buildings geojson data (previously created from the shape file)
blds=json.load(open('../building_region.geojson'))

#get the room usage data
usageAll=pd.read_csv('../asio_in_reservations2017.csv', encoding='latin1', sep=';')
# only consider about 4 months of data during term time.
usage=usageAll.iloc[8:51689]
usage=usage.fillna('0')
# replace NA by '0'

# create lists
orgsL=usage['organisationCode'].tolist()
bCodesL=usage['buildingCode'].tolist()
# create unique list of orgs
orgs=list(set(orgsL))

# some org codes mistakenly appearing in bld codes
# for each bld, if not 0 and if in orgs set, replace with 0 
for i in range(len(bCodesL)):
    if not bCodesL[i]=='0':
        if bCodesL[i] in orgs:
            print(bCodesL[i])
            bCodesL[i]='0'

# replace all org names with their first character
for i in range(len(orgsL)):
    orgsL[i]=orgsL[i][0]

orgs=list(set(orgsL))
bCodes=list(set(bCodesL))

orgs.remove('0')
bCodes.remove('0')

# In order to assign a hub building to each org, first create adjacency matrix between buildings and orgs based on usage
adj=np.zeros([len(bCodes), len(orgs)])
# for each row, if neither are NULL, increment the appropriate value of the adjacency matrix
for i in range(len(orgsL)):
    if not orgsL[i]=='0':
        if not bCodesL[i]=='0':
            k1=bCodes.index(bCodesL[i])
            k2=orgs.index(orgsL[i])
            adj[k1,k2]+=1

#Get coordinates of all building codes
bldLL=[]
for b in bCodes:
    bldLL.append(getBldLL(b, blds))

# Assign a home base (hub) for each org
# Don't allow 2 orgs to have the same hub.
# Don't assign hubs for which we don't have building locations

HubsLL=[]      
Hubs={}
for o in range(adj.shape[1]):
    oUsage=adj[:,o]
    mostUsed=oUsage.argsort()[-10:][::-1]
    done=0
    ind=0
    while done==0:
        if ((bCodes[mostUsed[ind]] not in Hubs.values()) & (len(bldLL[mostUsed[ind]])>0)):
            Hubs[orgs[o]]=bCodes[mostUsed[ind]]
            done=1
            HubsLL.append(bldLL[mostUsed[ind]])
        else:
            ind+=1
          

# Look at total occupancy over time
# get the timestamps as lists
# then convert to numerical format
startTimeStr= (usage['reservationDate']+' '+usage['startTime']).tolist()
endTimeStr= (usage['reservationDate']+' '+usage['endTime']).tolist()
startTimeM=[calendar.timegm(time.strptime(startTimeStr[i][:16], '%Y-%m-%d %H:%M'))for i in range(len(startTimeStr))] # numerical date (ignores time zones)
endTimeM=[calendar.timegm(time.strptime(endTimeStr[i][:16], '%Y-%m-%d %H:%M'))for i in range(len(startTimeStr))] 
lenBooking=[((endTimeM[i]-startTimeM[i])/(60*60)) for i in range(len(startTimeM))]
print('First Time :' + str(startTimeStr[np.argmin(startTimeM)]))
print('Last Time :' + str(endTimeStr[np.argmax(endTimeM)]))
# total time covered
length=np.max(endTimeM)-np.min(startTimeM)
numWeeks=int(length/(7*24*60*60))
#get start time of the first window
startWindow=int(np.min(startTimeM)/(3600*24))*(3600*24)

# Reorganise the data into fixed time windows of 1 hour
lenP=60*60 #1 hour window
numP=int(length/lenP) #total number of periods
totalOccupancy=[0 for i in range(numP)]
for i in range(len(startTimeM)):
    timePosS=int(((startTimeM[i])-startWindow)/lenP)
    timePosE=min(int((endTimeM[i]-startWindow)/lenP), numP-1)
    for tp in range(timePosS, timePosE):
        totalOccupancy[tp]+=1

windows=[datetime.datetime.utcfromtimestamp(startWindow+i*lenP) for i in range(numP)]
hours=[w.hour for w in windows] #hour of day associated with each time window
wdays=[w.weekday() for w in windows] #day of week associated with each time window
plt.plot(totalOccupancy)

# Baseline scenario- analyze occupancy levels for an average week
# get list of all rooms
roomsL=usage['spaceId'].tolist()
rooms=list(set(roomsL))
rooms.remove('0')

# build a matrix representing room occupancy by hour
occupancyByRoom=np.zeros([numP, len(rooms)])
for i in range(len(startTimeM)):
    timePosS=int(((startTimeM[i])-startWindow)/lenP)
    timePosE=min(int((endTimeM[i]-startWindow)/lenP), numP-1)
    rowRoom=roomsL[i]
    if not rowRoom=='0':
        k2=rooms.index(rowRoom)
        for tp in range(timePosS, timePosE): 
            #occupancyByRoom[tp, k2]=1
            occupancyByRoom[tp, k2]+=1
            #doesn't make much difference if you count multi-booking or not

#Room VT1 is multi-booked very often 
# TODO some are only booked for part of an hour and this is not accounted for.

# In order to find the % building occuoancy, first get room-building adjacency matrix
# Also get coordinates associated with each room
roomsLL=[]
delta_r_b=np.zeros([len(rooms), len(bCodes)])            
for i in range(len(rooms)):
    thisRoom=rooms[i]
    thisBld=bCodesL[roomsL.index(thisRoom)]
    if not thisBld=='0':
        indBld=bCodes.index(thisBld)
        delta_r_b[i, indBld]+=1
        roomsLL.append(bldLL[indBld])
    else:
        indBld=random.sample(range(len(bCodes)),1)[0]
        delta_r_b[i, indBld]+=1
        roomsLL.append(bldLL[indBld])
          
           
roomsPerBld=np.sum(delta_r_b, axis=0) #count rooms in each bld

occupancyByBld=np.dot(occupancyByRoom, delta_r_b)
denom= numpy.matlib.repmat(roomsPerBld,occupancyByBld.shape[0] , 1)
percentOccupancy=np.divide(occupancyByBld, denom)

percentOccupancy=np.nan_to_num(percentOccupancy)


avgWeek=[]
dayStart, dayEnd=9, 17
#get averages for monday to friday 8am to 8pm
for wkday in range(5):#monday is 0
    for hr in range(dayStart, dayEnd):
        wkdayIndices = [i for i, x in enumerate(wdays) if x == wkday]
        hrIndices = [i for i, x in enumerate(hours) if x == hr]
        indices=[ i for i in range(len(wdays)) if i in wkdayIndices and i in hrIndices]
        subset=percentOccupancy[indices,:]
        avg=np.mean(subset, axis=0).tolist()
        avgWeek.append(avg)

strTimesWeek=[dd + ' ' + str(hh+100)[1:3]+':00' for dd in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] for hh in range(dayStart, dayEnd) ]

# add the average usage statistics to the geojson
for f in range(len(blds['features'])):
    code=blds['features'][f]['properties']['buildingCo']
    if code in bCodes:
        ind=bCodes.index(code)
        blds['features'][f]['properties']['avgUsage']=[avgWeek[i][ind] for i in range(len(avgWeek))]
        

# Sharing scenario 1: each org has a home base and use other buildings as needed in order to meet all teaching requirements
# First need to get suitability of all rooms for each teaching type (as matrix)
teachTypesL=usage['teachingTypeName'].tolist()
teachTypes=list(set(teachTypesL))
teachTypes.remove('0')

roomUsageType=np.zeros([len(teachTypes), len(rooms)])
suitability=np.zeros([len(teachTypes), len(rooms)])
for i in range(len(teachTypesL)):
    if not teachTypesL[i]=='0':
        if not roomsL[i]=='0':
            k1=teachTypes.index(teachTypesL[i])
            k2=rooms.index(roomsL[i])
            roomUsageType[k1, k2]+=1 #count frequncy of each teaching type
            suitability[k1, k2]=1 #binary suitability

# find the weekly avg for each type of teaching for each dept (as matrix)
unknown=0 #keep track of unknown teaching types so the results can be scaled up appropriately
orgReqs=np.empty([len(teachTypes), len(orgs)])
for i in range(len(teachTypesL)):
    lb=max(0, lenBooking[i]) #some negative lengths in the data
    if not teachTypesL[i]=='0':
        if not orgsL[i]=='0':
            k1=teachTypes.index(teachTypesL[i])
            k2=orgs.index(orgsL[i])
            orgReqs[k1, k2]+=lb
        else:
            unknown+=lb
    else:
        unknown+=lb
factor=(np.sum(np.sum(orgReqs))+unknown)/np.sum(np.sum(orgReqs))
orgReqsCorrected=np.multiply(factor, orgReqs)     

orgReqsAvg=np.divide(orgReqsCorrected, numWeeks).astype(int)
orgHoursLeft=orgReqsAvg.copy()

# get distance between each hub and each room
# first need to get the coordinates of each hub and room in Cartesian coordinates
hubsXY=[]
roomsXY=[]
for i in range(len(HubsLL)):
    if len(HubsLL[i])>0:
        hubsXY.append(pyproj.transform(wgs84, utm35N, HubsLL[i][0], HubsLL[i][1]))
    else:
        hubsXY.append([])
for i in range(len(roomsLL)):
    if len(roomsLL[i])>0:
        roomsXY.append(pyproj.transform(wgs84, utm35N, roomsLL[i][0], roomsLL[i][1]))
    else:
        roomsXY.append([])
# create the distance matrix    
dist_Hubs_Rooms=np.empty([len(hubsXY), len(roomsXY)])
for i in range(len(hubsXY)):
    for j in range(len(roomsXY)):
        if ((len(hubsXY[i])>0)&(len(roomsXY[j])>0)):
            dist_Hubs_Rooms[i,j]=np.sqrt(np.power((hubsXY[i][0]-roomsXY[j][0]),2)+np.power((hubsXY[i][1]-roomsXY[j][1]),2))
        else:
            dist_Hubs_Rooms[i,j]=np.mean(dist_Hubs_Rooms)

# simulate a full week and in each hour:
    #each hub takes turns assigning a suitable vacant room to a randomly selected teaching purpose
    #time period ends when no more suitable rooms available  
occupancyByRoom_Adhoc=np.zeros([len(avgWeek), len(rooms)])

connections=[[] for i in range(len(avgWeek))]
doneAll=[0 for i in range(len(orgs))]
for t in range(len(avgWeek)):
    print(t)
    doneT= [0 for i in range(len(orgs))]
    c=0
    roomAvailability= [1 for i in range(len(rooms))]
    while sum(doneT)<len(doneT):
        currentOrg =c%len(orgs)
        ttList= random.sample(range(len(teachTypes)), len(teachTypes))
        turnTaken=0
        ttListInd=0
        while ttListInd<len(ttList) and turnTaken==0:
            currentTT=ttList[ttListInd]
            if orgHoursLeft[currentTT, currentOrg]>0: #if this org has any more requirement of this teaching type
                #get list of available room indices
                candidateRooms=[r for r in range(len(rooms)) if ((suitability[currentTT, r]==1)&roomAvailability[r]==1)]
                candidateDist=[dist_Hubs_Rooms[currentOrg,cr] for cr in candidateRooms]
                if len(candidateRooms)>0:
                    selectedRoom=candidateRooms[np.argmin(candidateDist)]
                    #selectedRoom=random.sample(candidateRooms,1)[0]
                    roomAvailability[selectedRoom]=0
                    orgHoursLeft[currentTT, currentOrg]-=1
                    turnTaken=1
                    occupancyByRoom_Adhoc[t, selectedRoom]+=1
#                    connections[t].append({'org': currentOrg, 'room': selectedRoom, 'teachingType': currentTT, 'origin': HubsLL[currentOrg], 'destination':roomsLL[selectedRoom]})
                    foundDuplicate=0
                    #check current list of connections to see if this one exists: is so increment it, if not create new one.
                    for i in range(len(connections[t])):
                        if ((connections[t][i]['origin']==HubsLL[currentOrg])&(connections[t][i]['destination']==roomsLL[selectedRoom])):
                            connections[t][i]['num']+=1
                            foundDuplicate=1
                    if foundDuplicate==0:
                        connections[t].append({'num':1, 'org': currentOrg, 'room': selectedRoom, 'teachingType': currentTT, 'origin': HubsLL[currentOrg], 'destination':roomsLL[selectedRoom]})
            ttListInd+=1
        if ttListInd==len(ttList):
            doneT[currentOrg]=1
        c+=1

# get the room and building occupancies based on the results of the simulation
occupancyByBld_Adhoc=np.dot(occupancyByRoom_Adhoc, delta_r_b)
denom= numpy.matlib.repmat(roomsPerBld,occupancyByBld_Adhoc.shape[0] , 1)
avgWeek_Adhoc=np.divide(occupancyByBld_Adhoc, denom)

avgWeek_Adhoc=np.nan_to_num(avgWeek_Adhoc).tolist()



#Sharing scenario 2: Adhoc sharing with double the students
# Due to the increased efficiency, a greater student population could be supported with the same buidlings
studentPopScale=1.5
orgReqsAvgX=np.multiply(studentPopScale, orgReqsAvg).astype(int)
orgHoursLeft=orgReqsAvgX.copy()

occupancyByRoom_AdhocX=np.zeros([len(avgWeek), len(rooms)])

connectionsX=[[] for i in range(len(avgWeek))]
doneAll=[0 for i in range(len(orgs))]
for t in range(len(avgWeek)):
    print(t)
    doneT= [0 for i in range(len(orgs))]
    c=0
    roomAvailability= [1 for i in range(len(rooms))]
    while sum(doneT)<len(doneT):
        currentOrg =c%len(orgs)
        ttList= random.sample(range(len(teachTypes)), len(teachTypes))
        turnTaken=0
        ttListInd=0
        while ttListInd<len(ttList) and turnTaken==0:
            currentTT=ttList[ttListInd]
            if orgHoursLeft[currentTT, currentOrg]>0: #if this org has any more requirement of this teaching type
                #get list of available room indices
                candidateRooms=[r for r in range(len(rooms)) if ((suitability[currentTT, r]==1)&roomAvailability[r]==1)]
                candidateDist=[dist_Hubs_Rooms[currentOrg,cr] for cr in candidateRooms]
                if len(candidateRooms)>0:
                    selectedRoom=candidateRooms[np.argmin(candidateDist)]
                    #selectedRoom=random.sample(candidateRooms,1)[0]
                    roomAvailability[selectedRoom]=0
                    orgHoursLeft[currentTT, currentOrg]-=1
                    turnTaken=1
                    occupancyByRoom_AdhocX[t, selectedRoom]+=1
                    foundDuplicate=0
                    #check current list of connections to see if this one exists: is so increment it, if not create new one.
                    for i in range(len(connectionsX[t])):
                        if ((connectionsX[t][i]['origin']==HubsLL[currentOrg])&(connectionsX[t][i]['destination']==roomsLL[selectedRoom])):
                            connectionsX[t][i]['num']+=1
                            foundDuplicate=1
                    if foundDuplicate==0:
                        connectionsX[t].append({'num':1, 'org': currentOrg, 'room': selectedRoom, 'teachingType': currentTT, 'origin': HubsLL[currentOrg], 'destination':roomsLL[selectedRoom]})
            ttListInd+=1
        if ttListInd==len(ttList):
            doneT[currentOrg]=1
        c+=1
#output a json: time periods: [latLon pair, 'teachingType', 'hub']
occupancyByBld_AdhocX=np.dot(occupancyByRoom_AdhocX, delta_r_b)
denom= numpy.matlib.repmat(roomsPerBld,occupancyByBld_AdhocX.shape[0] , 1)
avgWeek_AdhocX=np.divide(occupancyByBld_AdhocX, denom)

avgWeek_AdhocX=np.nan_to_num(avgWeek_AdhocX).tolist()



# add the results to the building geojson files
for f in range(len(blds['features'])):
    code=blds['features'][f]['properties']['buildingCo']
    if code in bCodes:
        ind=bCodes.index(code)
        blds['features'][f]['properties']['avgUsage_Adhoc']=[avgWeek_Adhoc[i][ind] for i in range(len(avgWeek))]
        blds['features'][f]['properties']['avgUsage_AdhocX']=[avgWeek_AdhocX[i][ind] for i in range(len(avgWeek))]
    if code in Hubs.values():
        blds['features'][f]['properties']['Hub']=1
    else:
        blds['features'][f]['properties']['Hub']=0
        
#save the results        
json.dump(blds, open('./Web/prepared/building_usage.geojson', 'w'))

json.dump({'connections_Adhoc':connections, 'connections_AdhocX':connectionsX,'times':strTimesWeek}, open('./Web/prepared/data.json', 'w'))           

