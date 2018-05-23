#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 09:51:43 2018

@author: twsee
"""

import pandas as pd
import matplotlib.pyplot as plt
#from osgeo import gdal
import numpy as np
import glob
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from rdp import rdp
import os
os.chdir('/Users/twsee/Desktop/NASA/Python/aircraft-metadata-db/Flight_Tracks/intex-b-dc8')

latitude=[]
longitude=[]
file = 'discoveraq-pds_p3b_20110701_R3.ict'
header=open(file).readline().rstrip()
header = int(header.split(' ')[0])
df = pd.read_csv(file, skiprows=header-1,delim_whitespace=True)
#    df = df.replace(-9999,np.NaN)
Lat=df['FMS_LAT'].values
Lon=df['FMS_LON'].values
#    for i in Lat:
#        latitude.append(i)
#    for i in Lon:
#        longitude.append(i)
#    
#    Lat=df['Latitude'].values
#    Lon=df['Longitude'].values
coordinates = df.as_matrix(columns=['LATITUDE','LONGITUDE'])
coords = rdp(coordinates,epsilon=0.015)
m = Basemap(width=12000000,height=900000,llcrnrlat=np.min(Lat)-5.25,urcrnrlat=np.max(Lat),llcrnrlon=np.min(Lon),urcrnrlon=np.max(Lon)+20.25,projection='stere',lat_1=np.average(Lat),lat_0=np.average(Lat),lon_0=np.average(Lon),resolution='l')
m.drawcoastlines()
m.drawstates()
m.drawcountries
x,y = m(Lon,Lat)
m.fillcontinents(color='tan',lake_color='aqua')
m.drawmapboundary(fill_color='aqua')
m.plot(x,y,color='red')
plt.savefig(('intex-dc8-'+file.split('_')[2]),dpi=1000)
