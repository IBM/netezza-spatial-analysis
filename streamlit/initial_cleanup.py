import pickle
from re import I
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from nzpyida import IdaDataBase, IdaDataFrame
from nzpyida.ae import NZFunTApply
import sklearn as sk
import sys
from connection import *


if idadb.exists_table("cleaned_properties"):
        idadb.drop_table("cleaned_properties")
      
code_cleanup_dataset = """def cleanup_dataset(self,df):
                import numpy as np
                import pandas as pd
                
                import sklearn
                import pickle
                import subprocess
                from sklearn.impute import SimpleImputer
                
                
            
                
                data = df.copy()
                                
                data = data.drop(axis =1 , columns = ['URL','REGION_URL','IMAGE_URL'])
                
                
                
               # Replacing the null values in categorical columns with the most frequent value in those particular columns
                for col in data.columns:
                                if data[col].dtype=='object':
                                    imputer = SimpleImputer(missing_values='', 
                strategy= 'most_frequent' ,fill_value='missing')
                                    data[col] = imputer.fit_transform(data[col].values.reshape(-1,1))
                
                #Dropping all the rows with null values in numerical columns as we already handled the null values in categorical columns 
                data.dropna(inplace=True)
                # #Outliers handling
                
                columns_with_outliers = ['PRICE','SQFEET','BEDS','BATHS']
                for i in columns_with_outliers:
                    column = data[i]
                    first = column.quantile(0.05)
                    third = column.quantile(0.90)
                    iqr = third - first
                    upper_limit = third + 1.5 * iqr
                    lower_limit = first - 1.5 * iqr
                    column.mask(column > upper_limit, upper_limit, inplace=True)
                    column.mask(column < lower_limit, lower_limit, inplace=True)
                
              
               
                predictions = data.copy()
                def print_output(x):
                    row = [x['ID'],x['REGION'],
                  x['PRICE'], x['TYPE'],
                    x['SQFEET'],x['BEDS'],
                    x['BATHS'],x['CATS_ALLOWED'],x['DOGS_ALLOWED'],x['SMOKING_ALLOWED'],
                    x['WHEELCHAIR_ACCESS'],x['ELECTRIC_VEHICLE_CHARGE'],
                    x['COMES_FURNISHED'],x['LAUNDRY_OPTIONS'],x['PARKING_OPTIONS'],x['LATITUDE'],x['LONGITUDE']]
                    self.output(row)
                predictions.apply(print_output, axis=1)
                
            
                
                    
"""


output_signature = {'ID':'int64','REGION':'str','PRICE':'double','TYPE':'str',
    'SQFEET':'double','BEDS':'float','BATHS':'float','CATS_ALLOWED':'int','DOGS_ALLOWED':'int',
'SMOKING_ALLOWED':'int','WHEELCHAIR_ACCESS':'int','ELECTRIC_VEHICLE_CHARGE'	: 'int','COMES_FURNISHED':'int',
'LAUNDRY_OPTIONS':'str','PARKING_OPTIONS':'str','LAT':'float','LON':'float'
    }


nz_fun_t_apply = NZFunTApply(df=properties_idadf, code_str=code_cleanup_dataset, parallel = False,fun_name ="cleanup_dataset", output_table = 'cleaned_properties',output_signature=output_signature)
result_idadf = nz_fun_t_apply.get_result()
result = result_idadf.as_dataframe()
print(result.head())

idadb.ida_query("ALTER TABLE cleaned_properties add column point st_geometry(100);")

idadb.ida_query(f'''UPDATE cleaned_properties set point=inza..ST_POINT(cleaned_properties.lon,
             cleaned_properties.lat) WHERE ID = cleaned_properties.ID;''')
idadb.ida_query('''ALTER TABLE cleaned_properties add DISTANCE_TO_SCHOOLS DOUBLE;''')
idadb.ida_query('''ALTER TABLE cleaned_properties add state_parks_count INTEGER NOT NULL DEFAULT 0;''')


#Updating the park count for each record
idadb.ida_query(f'''update cleaned_properties set cleaned_properties.state_parks_count = parks_count.count from 
(select temp.id,count(temp.c) as count from (select cleaned_properties.id,inza..ST_Intersects( 
inza..ST_WKTToSQL(inza..ST_AsText( 
inza..ST_Buffer(cleaned_properties.point 
,100,8,'mile'))) 
, national_parks.the_geom) as c from cleaned_properties,national_parks where c='True') as temp group by temp.id) as  
parks_count where parks_count.id=cleaned_properties.id;''')



#Get the national_parks_area for each record
idadb.ida_query(f'''update green_area set green_area.national_parks_area = d.sum  from( 
select f.id,SUM(f.area) as sum from (select temp.id,inza..ST_Area(inza..ST_WKTToSQL(temp.c),'mile') as area 
from (select cleaned_properties.id,inza..ST_AsText(inza..ST_Intersection( 
inza..ST_WKTToSQL(inza..ST_AsText( 
inza..ST_Buffer(cleaned_properties.point ,100,8,'mile'))) 
, national_parks.the_geom)) as c  from cleaned_properties,national_parks ) as temp  
where temp.c!='POINT EMPTY') as f group by f.id) as d where d.id = green_area.id;''') 