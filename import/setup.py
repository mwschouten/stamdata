#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 12:51:52 2018

@author: mathijs
"""
import os
from readkmz import readKMZ
import json

import re
from shapely.geometry import mapping


def textrounder(n):
    """ Gives you a function to round off at a fixed number of decimals 
    that works on a string: so can be used to postprocess e.g. geojson

    e.g.
        longstring = json.dumps( shapely.geometry.mapping(object) )
    
        f = textrounder(4) % ~10 m
        
        shortstring = f( longstring )

    """ 
    
    simpledec = re.compile(r"\d*\.\d+")

    roundingfrmt = "{:." + "{}".format(n) + "f}"

    def mround(match):
         return roundingfrmt.format(float(match.group()))
    
    def f(text):
        return re.sub(simpledec, mround, text)

    return f

rounder = textrounder(4)

def geo2str(geo):
    str = json.dumps(mapping(geo))
    return rounder(str)

Relaties = {'PCC' : 'Plan concerns',
            'ULI' : 'Under Licence',
            'PMH' : 'Permit holder',
            'OPR' : 'Operator',
            'WSH' : 'Well starts here',
            'WTF' : 'Well to field',
            'OWN' : 'Current owner',
            'FLD' : 'In field'}
      


vg_soorten = {'Opslagvergunning':'vg_opslag',
              'Koolwaterstoffen':'vg_winning_kws',
              'Steenzout':'vg_winning_zout'}



class NumberedItems(object):
    
    def __init__(self,yy=None):
        self.xx = []
        if yy is not None:
            for y in yy:
                self.append(y)
                
    def append(self,y):
        if y not in self.xx:
            self.xx.append(y)
    
    def getorcreate(self,y):
        try:
            return self.xx.index(y)
        except ValueError:
            self.xx.append(y)
            return len(self.xx)-1



class nlogdata(object):
    def __init__(self):
        self.objects = []
        self.info = []
        self.links = []

        self.vergunningen()
        self.velden()

    def get_object_index(self,name,otype,geostr="",bounds=[]):

        for i,item in enumerate(self.objects):
            if item[0]==name and item[1]==otype:
                return i
        self.objects.append((name,otype,geostr,bounds))
        return len(self.objects)-1



    def vergunningen(self):

        self.licence_names=[]
        
        for zoek in vg_soorten.keys():
            # READ NLOG DATA
            filename = 'data/' + [i for i in os.listdir('data') if zoek in i][0]
            res = readKMZ(filename,verbose=False)
            otype = vg_soorten[zoek]

            print ('Vergunningen - ',zoek)

            self.licence_names.extend([i[0] for i in res])
        
            for name, data, geom in res:   
     
                #vergunning object
                geostr = geo2str(geom.simplify(0.001))
                idx = self.get_object_index(name,otype,geostr,geom.bounds)
                
                # information items
                self.info.extend([(k,v,idx)  
                    for k,v in data.items()
                    if str(v) != '-'])
        
                # Make links:
                # Vergunninghouders
                vgh = [i.strip() for i in data['vergunninghouders'].split(',') if i != '-']
                for v in vgh:
                    m = self.get_object_index(v,'operator')
                    self.links.append((idx,m,'PMH'))
                    print(idx,m,name)
                
                # Operator
                name = data['uitvoerder']
                if name != '-':
                    m = self.get_object_index(name,'operator')
                    self.links.append((idx,m,'OPR'))
 
    
    def velden(self):
    
        # Velden
        filename = 'data/' + [i for i in os.listdir('data') if 'Velden' in i][0]
        res = readKMZ(filename,verbose=False)
        
        # fuzzy matching fields
        field2licence = {'Noorderdam': 'RIJSWIJK', 'Norg': 'DRENTHE IIb', 'Oldenzaal': 'TWENTHE', 'Ottoland': 'ANDEL Va', 'P09-B': 'P09c, P09e & P09f', 'P09-A': 'P09a, P09b & P09d', 'P15-11': 'P15a & P15b', 'P15-12': 'P15a & P15b', 'P15-13': 'P15a & P15b', 'P15-15': 'P15a & P15b', 'P15-09': 'P15a & P15b', 'P15-16': 'P15a & P15b', 'P15-17': 'P15a & P15b', 'P18-2': 'P18a', 'P18-4': 'P18a', 'Pernis': 'RIJSWIJK', 'Pernis-West': 'RIJSWIJK', 'Q05-A': 'Q05d', 'Q16-FA': 'Q16a', 'P15 Rijn': 'P15a & P15b', 'Rossum-Weerselo': 'ROSSUM-DE LUTTE', 'Rotterdam': 'RIJSWIJK', "'s-Gravenzande": 'RIJSWIJK', 'Saaksum': 'GRONINGEN', 'Schoonebeek Gas': 'SCHOONEBEEK', 'Sprang': 'WAALWIJK', 'Ureterp': 'GRONINGEN', 'Waalwijk-Noord': 'WAALWIJK', 'Wanneperveen': 'SCHOONEBEEK', 'IJsselmonde': 'RIJSWIJK', 'Geestvaartpolder': 'RIJSWIJK', 'Alkmaar': 'ALKMAAR', 'Andel-6 (Wijk & Aalburg)': 'ANDEL Va', 'Annerveen': 'GRONINGEN', 'B13-FA': 'B10c & B13a', 'Barendrecht': 'RIJSWIJK', 'Barendrecht-Ziedewij': 'RIJSWIJK', 'Berkel': 'RIJSWIJK', 'Brakel': 'ANDEL Va', 'Coevorden': 'SCHOONEBEEK', 'Collendoornerveen': 'SCHOONEBEEK', 'Dalen': 'SCHOONEBEEK', 'De Lier': 'RIJSWIJK', 'De Lutte': 'ROSSUM-DE LUTTE', 'De Wijk': 'SCHOONEBEEK', 'Donkerbroek - Main': 'DONKERBROEK', 'E17a-A': 'E17a & E17b', 'F03-FA': 'F03a', 'G14-A&B': 'G14 & G17b', 'G17a-S1': 'G17c & G17d', 'G17cd-A': 'G17c & G17d', 'Gaag': 'RIJSWIJK', 'Grijpskerk': 'GRONINGEN', 'Hardenberg': 'SCHOONEBEEK', 'Horizon': 'P09c, P09e & P09f', 'J03-C Unit': 'J03b & J06', 'K04-N': 'K04b & K05a', 'K05a-A': 'K04b & K05a', 'K05a-B': 'K04b & K05a', 'K05a-D': 'K04b & K05a', 'K05a-En': 'K04b & K05a', 'K05a-Es': 'K04b & K05a', 'K05-C Unit': 'K04b & K05a', 'K05-F': 'K04b & K05a', 'K05-G': 'K04b & K05a', 'K06-C': 'K06 & L07', 'K06-D': 'K06 & L07', 'K06-DN': 'K06 & L07', 'K06-G': 'K06 & L07', 'K06-N': 'K06 & L07', 'K06-T': 'K06 & L07', 'K07-FC': 'K07', 'K08-FA': 'K08 & K11a', 'K08-FC': 'K08 & K11a', 'K09ab-A': 'K09a & K09b', 'K09ab-B': 'K09a & K09b', 'K11-FB': 'K08 & K11a', 'K11-FC': 'K08 & K11a', 'K11-FA': 'K08 & K11a', 'K14-FA': 'K14a', 'K14-FB': 'K14a', 'K15-FH': 'K14a', 'Kommerzijl': 'GRONINGEN', 'L07-A': 'K06 & L07', 'L07-B': 'K06 & L07', 'L07-C': 'K06 & L07', 'L07-G': 'K09a & K09b', 'L07-H': 'K06 & L07', 'L07-H South-East': 'K06 & L07', 'L07-N': 'K06 & L07', 'L08-D': 'L11b', 'L10-CDA': 'L10 & L11a', 'L10-G': 'L10 & L11a', 'L10-K': 'L10 & L11a', 'L10-M': 'L10 & L11a', 'L10-S1': 'L10 & L11a', 'L10-S2': 'L10 & L11a', 'L10-S3': 'L10 & L11a', 'L10-S4': 'L10 & L11a', 'L11a-A': 'L10 & L11a', 'L11b-A': 'L11b', 'L11-Lark': 'L10 & L11a', 'L12a-B': 'L12b & L15b', 'L12b-C': 'L12b & L15b', 'L15b-A': 'L12b & L15b', 'Leidschendam': 'RIJSWIJK', 'Loon op Zand': 'WAALWIJK', 'Loon op Zand-Zuid': 'WAALWIJK', 'Maasdijk': 'RIJSWIJK', 'Markham': 'J03b & J06', 'Monster': 'RIJSWIJK', 'Hardenberg-Oost': 'SCHOONEBEEK', 'G14-C': 'G14 & G17b', 'P18-6': 'P18a', 'Schoonebeek Olie': 'SCHOONEBEEK', 'K09ab-C': 'K09a & K09b', 'K09ab-D': 'K09a & K09b', 'Aardgasbuffer Zuidwending': 'ZUIDWENDING', 'L10-N': 'L10 & L11a', 'Donkerbroek - West': 'DONKERBROEK', 'P15-19': 'P15a & P15b', 'L10-P': 'L10 & L11a', 'L11-Gillian': 'L11b'}
        
        for name, data, geom in res:
    
            #vergunning object
            geostr = geo2str(geom.simplify(0.001))
            self.objects.append((name,'field',geostr,geom.bounds))
            idx = len(self.objects)-1
    
    
            # Links: under licence, and operator                
            try:
                # use fuzzy match when it seemed needed, defaults to normal own
                licence_name = field2licence.get(name,data['licence area'])
                ilic = self.licence_names.index(licence_name)
            except: # Exception as ex:
                if not data['licence area'] == '-':
                    print('No licence : {} Licence: {}'.format(name,data['licence area']))
                ilic = None

            m = self.get_object_index(data['operator'],'operator')
            self.links.append((idx,m,'OPR'))
            if 'Snellius' in name:
                print('Snellius: ',idx,m,data['operator'])

            if ilic is not None:
                self.links.append((idx,ilic,'ULI'))
                            
           # information items
            self.info.extend([(k,v,idx)  
                for k,v in data.items()
                if str(v) != '-'])

    def output(self,filename='nlogdata.json'):
        data = {'objects':self.objects,
                'info':self.info,
                'links':self.links}
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)
     
    
#
#def putten(DB):
#    session = DB.Session()
#    
#    # Putten
#    filename = 'data/' + [i for i in os.listdir('data') if 'Boorgaten' in i][0]
#    res = readKMZ(filename,verbose=False)    
#      
#    ff = session.query(db.Obj).filter_by(otype='Field').all()
#    fields = {i.name:i for i in ff}    
#
# 
#    for o, data, geom in res:
#        put,created = db.get_or_create(session,db.Obj,name=o,otype='Field',wkt=geom.wkt)
#
#        # Link to field
#        fld = fields.get(data['veld naam'])
#        if fld is not None:
#            db.get_or_create(session,db.Link,lfr=put,lto=fld,ltype='FLD')   
#            
#        # Store all information fields
#        ii = [db.Info(par=k,value=v,obj=put) 
#                for k,v in data.items()
#                if str(v) is not '-']
#        session.add_all(ii)  
#    
#    session.commit()
#
#    
#    
#    
    
if __name__=="__main__":
    N = nlogdata()
    N.output()


""" NOTES

