import pandas as pd
import numpy as np
import os
from collections import defaultdict

def read_files(path, dictionaryreaderpath):
    df2014 = pd.read_excel(path + '\\' + '2017data.xlsx')
    df2013 = pd.read_excel(path + '\\' + '2016data.xlsx')
    dic =  pd.read_excel(dictionaryreaderpath + '\\' + 'dictionarygenerator.xlsx')
    abbreviationdic = dict(zip(dic.Abbreviation, dic.Name))
    required = dic.Abbreviation.tolist()
    dflist = []
    dflist.append(df2013)
    dflist.append(df2014)
    return dflist, abbreviationdic

def validation(dflist, abbreviationdic):
    # defaults to comparing the last two years
    dflist = dflist[:2]
    df1 = dflist[0]
    df2 = dflist[1]
    agencies = df1.Agency.tolist()
    dicValidationErrors = {}
    result = {}
    for agency in agencies:
        # skip some things that are specifically unique to this dataset--will add to them as we get more tribes
        skiplist = ['Cowlitz Indian Tribe', 'Makah Nation', 'Quinault Indian Nation','Stillaguamish Tribe of Indians', 'Testing agency']
        if agency in skiplist:
            continue
        joineddf = agency_selector(agency, df1, df2)
        if len(joineddf) == 1:
            continue
        fuels = fuel_efficiency(agency, df1, df2, abbreviationdic)
        dicValidationErrors, result = check(fuels, dicValidationErrors, result)
        values = missing_values(agency, df1, df2, abbreviationdic)
        dicValidationErrors, result = check(values, dicValidationErrors, result)
        speed = range_validation(agency, df1, df2, abbreviationdic, 'rvm', 'rvh', 'Vehicle Revenue Speed')
        dicValidationErrors, result = check(speed, dicValidationErrors, result)
        ptperrm =range_validation(agency, df1, df2, abbreviationdic, 'psgr', 'rvm', 'Passenger Trips per Revenue Mile')
        dicValidationErrors, result = check(ptperrm, dicValidationErrors, result)
        cprevmi = range_validation(agency, df1, df2, abbreviationdic, 'oex', 'rvm', 'Costs per Revenue Mile')
        dicValidationErrors, result = check(cprevmi, dicValidationErrors, result)
        cprevhr = range_validation(agency, df1, df2, abbreviationdic, 'oex', 'rvh', 'Costs per Revenue Hour')
        dicValidationErrors, result = check(cprevhr, dicValidationErrors, result)
        vrhperfte = range_validation(agency, df1, df2, abbreviationdic, 'rvh', 'fte', 'Vehicle Revenue Hours per Employee')
        dicValidationErrors, result = check(vrhperfte, dicValidationErrors, result)
        frperpastrips = range_validation(agency, df1, df2, abbreviationdic, 'rev', 'psgr', 'Farebox Revenues per Passenger Trip')
        dicValidationErrors, result = check(frperpastrips, dicValidationErrors, result)
        roundedNumbers = rounded_numbers(agency, df2, abbreviationdic)
        dicValidationErrors, result = check(roundedNumbers, dicValidationErrors, result)
        #dicTrends = trendlines(agency, df1, df2, abbreviationdic)
        #dicValidationErrors, result = check(dicTrends, dicValidationErrors, result)
    for i, j in result.items():
        result[i] = [item for sublist in j for item in sublist]
    df = pd.DataFrame({key : pd.Series(val) for key, val in result.items()})
    return df


