import pandas as pd
import pymysql.cursors
import numpy as np
import humanize
import sql_scripts_for_summary as sqlscripts
from xlsxwriter.utility import xl_rowcol_to_cell
pd.options.display.float_format = '{:,}'.format


def run_sql_script(sql_script, db):
    sql_script = sql_script
    connection = pymysql.connect(host='UCC1038029',
                                 user='nathans',
                                 password='shalom33',
                                 db=db,
                                 cursorclass=pymysql.cursors.DictCursor)
    df = pd.read_sql(sql_script, con=connection)
    return df

def populate_sql_script(measure, year):
    queryString = clean_metrics(measure)
    script = '''Select Yr, Sum({}) as Total_{} from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype 
    as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group by Yr;'''.format(queryString, measure, year)
    return script

def clean_metrics(measure):
    replacement_list = ['rvh', 'psgr', 'rvm', 'rev', 'oex']
    queryString = 'rvh_do_fixed+rvh_do_light+rvh_do_route+rvh_do_demand+rvh_do_van+rvh_do_CB+rvh_do_RB+rvh_do_SR+rvh_do_TB+rvh_pt_fixed+rvh_pt_com+rvh_pt_light+rvh_pt_route+rvh_pt_demand+rvh_pt_CB+rvh_pt_RB+rvh_pt_DT+rvh_pt_SR+rvh_pt_TB'
    for i in replacement_list:
        queryString = queryString.replace(i, measure)
    return queryString



def modify_percentage(percentage):
    if percentage < 0:
        percentage = abs(percentage)
    percentage = str(percentage)
    percentage = percentage.replace('.0', '')
    return percentage

def find_fixed_percentage(year, db, df, measure):
    script = '''Select Yr, Sum(rvh_do_fixed+rvh_pt_fixed+rvh_do_TB+ rvh_pt_TB+rvh_do_CB+rvh_pt_CB+rvh_do_RB +rvh_pt_RB)/Sum(rvh_do_fixed+rvh_do_light+rvh_do_route+rvh_do_demand+rvh_do_van+rvh_do_CB+rvh_do_RB+rvh_do_SR+rvh_do_TB+rvh_pt_fixed+rvh_pt_com+rvh_pt_light+rvh_pt_route+rvh_pt_demand+rvh_pt_CB+rvh_pt_RB+rvh_pt_DT+rvh_pt_SR+rvh_pt_TB) as Total_Fixed from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype 
        as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group by Yr;'''.format(year)
    script = script.replace('rvh', measure)
    connection = pymysql.connect(host='UCC1038029',
                                 user='nathans',
                                 password='shalom33',
                                 db=db,
                                 cursorclass=pymysql.cursors.DictCursor)
    rvh_df = pd.read_sql(script, con=connection)
    df = pd.concat([df, rvh_df], axis=1)
    df.iloc[:, 3] = df.iloc[:, 3].apply(lambda x: round(x * 100, 1))
    return df

def prepare_df(yearOfReport, previousYear, measure):
    script = populate_sql_script(measure, (yearOfReport, previousYear))
    df = run_sql_script(script, 'ptsummary_transit')
    return df

def text_formation_from_df_financial(category, df):
    percentage = (df.loc[0][1] - df.loc[1][1]) / df.loc[1][1]
    percentage = round(percentage * 100, 1)
    df.iloc[:,1] = df.iloc[:,1].apply(lambda x: humanize.intword(x))
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: str(x).replace('.0', ''))
    if percentage > 0:
        percentage = modify_percentage(percentage)
        text = '{} increased {} percent, from around ${} in {} to about ${} in {}.'.format(category, percentage, df.loc[1][1], int(df.loc[1][0]), df.loc[0][1], int(df.loc[0][0]))
    elif percentage < 0:
        percentage = modify_percentage(percentage)
        text = '{} decreased {} percent, from around ${} in {} to about ${} in {}.'.format(category, percentage, df.loc[1][1], int(df.loc[1][0]), df.loc[0][1], int(df.loc[0][0]))
    return text


