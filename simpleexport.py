import pandas as pd
import sqlscripts
import pypyodbc

def connecttodb(sqlquery):
    cnxn = pypyodbc.connect(driver='{SQL Server}', server = 'HQOLYMSQL09P', database = 'CTRSurvey')
    df1 = pd.read_sql_query(sqlquery, cnxn)
    return df1

df = connecttodb(sqlscripts.sqlscript3)
print(df.head())
df.to_csv(r'C:\Users\SchumeN\Documents\CTR\ctrgeography\worksitedata.csv')
