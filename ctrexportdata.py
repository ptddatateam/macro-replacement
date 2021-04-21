import pandas as pd
import numpy as np
import sqlscripts
import pypyodbc

'''This script is a way to get and process SQL Queries so that they are immediately amenable to analytics in a variety of ways. To that end, I've made most variables on the suvey into categorical variables
replaced unanswered portions with 0s (methodologically debatable, but often necessary), and combined different layerings of historical data, at least in the output. Better layering could be done on the SQL side to avoid
such methodological problems, but this seems defendable in the immediate context (and is easy enough to change).'''


def connecttodb(sqlquery1, sqlquery2):
    cnxn = pypyodbc.connect(driver='{SQL Server}', server = 'HQOLYMSQL09P', database = 'CTRSurvey')
    df1 = pd.read_sql_query(sqlquery1, cnxn)
    df1 = df1.pivot(index = 'surveyresponseid', columns = 'question', values = 'domainvaluetext')
    df2 = pd.read_sql_query(sqlquery2, cnxn)
    df2 = df2.set_index('surveyresponseid')
    df = pd.concat([df1, df2], axis=1)
    return df

def changecolumnnames(df, columndictionary):
    df = df.rename(columns=columndictionary)
    df = df.drop('irrelevant', axis = 1)
    return df

def concatenateddf(df, columnname):
    newdf = pd.get_dummies(df[columnname])
    df = pd.concat([newdf, df], axis = 1)
    df = df.drop(columnname, axis = 1)
    return df

def change_labels(df, columnname):
    labels = columnname.split('_')
    suffix = labels[1]
    df[columnname] = df[columnname].replace('No Answer/Blank', '0')
    df[columnname] = df[columnname].replace(np.nan, '0')
    df[columnname] = df[columnname].replace('Did Not Work(day off, sick, etc.)', 'TransType_' + suffix + '_dayoff')
    df[columnname] = df[columnname].str.replace('Drove Alone', 'TransType_' + suffix + '_sov')
    df[columnname] = df[columnname].str.replace('Teleworked', 'TransType_' + suffix + '_telework')
    df[columnname] = df[columnname].str.replace('Took The bus', 'TransType_' + suffix + '_bus')
    df[columnname] = df[columnname].str.replace('Carpooled', 'TransType_' + suffix + '_carpool')
    df[columnname] = df[columnname].str.replace('Walked', 'TransType_' + suffix + '_walked')
    df[columnname] = df[columnname].str.replace('Rode The Train/light rail/streetcar', 'TransType_' + suffix + '_rail')
    df[columnname] = df[columnname].str.replace('Rode A Bicycle', 'TransType_' + suffix + '_bike')
    df[columnname] = df[columnname].str.replace('Compressed WorkWeek Day Off', 'TransType_' + suffix + '_compressww')
    df[columnname] = df[columnname].str.replace('Other', 'TransType_' + suffix + '_other')
    df[columnname] = df[columnname].str.replace('Motorcycle/Moped', 'TransType_' + suffix + '_2wheeledvehicle')
    df[columnname] = df[columnname].str.replace('Overnight Business Trip', 'TransType_' + suffix + '_businesstrip')
    df[columnname] = df[columnname].str.replace('Vanpooled', 'TransType_' + suffix + '_vanpool')
    df[columnname] = df[columnname].str.replace('Boarded ferry with car/van/bus', 'TransType_' + suffix + '_driveonferry')
    df[columnname] = df[columnname].str.replace('Used ferry as walk-on passenger', 'TransType_' + suffix + '_walkonferry')
    df[columnname] = df[columnname].fillna(0)
    dummydf = pd.get_dummies(df[columnname])
    dummydf = dummydf.drop('0', axis = 1)
    df = pd.concat([dummydf, df], axis = 1)
    df = df.drop(columnname, axis = 1)
    return df

def likelytotry(df, columnname):
    labels = columnname.split('try')
    suffix = labels[1]
    df[columnname] = df[columnname].str.replace("Not An Option", 'AttitudeToCTR' + "NotAnOption" + suffix)
    df[columnname] = df[columnname].str.replace("Not Likely", 'AttitudeToCTR' + "LowLikelihood" + suffix)
    df[columnname] = df[columnname].str.replace("Likely", 'AttitudeToCTR' + "Likely" + suffix)
    df[columnname] = df[columnname].str.replace("Do Now", 'AttitudeToCTR' + "DoNow" + suffix)
    df[columnname] = df[columnname].replace("No Answer/Blank", np.nan)
    df[columnname] = df[columnname].fillna(0)
    dummydf = pd.get_dummies(df[columnname])
    df = pd.concat([dummydf, df], axis = 1)
    df = df.drop(columnname, axis = 1)
    df = df.drop(0, axis = 1)
    return df

