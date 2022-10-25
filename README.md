# netezza-spatial-analysis

## Installation
 


   Install the package nzpyida in a python environment on your client machine. 

   This python package allows us to interact with Netezza database, push SQL queries and custom Python analytics from client environment. 

    pip install nzpyida 

   Install INZA (any version starting from 11.2.1.0) on the Netezza server. Note that Netezza cloud instances have INZA installed by default and this step is not needed. 

 INZA is the Netezza's built-in analytics package and it offers geospatial operations through two cartridges, nzspatial and nzspatial_esri. At a time, only one of the two cartridges can be registered. For the purpose of this article, we use nzspatial_esri. 

#### Steps for cartridge installation & registration: 

(a) To check the list of cartridges installed 

    nzcm –installed   

(b)  To install the cartridge (if nzspatial_esri is not displayed in the list)  

    nzcm –install nzspatial_esri 

(c)  To register and verify the registration after the installation 

    nzcm –register nzspatial_esri 

    nzcm –verify nzspatial_esri 

 

### Install streamlit package and the custom streamlit components in the client environment 

 - Streamlit  is a python package that turns data scripts into beautiful web apps without the hassle of a server setup  

         pip install streamlit 

 

 - streamlit-option-menu is a custom streamlit component that enables multi-page applications in Streamlit. 

 	    pip install streamlit-option-menu 

 - streamlit-aggrid is a custom streamlit component that renders customizable grids. 

 	    pip install streamlit-aggrid 
      
      
      
      
 ## Uploading dataset to the netezza database
 
 
 1. Create a new database using the nzsql utility. This is where your data is going to reside. 

  (a) Connect to the ‘system’ database. 

       [nz@guayules1 ~] $ nzsql 

       Welcome to nzsql, the IBM Netezza SQL interactive terminal. 

 

       Type:  \h for help with SQL commands 

              \? for help on internal slash commands 

              \g or terminate with semicolon to execute query 

              \q to quit 

 

       SYSTEM.ADMIN(ADMIN)=> 

 

  (b)  Create the database needed using the following database command. 

       SYSTEM.ADMIN(ADMIN)=> create database HOUSING; 

       CREATE DATABASE 

 

  (c) Quit the current ‘system’ database using \q and reconnect using your newly created database. 

 

       SYSTEM.ADMIN(ADMIN)=> \q 

       [nz@guayules1 ~] $ nzsql -d housing; 

       Welcome to nzsql, the IBM Netezza SQL interactive terminal. 



       Type:  \h for help with SQL commands 

              \? for help on internal slash commands 

              \g or terminate with semicolon to execute query 

              \q to quit 

       HOUSING.ADMIN(ADMIN)=> 

 

2. Upload the dataset to the Netezza Performance Server. 

 (a) Create the table for the properties data: 

 

       HOUSING.ADMIN(ADMIN)=> create table properties(id BIGINT, url VARCHAR (300), region VARCHAR(300), region_url VARCHAR(300), price INTEGER, type VARCHAR(100), sqfeet INTEGER, beds FLOAT, baths FLOAT , cats_allowed INTEGER, dogs_allowed INTEGER, smoking_allowed INTEGER, wheelchair_access INTEGER , electric_vehicle_charge INTEGER, comes_furnished INTEGER, laundry_options VARCHAR(200), parking_options VARCHAR(300), image_url VARCHAR(300), lat DOUBLE, long DOUBLE); 

 

(b) Load the properties dataset into the properties table 

 

       nzload -df housing_train.csv -t properties -db housing -pw password -nullValue NA -boolStyle Yes_No -skipRows 1 -delim ',' 

 

       Load session of table 'PROPERTIES' completed successfully 

 

(c) Create the table for the schools data: 

       HOUSING.ADMIN(ADMIN)=> create table Public_Schools(OBJECTID BIGINT,NAME VARCHAR(300),ADDRESS VARCHAR(300),CITY VARCHAR(100),STATUS INTEGER,LAT DOUBLE,LON DOUBLE,ENROLLMENT INTEGER); 

 

(d) Load the schools dataset into public_schools table: 

       nzload -df Public_Schools.csv -t Public_Schools -db housing -pw password -nullValue NA -boolStyle Yes_No -skipRows 1 -delim ',' 

     

       Load session of table 'PUBLIC_SCHOOLS' completed successfully 

## Accessing  database tables using nzpyida: 

 

       from nzpyida import IdaDataBase, IdaDataFrame 



       dsn ={ 

               "database":"HOUSING", 

               "port" :5480, 

               "host" : "xxx", 

               "securityLevel":0, 

               "logLevel":0 

               } 

  

       idadb = IdaDataBase(dsn, uid="admin",pwd="password") 

       properties_idadf= IdaDataFrame(idadb, ‘PROPERTIES’) 

       properties_idadf.head() 
