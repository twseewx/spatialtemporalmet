#!/bin/bash

TR=`pwd`
echo "Installing required packages"

pip install -r requirements.txt

echo "Finished installing required packages"

echo "Creating database for population"

sh ./create_db.sh

echo "Finished creating database"

echo "Running python script for geometric shape creation and insertion into database"

python ${TR}/metadata-dbpopulation.py

echo "Finished populating database"