def generate_text(category, yearOfReport, previousYear, measure):
    df = prepare_df(yearOfReport, previousYear, measure)
    if measure in ['rvh', 'psgr']:
        df = find_fixed_percentage((yearOfReport,previousYear), 'ptsummary_transit', df, measure)
    percentage = (df.loc[0][1] - df.loc[1][1]) / df.loc[1][1]
    percentage = round(percentage * 100, 1)
    df.iloc[:,1] = df.iloc[:,1].apply(lambda x: humanize.intword(x))
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: str(x).replace('.0', ''))
    if percentage > 0:
        percentage = modify_percentage(percentage)
        if measure in ['rev', 'oex']:
            text = 'Total {} increased {} percent, from around ${} in {} to about ${} in {}.'.format(category, percentage, df.loc[1][1], int(df.loc[1][0]), df.loc[0][1], int(df.loc[0][0]))
        else:
            text = 'Total {} increased {} percent, from around {} in {} to about {} in {}.'.format(category, percentage, df.loc[1][1], int(df.loc[1][0]), df.loc[0][1], int(df.loc[0][0]))
    elif percentage < 0:
        percentage = modify_percentage(percentage)
        if measure in ['rev', 'oex']:
            text = 'Total {} increased {} percent, from around ${} in {} to about ${} in {}.'.format(category, percentage, df.loc[1][1], int(df.loc[1][0]), df.loc[0][1], int(df.loc[0][0]))
        else:
            text = 'Total {} increased {} percent, from around {} in {} to about {} in {}.'.format(category, percentage, df.loc[1][1], int(df.loc[1][0]), df.loc[0][1], int(df.loc[0][0]))
    # heres a separate bit of logic to produce the revenue vehicle hour text
    if measure in ['rvh', 'psgr']:
        if df.loc[0][3] > df.loc[1][3]:
            rvh_text = 'Fixed route services accounted for {} percent of total {} in {}, up from {} percent in {}.'.format(df.loc[0][3], category, int(df.loc[0][0]), df.loc[1][3], int(df.loc[1][0]))
        else:
            rvh_text = 'Fixed route services accounted for {} percent of total {} in {}, down from {} percent in {}.'.format(df.loc[0][3], category, int(df.loc[0][0]), df.loc[1][3], int(df.loc[1][0]))
        text = text + " "+ rvh_text
    if measure in ['rev']:
        rev_text = rev_oex_calculator((yearOfReport,previousYear))
        text = text + " " + rev_text
    return text

# this sql script is messed up
def rev_oex_calculator(yearOfReport):
    dfFares = run_sql_script(sqlscripts.fares.format(yearOfReport), 'ptsummary_transit')
    dfOperatingRevenues = run_sql_script(sqlscripts.operating_revenues.format(yearOfReport), 'ptsummary_transit')
    df = pd.concat([dfFares, dfOperatingRevenues], axis = 1)
    df = deduplicate(df)
    df['Real_Op_Revs'] = df['Fares'] +df['Operating_Revenues']
    df['Percent']= df['Fares']/df['Real_Op_Revs']
    df['Percent'] = df['Percent'].apply(lambda x:round(x*100, 2))
    df = df[['Yr', 'Percent']]
    df['Yr'] = df['Yr'].apply(lambda x: int(x))
    if df.loc[0][1] > df.loc[1][1]:
        text = 'These revenues accounted for {} percent of the operating revenues for the state\'s transit agencies, up from {} in {}'.format(df.loc[0][1],
                                                                                                                                              df.loc[1][0], df.loc[1][1])
    else:
        text = 'These revenues accounted for {} percent of the operating revenues for the state\'s transit agencies, down from {} in {}'.format(
            df.loc[0][1],
            df.loc[1][0], df.loc[1][1])
    return text



def deduplicate(df):
    df = df.transpose()
    df = df.drop_duplicates()
    df = df.transpose()
    return df

def iterate_through_revenues(df):
    randomText = []
    for column in df.columns:
        new_df = df[[column]]
        new_df = new_df.reset_index()
        column = column.replace('_', ' ')
        text = text_formation_from_df_financial(column, new_df)
        randomText.append(text)
    return randomText