def fixtranstype(df):
    df = change_labels(df, 'TransType_Mon')
    df = change_labels(df, 'TransType_Tue')
    df = change_labels(df, 'TransType_Wed')
    df = change_labels(df, 'TransType_Thu')
    df = change_labels(df, 'TransType_Fri')
    df = change_labels(df, 'TransType_Sat')
    df = change_labels(df, 'TransType_Sun')
    return df

def fixattitudinaldata(df):
    if 'likelytotryCompressed' or 'likelytotrycarpool' in df:
        df = likelytotry(df, 'likelytotryCompressed')
        df = likelytotry(df, 'likelytotrycarpool')
        df = likelytotry(df, 'likelytotryVAN')
        df = likelytotry(df, 'likelytotrybus')
        df = likelytotry(df, 'likelytotryTrain')
        df = likelytotry(df, 'likelytotryBicycle')
        df = likelytotry(df, 'likelytotryWalking')
        df = likelytotry(df, 'likelytotryTeleWork')
    return df

def categoricaltransitdata(df):
    rail = df.columns[df.columns.str.contains('TransType' and 'rail')]
    bus = df.columns[df.columns.str.contains('TransType' and '_bus')]
    transit = rail.tolist() + bus.tolist()
    df['transitscore'] = df[transit].sum(axis=1)
    df['UsesTransit'] = np.where(df['transitscore'] > 0, 1, 0)
    df['RegularTransitRider'] = np.where(df['transitscore'] > 3, 1, 0)
    df = df.drop('transitscore', axis=1)
    return df

