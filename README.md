# Spatial and Temporal Metadata Generation Script

To install necessary packages for python run:
`pip install -r requirements.txt`

Then run `create_db.sh` to install the necessary postGIS enabled database and associated tables. 

The `aircraftmetadata.py` script uses flight tracks within this directory structure to populate a database that has boundingboxes, 30second, 60second, and line simplification algorithm generated flight tracks for investigation of database search metrics. The goal of this script is to read in the campaign flight tracks for multiple campaigns and produce a spatial/temporal database for investigating the best course of action for representation of in-situ data files.

Currently bounding boxes, polygons, and multi-polygons are being used to represent the in-situ metadata. It is assumed that use of a line simplification algorithm(2D and 3D) will better represent the actual location of data points more accurately without creating a drastic increase in search times for data discovery.  