def calculate_sound_tax_total(yearOfReport):
     lt = run_sql_script(sqlscripts.random_text_local_tax.format(yearOfReport), 'ptsummary_transit')
     sound = run_sql_script(sqlscripts.random_text_local_tax_sound.format(yearOfReport), 'ptsummary_transit')
     df = pd.concat([sound, lt], axis = 1)
     local_percent = df['Sound']/df['Local_Tax']
     local_percent = local_percent.apply(lambda x: round(x * 100, 1))
     localPercentDataFrame = pd.DataFrame(local_percent)
     lPerDf = localPercentDataFrame.reset_index()
     if lPerDf.loc[0][1] > lPerDf.loc[1][1]:
        soundText = 'Sound Transit represented {} percent of the total local tax revenues collected for public transit in {}, up from {} in {}'.format(lPerDf.loc[0][1], lPerDf.loc[0][0], lPerDf.loc[1][1], lPerDf.loc[1][0])
     else:
         soundText = 'Sound Transit represented {} percent of the total local tax revenues collected for public transit in {}, down from {} in {}'.format(
             lPerDf.loc[0][1], lPerDf.loc[0][0], lPerDf.loc[1][1], lPerDf.loc[1][0])
     return soundText


def revenue_and_investment_script(yearOfReport):
    rev_df = run_sql_script(sqlscripts.sw_invest_rev.format(yearOfReport), 'ptsummary_transit')
    rev_in = run_sql_script(sqlscripts.sw_invest_td.format(yearOfReport), 'ptsummary_transit')
    rev_exp = run_sql_script(sqlscripts.sw_invest_exp.format(yearOfReport), 'ptsummary_transit')
    df = pd.concat([rev_df, rev_in, rev_exp], axis=1)
    df = deduplicate(df)
    df.Yr = df.Yr.apply(lambda x: int(x))
    df = df.set_index('Yr')
    df['Local_Revenues'] = df['Farebox_Revenues'] + df['Local_Tax'] + df['Other_Local_Revenue']
    rev_df = df[['Local_Revenues', 'State_Revenues', 'Federal_Revenues']]

    rev_df['Total Revenues'] = list((rev_df.sum(axis = 1)))
    df['Total Revenues'] = rev_df['Total Revenues']  # need this for Local tax

    # builds the revenue random text
    revenueRandomText = iterate_through_revenues(rev_df)
    localTaxDf = pd.DataFrame(df['Local_Tax'])
    localTaxText = iterate_through_revenues(localTaxDf)
    # local tax revenues random text
    local_percent = df['Local_Tax']/df['Total Revenues']
    local_percent = local_percent.apply(lambda x: round(x*100, 2))
    localPercentDataFrame = pd.DataFrame(local_percent)
    localPercentDataFrame = localPercentDataFrame.reset_index()
    if localPercentDataFrame.loc[0][1] > localPercentDataFrame.loc[1][1]:
        localPercentText = 'These revenues accounted for {} percent of all revenues (both operating and capital) for the state\'s public transit agencies, up from {} percent in {}'.format(localPercentDataFrame.loc[0][1], localPercentDataFrame.loc[1][1], localPercentDataFrame.loc[1][0])
    else:
        localPercentText = 'These revenues accounted for {} percent of all revenues (both operating and capital) for the state\'s public transit agencies, down from {} percent in {}'.format(
            localPercentDataFrame.loc[0][1], localPercentDataFrame.loc[1][1], localPercentDataFrame.loc[1][0])
    localTaxText = localTaxText[0] + " " + localPercentText
    revenueRandomText.append(localTaxText)
    soundText = calculate_sound_tax_total(yearOfReport)
    revenueRandomText.append(soundText)


    return revenueRandomText






def main(yearOfReport, path):
    randomTextDictionary = {'revenue vehicle hours': 'rvh', 'revenue vehicle miles': 'rvm', 'passenger trips': 'psgr', 'farebox revenues': 'rev', 'operating expenses': 'oex', 'farebox revenues':'rev'}
    previousYear = yearOfReport -1
    randomTextList = []
    for key, value in randomTextDictionary.items():
        text = generate_text(key, yearOfReport, previousYear, value)
        randomTextList.append(text)
    revenueRandomText = revenue_and_investment_script((yearOfReport, previousYear))






if __name__ == "__main__":
    main(2017, r'C:\Users\SchumeN\Documents\ptstest\newtest\invest_test')





