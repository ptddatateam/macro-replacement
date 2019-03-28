import pandas as pd
import numpy as np
import sqlscripts
import pypyodbc

'''This script is a way to get and process SQL Queries so that they are immediately amenable to analytics in a variety of ways. To that end, I've made most variables on the suvey into categorical variables
replaced unanswered portions with 0s (methodologically debatable, but often necessary), and combined different layerings of historical data, at least in the output. Better layering could be done on the SQL side to avoid
such methodological problems, but this seems defendable in the immediate context (and is easy enough to change).'''


def connecttodb(sqlquery1):
    cnxn = pypyodbc.connect(driver='{SQL Server}', server = 'HQOLYMSQL09P', database = 'CTRSurvey')
    df1 = pd.read_sql_query(sqlquery1, cnxn)
    return df1


df = connecttodb(sqlscripts.whatcomworksitescript)
df.to_csv(r'C:\Users\SchumeN\Documents\I5wideningproject\whatcomctrdataraw.csv')
