#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 08:17:14 2017

@author: Timothy See - timothy.w.see@nasa.gov or twsee6@gmail.com
GitHub: https://github.com/twseewx/spatialtemporalmet
"""
from __future__ import print_function

import os
#import mysql.connector
#from mysql.connector import errorcode
import pandas as pd
import numpy as np
from rdp import rdp
#import time as t
#import calendar
import re
import glob
from sqlalchemy import create_engine
#from geopandas import GeoDataFrame
from shapely.wkt import loads
from shapely.geometry import LineString, box
import re
#Open filename and parse down to header line number
#os.chdir('/Users/twsee/Desktop/NASA/Python/aircraft-metadata-db/Flight_Tracks/discoveraq-ca')
#files = glob.glob('*.[iI][cC][tT]')
#dbcredentialFile='~/.pgpass'
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

campaign = ['discoveraq-ca','discoveraq-co','discoveraq-md','discoveraq-tx',
             'frappe','intex-b-c130','intex-b-dc8','intex-na','seac4rs']
latitude = {'discoveraq-ca':'Latitude','discoveraq-co':' FMS_LAT',
            'discoveraq-md':'FMS_LAT','discoveraq-tx':' FMS_LAT',
            'frappe':'GGLAT','intex-b-c130':'GGLAT',
            'intex-b-dc8':'LATITUDE,','intex-na':'LATITUDE',
            'seac4rs':'Latitude'}
longitude = {'discoveraq-ca':'Longitude','discoveraq-co':' FMS_LON',
            'discoveraq-md':'FMS_LON','discoveraq-tx':' FMS_LON',
            'frappe':'GGLON','intex-b-c130':'GGLON',
            'intex-b-dc8':'LONGITUDE,','intex-na':'LONGITUDE',
            'seac4rs':'Latitude'}
altitude = {'discoveraq-ca':'Pressure_Altitude','discoveraq-co':' FMS_ALT_PRES',
            'discoveraq-md':'FMS_ALT_PRES','discoveraq-tx':' FMS_ALT_PRES',
            'frappe':'GGALT','intex-b-c130':'PALT',
            'intex-b-dc8':'ALTITUDE_PRESSURE,','intex-na':'ALTITUDE_PRESSURE',
            'seac4rs':'Pressure_Altitude'}
conversion = {'discoveraq-ca':True,'discoveraq-co':True,
            'discoveraq-md':True,'discoveraq-tx':True,
            'frappe':False,'intex-b-c130':False,
            'intex-b-dc8':False,'intex-na':False,
            'seac4rs':True}
path = '/Users/twsee/Desktop/NASA/Python/aircraft-metadata-db/Flight_Tracks/'

#function for creating a DB network connection.
def configDBEngine():
    dbserver='localhost'
    database='spatial_db'
    dblogin='postgres'
    dbserverPort='5432'
    dbPrimaryTable='flight_geometries'
    #parse password from the database credential configuration file (dbcredentialFile)
#    pgpass = pd.read_csv(dbcredentialFile,header=None,names=['dbserver','port','database','login','password'],sep=':')
#    dbpassword=pgpass.query('dbserver==\''+dbserver+'\' & login==\''+dblogin+'\'')['password'].item()
    #create sqlalchemy database connection
    engine = create_engine('postgresql+psycopg2://'+dblogin+':'+dbpassword+'@'+dbserver+':'+dbserverPort+'/'+database)
    return engine


engine = configDBEngine()




def getcolumns(index):
    """
        Gathers the associated lat,lon,alt column names

        Parameters
        ----------
        arg1: int
            index for dict referencing
        
        Returns 
        -------
        lat,lon,alt: strings
        """
    lat = latitude[campaign[index]]
    lon = longitude[campaign[index]]
    alt = altitude[campaign[index]]
    convert = conversion[campaign[index]]
    return lat,lon,alt,convert




def changedir(index):
    """
        uses an index to reference the proper path of input flight files

        Parameters
        ----------
        arg1: int
            index for dict referencing
            
        Returns
        -------
        None
        """
    os.chdir(path+campaign[index])
    return None




def gatherfiles():
    """
        Gathers the ICT files to be processed in each campaign directory

        Parameters
        ----------
        None

        Returns
        -------
        files: list
        """
    files = glob.glob('*.[iI][cC][tT]')
    return files




def getyyyymmdd(filename):
    """
        parses filename to get the year-month-day of the flight

        Parameters
        ----------
        arg1: str
           filename

        Returns
        -------
        yyyymmdd: str
        """
    yyyymmdd=filename.split('_')[2]
    return yyyymmdd




def minmaxlatlon(matrix):
    """
        gets the min/max lat/lon to create a bounding box geometric object

        Parameters
        ----------
        arg1: matrix
           2Dimensional - matrix of lat/lons for each flight

        Returns
        -------
        boundingbox: geometric object
        """
    minlat = np.nanmin(matrix[:,1])
    maxlat = np.nanmax(matrix[:,1])
    minlon = np.nanmin(matrix[:,0])
    maxlon = np.nanmax(matrix[:,0])
    print(minlat,minlon,maxlat,maxlon)
    boundingbox = box(minlon,minlat,maxlon,maxlat)
    return boundingbox




def getflagvalue(file,split):
    """
        gets flag values for representing bad data within the file

        Parameters
        ----------
        arg1: file
            filename 


        Returns
        -------
        flag: float of the dataflag
        """
    with open(file) as f:
        for i in np.arange(11):
            f.readline()
        flag = f.readline().split(split)[0]
        return float(flag)
    
    
    
    
def removeflaggeddata(coordinates,dataflag):
    """
        replaces the dataflags from getflagvalue() with np.nans then 
        removes the nans from the coordinate pairs

        Parameters
        ----------
        arg1: matrix
            coordinate(lat/lon) from the dataset
        arg2: float
            dataflag representing the value of missing data

        Returns
        -------
        coordinates with dataflags replaced then nans removed
        """
    coordinates = coordinates.replace(float(dataflag),np.NaN)
    coordinates = coordinates[~np.isnan(coordinates).any(axis=1)]
    print(np.min(coordinates))
    return coordinates
    
    


def createRDPobjects(coordinates,eps):
    """
        Calls the RDP package to perform the line simplification algorithm

        Parameters
        ----------
        arg1: matrix
           coordinate pairs used for simplification
        arg2: float
           the epsilon value, which controls the resolution of the 
           simplification - small for higher res, larger for lower res

        Returns
        -------
        geometric object that is the simplified line
        """
    simplified = rdp(coordinates,epsilon = eps)
    return simplified
    
def inserttracks(mission,date,bb,thirty,sixty,rdp2D,rdp3D):
    statement = ("INSERT INTO flight_geometries (campaign,date,boundingbox, every30points,every60points,rdp2dline,rdp3dline) VALUES ('"+str(mission)+"','"+str(date)+"',ST_GEOMFROMTEXT('"+bb+"',4326),ST_GEOMFROMTEXT('"+thirty+"',4326),ST_GEOMFROMTEXT('"+sixty+"',4326),ST_GEOMFROMTEXT('"+rdp2D+"',4326),ST_GEOMFROMTEXT('"+rdp3D+"',4326))")
    connection.execute(statement)

def creategeomobjects(mission, lat,lon,alt,filename,convert):
    """
        create the geometric objects for every30/60th points,
        rdp2D and 3D, as well as the bounding box of the flight.
        
        Parameters
        ----------
        arg1: str
            column header for latitude
        arg2: str
            column header for longitude
        arg3: str
            column header for altitude
        arg4: list
            list of all filenames with associated campaign/directory
        arg5: boolean
            True or False depending if the file needs converted from m-ft

        Returns
        -------
        geometric object that is the simplified line
        """
    for file in filename:
        date = getyyyymmdd(file)
        print(date)
        header_line=open(file).readline().rstrip()
        try:
            num_header_lines=int(header_line.split(',')[0])
            split = ','
        except:
            num_header_lines=int(header_line.split(' ')[0])
            split = ' ' 
        if split == ',':
            dataframe = pd.read_csv(file,skiprows = (num_header_lines-1))
        else:
            dataframe = pd.read_csv(file, skiprows = (num_header_lines-1),
                                    delim_whitespace=True)
        dataflag = getflagvalue(file,split)
        coords2d = dataframe[[lon,lat]]
        coords3d = dataframe[[lon,lat,alt]]
        coordinates2D = removeflaggeddata(coords2d,dataflag)
        coordinates3D = removeflaggeddata(coords3d,dataflag)
        latlon2d = coordinates2D.as_matrix(columns=[lon,lat])
        latlon3d = coordinates3D.as_matrix(columns=[lon,lat,alt])
        boundingbox = str(minmaxlatlon(latlon2d))
        every30thpoint = str(LineString(latlon2d[::30]))
        every60thpoint = str(LineString(latlon2d[::60]))
        rdp2D = rdp(latlon2d,0.015)
        rdp3D = rdp(latlon3d,0.015)
        rdpline2D = str(LineString(rdp2D))
        rdpline3D = str(LineString(rdp3D))
#        wktrdp2d = rdpline2D.wkt
#        wktrdp3d = rdpline3D.wkt
        inserttracks(mission,date,boundingbox,every30thpoint,every60thpoint,rdpline2D,rdpline3D)


# do not forget to add bounding box back in - ST_GEOMFROMTEXT('"+bb+"',4326)
# the statement greatly needs the bounding box input

engine = configDBEngine()
connection = engine.connect()
for index in np.arange(len(campaign)):
    print(campaign[index])
    mission = campaign[index]
    changedir(index)
    files = gatherfiles()
    lat,lon,alt,convert = getcolumns(index)
    creategeomobjects(mission,lat,lon,alt,files,convert)
    
    
#for filename in files:
#    collat='Latitude'
#    collon='Longitude'
#    colalt='GPS_Altitude'
#    time='Start_UTC'
#    file = str(filename)
#    splitfilename = file.split('_')
#    yyyymmdd=splitfilename[2]
#    epicSeconds=calendar.timegm(t.strptime(yyyymmdd,'%Y%m%d')) 
#    header=open(file).readline().rstrip()
#    header = int(header.split(',')[0])
#    fullres = pd.read_csv(file, skiprows=(header-1))
#    fullres = fullres.replace(-9999,np.NaN)
#    fullres[time]=fullres[time]+epicSeconds
#    fullresmet=fullres[[time,collat,collon,colalt]]
#    fullresmet['Date']=yyyymmdd
#    fullresmet['Campaign']=campaign
#    fullresmet.columns = ['Start_UTC','Latitude','Longitude','GPS_Altitude','Date','Campaign']
##    fullres[colalt] = fullres[colalt]*0.3048 #convert f to m
#    Lat=fullres[collat]
#    Lon=fullres[collon]
#    Alt=fullres[colalt]
##2D RDP simplification and representation of all columns from original DB(fullres)
#    coordinates = fullres.as_matrix(columns=[collat,collon])
#    fullresline = LineString(coordinates)
#    fullresbb = box(np.nanmin(coordinates[:,1]),np.nanmin(coordinates[:,0]),np.nanmax(coordinates[:,1]),np.nanmax(coordinates[:,0]))
#    rdpcoord = rdp(coordinates, epsilon = 0.015)
#    rdpline = LineString(rdpcoord)
#    simplifieddf = fullres.loc[fullres[collat].isin(rdpcoord[:,0]) & fullres[collon].isin(rdpcoord[:,1])]
#    noduplicatesdf = simplifieddf.drop_duplicates(collat)
#    noduplicatesdfmet=noduplicatesdf[[time,collat,collon,colalt]]
#    noduplicatesdfmet['Date']=yyyymmdd
#    noduplicatesdfmet['Campaign']=campaign
#    noduplicatesdfmet.columns = ['Start_UTC','Latitude','Longitude','GPS_Altitude','Date','Campaign']
#
#    rdplinebb = box(np.nanmin(rdpcoord[:,1]),np.nanmin(rdpcoord[:,0]),np.nanmax(rdpcoord[:,1]),np.nanmax(rdpcoord[:,0]))
##3D RDP Simplification and representation of all columns from orgiginal DB(fullres)
##Create LineString for 3D RDP, find the simplified fields and match for 
#    coord3d = fullres.as_matrix(columns=[collat,collon,colalt])
#    coord3dsimplified = rdp(coord3d, epsilon=0.015)
#    rdp3dline = LineString(coord3d)
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