def fuel_efficiency(agency, df1, df2, abbreviationdic):
    joineddf = agency_selector(agency, df1, df2)
    fuellist = ['gfc', 'elc', 'dfc', 'cng', 'prp']
    results = []
    for fuel in fuellist:
        fueldf = joineddf[joineddf.columns[joineddf.columns.str.contains(fuel)]].dropna(axis =1)
        if fueldf.empty == True:
            continue
        modes = []
        try:
            fueldf = fueldf.drop(fuel+'_nar', axis = 1)
        except:
            pass
        rvm = []
        for i in modes:
            rvm.append('rvm_' + i)
        for i in fueldf.columns:
            modes.append(i.replace(fuel + '_', ''))
        rvmdfcols = joineddf.columns[joineddf.columns.isin(rvm)]
        rvmdf = joineddf[rvmdfcols]
        try:
            rvmdf = rvmdf.drop('rvm_nar', axis = 1)
        except:
            pass
        zippedcollist = zip(fueldf.columns, rvmdf.columns)
        newdf = pd.DataFrame()
        for j, k in zippedcollist:
            col = j + '_mpg'
            newdf[col] = rvmdf[k] / fueldf[j]
        for i in newdf.columns:
            change = (newdf[i][1] / newdf[i][0])-1
            fuelcolumn = i.replace('_mpg', '')
            rvmcolumn = i.replace('_mpg', '')
            rvmcolumn = rvmcolumn.replace(fuel, 'rvm')
            if change > .2:
                results.append(
                    'Error Type: {} is out of range from last year\'s numbers, having increased by twenty percent or more. Please revise {}: {} or {}: {}, or explain the change'.format(
                        i, fueldf[fuelcolumn][1], abbreviationdic[fuelcolumn], rvmdf[rvmcolumn][1],
                        abbreviationdic[rvmcolumn]))
            elif change < -.2:
                results.append(
                    'Error Type: {} is out of range from last year\'s numbers, having decreased by twenty percent or more. Please revise {}: {} or {}: {}, or explain the change'.format(
                        i, fueldf[fuelcolumn][1], abbreviationdic[fuelcolumn], rvmdf[rvmcolumn][1],
                        abbreviationdic[rvmcolumn]))
    if results == []:
        return False
    else:
        res = {agency: results}
        return res



def trendlines(agency, df1, df2, abbreviationdic):
    modes = ['do_CB', 'do_demand', 'do_fixed', 'do_light', 'do_RB', 'do_route', 'do_SR', 'do_TB', 'do_van',
             'pt_CB', 'pt_com', 'pt_demand', 'pt_DT', 'pt_fixed', 'pt_light', 'pt_RB', 'pt_route', 'pt_SR', 'pt_TB']
    joineddf = agency_selector(agency, df1, df2)
    errorsdic = {}
    for mode in modes:
        modedf = joineddf[joineddf.columns[joineddf.columns.str.contains(mode)]].dropna(axis=1)
        if modedf.empty == True:
            continue
        # to be resusicated, this would need to cut total vehicle miles, total revenue hour, and total ftes
        # also, it is not finding gfc_demand, add it to the abbreviaton dic
        modedf.columns = [abbreviationdic[c] for c in modedf.columns]
        modedf = modedf.append(modedf.loc[1] / modedf.loc[0] - 1, ignore_index=True)
        increased = modedf.loc[2][modedf.loc[2] > 0].count()
        decreased = modedf.loc[2][modedf.loc[2] < 0].count()
        if increased >= 5:
            trendlinelist = []
            avg =  modedf.loc[2][modedf.loc[2] > 0].mean()
            sd = modedf.loc[2][modedf.loc[2] > 0].std() * 2
            trendlinelist.append('TREND: {} increased. Average increase = {}. 2 stds = {}'.format(mode,avg,sd))
            categories = modedf.loc[2][modedf.loc[2] > sd].to_dict()
            categorieslist = list(categories.keys())
            for cat in categorieslist:
                trendlinelist.append(
                    'The category {} has a percentage increase ({} %) that is significantly larger than the rest of the data for this mode'.format(
                        cat, round(categories[cat] * 100, 2)))
            decrease = modedf.loc[2][modedf.loc[2] < -0.05].to_dict()
            decreasedlist = list(decrease.keys())
            for decline in decreasedlist:
                trendlinelist.append(
                    'The category {} had a significant decrease ({} %) while the rest of the data for this mode increased'.format(
                        decline, round(decrease[decline] * 100, 2)))
        if decreased >= 5:
            trendlinelist = []
            avg = modedf.loc[2][modedf.loc[2] < 0].mean()
            sd = modedf.loc[2][modedf.loc[2] < 0].std() * 2
            trendlinelist.append("TREND: {} decreased.  Avg decrease ={}. 2 sds = {}".format(mode, avg, sd))
            categories = modedf.loc[2][modedf.loc[2] < sd].to_dict()
            categorieslist = list(categories.keys())
            for cat in categorieslist:
                trendlinelist.append(
                    'The category {} has a percentage decrease ({} %) that is significantly larger than the rest of the data for this mode'.format(
                        cat, round(categories[cat] * 100, 2)))
            increased = modedf.loc[2][modedf.loc[2] > 0.05].to_dict()
            increasedlist = list(increased.keys())
            for incline in increasedlist:
                trendlinelist.append(
                    'The category {} had a significant increase ({} %) while the rest of the data for this mode decreased'.format(
                        incline, round(increased[incline] * 100, 2)))
        try:
            errorsdic.update({agency: trendlinelist})
        except:
            continue
    return errorsdic



