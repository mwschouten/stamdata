#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 09:20:41 2019

@author: mathijs
"""
import xlrd

import requests
import requests_cache
requests_cache.install_cache('bag_cache')

import re

def deblank(x):
    return re.sub(r'\s+', '', x)

def get_bag_location(id):
    url = 'https://bagviewer.kadaster.nl/lvbag/bag-viewer/api/bag/bevragen?objectIds='
    r = requests.get(url+id)
    if r.ok:
        data = r.json()
        xy = data[0]['geometry']['coordinates']
        return xy
    else:
        return None

class XlsxReader(object):
    
    def __init__(self,infile,lookfor=None):
        self.infile = infile
        self.lookfor = lookfor or 'AdresID'
        
        self.wb = xlrd.open_workbook(infile)
        self.sheet = self.wb.sheet_by_index(0)
        self.header = self.get_header()
        
    # find row with adresid in it:
    def get_header_row(self):
        i=0
        while self.lookfor not in [i.value for i in self.sheet.row(i)]:
            i+=1
            if i == self.sheet.nrows:
                raise(f'No row found with {self.lookfor} in it')    
        self.header_index = i
    
    def get_header(self):
        self.get_header_row()
        headers = [i.value for i in self.sheet.row(self.header_index)]
        hh = {deblank(h):i for i,h in enumerate(headers) if h}
        return hh
    
    def data(self):    
        for ir in range(self.header_index+1,self.sheet.nrows):
            row = self.sheet.row(ir)
            yield {key:row[i].value for key,i in sorted(self.header.items(),key=lambda x:x[1])}



#    
#id = '0024200000161215'
#print(id, get_bag_location(id))


infile = 'planning.xlsx'
R = XlsxReader(infile)
d = next(R.data())
xy = get_bag_location(d['AdresID'])

