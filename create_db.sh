#!/bin/bash
# code to generate the spatial_db, it wil remove
# databases with the same name to create a new database
# this is a destructive file i.e. will drop/create DB
DB=spatial_db
DBUSER=postgres
mkdb(){

	dbname=${1}
	isWithPostGIS=${2}
	user=${3}
	echo "$0: DROP/CREATE ${dbname}"

	dropdb ${dbname} 2>/dev/null
	createdb ${dbname} \
		&& ${isWithPostGIS} && psql ${dbname} -c "create extension postgis;" || true \
		&& pg_restore -U ${user} --no-acl --no-owner -d ${dbname} < ${dbname}.sql

}
mkdb ${DB} true ${DBUSER} 