Full list of all operators:

import collections

operators = collections.defaultdict(list)
for i in session.query(db.Link).filter_by(ltype='OPR').all():
    operators[i.lto.name].append(i.lfr.name)


Show list of licences:
=======================

Match fields to their licence
    
oo = session.query(db.Obj).filter_by(otype='Koolwaterstoffen').all()
oo.extend(session.query(db.Obj).filter_by(otype='Opslagvergunning').all())

licences = [o.name for o in oo]

fld = [(n,d['licence area']) for n,d,g in res]

# Set 0: geen licence area
s0 = [i for i,l in fld if l=='-']

# Set 1 : een op een match
s1 = [i for i,l in fld if l in licences]

s1b = [i for i,l in fld if l.replace('&',',') in licences]

# Rest is more complicated
fldcomp = [f for f in fld if f[0] not in s0 and f[0] not in s1]

# Fuzzy matching
# ==============
matching={}
print ("{:>40}    < match >    {}".format('field-licence',100,'matching licence?'))
print('-'*60)
for f in fldcomp:
    m,value = process.extractOne(f[1], licences)
    if value < 80:
        print ("{:20} {:>20}    < {:>3}% >    {}".format(f[0],f[1],value,m))
    else:
        matching[f[0]] = m        
        
# Add manually confirmed looking OK
matching['P02-NE'] = 'F02a'
matching['P02-SE'] = 'F02a'
print(matching)        



