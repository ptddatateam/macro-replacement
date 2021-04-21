import os
import sys
import win32com.client
import pandas as pd
import numpy as np
from pywintypes import com_error
import re


'''This script is intended for programmatically cracking ntd workbooks and extracting relevant text data so that it can be used for the summary of public transportation'''

def unprotect_xlsx_reduced_reporting_form(filename, password_string):
    # this function is meant to deal with the fact that ntd workbooks are password protected, and it serially unprotects these worksheets, avoiding the process of manually doing so
    # this is a function call, which takes a set of parameters, a file's name and a password string
    xclapp = win32com.client.Dispatch("Excel.Application")
    # this call opens an excel app through python
    workbook = xclapp.Workbooks.Open(filename, False, False, None)
    # using the excel app, this function sets up an instance of a specific workbook, opening the specific filename
    worksheet = workbook.Worksheets('Reduced Reporting Template')
    # this uses the same excel app to open an instance of a worksheet, specifically the Reduced Reporting Template, which is where most of the NTD data lives
    try:
        worksheet.Unprotect(password_string)
    except com_error as error:
        pass
    # this instance of the excel app unprotects the specified sheet, utilizing the password string
    # it is lodged within a try/except set of logic, which tries to unprotect the sheet, and if it fails (ie the password is some sort of internal ntd thing), it does not fail, but continues looping through files
    xclapp.DisplayAlerts = False
    # necessary so that you don't get a lot of rando menus and clickthroughs to do
    workbook.Save()
    # saves the unprotected workbook
    xclapp.Quit()
    # quits the workbook

def unprotect_xlsx_a30_vehiclereportingform(filename, password_string):
    # this function unprotects the a30 vehicle reporting form
    # the function call takes two parameters, a filename and a password, which needs to be passed in as a string, ie, like so 'password'
    xclapp = win32com.client.Dispatch("Excel.Application")
    # this calls open an excel app
    workbook = xclapp.Workbooks.Open(filename, False, False, None)
    # this call opens a workbook
    worksheet = workbook.Worksheets('Revenue Vehicle Inventory A-30')
    # gets to the revenue vehicle inventory a-30
    try:
        worksheet.Unprotect(password_string)
    except com_error as error:
        pass
    # this instance of the excel app unprotects the specified sheet, utilizing the password string
    # it is lodged within a try/except set of logic, which tries to unprotect the sheet, and if it fails (ie the password is some sort of internal ntd thing), it does not fail, but continues looping through files
    xclapp.DisplayAlerts = False
    # necessary to avoid random menus
    workbook.Save()
    # saves the unprotected workbook
    xclapp.Quit()
    # quits the app

def change_transit_provider_type(transitProviderType):
    # this function is used to read a column in the ntd workbook that lists the transit types associated with particular pieces of data like operating expenses, fare revenues, etc.
    transitTypeDictionary = {'Demand Response': 'DR', 'Commuter Bus': 'CB', 'Mobile Bus': 'MB', 'Vanpool': 'VP', 'Bus': 'MB'}
    # this dictionary replaces the full names of these transit types with abbreviations. It is a data type that records the relationships between two types of data

    try:
        transformedData = transitTypeDictionary[transitProviderType]
        return transformedData
    # it searches for the long name in a dictionary, and if it finds it, the function returns the abbreviation
    except:
        transformedData = 0
        return transformedData
    # if it does not find the long name, it turns the data into a 0, which is useful for filtering out extraneous data later on

def change_category_name(df):
    # this is a short function that aggregates the various data types into column names for the purposes of writing them out to an excel sheet
    df['RealCategory'] = df.Category + df.Type + df.FundingColumn
    # builds the category name from the category, transit type, and funding type column
    df.RealCategory = df.RealCategory.str.replace('0', '')
    # cleans out any 0s or empty strings
    df.RealCategory = df.RealCategory.str.replace(" ", "")
    df = df.drop(['Category', 'Type', 'FundingColumn'], axis = 1)
    # having built this new category string, it drops the building block columns and then returns the dataframe
    return df

def find_agency(path):
    # a small function that reads the filename and extracts the agency name
    agencyName = os.path.basename(path)
    # takes the name of the file from the path, and turns it into the agency name
    agencyName = agencyName.replace("NTD RY", "")
    # strips the extraneous bits out of the file name
    agencyName = re.sub(r'[0-9]{4}', '', agencyName)
    # strips the year out (and it is year agnostic)
    agencyName = agencyName.replace('.xlsx', "")
    # takes out the .xlsx ending
    # more cleaning code can be added here, if necessary
    return agencyName
    # returns the data name

