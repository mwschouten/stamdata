#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 21:26:31 2019

@author: mathijs
"""

import xlrd

import os
import json
import requests
import datetime
from collections import Counter
from collections import namedtuple
from collections import defaultdict
 

flds = ['Boorgatcode','UWI','Veld Code','Boorfirma',
        'Boortoren/-platform','Boorgat / Sidetrack',
        'Opdrachtgever','Huidige eigenaar','Boorgatstatus',
        'Boorgatnaam','NITG nummer','Einddatum','Startdatum',
        'Aangeleverd Stelsel','Aangeleverde Y','Aangeleverde X',
        'Mijnbouwwerk Naam','Mijnbouwwerk Code','On offshore', 
        'Longitude WGS84','Latitude WGS84','Veld Naam']

flds_tosave = {'Boorgatcode':'Code',
               'UWI':'UWI',
               'Boorfirma':'Boorfirma',
               'Boortorenorplatform':'Boororen/platform',
               'Opdrachtgever':'Oprachtgever',
               'Huidige_eigenaar':'Huidige eigenaar',
               'Boorgatstatus':'Status',
               'Boorgatnaam':'Naam',
               'On_offshore':'Onshore/offshore', 
               'Veld_Naam':'Veld'}

def point2str(x,y):
    return f"{{'type': 'Point', 'coordinates': [{x:.5f}, {y:.5f}]}}"

def make_valid(s):
    vervang = [(' ','_'),('/','or'),('-','')]
    for i,j in vervang:
        s = s.replace(i,j)
    return s

fld_valid = [make_valid(i) for i in flds]
Put = namedtuple('Put',fld_valid)
        
def get_geobor():
    today = datetime.date.today().strftime('%Y%m%d')
    filename = 'data/geobor/geobor_{}.xls'.format(today)
    if not os.path.exists(filename):
        print('Download : ',filename)
        url = 'https://www.nlog.nl/nlog/queryAllWellLocations?menu=act&ACT_DOWNLOAD_RESULT=true&all=true'
        r = requests.get(url, allow_redirects=True)
        open(filename, 'wb').write(r.content)

    print('file: ',filename)
    return filename

def lees_putten(f):
    i_code = flds.index( 'Boorgatcode')    

    wb = xlrd.open_workbook(f)
    s = wb.sheet_by_index(0)
    hh = [i.value for i in s.row(0)]
    ii = [hh.index(f) for f in flds]
    pp = {}
    for ir in range(1,s.nrows):
        row = s.row(ir)
        data = [row[i].value for i in ii]
        pp[data[i_code]] = Put(*data)
    return pp

def get_changes(pp1,pp2):
    print('----------------------------')             
    print('Compare two date nlog geobor')
    print('----------------------------')

    i_owner = flds.index( 'Huidige eigenaar')
    
    n1 = list(pp1.keys())
    n2 = list(pp2.keys())    
    
    # common
    changed={}
    changes=[]
    c01 = [i for i in n1 if i in n2]
    for n in c01:
        if pp1[n] != pp2[n]:
            changed[n] = (pp1[n],pp2[n])
            for f,a,b in zip(flds,pp1[n],pp2[n]):
                if a !=b:
                    changes.append((n,pp1[n][i_owner],f,a,b))
    
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
    print('\nChanges:')
    for c in changes:    
        print('    {:15s} : {:25s} :: {:15} {:>20} -> {}'.format(*c))
    

def putwerkveld(pp):    
    """ make a list of [(p,w,v), ...] 
    with putnaam, mijnbouwwerk, veld
    """
    i_mbw = flds.index('Mijnbouwwerk Naam')
    i_fld = flds.index('Veld Naam')
    return [(i,j[i_mbw],j[i_fld]) 
            for i,j in pp.items() 
            if j[5]=='BRH']


# from collections import defaultdict
# from shapely.geometry import Point, MultiPoint

# q = defaultdict(list)
# for p,m,v  in pmv:
#     q[m].append(p)
    

 
#     mbw = 'Zuidwending Zoutwinning'
#     i_lon = flds.index('Longitude WGS84')
#     i_lat = flds.index('Latitude WGS84')
   
#     mp = MultiPoint([Point(pp1[p][i_lon],pp1[p][i_lat]) for p in q[mbw]])
#     g = mp.convex_hull().buffer(0.0001)
def quickcompare():
    #    Get today
    fn = get_geobor()
    pp1 = lees_putten(fn)  
#    Get another date
    pp2 = lees_putten('data/geobor/geobor_20190702.xls') 
    print('----------------------------')             
    print('Compare today to 2 juli 2019')
    print('----------------------------')
    get_changes(pp1,pp2)


def load_operators(fn = 'nlogdata.json'):
    with open(fn) as fi:
        d = json.load(fi)
    return [i[0] for i in d['objects'] if i[1]=='operator']

def load_fields(fn = 'nlogdata.json'):
    with open(fn) as fi:
        d = json.load(fi)
    return [i[0] for i in d['objects'] if i[1]=='field']

def load_fields_operators(fn = 'nlogdata.json'):
    with open(fn) as fi:
        d = json.load(fi)
    # get indices for field objects        
    fld_ind = {data[0]:i for i,data in enumerate(d['objects']) 
        if data[1]=='field'}
    # links type opr for each of the field indices
    operators = {i:d['objects'][j][0] 
                 for i,j,k in d['links'] if k=='OPR'}
    # combine
    return {i:operators[j] for i,j in fld_ind.items()}

def locs_per_operator(pp):
    aa = defaultdict(list)
    for p in pp.values():
        aa[p[7]].append(p[8])
    return aa


def geothermie(pp):
    pwv = putwerkveld(pp)
    ff2  = [i[2] for i in pwv]
    velden = [k for k in Counter([i for i in ff2 if i]).keys() if 'Geothermie' in k]
    putten = [i[0] for i in pwv if i[2] in velden]
    return velden,putten

def show_match_owners_operators(pp):            
    # Compare huidige eigenaar of wells with fields operator
    cof= [(i,j.Huidige_eigenaar,j.Veld_Naam) for i,j in pp.items()]

    fld_opr = load_fields_operators()
    compare = [(put,owner, fld_opr.get(veld,''))
                for put,owner,veld in cof 
                if veld]
    
    
    match = defaultdict(list)
    for i,j,k in compare:        
        match[j].append(k)
    
    for i,j in match.items():
        print(i,set(j))

def unknown_fields(pp):
    # not connected to a known field
    pv = [(i,j.Veld_Naam) for i,j in pp.items()]
    fields = load_fields()
    pv0 = [i for i in pv if i[1] not in fields and i[1]]
    unknown_fields = list(set(i[1] for i in pv0))
    return unknown_fields


def all_unique(data):
    return len(set(data)) == len(data)

def output(pp, filename='nlogputten.json',save=False):

    # Collect boreholes
    objects = []
    info = []
    links = []
    
    for k,v in pp.items():
        if v.Boorgat_or_Sidetrack =='BRH':

            geostr = point2str(v.Longitude_WGS84,v.Latitude_WGS84)

            bounds = [v.Longitude_WGS84,v.Latitude_WGS84,v.Longitude_WGS84,v.Latitude_WGS84]
            objects.append((k,'borehole',geostr,bounds))

            for f,d in flds_tosave.items():
                info.append((d,getattr(v,f),k))
    
            links.append((k,v.Huidige_eigenaar,'OPR'))

            if v.Veld_Naam:
                links.append((k,v.Veld_Naam,'FLD'))

            if v.Mijnbouwwerk_Naam:
                links.append((k,v.Mijnbouwwerk_Naam,'MBW'))

    data = {'objects':objects,
            'info':info,
            'links':links}
    
    print ( ' Objects : ',len(objects))
    print ( ' Info    : ',len(info))
    print ( ' Links   : ',len(links))

    if not all_unique([i[0]+i[1] for i in objects]):
        raise(Exception('Objects not all uniquely named'))
        
    if save:
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

    return data


if __name__=="__main__":

    #    Get today
    fn = get_geobor()
    pp = lees_putten(fn)

    pp2 = {i:pp[i] for i in list(pp.keys())}


    data = output(pp2,save=True)        

        














if False:
# Various checks

    # abandoned and still connected to a field?
    pv = [(i,j.Veld_Naam) for i,j in pp.items() 
            if j.Boorgatstatus == 'Abandoned' and j.Veld_Naam]




