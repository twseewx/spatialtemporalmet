#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 09:53:01 2018

@author: twsee
"""
import pandas as pd
import glob
import os
os.chdir('/Users/twsee/Desktop/NASA/Python/aircraft-metadata-db/Flight_Tracks/discoveraq-md')
file = glob.glob('*.ict')
lat = 'FMS_LAT'
lon = 'FMS_LON'
for filename in file:
    header=open(filename).readline().rstrip()
    header = int(header.split(',')[0])
    df = pd.read_csv(filename,skiprows=(header-1))
    df =df[[lon,lat]]
    df.to_csv(filename.split('.')[0]+'.csv')