Putten
======

pf = [(i,j['veld naam']) for i,j,k in res ]
  
ff = session.query(db.Obj).filter_by(otype='Field').all()
fieldnames = [i.name for i in ff]


# Set 0: geen licence area
s0 = [p for p,f in pf if f=='-']

# Set 1 : een op een match
s1 = [p for p,f in pf if f in fieldnames]

# Rest is more complicated
comp = [p for p in pf if p[0] not in s0 and p[0] not in s1]
  
compnames = [i[0] for i in comp]
Counter([j['boorgatdoel'] for i,j,k in compres])

#Wat voor putten zijn lastig:
#    
#Counter({'Aardwarmte-exploratie': 42,
#         'Exploratie koolwaterstof': 7,
#         'Ontwikkeling aardwarmtewinning': 3,
#         'Ontwikkeling koolwaterstof': 30,
#         'Ontwikkeling zoutwinning': 292,
#         'Zoutexploratie': 4})


# Welke putten hebben geen veld ('-') ? Vooral veel exploratie putten

nofld = [p for p in res if p[0] in s0]
Counter([j['boorgatdoel'] for i,j,k in nofld])

#Counter({'Aardwarmte-exploratie': 6,
#         'Evaluatie koolwaterstof': 282,
#         'Exploratie': 166,
#         'Exploratie koolwaterstof': 1334,
#         'Geologische verkenning': 47,
#         'Observatie': 27,
#         'Onbekend': 13,
#         'Ontwikkeling': 1,
#         'Ontwikkeling aardwarmtewinning': 1,
#         'Ontwikkeling grondwaterwinning': 1,
#         'Ontwikkeling koolwaterstof': 1275,
#         'Ontwikkeling koolwaterstof door injectie': 4,
#         'Ontwikkeling steenkool': 12,
#         'Ontwikkeling zoutwinning': 301,
#         'Steenkoolexploratie': 95,
#         'Zoutexploratie': 19})


Juni 2019
Missende vergunningen

No licence : P02-NE Licence: P02-1, P02a-2
No licence : P02-SE Licence: P02-1, P02a-2
No licence : P14-A Licence: P14a-1, P14a-2
No licence : Q08-A Licence: Q08
No licence : Q08-B Licence: Q08
No licence : Castricum-Zee Licence: Q08
No licence : K10-B (gas) Licence: K10a
No licence : K10-V Licence: K10b, K10c
No licence : L06d-S1 Licence: L06d


"""
