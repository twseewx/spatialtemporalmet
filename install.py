#script to install necessary pyhton packages to populate database
#and create geometric objects

import pip


def install(package):
    pip.main(['install', package])

#currently this is not working, need to figure out pip10.0 issues with main.
if __name__ == '__main__':
    install('numpy')
    install('psycopg2>=2.5.2')
    install('sqlalchemy>=0.9.4')
    install('pandas')
    install('rdp')
    install('shapely')
    install('argparse')
    
#import os
#import mysql.connector
#from mysql.connector import errorcode
#import pandas as pd
#import numpy as np
#from rdp import rdp
#import time as t
#import calendar
#import re
#import glob
#import psycopg2
#from geoalchemy2 import Geometry, WKTElement
#from sqlalchemy import create_engine
#from geopandas import GeoDataFrame
#from shapely.geometry import Point, LineString, box
#import re