def makerr20dataframe(path, fundingType, excelcolumns):
    # builds a dataframe of data from the rr20 (reduced reporting template) sheet
    # this function is used twice, once for capital, and once for operating
    # the function call takes a path for the file, a type (operating or capital), and specific excel columns
    # will say more about the excel columns below
    df = pd.read_excel(path, sheet_name='Reduced Reporting Template', usecols=excelcolumns)
    # this is a read function, which uses the pandas library to read the specific excel sheet reducing report template, and the specific columns
    df = df.loc[50: 184].dropna(thresh=2)
    # this code cuts the extraneous parts of the dataframe out, and deletes rows that have more than 2 empty columns (nas)
    df.columns = ['Category', 'Type', 'Values']
    # since there are three columns, it changes the names to category (local funds, state funds, etc.), type-dr, mb, cb, or vp, and values, the actual numbers
    df.Type = df.Type.apply(lambda x: change_transit_provider_type(x))
    # this code takes the change transit provider function up above and applies it to the type column, turning it from long names to abbreviations
    df['FundingColumn'] = fundingType
    # create a column that lists whether funding data has to do with operating expense or capital expenses
    agencyName = find_agency(path)
    # uses the find agency function to build a column with the agency name from the path
    df['Agency'] = agencyName
    df = df.astype(str)
    # converts all the data in the dataframe to the string data type
    df = df[~df.Values.str.contains(fundingType)]
    # the words operating or capital show up a lot in the values column, since the form is vertical. This function excludes any values that are equal to operating or capital, to clean out the dataframe
    df = df[~df.Category.str.contains('nan')]
    # excludes nan (basically, undefined or empty space) from the category column
    df = change_category_name(df)
    # uses the change category function to remake the dataframe's categories, so that they reflect the datatypes necessary for the macro
    df = df.reset_index()
    df = df.drop('index', axis=1)
    # drops the old index, so that i can reshape the data
    df = df.pivot(index='Agency', columns='RealCategory', values='Values')
    # pivots the dataframe so that the columns are categories, the values are values, and the index is the agency
    return df

def find_volunteers(path):
    # this function looks for volunteer drivers and vehicles in the excel sheet rr template
    volunteerdf = pd.read_excel(path,sheet_name='Reduced Reporting Template', usecols='C, E, H, L')
    # uses specific columns
    volunteerdf['Unnamed: 0'] = volunteerdf['Unnamed: 0'].astype(str)
    # turns this dataframe column into string
    volunteerdf = volunteerdf[volunteerdf['Unnamed: 0'].str.contains('Number of volunteer drivers')]
    # this code uses indexing to find the one specific row where the volunteer drivers and vehicles is located
    volunteerdf.columns = ["Category", "Values", "Category", "Values"]
    # names the columns so that they can be pivoted and joined with the rest of the data
    volunteerdf = volunteerdf.reset_index()
    volunteerdf = volunteerdf.drop('index', axis=1)
    # drops the index
    volunteerdf1 = volunteerdf.iloc[:, :2]
    volunteerdf2 = volunteerdf.iloc[:, 2:]
    # splits the categories into separate dataframes
    volunteerdf = pd.concat([volunteerdf1, volunteerdf2], axis=0)
    # rejoins them vertically, make its easier to pivot them
    agencyname = find_agency(path)
    volunteerdf['Agency'] = agencyname
    # adds agency to dataframe
    volunteerdf = volunteerdf.pivot(index='Agency', columns='Category', values="Values")
    # pivots the dataframe and returns it
    return volunteerdf

def find_annual_data(path):
    # this function looks at the annual data by mode, which is poorly arranged
    df = pd.read_excel(path, sheet_name='Reduced Reporting Template', usecols="C, E, H, J, L, N")
    # takes a lot of columns
    df['Unnamed: 0'] = df["Unnamed: 0"].apply(change_transit_provider_type, 'Unnamed: 0')
    # this section hits the transit type, and changes it to abbreviation
    categories = ['Mode', 'AnnualVehicleRevenueMiles', 'AnnualVehicleRevenueHours', "AnnualTotalUnlinkedPassengerTrips",'SponsoredUnlinkedPassengerTrips', "VOMS"]
    # builds a set of categories that are arranged horizontally above the relevant data
    actualdata = df[df['Unnamed: 0'] != 0].transpose().fillna(0)
    # have to move the data round
    colnames = actualdata.loc['Unnamed: 0'].unique()
    # finds the unique column names
    actualdata.columns = colnames
    actualdata = actualdata.reset_index().drop('index', axis=1)
    actualdata = actualdata.stack(level=0).reset_index().sort_values(by='level_1').drop('level_0', axis=1)
    actualdata = actualdata.reset_index().drop(['index', 'level_1'], axis=1)
    # resets and reshapes this for easier analysis
    modelist = actualdata[0].tolist()
    # takes the first column of this dataframe and turns it into a list
    modes = [i for i in modelist if i in ['DR', 'MB', 'CB', 'VP']]
    # builds a list of relevant transit types abbreviations
    labelcolumn = []
    for i in modes:
        modelist = [s + '_' + i for s in categories]
        labelcolumn.append(modelist)
        # appends these specific mode types to the aforementioned categories, so that they can be used in the macro
    labels = [item for sublist in labelcolumn for item in sublist]
    # builds the actual label columns
    actualdata['labels'] = labels
    agencyname = find_agency(path)
    actualdata['agency'] = agencyname
    # adds the agency name
    actualdata.columns = ['values', 'labels', 'agency']
    # puts in column names
    actualdata = actualdata.pivot(index='agency', columns='labels', values='values')
    # reshapes the data for output
    return actualdata