def agency_selector(agency, df1, df2):
    xdf1 = df1[df1.Agency == agency]
    xdf2 = df2[df2.Agency == agency]
    try:
        joineddf = pd.concat([xdf1, xdf2], axis=0).reset_index().drop(['index', 'nan'], axis=1)
    except:
        joineddf = pd.concat([xdf1, xdf2], axis=0).reset_index().drop('index', axis=1)
    return joineddf

def check(dict, errorsdic, result):
    if dict != False:
        for key in (dict.keys() | errorsdic.keys()):
            if key in dict: result.setdefault(key, []).append(dict[key])
            if key in errorsdic: result.setdefault(key, []).append(errorsdic[key])
    errorsdic = {}
    return errorsdic, result

def range_validation(agency, df1, df2, abbreviationdic, colname1, colname2, valuetestedfor):
   joineddf = agency_selector(agency, df1, df2)
   for i in joineddf.columns:
       try:
           joineddf[i] = joineddf[i].astype(float)
       except:
           joineddf = joineddf.drop(i, axis = 1)
   xdf1 = joineddf[joineddf.columns[joineddf.columns.str.contains(colname1)]].dropna(axis=1)
   try:
       xdf1 = xdf1.drop('other_rev', axis = 1)
   except:
       pass
   xdf2 = joineddf[joineddf.columns[joineddf.columns.str.contains(colname2)]].dropna(axis=1)
   try:
       xdf2 = xdf2.drop('other_rev',axis = 1)
   except:
       pass
   cols = list(zip(xdf1.columns, xdf2.columns))
   results = []
   for x, y in cols:
       rs = xdf1[x] / xdf2[y]
       change = (rs[1] / rs[0]) - 1
       if change < -0.1:
           results.append(
               'Error Type:{}--{} (the value from last year was {}) is out of range from last year\'s numbers, having decreased by {}. Please revise {}: {} or {}: {}, or explain the change'.format(valuetestedfor, round(rs[1], 2), round(rs[0],2), round(change, 2)*100, abbreviationdic[x], xdf1[x][1], abbreviationdic[y], xdf2[y][1]))
       elif change > 0.1:
           results.append(
               'Error Type {}--{} (the value from last year was {}) is out of range from last year\'s numbers, having increased by {}. Please revise {}: {} or {}: {}, or explain the change'.format(valuetestedfor,round(rs[1], 2), round(rs[0], 2), round(change, 2)*100, abbreviationdic[x], xdf1[x][1], abbreviationdic[y], xdf2[y][1]))
   if results == []:
       return False
   else:
        res = {agency: results}
        return res


