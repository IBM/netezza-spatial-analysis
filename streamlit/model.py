import pickle
from re import I
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from nzpyida import IdaDataBase, IdaDataFrame
from nzpyida.ae import NZFunGroupedApply
import sklearn as sk
import sys
from connection import *







if idadb.exists_table("predictions"):
        idadb.drop_table("predictions")

idadb.ida_query('''update cleaned_properties set cleaned_properties.distance_to_schools = temp.distance_to_schools 
                                from (select cleaned_properties.id,MIN(inza..ST_DISTANCE(
                                inza..ST_Transform(cleaned_properties.point, 4326), 
                                inza..ST_Transform(Public_Schools.point,4326),
                                'mile')) as distance_to_schools from Public_Schools,cleaned_properties 
                                where cleaned_properties.REGION = LOWER(Public_Schools.CITY)
                                GROUP BY cleaned_properties.id) as temp
                                where temp.id = cleaned_properties.id; ''')




code_house_prediction_model = """def house_prediction_model(self,df):
                import numpy as np
                import pandas as pd
                
                import sklearn
                import pickle
                import subprocess
                
                from sklearn.model_selection import cross_val_score
                from sklearn.model_selection import train_test_split
                from sklearn.linear_model import LinearRegression
                from sklearn.ensemble import GradientBoostingRegressor
                # from xgboost import XGBRegressor
                from sklearn.preprocessing import LabelEncoder
                from sklearn.metrics import r2_score,mean_squared_error
                
            
                
                data = df.copy()
                
                

                data['DISTANCE_TO_SCHOOLS'] = data['DISTANCE_TO_SCHOOLS'].replace(to_replace = 0 , value = 10000)
                data['DISTANCE_TO_SCHOOLS'] = data['DISTANCE_TO_SCHOOLS']/data['DISTANCE_TO_SCHOOLS'].abs().max()
            
                encoder={}
                categorical_columns_list = []
                for i in data.columns:
                    if data[i].dtype == 'object':
                        categorical_columns_list.append(i)
                        encoder[i] = LabelEncoder()
                        encoder[i].fit(list(data[i].values))
                        data[i] = encoder[i].transform(list(data[i].values))
                
                
                #Splitting into training and testing dataset
                
                y = data['PRICE']
                X = data.drop(columns=['PRICE'],axis=1)
                
                X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.20 , train_size = 0.80, random_state=100)
                
        
                
                #Gradient Boosting Regression
                from sklearn.ensemble import GradientBoostingRegressor
                
                gbr = GradientBoostingRegressor()
                gbr.fit(X_train, y_train)
                y_pred_gbr= gbr.predict(X_test)
                y_pred_gbr = np.around(y_pred_gbr,decimals=0)
                r2_score = gbr.score(X_test,y_test)
                
                
                from sklearn.model_selection import cross_val_score
                cv_scores = np.sqrt(-cross_val_score(gbr, X, y,scoring='neg_mean_squared_error',cv=2))
                final_score = (np.mean(cv_scores/y.max()))
                
                predictions = X_test.copy()
                
                for column in categorical_columns_list:   
                    predictions[column] = encoder[column].inverse_transform(list(predictions[column].values))
                
                predictions['PRICE_PREDICTED'] = y_pred_gbr
                predictions['ACCURACY'] = r2_score
                def print_output(x):
                    row = [x['ID'],x['REGION'],
                   x['TYPE'],x['PRICE_PREDICTED'],
                    x['SQFEET'],x['BEDS'],
                    x['BATHS'],x['CATS_ALLOWED'],x['DOGS_ALLOWED'],x['SMOKING_ALLOWED'],
                    x['WHEELCHAIR_ACCESS'],x['ELECTRIC_VEHICLE_CHARGE'],
                    x['COMES_FURNISHED'],x['LAUNDRY_OPTIONS'],x['PARKING_OPTIONS'],x['DISTANCE_TO_SCHOOLS'],x['ACCURACY']]
                    self.output(row)
                predictions.apply(print_output, axis=1)
                
            
                pickle.dump(gbr, open('/export/home/nz/git_repo/models-repo/model.pkl','wb'))
                
                    
"""


output_signature = {'ID':'int64','REGION':'str','TYPE':'str','PRICE_PREDICTED':'double',
    'SQFEET':'double','BEDS':'float','BATHS':'float','CATS_ALLOWED':'int','DOGS_ALLOWED':'int',
'SMOKING_ALLOWED':'int','WHEELCHAIR_ACCESS':'int','ELECTRIC_VEHICLE_CHARGE'	: 'int','COMES_FURNISHED':'int',
'LAUNDRY_OPTIONS':'str','PARKING_OPTIONS':'str','DISTANCE_TO_SCHOOLS':'double','ACCURACY':'double'
    }


nz_fun_grouped_apply = NZFunGroupedApply(df=cleaned_properties_idadf, columns = ['ID','REGION','TYPE','SQFEET','PRICE','BEDS','BATHS','CATS_ALLOWED','DOGS_ALLOWED'
,'SMOKING_ALLOWED','WHEELCHAIR_ACCESS','ELECTRIC_VEHICLE_CHARGE','COMES_FURNISHED','LAUNDRY_OPTIONS','PARKING_OPTIONS','DISTANCE_TO_SCHOOLS'],code_str=code_house_prediction_model, index='REGION',fun_name ="house_prediction_model", output_table='predictions',output_signature=output_signature)
result_idadf = nz_fun_grouped_apply.get_result()
result = result_idadf.as_dataframe()
print(result)



