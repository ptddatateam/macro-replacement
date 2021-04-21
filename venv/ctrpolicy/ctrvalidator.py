import pandas as pd
import numpy as np



def read_ctr_file(path):
    df = pd.read_excel(path, sheet_name = 'Worksites_CountTowardsGoal')
    df = df.reset_index()
    cols = df.loc[0].tolist()
    df.columns = cols
    df = df.loc[1:]
    return df


def employee_measures(df):
    df['Error: Total Employees greater than Surveys Distributed'] = np.nan
    index = df[df['Total Employees'] < df['Expanded Surveys Distributed']].index.tolist()
    df['Error: Employees greater than Surveys Distributed'].loc[index] = df['Error: Employees greater than Surveys Distributed'].loc[index] = True
    # checks to see that there are more employees than surveys distributed, records errors in a separate error column
    df['Error: More Surveys Returned than Distributed'] = np.nan
    index = df[df['Expanded Surveys Distributed'] < df['Expanded Surveys Returned']].index.tolist()
    df['Error: More Surveys Returned than Distributed'].loc[index] = df['Error: More Surveys Returned than Distributed'].loc[index] = True
    # checks to see if more surveys were returned than distributed
    df['Error: Response Rate Seems Off'] = np.nan
    df['Response Rate'] = df['Response Rate'].astype(float).apply(lambda x: round(x, 4))
    df['check_response_rate'] = (df['Expanded Surveys Returned'] / df['Expanded Surveys Distributed'] * 100).apply(lambda x: round(x, 4))
    index = df[df['Response Rate'] != df['check_response_rate']].index.tolist()
    df['Error: Response Rate Seems Off'].loc[index] = df['Error: Response Rate Seems Off'].loc[index] = True
    # checks response rates again to make sure reporting got it correct, checks them to four decimal places
    return df

def calculate_trips(df):
    df['sumcolumn'] = df[['Weekly Drive Alone Trips',
                          'Weekly Carpool Trips', 'Weekly Vanpool Trips',
                          'Weekly 1-Motorcycle Trips', 'Weekly 2-Motorcycle Trips',
                          'Weekly Bus Trips', 'Weekly Train/Lightrail/Street Car Trips',
                          'Weekly Bike Trips', 'Weekly Walk Trips', 'Weekly Telework Trips',
                          'Weekly CWW Days', 'Weekly Used Ferry as Walk-on Passenager',
                          'Weekly Boarded Ferry with Car/Bus/Van', 'Weekly Other Trips']].sum(axis=1).apply(lambda x: round(x, 2))
    df['Total Weekly Trips'] = df['Total Weekly Trips'].apply(lambda x: round(x, 2))
    differencesdf = df[df['Total Weekly Trips'] != df['sumcolumn']][['Total Weekly Trips', 'sumcolumn']]
    diffdf = differencesdf.iloc[:, 0] - differencesdf.iloc[:, 1]
    diffdf = pd.DataFrame(diffdf)
    diffdf = diffdf[diffdf[0] >= 1.00]
    diffdf.columns =['Error: Difference between Weekly Trips and Summed Weekly Trips:this column is the difference']
    df = pd.concat([df, diffdf], axis=1).drop('sumcolumn', axis=1)
    # checks to make sure that weekly trips and summed weekly trips are the same
    return df


def check_agg_report(df, trippercentdic):
    df = calculate_errors('NDAT Rate', ['Alone Share', 'Carpool Share',	'Van Share', 'Motorcycle Share', 'Bus Share', 'Train Share',
                                        'Bike Share', 'Walk Share',	'Tele Share', 'CWW Share', 'Used Ferry Share','Boarded Ferry Share'], df, 'Error: NDAT Rate')
    for value in trippercentdic.values():
        df = trip_percent_checker(value[0], value[1], df, value[2])
    return df



def trip_percent_checker(originaltrip, trippercentage, df, error):
    if isinstance(originaltrip, list):
        df[originaltrip] = df[originaltrip].astype(float)
        newdf = df[originaltrip]
        df['summedcol'] = newdf.sum(axis=0)
        df[['summedcol', trippercentage, 'Total Weekly Trips']] = df[['summedcol', trippercentage, 'Total Weekly Trips']].astype(float).apply(lambda x: round(x, 2))
        df['calculated percent'] = df['summedcol'] / df['Total Weekly Trips']
        df['calculated percent'] = df['calculated percent'].apply(lambda x: round(x, 2))
        try:
            diffdf = df[df[trippercentage] != df['calculated percent']['calculated percent']]
        except KeyError:
            return df.drop(['summedcol', 'calculated percent'], axis = 1)
        diffdf = differencesdf.iloc[:, 0] - differencesdf.iloc[:, 1]
        diffdf = pd.DataFrame(diffdf)
        diffdf = diffdf[diffdf[0] >= 1.00]
        diffdf.columns = [columnname]
        df = pd.concat([df, diffdf], axis=1).drop(['calculated percent', 'summedcol'], axis=1)
        return df
    df[[originaltrip, trippercentage, 'Total Weekly Trips']] = df[[originaltrip, trippercentage, 'Total Weekly Trips']].astype(float).apply(lambda x: round(x,2))
    df['calculated percent'] = df[originaltrip]/df['Total Weekly Trips']
    df['calculated percent'] = df['calculated percent'].apply(lambda x: round(x, 2))
    try:
        diffdf = df[df[trippercentage] != df['calculated percent']['calculated percent']]
    except KeyError:
        return df.drop('calculated percent', axis = 1)
    diffdf = differencesdf.iloc[:,0] - differencesdf.iloc[:, 1]
    diffdf = pd.DataFrame(diffdf)
    diffdf = diffdf[diffdf[0] >= 1.00]
    diffdf.columns = [columnname]
    df = pd.concat([df, diffdf], axis = 1).drop('calculated percent', axis = 1)
    return df


