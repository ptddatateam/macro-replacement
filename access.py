import pyodbc
import pandas as pd
import os

'''This function reads and transforms access databases from the Summary of Public Transportation, so that they can be used for validation purposes'''


def build_dataframe(path, table):
    ODBC_CONN_STR = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;' %path
    conn = pyodbc.connect(ODBC_CONN_STR)
    sqlquery = 'Select * FROM {}'.format(table)
    cursor = conn.execute(sqlquery)
    expenditures = []
    for row in cursor:
        expenditures.append(row)
    names = list(map(lambda x: x[0], cursor.description))
    df = pd.DataFrame.from_records(expenditures)
    df.columns = names
    df = df.set_index('Agnc')
    return df

def assemble_dataframe(path):
    tables = ['Expenditures', 'Revenue', 'SystemData', 'SystemSummary']
    dataframelist = []
    for table in tables:
        df = build_dataframe(path, table)
        dataframelist.append(df)
    realdf = pd.concat(dataframelist, axis=1)
    return realdf

def Main(path):
    files = os.listdir(path)
    files = [file for file in files if file.endswith('.mdb') or file.endswith('.accdb')]
    for file in files:
        filename = file.replace('.mdb', '')
        filename = file.replace('.accdb', '')
        newpath = path + '\\' + file
        df = assemble_dataframe(newpath)
        df.to_csv(path + '\\'+ filename + '.csv')
if __name__ == "__main__":
    Main(r'C:\Users\SchumeN\Documents\TPS\validationfolder')
