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
    try:
        df = df[df.Sheet != 'BLANK']
    except:
        pass
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
    print(df['Agency'])
    df.year = df.year.astype(str)
    return df

def range_validator(df, column1, column2, type):
    if df[column1].isna().any() == True or df[column2].isna().any() == True:
        return False
    else:
        column1list = df[column1].tolist()
        column2list = df[column2].tolist()
        year1value = column1list[0]/column2list[0]
        year2value = column1list[1]/column2list[1]
        change = (year2value/year1value) - 1
        if change < -.1:
            return '{} is out of range from last year\'s numbers, having decreased by ten percent or more. Please revise {}: {} or {}: {}, or explain the change'.format(type, column1, column1list[1], column2,column2list[1])
        elif change > .1:
            return '{} is out of range from last year\'s numbers, having increased by ten percent or more. Please revise {}: {} or {}: {}, or explain the change'.format(type, column1, column1list[1], column2,column2list[1])
        else:
            return False

def check(errorlist, inputx):
    if inputx != False:
        errorlist.append(inputx)
    return errorlist

def fuel_check(xdf):
    xdf['BioDiesel Fuel Consumed (gallons)'] = xdf['BioDiesel Fuel Consumed (gallons)'].fillna(0.0)
    xdf['Diesel Fuel Consumed (gallons)'] = xdf['Diesel Fuel Consumed (gallons)'].fillna(0.0)
    xdf['fuel'] = xdf['Diesel Fuel Consumed (gallons)'] + xdf['BioDiesel Fuel Consumed (gallons)']
    return xdf

def validation_errors(df, year1, year2):
    agencies = list(df.Agency.unique())
    errordic = {}
    for agency in agencies:
        errorlist = []
        xdf =df[df.Agency == agency]
        xdf.year = xdf.year.astype(str)
        xdf = xdf[xdf.year.isin([year1, year2])]
        xdf = xdf.replace(0.0, np.nan)
        rvs = range_validator(xdf, 'Revenue Vessel Miles ', 'Revenue Vessel Hours', 'Revenue Vessel Speed')
        errorlist = check(errorlist, rvs)
        costperrevenuemile = range_validator(xdf, 'Operating Expenses', 'Revenue Vessel Miles ', 'Costs per Revenue Mile')
        errorlist = check(errorlist, costperrevenuemile)
        costsperrevenuehour = range_validator(xdf, 'Operating Expenses', 'Revenue Vessel Hours', 'Costs per Revenue Hour')
        errorlist = check(errorlist, costsperrevenuehour)
        fareboxrevenuesperpassengertrip = range_validator(xdf, 'Farebox Revenues (Passenger, Auto & Driver Fares)', 'Passenger Trips', 'Farebox Revenues per Passenger Trip')
        errorlist = check(errorlist, fareboxrevenuesperpassengertrip)
        revenuemilesperpassengertrip = range_validator(xdf, 'Revenue Vessel Miles ', 'Passenger Trips', 'Revenue Miles per Passenger Trip')
        errorlist = check(errorlist, revenuemilesperpassengertrip)
        xdf = fuel_check(xdf)
        milespergallon = range_validator(xdf, 'Revenue Vessel Miles ', 'fuel', 'Revenue Miles per Gallon')
        errorlist = check(errorlist, milespergallon)
        errordic[agency] = errorlist
    df = pd.DataFrame({key: pd.Series(val) for key, val in errordic.items()})
    return df


df = read_files(r'I:\Public_Transportation\Data_Team\PT_Summary\2017\Ferries\Received_Sheets')
df.to_csv(r'I:\Public_Transportation\Data_Team\PT_Summary\2017\Ferries\Received_Sheets\Validation\ferrydata.csv')

#df = pd.read_csv(r'C:\Users\SchumeN\Documents\TPS\ferryvalidator\Confirmed\ferrydata.csv')
df = validation_errors(df, '2016.0', '2017.0')
df.to_csv(r'I:\Public_Transportation\Data_Team\PT_Summary\2017\Ferries\Received_Sheets\Validation\ferryerrors.csv')

