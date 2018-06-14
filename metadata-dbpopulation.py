#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 08:17:14 2017

@author: Timothy See - timothy.w.see@nasa.gov or twsee6@gmail.com
GitHub: https://github.com/twseewx/spatialtemporalmet
"""
from __future__ import print_function

import os
import pandas as pd
import numpy as np
from rdp import rdp
import re
import glob
from sqlalchemy import create_engine
from shapely.wkt import loads
from shapely.geometry import LineString, box
import re

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
            'seac4rs':'Longitude'}
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
    """
        function for creating the database connection
        using SQL Alchemy package from python
        
    """
    dbserver='localhost'
    database='spatial_db'
    dblogin='postgres'
    dbserverPort='5432'
    dbpassword='gisguest'
    engine = create_engine('postgresql+psycopg2://'+dblogin+':'+dbpassword+'@'+dbserver+':'+dbserverPort+'/'+database)
    return engine

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
        gathered using glob

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
    return coordinates
    
    


#def createRDPobjects(coordinates,eps):
#    """
#        Calls the RDP package to perform the line simplification algorithm
#
#        Parameters
#        ----------
#        arg1: matrix
#           coordinate pairs used for simplification
#        arg2: float
#           the epsilon value, which controls the resolution of the 
#           simplification - small for higher res, larger for lower res
#
#        Returns
#        -------
#        geometric object that is the simplified line
#        """
#    simplified = rdp(coordinates,epsilon = eps)
#    return simplified
    
def inserttracks(mission,date,bb,thirty,sixty,rdp2D,rdp3D):
    """
        This holds the statement for placing the flight tracks
        into the database created, it inserts the information into the 
        designated database associated with configDBengine() function above
        
        
        Parameters
        ----------
        arg1: str
            mission acronym associated with the flight
        arg2: date
            date of the flight
        arg3: geometry
            bounding box object to be placed into the database
        arg4: geometry
            every 30th datapoint of the original file as a linestring
        arg5: geometry
            every 60th datapoint of the original file as a linestring
        arg6: geometry
            the RDP line simplification algorithm output for 2dimensions
        arg7: geometry
            the RDP line simplification alrogithm output for 3dimensions
            
            
        Returns
        -------
        None
    """
            
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
        None
    """
    for file in filename:
        date = getyyyymmdd(file)
        print("Creating Flight Tracks for date: "+date)
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
        inserttracks(mission,date,boundingbox,every30thpoint,every60thpoint,rdpline2D,rdpline3D)
        print("Finished Inserting Flight Tracks for date: " +date)



engine = configDBEngine()
connection = engine.connect()
for index in np.arange(len(campaign)):
    print('Starting Campaign: '+campaign[index])
    mission = campaign[index]
    changedir(index)
    files = gatherfiles()
    lat,lon,alt,convert = getcolumns(index)
    creategeomobjects(mission,lat,lon,alt,files,convert)
    
    
