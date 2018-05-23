#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 08:17:14 2017

@author: twsee
"""
from __future__ import print_function
import os
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import numpy as np
from rdp import rdp
import time as t
import calendar
import re
import glob
import psycopg2
from geoalchemy2 import Geometry, WKTElement
from sqlalchemy import create_engine
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, box
import re
#Open filename and parse down to header line number
os.chdir('/Users/twsee/Desktop/NASA/Python/aircraft-metadata-db/Flight_Tracks/discoveraq-ca')
files = glob.glob('*.[iI][cC][tT]')
dbcredentialFile='~/.pgpass'
#dbserver='dsrvr121.larc.nasa.gov'
dbserver='localhost'
database='aircraft_gis'
#dblogin='taddev'
dblogin='postgres'
dbPrimaryTable='discoveraq_p3_pds4'
dbSecondaryTable='p3_min_seg2'
#dbserverPort='3070'
dbserverPort='5432'
#dbpassword=None
dbpassword='gisguest'
#function for creating a DB network connection.
def configDBEngine():
    #parse password from the database credential configuration file (dbcredentialFile)
#    pgpass = pd.read_csv(dbcredentialFile,header=None,names=['dbserver','port','database','login','password'],sep=':')
#    dbpassword=pgpass.query('dbserver==\''+dbserver+'\' & login==\''+dblogin+'\'')['password'].item()
    #create sqlalchemy database connection
    engine = create_engine('postgresql+psycopg2://'+dblogin+':'+dbpassword+'@'+dbserver+':'+dbserverPort+'/'+database)
    return engine
#connect to database
engine = configDBEngine()
#using pandas and glob get all 
campaign = 'discoveraq-ca'
campaignlatmin=90.0
campaignlatmax=-90.0
campaignlonmin=180.0
campaignlonmax=-180.0
for filename in files:
    collat='Latitude'
    collon='Longitude'
    colalt='GPS_Altitude'
    time='Start_UTC'
    file = str(filename)
    splitfilename = file.split('_')
    yyyymmdd=splitfilename[2]
    epicSeconds=calendar.timegm(t.strptime(yyyymmdd,'%Y%m%d')) 
    header=open(file).readline().rstrip()
    header = int(header.split(',')[0])
    fullres = pd.read_csv(file, skiprows=(header-1))
    fullres = fullres.replace(-9999,np.NaN)
    fullres[time]=fullres[time]+epicSeconds
    fullresmet=fullres[[time,collat,collon,colalt]]
    fullresmet['Date']=yyyymmdd
    fullresmet['Campaign']=campaign
    fullresmet.columns = ['Start_UTC','Latitude','Longitude','GPS_Altitude','Date','Campaign']
#    fullres[colalt] = fullres[colalt]*0.3048 #convert f to m
    Lat=fullres[collat]
    Lon=fullres[collon]
    Alt=fullres[colalt]
#2D RDP simplification and representation of all columns from original DB(fullres)
    coordinates = fullres.as_matrix(columns=[collat,collon])
    fullresline = LineString(coordinates)
    fullresbb = box(np.nanmin(coordinates[:,1]),np.nanmin(coordinates[:,0]),np.nanmax(coordinates[:,1]),np.nanmax(coordinates[:,0]))
    rdpcoord = rdp(coordinates, epsilon = 0.015)
    rdpline = LineString(rdpcoord)
    simplifieddf = fullres.loc[fullres[collat].isin(rdpcoord[:,0]) & fullres[collon].isin(rdpcoord[:,1])]
    noduplicatesdf = simplifieddf.drop_duplicates(collat)
    noduplicatesdfmet=noduplicatesdf[[time,collat,collon,colalt]]
    noduplicatesdfmet['Date']=yyyymmdd
    noduplicatesdfmet['Campaign']=campaign
    noduplicatesdfmet.columns = ['Start_UTC','Latitude','Longitude','GPS_Altitude','Date','Campaign']

    rdplinebb = box(np.nanmin(rdpcoord[:,1]),np.nanmin(rdpcoord[:,0]),np.nanmax(rdpcoord[:,1]),np.nanmax(rdpcoord[:,0]))
#3D RDP Simplification and representation of all columns from orgiginal DB(fullres)
#Create LineString for 3D RDP, find the simplified fields and match for 
    coord3d = fullres.as_matrix(columns=[collat,collon,colalt])
    coord3dsimplified = rdp(coord3d, epsilon=0.015)
    rdp3dline = LineString(coord3d)
#    simplified3ddf = fullres.loc[fullres[collat].isin(coord3dsimplified[:,0]) & fullres[collon].isin(coord3dsimplified[:,1]) & fullres[colalt].isin(coord3dsimplified[:,2])]
#    simplified3ddfmet=simplified3ddf[[time,collat,collon,colalt]]
#    simplified3ddfmet['Date']=yyyymmdd
#    simplified3ddfmet['Campaign']=campaign
#    simplified3ddfmet.columns = ['Start_UTC','Latitude','Longitude','GPS_Altitude','Date','Campaign']
#    rdp3dlinebb = box(np.nanmin(coord3dsimplified[:,1]),np.nanmin(coord3dsimplified[:,0]),np.nanmax(coord3dsimplified[:,1]),np.nanmax(coord3dsimplified[:,0]))
#    
##every 30th point representation, create LineString, create just metadata fields
#    every30thpoint = fullres.iloc[::30,:]
#    every30coord = every30thpoint.as_matrix(columns=[collat,collon])
#    every30line = LineString(every30coord)
#    every30thpointmet=every30thpoint[[time,collat,collon,colalt]]
#    every30thpointmet['Date']=yyyymmdd
#    every30thpointmet['Campaign']=campaign
#    every30thpointmet.columns = ['Start_UTC','Latitude','Longitude','GPS_Altitude','Date','Campaign']
#    every30linebb = box(np.nanmin(every30coord[:,1]),np.nanmin(every30coord[:,0]),np.nanmax(every30coord[:,1]),np.nanmax(every30coord[:,0]))
##every 60th point representation, create linestring, create just metadata fields
#    every60thpoint = fullres.iloc[::60,:]
#    every60coord = every60thpoint.as_matrix(columns=[collat,collon])
#    every60line = LineString(every60coord)
#    every60thpointmet = every60thpoint[[time,collat,collon,colalt]]
#    every60thpointmet['Date']=yyyymmdd
#    every60thpointmet['Campaign']=campaign
#    every60thpointmet.columns = ['Start_UTC','Latitude','Longitude','GPS_Altitude','Date','Campaign']
#    every60linebb = box(np.nanmin(every60coord[:,1]),np.nanmin(every60coord[:,0]),np.nanmax(every60coord[:,1]),np.nanmax(every60coord[:,0]))
#    wkbdata = {'Campaign':[campaign],
#            'Date':[yyyymmdd],
#            'FullRes':[fullresline.wkb],
#            'FullRes-BB':[fullresbb.wkb],
#            'Every30Points':[every30line.wkb],
#            'Every30Points-BB':[every30linebb.wkb],
#            'Every60Points':[every60line.wkb],
#            'Every60Points-BB':[every60linebb.wkb],
#            'Rdp2DLine':[rdpline.wkb],
#            'Rdp2DLine-BB':[rdplinebb.wkb],
#            'Rdp3DLine':[rdp3dline.wkb],
#            'Rdp3DLine-BB':[rdp3dlinebb.wkb]}
#    geomdata = {'Campaign':[campaign],
#            'Date':[yyyymmdd],
#            'FullRes':[fullresline.wkt],
#            'FullRes-BB':[fullresbb.wkt],
#            'Every30Points':[every30line.wkt],
#            'Every30Points-BB':[every30linebb.wkt],
#            'Every60Points':[every60line.wkt],
#            'Every60Points-BB':[every60linebb.wkt],
#            'Rdp2DLine':[rdpline.wkt],
#            'Rdp2DLine-BB':[rdplinebb.wkt],
#            'Rdp3DLine':[rdp3dline.wkt],
#            'Rdp3DLine-BB':[rdp3dlinebb.wkt]}
#    wkbdataframe = pd.DataFrame(wkbdata, index=None)
#    geomdataframe = pd.DataFrame(geomdata, index=None)
##print statement to denote what file is being worked on.
#    if np.nanmin(fullres[collat]) < campaignlatmin:
#        campaignlatmin = np.nanmin(fullres[collat])
#    if np.nanmax(fullres[collat]) > campaignlatmax:
#        campaignlatmax = np.nanmax(fullres[collat])
#    if np.nanmin(fullres[collon]) < campaignlonmin:
#        campaignlonmin = np.nanmin(fullres[collon])
#    if np.nanmax(fullres[collon]) > campaignlonmax:
#        campaignlonmax = np.nanmax(fullres[collon])
#    print(filename)
    
    
##TODO - figure out how to get the lines into the database and make sure
##TODO - that they are in proper representation, seems like using GIS commands
##TODO - in a postgis sql database is the best course of action.
## Section below writes the data structures for each of the full res/30/60/2D/3D 
## data with the associated original data for each simplified point.
    
#    fullres.to_sql((splitfilename[0]+'-'+splitfilename[1]+'-'+'fullres'),engine,if_exists='append',index=False)
#    noduplicatesdf.to_sql((splitfilename[0]+'-'+splitfilename[1]+'-'+'2dsimplified'),engine,if_exists='append',index=False)
#    simplified3ddf.to_sql((splitfilename[0]+'-'+splitfilename[1]+'-'+'3dsimplified'),engine,if_exists='append',index=False)
#    every30thpoint.to_sql((splitfilename[0]+'-'+splitfilename[1]+'-'+'every30thpoint'),engine,if_exists='append',index=False)
#    every60thpoint.to_sql((splitfilename[0]+'-'+splitfilename[1]+'-'+'every60thpoint'),engine,if_exists='append',index=False)
    
## Writes the well known binary and well known text geometry types to 
## the SQL database.
#    wkbdataframe.to_sql(('p3b_daily_flight_track_wkb'),engine,if_exists='append',index=False)
#    geomdataframe.to_sql(('p3b_daily_flight_track_geom'),engine,if_exists='append',index=False)
    
#TODO - Get geom represented as linestring within the database, it will not let me populate
#TODO with the linstring currently (20180109)
    
#THis populates the database with only associated metadata fields not all fields withint he nav datafile
#    fullresmet.to_sql(('campaign-fullres-metadata'),engine,if_exists='append',index=False)
#    noduplicatesdfmet.to_sql(('campaign-2dsimplified-metadata'),engine,if_exists='append',index=False)
#    simplified3ddfmet.to_sql(('campaign-3dsimplified-metadata'),engine,if_exists='append',index=False)
#    every30thpointmet.to_sql(('campaign-every30thpoint-metadata'),engine,if_exists='append',index=False)
#    every60thpointmet.to_sql(('campaign-every60thpoint-metadata'),engine,if_exists='append',index=False)