def calculate_errors(comparisonfield, originalfields, df, columnname):
    df[comparisonfield] = df[comparisonfield].astype(float)
    df[comparisonfield] = df[comparisonfield].apply(lambda x: round(x, 2))
    df['sumcolumn'] = df[originalfields].sum(axis = 1).apply(lambda x: round(x,2))
    try:
        differencesdf = df[df[comparisonfield] != df['sumcolumn'][['sumcolumn', comparisonfield]]]
    except KeyError:
        return df.drop('sumcolumn', axis = 1)
    diffdf = differencesdf.iloc[:,0] - differencesdf.iloc[:, 1]
    diffdf = pd.DataFrame(diffdf)
    diffdf = diffdf[diffdf[0] >= 1.00]
    diffdf.columns = [columnname]
    df = pd.concat([df, diffdf], axis = 1).drop('sumcolumn', axis = 1)
    return df



def build_error_df(sharelist):
    errorcolumnlist = sharelist + ['index', 'CTR Identification Code']
    newdf = pd.DataFrame(columns=errorcolumnlist)
    return newdf

def prep_df(df, cycle1, cycle2):
    df = df[df['Total Employees'] > 40]
    dfold = df[df['Survey_Cycle'] == cycle1].copy()
    dfnew = df[df['Survey_Cycle'] == cycle2].copy()
    # indexing columns
    dfold[dfold.columns[dfold.columns.str.contains('Share')]] = dfold[dfold.columns[dfold.columns.str.contains('Share')]].astype(float)
    dfnew[dfnew.columns[dfnew.columns.str.contains('Share')]] = dfnew[dfnew.columns[dfnew.columns.str.contains('Share')]].astype(float)
    # converts both dataframes to floats
    sharelist = dfnew.columns[dfnew.columns.str.contains('Share')].tolist()
    sharelist = sharelist + ['NDAT Rate']
    # builds a list of columns to investigate
    dfold["NDAT Rate"] = dfold["NDAT Rate"].apply(lambda x: x*.01)
    dfnew["NDAT Rate"] = dfnew["NDAT Rate"].apply(lambda x: x*.01)
    # converts the NDAT Rate to a decimal
    errordf = build_error_df(sharelist)
    # passes in the list of columns from the dataframe, builds a dataframe to record errors
    return dfold, dfnew, sharelist, errordf


def process_error_df(errordf, df):
    errordf = errordf.set_index('index')
    # sets the index before adding an error column in
    errordf.columns = [('Error: ' + i) for i in errordf.columns]
    # adds error to each column
    fixeddf = df.join(errordf)
    # joins the generated df to the errordf
    errorsctridcode = fixeddf[fixeddf['Error: CTR Identification Code'].notnull()]['Error: CTR Identification Code'].unique().tolist()
    fixeddf = fixeddf[fixeddf['CTR Identification Code'].isin(errorsctridcode)]
    surveys = ['2015/2016', '2017/2018']
    fixeddf = fixeddf[fixeddf['Survey_Cycle'].isin(surveys)]
    fixeddf = fixeddf.reset_index().drop('index', axis = 1)
    print(fixeddf)

    # pulls out an index for both the errors, and the previous year before, to show contrast
    # filters the df appropriately
    return fixeddf