def cleaning_function(df):
    # cleans up commuter participation variable
    if 'BeginWorkBetween6and9am' in df:
        df['BeginWorkBetween6and9am'] = df['BeginWorkBetween6and9am'].str.replace('Yes', 'Beginbtw6and9am')
        df['BeginWorkBetween6and9am'] = df['BeginWorkBetween6and9am'].str.replace('No', 'DidNotBeginbtw6and9am')
        df['BeginWorkBetween6and9am'] = df['BeginWorkBetween6and9am'].fillna(0)
        df = concatenateddf(df, 'BeginWorkBetween6and9am')

    # cleans up paying for parking variable
    if 'PayforParking' in df:
        df.PayforParking = df.PayforParking.replace('Yes', 'PaidforParking')
        df.PayforParking = df.PayforParking.replace('No', 'DidNotPayforParking')
        df.PayforParking = df.PayforParking.fillna(0)
        df = concatenateddf(df, 'PayforParking')

    # cleans up and featurizes telework days
    if 'HowManyTeleworkDaysintwoweeks' in df:
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.astype(str)
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.apply(lambda x: x.lower())
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.str.replace('no days', '0')
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.str.replace(' days', '')
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.str.replace(' day', '')
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.str.replace('no answer/blank', '0')
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.str.replace('none', '0')
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.str.replace('nan', '0')
        df.HowManyTeleworkDaysintwoweeks = df.HowManyTeleworkDaysintwoweeks.astype(float)

    # checks in on Telework
    if 'Teleworkinpasttwoweeks' in df.columns:
        df.Teleworkinpasttwoweeks = df.Teleworkinpasttwoweeks.str.replace('Yes', "TeleworkedInPastTwoWeeks")
        df.Teleworkinpasttwoweeks = df.Teleworkinpasttwoweeks.replace('No Answer/Blank', 0)
        df.Teleworkinpasttwoweeks = df.Teleworkinpasttwoweeks.str.replace('No', 'DidNotTeleworkInPastTwoWeeks')
        df.Teleworkinpasttwoweeks = df.Teleworkinpasttwoweeks.fillna(0)
        df = concatenateddf(df, 'Teleworkinpasttwoweeks')
    # cleans up the work schedule column

    if 'SOVRecentDayDidYouPayToPark' in df:
        df['SOVRecentDayDidYouPayToPark'] = df['SOVRecentDayDidYouPayToPark'].str.replace('Yes', 'SOVPaidToParkMostRecentDay')
        df['SOVRecentDayDidYouPayToPark'] = df['SOVRecentDayDidYouPayToPark'].str.replace('No', 'SOVDidNotPayToParkMostRecentDay')
        df['SOVRecentDayDidYouPayToPark'] = df['SOVRecentDayDidYouPayToPark'].str.replace("I don't drive alone", 'NeverSOVPayToParkMostRecentDay')
        df['SOVRecentDayDidYouPayToPark'] = df['SOVRecentDayDidYouPayToPark'].fillna(0)
        df = concatenateddf(df, 'SOVRecentDayDidYouPayToPark')
    if 'HowOftenDoYouTelework' in df:

        df['HowOftenDoYouTelework'] = df['HowOftenDoYouTelework'].str.replace("1 day/week", 'TeleworkOnceAWeek')
        df['HowOftenDoYouTelework'] = df['HowOftenDoYouTelework'].str.replace("1-2 days/month", 'TeleworkACoupleTimesAMonth')
        df['HowOftenDoYouTelework'] = df['HowOftenDoYouTelework'].str.replace("2 days/week",'TeleworkTwiceAWeek')
        df['HowOftenDoYouTelework'] = df['HowOftenDoYouTelework'].str.replace("3 days/week", 'TeleworkThriceAWeek')
        df['HowOftenDoYouTelework'] = df['HowOftenDoYouTelework'].str.replace("I don't telework", 'TeleworkNever')
        df['HowOftenDoYouTelework'] = df['HowOftenDoYouTelework'].str.replace("Occasionally, on an as-needed basis", 'TeleworkOccasionally')
        df['HowOftenDoYouTelework'] = df['HowOftenDoYouTelework'].str.replace("0",'TeleworkNever')
        df = concatenateddf(df, 'HowOftenDoYouTelework')
    df.WorkSchedule = df.WorkSchedule.str.replace('3 days a week', 'WS_3days/week')
    df.WorkSchedule = df.WorkSchedule.str.replace('5 days a week', 'WS_5days/week')
    df.WorkSchedule = df.WorkSchedule.replace('No Answer/Blank', 0)
    df.WorkSchedule = df.WorkSchedule.str.replace('Other', 'WS_otherdays/week')
    df.WorkSchedule = df.WorkSchedule.str.replace('7 days in 2 weeks', 'WS_7days/2weeks')
    df.WorkSchedule = df.WorkSchedule.str.replace('4 days a weeks', 'WS_4tenhrdaysweek')
    df.WorkSchedule = df.WorkSchedule.str.replace('9 Days in 2 weeks', 'WS_9days/2weeks')
    df.WorkSchedule = df.WorkSchedule.str.replace(r"\(.*\)", "")
    df.WorkSchedule = df.WorkSchedule.str.strip()
    worksched = pd.get_dummies(df.WorkSchedule)
    df = pd.concat([worksched, df], axis=1)
    df = df.drop("WorkSchedule", axis=1)
    # cleaning function for question 1, Employment Status
    worktime = pd.get_dummies(df['EmploymentStatus'])
    df = pd.concat([worktime, df], axis=1)
    df = df.drop('EmploymentStatus', axis=1)
    # turns typical week into a dummy variable
    df.TypicalWeek = df.TypicalWeek.str.replace('Yes', 'TypicalWeek')
    df.TypicalWeek = df.TypicalWeek.replace('No Answer/Blank', 0)
    df.TypicalWeek = df.TypicalWeek.str.replace('No', 'AtypicalWeek')
    typical = pd.get_dummies(df.TypicalWeek)
    df = pd.concat([typical, df], axis=1)
    df = df.drop('TypicalWeek', axis=1)
    # cleaning and transformation function for number of people in car or van pool
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].astype(str)
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].apply(lambda x: x.lower())
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].str.replace(' persons', "")
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].str.replace(' person', "")
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].str.replace(' people', "")
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].str.replace('no answer/blank', '0')
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].str.replace('nan', '0')
    df['PeopleInVanOrCarpool'] = df['PeopleInVanOrCarpool'].astype(float)
    df = df.replace('Yes', 1)
    df = df.replace('No', 0)
    df = df.replace('No Answer/Blank', 0)
    df = df.drop(0, axis = 1)
    return df
def Main(filename):
    df = connecttodb(sqlscripts.sqlscript1, sqlscripts.sqlscript2)
    df = changecolumnnames(df, sqlscripts.labelcoding)
    df = fixtranstype(df)
    df = fixattitudinaldata(df)
    df = cleaning_function(df)
    df = categoricaltransitdata(df)
    df.to_csv(filename)
if __name__ == "__main__":
    Main(r'C:\Users\SchumeN\Documents\I5wideningproject\whatcomctrdataraw.csv')