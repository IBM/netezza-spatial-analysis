from connection import *
import pandas as pd
import numpy as np

def get_matching_records(features_list):
    rows = cleaned_properties_idadf.ida_query('''SELECT ID,PRICE,REGION,BEDS,BATHS,SQFEET,CATS_ALLOWED,DOGS_ALLOWED, SMOKING_ALLOWED,WHEELCHAIR_ACCESS, ELECTRIC_VEHICLE_CHARGE,COMES_FURNISHED,
    LAT as "lat" , LON as "lon" FROM cleaned_properties 
                                        WHERE BEDS>={0} AND BATHS>={1} AND SQFEET>={2} AND CATS_ALLOWED >={3} 
                                        AND DOGS_ALLOWED >={4} AND SMOKING_ALLOWED>={5} AND WHEELCHAIR_ACCESS >={6}
                                         AND ELECTRIC_VEHICLE_CHARGE >= {7}
                                        AND COMES_FURNISHED>={8} ;  
                            '''
                            .format(features_list['beds'],features_list['baths'],features_list['sqfeet'],
                            features_list['cats'],features_list['dogs'],features_list['Smoking Allowed'],features_list['Wheel-Chair Access'],
                            features_list['Electric-vehicle charging'],features_list['Furnished Apartment'],
                            features_list['Laundry'],features_list['Garage parking']))
    return rows

def get_range_of_values(column):
    max_value = cleaned_properties_idadf.ida_query('SELECT MAX({}) FROM cleaned_properties'.format(column))
    min_value = cleaned_properties_idadf.ida_query('SELECT MIN({}) FROM cleaned_properties'.format(column))
    return max_value,min_value


def get_all_records():
    rows = cleaned_properties_idadf.ida_query('''SELECT * FROM predictions;''')
    return rows


def get_houses_in_the_area(record_id,buffer_miles):
    try:
        #User selects a record 
        record_selected_by_user = cleaned_properties_idadf.ida_query(f'''SELECT inza..ST_AsText(POINT) 
                            as POINT,REGION,PRICE from cleaned_properties where id = {record_id}''')
        print(record_selected_by_user['POINT'][0])

        #Getting the buffer region around the specified point 

        buffer_region = cleaned_properties_idadf.ida_query(f'''SELECT inza..ST_AsText(inza..ST_Buffer 

        (inza..ST_WKTToSQL('{record_selected_by_user['POINT'][0]}') 

        ,{buffer_miles},8,'mile'))''') 
        properties_within_distance = cleaned_properties_idadf.ida_query(f'''SELECT price from cleaned_properties where inza..ST_Contains( 

        inza..ST_WKTToSQL('{buffer_region[0]}'),inza..ST_WKTToSQL(inza..ST_AsText(cleaned_properties.point)) 

        );''') 

        summary_list = [max(properties_within_distance),min(properties_within_distance),np.mean(properties_within_distance)]

        properties_list = idadb.ida_query(f'''SELECT * from 		cleaned_properties where 

region='{record_selected_by_user['REGION'][0]}'  

and PRICE BETWEEN {min(properties_within_distance)} and { 

max(properties_within_distance)} ''') 
        
        return summary_list,properties_list
    
    except:
        return 'Statistics for the region could not be found'


def get_discounted_houses(record_id):

    try:
        #User selects a record 
        record_selected_by_user = cleaned_properties_idadf.ida_query(f'''SELECT inza..ST_AsText(POINT) as POINT,REGION,
                                                PRICE from cleaned_properties where id = {record_id}''')

        #Get all the records where it is lower than the discounted price.
        selected_house_price = record_selected_by_user['PRICE'][0]
        discount = 10

        final_price = selected_house_price*(1-(discount/100))

        #Calculate distances between properties display all the records matching the condition

        final_houses_with_discounted_prices = idadb.ida_query(f'''select temp.id,temp.price,temp.distance_between_properties,temp.region,
        temp.beds,temp.baths,temp.sqfeet,temp.cats_allowed,temp.dogs_allowed,temp.smoking_allowed,temp.wheelchair_access,temp.electric_vehicle_charge,
        temp.comes_furnished
         from  ( select cleaned_properties.*,inza..ST_Distance(
                            inza..ST_Transform(inza..ST_WKTToSQL(inza..ST_AsText(cleaned_properties.point)), 4326), 
                            inza..ST_Transform(inza..ST_WKTToSQL('{record_selected_by_user['POINT'][0]}'),4326), 'mile')as 
                            distance_between_properties from cleaned_properties) as temp 
                            where temp.price<={final_price} and temp.distance_between_properties<5 order by temp.distance_between_properties;''')


        return final_houses_with_discounted_prices
    except:
        return 'No houses found nearby at a discount'

    
def get_green_area(record_id):
    try:
        record_selected_by_user =  cleaned_properties_idadf.ida_query(f'''SELECT inza..ST_AsText(POINT) as POINT,REGION from cleaned_properties where id = {record_id} ''')
        
        #Getting the properties in the same region ordered by national_parks_area and park_count
        ranked_properties = cleaned_properties_idadf.ida_query(f'''select green_area.national_parks_area,temp.state_parks_count,temp.ID,
        temp.PRICE,temp.REGION,temp.BEDS,temp.BATHS,temp.SQFEET,temp.CATS_ALLOWED,temp.DOGS_ALLOWED, temp.SMOKING_ALLOWED,temp.WHEELCHAIR_ACCESS, 
        temp.ELECTRIC_VEHICLE_CHARGE,temp.COMES_FURNISHED,temp.LAT as "lat" , temp.LON as "lon"  from (SELECT * from cleaned_properties where 
                                        cleaned_properties.region ='{record_selected_by_user['REGION'][0]}') as temp inner join green_area
                                        on green_area.id = temp.id 
                                        order by state_parks_count desc,national_parks_area desc;''')

        green_information = [200,ranked_properties]

        return green_information
    except:
        return [404,'Unknown error happened! Green information could not be found, please try again..']