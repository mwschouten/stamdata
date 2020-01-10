#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 11:02:33 2019

@author: mathijs
"""
import os
from readkmz import readKMZ

flds = ['Veld Code','Boorfirma','Boortoren/-platform','Opdrachtgever','Huidige eigenaar','Boorgatstatus','Boorgatnaam','Boorgatcode','UWI','NITG nummer','Einddatum','Startdatum','Aangeleverd stelsel','Aangeleverde Y','Aangeleverde X','Mijnbouwwerk Naam','Mijnbouwwerk Code','On offshore']

file1 = 'data/vergelijk/NLOG_Boorgaten_GCS_WGS_1984_20170112.kmz'
file2 = 'data/vergelijk/nlog_boorgaten_gcs_wgs_1984_20180710.kmz'

res1 = readKMZ(file1,verbose=False)
res2 = readKMZ(file2,verbose=False)    

pp1 = {r[0]:[r[1][f.lower()] for f in flds] for r in res1}
pp2 = {r[0]:[r[1][f.lower()] for f in flds] for r in res2}

n1 = [i[0] for i in res1]
n2 = [i[0] for i in res2]

# common

#print('{:15} : {:20} : {:>20} -> {:<20}'.format(n,f,a,b))

changed={}
changes=[]
c01 = [i for i in n1 if i in n2]
for n in c01:
    if pp1[n] != pp2[n]:
        changed[n] = (pp1[n],pp2[n])
        for f,a,b in zip(flds,pp1[n],pp2[n]):
            if a !=b:
                changes.append((n,pp1[n][4],f,a,b))

# new
d01 = [i for i in n2 if i not in n1]
print('Found {} new wells'.format(len(d01)))
print(', '.join(d01))
print()

# lost
d10 = [i for i in n1 if i not in n2]
print('Found {} lost wells'.format(len(d10)))
print(', '.join(d10))
print()


print('Detected changes    : ',len(changes))
print(' to how many wells  : ',len(Counter([i[0] for i in changes])))

