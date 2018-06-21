# Spatial and Temporal Metadata Generation Script

Created and tested on MacOS

Operating system must have Python3 and PSQL installed, `create_db.sh` will use `pg_restore` in order to create the database for population.

A known issue is that if the `geos` package was installed with homebrew, it will cause some issues with the use of the `Shapely` package within python. 

To run the entire repo `./run.sh`

# Explanation of contents

The `aircraftmetadata.py` script uses flight tracks within this directory structure to populate a database that has boundingboxes, 30second, 60second, and line simplification algorithm(2D and 3D) generated flight tracks for investigation of database search metrics. 

The goal of this script is to read in the campaign flight tracks for multiple campaigns and produce a spatial/temporal database for investigating the best representation of in-situ data files.

Currently bounding boxes, polygons, and multi-polygons are being used to represent the in-situ metadata. It is assumed that use of a line simplification algorithm(2D and 3D) will better represent the actual location of data points more accurately without creating a drastic increase in search times for data discovery. 

In order to properly assess which of the metadata representations is best, there needs to be a robust database to conduct search comparisons on. 

# Future Necessary Work

One such type of metadata representation still needs to be created in order to properly compare the types. MultiPolygons, which were to be generated with SIPSMetGen, need to be created and populated within the database as well. A NASA ASDC confluence page was created in order to document the process for creating SIPSMetGen polygons. The page will either be shared through confluence if possible, or exported as a PDF and supplied via e-mail or within this repo. 

Creation of these MultiPolygons was in process. However, some data files failed to represent inner exclusion polygon shapes with their outer inclusion polygon shapes. The issues were never fully addressed and the SIPSMetGen software engineers should continue to be contacted in order to address the inability of some files to produce inner exclusion polygons. 

Until MultiPolygons are created and inserted into the database, the search metrics to discover which representation is best will be unable to be conducted.  