def rounded_numbers(agency, df2, abbreviationdic):
    absoluteUnit = df2[df2.Agency == agency].dropna(axis=1)
    numericCategories = list(abbreviationdic.keys())
    numericCategories = numericCategories[1:]
    absoluteUnit = absoluteUnit[[column for column in absoluteUnit.columns if column in numericCategories]]
    for i in absoluteUnit.columns:
        try:
            absoluteUnit[i] = absoluteUnit[i].astype(int)
        except:
            absoluteUnit = absoluteUnit.drop(i, axis = 1)
    columns = absoluteUnit.columns.tolist()
    values = absoluteUnit.values
    values = values[0].tolist()
    zippy = zip(columns, values)
    roundedErrors = []
    for typeOfDatum, valueOfDatum in zippy:
        if valueOfDatum == 0:
            continue
        elif valueOfDatum % 10 == 0:
            roundedErrors.append('Error Type: Rounded Number Is {} with a value of {} rounded? It is unlikely that these figures will end in zero'.format(abbreviationdic[typeOfDatum], valueOfDatum))
    if roundedErrors == []:
        return False
    else:
        res = {agency: roundedErrors}
        return res






def missing_values(agency, df1, df2, abbreviationdic):
    # this function checks for missing values, takes in dataframes to compare, agency (as agency loop is central function), and dictionary of abbreviations
    xdf1 = df1[df1.Agency == agency]
    xdf2 = df2[df2.Agency == agency]
    # filters both dfs for this specific agency
    xdf1 = xdf1.drop('Agency', axis = 1)
    xdf2 = xdf2.drop('Agency', axis = 1)
    # drops the agency section
    joineddf = pd.concat([xdf1, xdf2], axis=0).reset_index().drop('index', axis=1)
    # joins the two dataframes as rows (column names are the same. It's a long dataframe with columns and two values underneath it
    joineddf = joineddf.drop('rpKey', axis = 1)
    # drops the rpKey section, as it makes some of the work I'm trying to do here difficult
    joineddf = joineddf.astype(str)
    # turns all columns into strings
    missingvaluesdic = {}
    # instantiates a dictionary for missing values, to be returned at end of the funtion
    agencyvalues = []
    for k in joineddf.columns:
        # it iterates through the columns of the joined dataframe
        # this is a results list, that ultimately gets pushed back into the main validation framework
        if joineddf[k][0] == 'nan' and joineddf[k][1] != 'nan':
            # first iteration checks to see if there was a missing value in the first year, and there is now a reported value
            try:
                agencyvalues.append(
                    'Error Type Missing Values: {} did not have a value last year, but has one reported this year'.format(abbreviationdic[k]))
                # this part appends an error message and translates it from its abbreviation to its full form, for use as errpr
            except:
                agencyvalues.append('Error Type Missing Values: {} did not have a value last year, but has one reported this year'.format(k))
                # since the values and abbreviations have changed over time, need to set up a catch in case the value or abbreviation is missing
        elif joineddf[k][0] != 'nan' and joineddf[k][1] == 'nan':
            # same as above, but for if a value was reported last year, but there is not a reported value this year
            try:
                agencyvalues.append(
                    'Error Type Missing Values: {} was not reported last year, but was reported this year'.format(abbreviationdic[k]))
            except:
                agencyvalues.append('Error Type Missing Values: {} was not reported last year, but was reported this year'.format(k))
    try:
        missingvaluesdic = {agency: agencyvalues}
        # this section attempts to construct a dictionary
        # if there's no values to include, it fails, and returns an empty dictionary
    except:
        pass
    return missingvaluesdic

def Main(inputpath, dictionaryreaderpath, outputpath):
    # takes the path, reads everything in the relevant directory
   dflist, abbreviationdic = read_files(inputpath, dictionaryreaderpath)
    # generates a list of dataframes in this directory, and a set of abbreviations
   df = validation(dflist, abbreviationdic)
    # it's a validation function
   df.to_csv(outputpath)
    # outputs thit to a csv
if __name__ == "__main__":
    Main(r'I:\Public_Transportation\Data_Team\PT_Summary\2017\PTRS_Data\07-26-18_Pull\Validation', r'C:\Users\SchumeN\Documents\TPS\validationfolder',  r'I:\Public_Transportation\Data_Team\PT_Summary\2017\PTRS_Data\07-26-18_Pull\Validation\validationtestsrevised.csv')

    # user guide
    # make sure the paths line up
    # be sure Agency is in the dataset, or else everything will sputter out
    # update the dictionary generator with any new data types that are collected this year