def find_vehicles_sums(path):
    df = pd.read_excel(path, sheet_name='Revenue Vehicle Inventory A-30', usecols="E, S")
    # this function reads the A30; it seems to me that these columns are the most likely to change
    df = df.replace('Total Vehicles', 0)
    df = df.replace('ADA Accessible Vehicles', 0)
    # replaces these two so they can be summed up
    df = df.fillna(0)
    # fills nas
    newdf = df.sum()
    # sums the data
    sums = []
    for i in newdf:
        sums.append(i)
        # appends the relevant sums
    df = pd.DataFrame([df.columns, sums]).transpose()
    # turns them into a dataframe
    df.columns = ['labels', 'values']
    # renames the columns
    agencyname = find_agency(path)
    df['agency'] = agencyname
    # includes the agency
    vehicles = df.pivot(index='agency', columns='labels', values='values')
    # pivots the data so its relevant to the macro
    return vehicles



def workbookreader(path, password):
    #unprotect_xlsx_reduced_reporting_form(path, password)
    # function call to unprotect the reduced reporting form
    #unprotect_xlsx_a30_vehiclereportingform(path, password)
    # function call to unprotect the 130
    operatingdf = makerr20dataframe(path, 'Operating', 'C, E, H')
    # this is where things might get a bit tricky, be sure to add the relevant columns here, as a set of comma separated capital letters, include the column where the mode is specified, the column of names and the column of values associated with operating
    capitaldf = makerr20dataframe(path, 'Capital', 'C, E, S')
    # same thing here, but be sure to specify the column of names, the column of modes, and the column of values (should be only one column different between the two)
    rr20df = pd.concat([capitaldf, operatingdf], axis=1).replace('nan', '0')
    # this concatenates these two different dataframes
    rr20df = rr20df.astype(float)
    rr20df = rr20df.fillna(0)
    # turns them into floats and turns any nas into 0s
    voldf = find_volunteers(path)
    # searchs for volunteers
    rr20df = pd.concat([rr20df, voldf], axis=1)
    # concatenates volunteers and rr20
    annualdata = find_annual_data(path)
    # finds the annual data
    rr20df = pd.concat([rr20df, annualdata], axis = 1)
    # concatenates rr20 and annual data
    # some times the password is different for the a30 and the rr20, so I built a try and except into here, so that it doesn't fail and ruin all of the program
    try:
        vehicles = find_vehicles_sums(path)
        rr20df = pd.concat([vehicles, rr20df], axis = 1)
        # finds the vehicle totals that we care about and concatenates them with the previously extracted info
    except:
        pass
    return rr20df

def eliminate_emptycolumns(df):
    # its a function to get rid of the empty columns, which get picked up along the away
    for i in df.columns:
        try:
            if df[i].sum() == 0:
                df = df.drop(i, axis = 1)
    # checks to see that the columns sum to 0, if so, it drops them
        except TypeError:
            continue
            # occasionally, there are type errors, so this just passes it through, so that doesnt happen
    return df

def Main(path, password, outputpath):
    ntdlist = os.listdir(path)
    # this is the main function, which houses all the functionalities described above
    # this section uses the os library to generate a list of all the files in the target directory
    for i in ntdlist:
        print(i)
        # it generates a list, and iterates through it, and behaves somewhat differently if it's the first, since it has to build a dataframe
        if ntdlist.index(i) == 0:
            maindf = workbookreader(path + '\\'+ i, password)
        else:
            df = workbookreader(path + '\\' + i, password)
            maindf = pd.concat([maindf, df], axis = 0, join = 'outer')
            # at the end of each iteration, it builds a larger dataframe
    maindf = eliminate_emptycolumns(maindf)
    # cut out any empty columns
    maindf.to_csv(outputpath)
    # creates an output path
if __name__ == "__main__":
    Main(r'G:\Evaluation Group\National Transit Database\2017 NTD\Responses\\entered\\CommunityProviders', 'ntd2017', r'C:\Users\SchumeN\Documents\TPS\rawntddata.csv')