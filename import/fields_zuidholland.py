#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:49:57 2019

@author: mathijs
"""
import os
from readkmz import readKMZ
from tiles import mapaxes
import shapely


def plotbound(a,g,*args,**kwargs):
    """ Plot lines for a polygon
        a    axes to plot to
        g    geometry to plot
        add arguments to plot, e.g. color='green', lw=3
    """
    if type(g)==shapely.geometry.multipolygon.MultiPolygon:
        for i in g:
            plotbound(a,i,*args,**kwargs)
    elif type(g)==shapely.geometry.polygon.Polygon:
        x,y=g.exterior.coords.xy
        a.fill(x,y,*args,**kwargs)
    else:
        print('ERROR WRONG TYPE: ',type(g))

def fields_plot():
    filename = 'data/' + [i for i in os.listdir('data') if 'Velden' in i][0]
    res = readKMZ(filename,verbose=False)
    
    
#    w,s,e,n = 4,51.8,4.6,52.2
    w,s,e,n = 4.1,51.9,4.6,52.2
    f,a = mapaxes.mapaxes(bounds=(w,s,e,n),dpi=150,figsize=(12,12))
    
    area = shapely.geometry.Polygon(((w,s),(e,s),(e,n),(w,n)))
    for name,data,g in res :
        if g.intersects(area):
            gb = g.buffer(0.03)
            plotbound(a,gb,color='lightgreen',alpha=0.2)
            plotbound(a,g,color='g',alpha=0.5)
            x,y = g.centroid.coords.xy
            a.text(float(x[0]),float(y[0]),name)
    a.set_xlim((w,e))
    a.set_ylim((s,n))
    return f,a


if __name__=='__main__':

"""
geef de velden in zid holland weer, met een buffer van ca 2-3 km
(onhandig door lat/lon coordinaten, noord-zuid ca 3 km, oostwest 2)

plot daaarover de geothermie putten

"""
    
    
    from check_nlog import get_geobor, lees_putten        
    
    #    Get today
    fn = get_geobor()
    pp = lees_putten(fn)  
    f,a = fields_plot()        
    
    gv,gp = geothermie(pp)
    for p in gp:
        x = pp[p].Longitude_WGS84
        y = pp[p].Latitude_WGS84
        a.plot(x,y,'o',c='red',ms=10)
            
