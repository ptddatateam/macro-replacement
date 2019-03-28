import pandas as pd
import numpy as np
import os

def read_files(path):
    ferries = os.listdir(path)
    count = 0
    ferries = [i for i in ferries if 'xlsx' in i]
    for ferry in ferries:
        df = pd.read_excel(path + '\\'+ ferry)
        df = process_ferry_sheet(df)
        if count == 0:
            newdf = df
        else:
            newdf, df = comparedfs(newdf, df)
            newdf = pd.concat([df,newdf], axis = 0)
        count +=1
    return newdf

def comparedfs(df1, df2):
    df1columns = df1.columns.tolist()
    df2columns = df2.columns.tolist()
    missingdf1cols = [i for i in df1columns if i not in df2columns]
    for col in missingdf1cols:
        df2[col] = np.nan
    missingdf2cols = [i for i in df2columns if i not in df1columns]
    for col in missingdf2cols:
        df1[col] = np.nan
    _, i = np.unique(df1.columns, return_index=True)
    df1 = df1.iloc[:, i]
    _, i = np.unique(df2.columns, return_index=True)
    df2 = df2.iloc[:, i]
    return df1, df2

def process_ferry_sheet(df):
    df = df[df.Sheet != 'BLANK']
    agencyname = df.columns[3]
    df = df.reset_index()
    df = df.replace('-', np.nan)
    df = df.replace('X', np.nan)
    df = df.dropna(axis=0, thresh=5)
    df = df.reset_index().drop('index', axis=1)
    df = df.drop('level_0', axis=1)
    df.columns = df.loc[0].astype(str).tolist()
    df = df[df["MAIN HEADER"] != 'MAIN HEADER']
    df = df.iloc[:, 3:].reset_index().drop('index', axis=1)
    df = df.transpose()
    df.columns = df.loc['Operating Information'].tolist()
    df = df.reset_index()
    df = df.drop(0, axis=0)
    df = df.rename(columns={'index': 'year'})
    df['Agency'] = agencyname
    df.year = df.year.astype(str)
    return df


df = read_files(r'C:\Users\SchumeN\Documents\TPS\ferryvalidator\Confirmed')

print(df)