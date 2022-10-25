from nzpyida import IdaDataBase, IdaDataFrame
from nzpyida.ae import NZFunTApply,NZFunGroupedApply



nzpy_dsn ={
        "database":"housing",
         "port" :5480,
        "host" : "x.xx.xxx.xxx",
        "securityLevel":3,
        "logLevel":0
       }

idadb = IdaDataBase(nzpy_dsn, uid="admin", pwd="password")


if idadb.exists_table("properties"):
    properties_idadf =  IdaDataFrame(idadb,'properties')
if idadb.exists_table("cleaned_properties"):
    cleaned_properties_idadf =  IdaDataFrame(idadb,'cleaned_properties')

if idadb.exists_table("Public_Schools"):
    schools_idadf =  IdaDataFrame(idadb,'Public_Schools')
