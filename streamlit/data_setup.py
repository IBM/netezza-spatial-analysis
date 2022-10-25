import geopandas as gpd
from connection import *



fp = "data/national_parks/ne_10m_parks_and_protected_lands_area.shp" 

data = gpd.read_file(fp) 

 

for row in data.iterrows(): 

    idadb.ida_query(f'''INSERT INTO national_parks(the_geom) VALUES (inza..ST_WKTToSQL(' {row [1] ['geometry'] } ' ))''') 

southcamp = gpd.read_file("data/SouthCamp.csv") 

southcamp = gpd.GeoDataFrame(southcamp,geometry=gpd.points_from_xy(southcamp.field_1, southcamp.field_2)) 

 

northeast = gpd.read_file("data/NortheastCamp.csv") 

northeast = gpd.GeoDataFrame(northeast,geometry=gpd.points_from_xy(northeast.field_1, northeast.field_2)) 

  

midwest = gpd.read_file("data/MidwestCamp.csv") 

midwest = gpd.GeoDataFrame(midwest,geometry=gpd.points_from_xy(midwest.field_1, midwest.field_2)) 

 

southwest = gpd.read_file("data/SouthwestCamp.csv") 

southwest = gpd.GeoDataFrame(southwest,geometry=gpd.points_from_xy(southwest.field_1, southwest.field_2)) 

 

west = gpd.read_file("data/WestCamp.csv") 

west = gpd.GeoDataFrame(west,geometry=gpd.points_from_xy(west.field_1, west.field_2)) 

 

#Creating a list of all the regions together  

parks_regions_list = [west,southcamp,midwest,northeast,southwest] 

for region in parks_regions_list: 

    for i in region.iterrows(): 

        idadb.ida_query(f'''INSERT INTO state_parks(park_point) VALUES ( 

inza..ST_WKTToSQL('{i[1]['geometry']}'))''')


#Adding point data for public_schools
idadb.ida_query('''ALTER TABLE Public_Schools ADD COLUMN POINT ST_GEOMETRY(200);''')
idadb.ida_query(f'''UPDATE Public_Schools set point=inza..ST_POINT(Public_Schools.LON, 

             Public_Schools.LAT) WHERE OBJECTID = Public_Schools.OBJECTID;''') 