def percent_changes(df, cycle1, cycle2):
    dfold, dfnew, sharelist, errordf = prep_df(df, cycle1, cycle2)
    # main function of which builds the errordf
    for index, row in dfnew.iterrows():
        # iterates through the rows of the current cycles dataframe
        ctridcode = row['CTR Identification Code']
        # finds the ctr id code
        merged = pd.concat([dfold[dfold['CTR Identification Code'] == ctridcode][sharelist],dfnew[dfnew['CTR Identification Code'] == ctridcode][sharelist]], axis=0)
        # concatenates the old and the new row with the same ctr id code into a dataframe, so that they can be compared
        if len(merged) < 2:
            continue
            # filters out any sites that have just been added recently or did not report for the past year
        merged = merged.reset_index().drop('index', axis=1)
        # changes the index to avoid annoying indexing issues
        changes = (merged.loc[1] - merged.loc[0])
        # records changes in absolute percent terms, yoy
        changes = pd.Series(changes)
        # turns this series into a series so that it can be appended onto something
        changes = changes.apply(lambda x: abs(x))
        # pulls the absolute value of the changes (useful for filtering purposes)
        merged = merged.append(changes, ignore_index=True)
        # appends this series to the original dataframe
        merged = merged.fillna(0.0)
        merged = merged.replace(np.inf, 0.0)
        # some maintenance issues
        checklist = merged.loc[2][merged.loc[2] > 0.15].index.tolist()
        # filters categories that have changes greater than 10% in either direction
        if checklist != []:
            index = df[(df['CTR Identification Code'] == ctridcode) & (df['Survey_Cycle'] == '2017/2018')].index
            iterate = merged[checklist].columns
            # makes a list of the columns to look over
            resultsdic = {}
            # stores the results in a resultsdic
            for i in iterate:
                # iterates through all potential errors, adds them to resultsdic, sorts them by if its an increase or a decrease
                if merged[i][0] > merged[i][1]:
                    errormessage = round(-merged[i][2], 3)
                    resultsdic[i] = errormessage
                elif merged[i][0] < merged[i][1]:
                    errormessage = round(merged[i][2], 3)
                    resultsdic[i] = errormessage
                elif (merged[i][0] == 0.000000) or (merged[i][1] == 0.000000):
                    errormessage = '{} is missing data, and this percentage increase reflects that'.format(i)
                    resultsdic[i] = errormessage
            resultsdic['CTR Identification Code'] = ctridcode
            resultsdic['index'] = index[0]
            errordf = errordf.append(resultsdic, ignore_index = True)
    errordf = process_error_df(errordf, df)
    return errordf





def main(path, cycle1, cycle2):
    df = read_ctr_file(path)
    #df = df[df['Survey_Cycle'] == cycle]
    df = percent_changes(df, cycle1, cycle2)
    #df = df.reset_index().drop('index', axis = 1)
    # df = employee_measures(df)
    #df = calculate_trips(df)
    #df['NDAT Rate'] = df['NDAT Rate'].astype(float)
    #df['NDAT Rate'] = df['NDAT Rate']*.01
    #df = check_agg_report(df, trippercentdic)
    df.to_csv(r'C:\Users\SchumeN\Documents\CTR\ctrvalidator\results.csv')



trippercentdic = {'alone':['Weekly Drive Alone Trips', 'Alone Share', 'Error: Mismatch Between Percent and Reported Alone Trips'],
                 'carpool': ['Weekly Carpool Trips', 'Carpool Share', 'Error: Mismatch btw Percent and Reported Carpool Trips'],
                  'vanpool': ['Weekly Vanpool Trips', 'Van Share', 'Error: Mismatch btw Percent and Reported Vanpool Trips'],
                  'bus': ['Weekly Bus Trips', 'Bus Share', 'Error: Mismatch btw Percent and Reported Bus Trips'],
                  'train': ['Weekly Train/Lightrail/Street Car Trips', 'Train Share', 'Error: Mismatch btw Percent and Reported Train Trips'],
                  'bike': ['Weekly Bike Trips', 'Bike Share', 'Error: Mismatch btw Percent and Reported Bike Trips'],
                  'walk': ['Weekly Walk Trips', 'Walk Share', 'Error: Mismatch btw Percent and Reported Walk Trips'],
                  'tele': ['Weekly Telework Trips', 'Tele Share', 'Error: Mismatch btw Percent and Reported Tele Work'],
                  'cww': ['Weekly CWW Days', 'CWW Share', 'Error: Mismatch btw Percent and Reported CWW'],
                  'Used Ferry': ['Weekly Used Ferry as Walk-on Passenager', 'Used Ferry Share', 'Error: Mismatch btw Percent and Reported Ferry Use'],
                  'boarded ferry': ['Weekly Boarded Ferry with Car/Bus/Van', 'Boarded Ferry Share', 'Error: Mismatch btw Percent and Reported Ferry Boardings'],
                  'motorcycle': [['Weekly 1-Motorcycle Trips', 'Weekly 2-Motorcycle Trips'], 'Motorcycle Share', 'Error Mismatch btw Percent and Reproted Motorcycle Trips'],
                  'other': ['Weekly Other Trips', 'Other Share', 'Error: Mismatch btw Percent and Reported Other Trips']
                  }






if __name__ == "__main__":
    main(r'C:\Users\SchumeN\Documents\CTR\ctrvalidator\aggreport.xlsx', '2015/2016', '2017/2018')