# Dashboard - Evertrack Version Monitor 
Dashboard to monitor Evertrack version on company hostnames

## Features
the page contains:
a bar chart with the number of hosts per version, filtered by company;
a bar chart with the quantity of hosts per company, filtered by version;
a table with the raw data extracted from SQLServer, with each host found version.

## Requirements 
Python 3.*
Pandas, Pyodbc, Python-Dotenv


## Setup 
in order to use the html page, you must create a .env file in the project root, with the following variables:

DB_SERVER=server IP
DB_NAME=Database name
DB_USER=Database User login
DB_PASS=Database User Password
OUTPUT_PATH=Output json data file path
QUERY_PATH=Input SQL Query file 

## Usage
Run the get_data.py to generate the data.json, this json will feed the charts  
