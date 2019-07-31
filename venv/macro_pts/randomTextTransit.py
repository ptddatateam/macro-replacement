import pandas as pd
import pymysql.cursors
import numpy as np
import humanize
import csv
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
    percentage = (df.loc[1][1] - df.loc[0][1]) / df.loc[0][1]
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
    percentage = (df.loc[1][1] - df.loc[0][1]) / df.loc[0][1]
    percentage = round(percentage * 100, 1)
    print(percentage)
    df.iloc[:,1] = df.iloc[:,1].apply(lambda x: humanize.intword(x))
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: str(x).replace('.0', ''))
    print(percentage)
    if percentage > 0:
        percentage = modify_percentage(percentage)
        if measure in ['rev', 'oex']:
            text = 'Total {} increased {} percent, from around ${} in {} to about ${} in {}.'.format(category, percentage, df.loc[0][1], int(df.loc[0][0]), df.loc[1][1], int(df.loc[1][0]))
        else:
            text = 'Total {} increased {} percent, from around {} in {} to about {} in {}.'.format(category, percentage, df.loc[0][1], int(df.loc[0][0]), df.loc[1][1], int(df.loc[1][0]))
        print(text)
    else:
        percentage = modify_percentage(percentage)
        if 'rev' in measure or 'oex' in measure:
            text = 'Total {} increased {} percent, from around ${} in {} to about ${} in {}.'.format(category, percentage, df.loc[0][1], int(df.loc[0][0]), df.loc[1][1], int(df.loc[1][0]))
        else:
            text = 'Total {} decreased {} percent, from around {} in {} to about {} in {}.'.format(category, percentage, df.loc[0][1], int(df.loc[0][0]), df.loc[1][1], int(df.loc[1][0]))
    # heres a separate bit of logic to produce the revenue vehicle hour text
    if measure in ['rvh', 'psgr']:
        if df.loc[0][3] > df.loc[1][3]:
            rvh_text = 'Fixed route services accounted for {} percent of total {} in {}, up from {} percent in {}.'.format(df.loc[0][3], category, int(df.loc[0][0]), df.loc[1][3], int(df.loc[1][0]))
        else:
            rvh_text = 'Fixed route services accounted for {} percent of total {} in {}, down from {} percent in {}.'.format(df.loc[0][3], category, int(df.loc[0][0]), df.loc[1][3], int(df.loc[1][0]))
        text = text + " "+ rvh_text
    if measure in ['rev']:
        print(percentage)
        rev_text = rev_oex_calculator((yearOfReport,previousYear))
        print(rev_text)
        text = text + " " + rev_text
    return text


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
    print(df)
    if df.loc[1][1] > df.loc[0][1]:
        text = 'These revenues accounted for {} percent of the operating revenues for the state\'s transit agencies, up from {} in {}'.format(df.loc[1][1],
                                                                                                                                              df.loc[0][1], int(df.loc[0][0]))
    else:
        text = 'These revenues accounted for {} percent of the operating revenues for the state\'s transit agencies, down from {} in {}'.format(
            df.loc[1][1],
            df.loc[0][1], int(df.loc[0][0]))
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
        soundText = 'Sound Transit represented {} percent of the total local tax revenues collected for public transit in {}, up from {} in {}'.format(lPerDf.loc[0][1], int(lPerDf.loc[0][0]), lPerDf.loc[1][1], int(lPerDf.loc[1][0]))
     else:
         soundText = 'Sound Transit represented {} percent of the total local tax revenues collected for public transit in {}, down from {} in {}'.format(
             lPerDf.loc[0][1], int(df.loc[0][0]), lPerDf.loc[1][1], int(df.loc[1][0]))
     return soundText


def revenue_and_investment_script(yearOfReport):
    rev_df = run_sql_script(sqlscripts.sw_invest_rev.format(yearOfReport), 'ptsummary_transit')
    print(rev_df['Other_Operating_Revenue'])
    rev_in = run_sql_script(sqlscripts.sw_invest_td.format(yearOfReport), 'ptsummary_transit')
    rev_exp = run_sql_script(sqlscripts.sw_invest_exp.format(yearOfReport), 'ptsummary_transit')
    df = pd.concat([rev_df, rev_in, rev_exp], axis=1)
    df = deduplicate(df)
    df.Yr = df.Yr.apply(lambda x: int(x))
    df = df.set_index('Yr')
    df['Local_Revenues'] = df['Farebox_Revenues'] + df['Local_Tax'] + df['Other_Local_Revenue']
    df['Total_Investments'] = df['Operating_Investments'] + df['Federal_Capital_Investment'] + df['State_Capital_Investment'] + df['Local_Capital_Investment'] + df['Other_Capital_Investment']
    rev_df = df[['Local_Revenues', 'State_Revenues', 'Federal_Revenues']]
    inv_df = df[['Total_Investments', 'Operating_Investments', 'Federal_Capital_Investment', 'State_Capital_Investment', 'Local_Capital_Investment', 'Other_Capital_Investment']]
    inv_df.columns = [column.lower().capitalize() for column in inv_df.columns]
    investmentRandomText = iterate_through_revenues(inv_df)
    rev_df['Total Revenues'] = list((rev_df.sum(axis = 1)))
    df['Total Revenues'] = rev_df['Total Revenues']  # need this for Local tax
    rev_df.columns = [column.lower().capitalize() for column in rev_df.columns]
    df.columns = [column.lower().capitalize() for column in df.columns]

    # builds the revenue random text
    revenueRandomText = iterate_through_revenues(rev_df)
    localTaxDf = pd.DataFrame(df['Local_tax'])
    localTaxText = iterate_through_revenues(localTaxDf)
    # local tax revenues random text
    local_percent = df['Local_tax']/df['Total revenues']
    local_percent = local_percent.apply(lambda x: round(x*100, 2))
    localPercentDataFrame = pd.DataFrame(local_percent)
    localPercentDataFrame = localPercentDataFrame.reset_index()
    print(localPercentDataFrame)
    if localPercentDataFrame.loc[0][1] > localPercentDataFrame.loc[1][1]:
        localPercentText = 'These revenues accounted for {} percent of all revenues (both operating and capital) for the state\'s public transit agencies, up from {} percent in {}'.format(localPercentDataFrame.loc[0][1], localPercentDataFrame.loc[1][1], int(localPercentDataFrame.loc[1]['Yr']))
    else:
        localPercentText = 'These revenues accounted for {} percent of all revenues (both operating and capital) for the state\'s public transit agencies, down from {} percent in {}'.format(
            localPercentDataFrame.loc[0][1], localPercentDataFrame.loc[1][1], int(localPercentDataFrame.loc[1]['Yr']))
    localTaxText = localTaxText[0] + " " + localPercentText
    revenueRandomText.append(localTaxText)
    soundText = calculate_sound_tax_total(yearOfReport)
    revenueRandomText.append(soundText)
    financialRandomText = revenueRandomText + investmentRandomText
    return financialRandomText

def to_csv(res, path):
    with open(path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter = ',')
        for i in res:
            writer.writerow([i])


def find_fare_percent_changes(yearOfReport):
    transit_list = ['asotin', 'ben franklin', 'Central Transit', 'clallam', 'columbia', 'community', 'ctran',
                         'CUBS', 'everett', 'garfield',
                         'grant', 'grays', 'intercity', 'island', 'jefferson', 'king', 'kitsap', 'link', 'mason',
                         'Okanogan County Transit Authority', 'pacific', 'pierce', 'pullman',
                         'selah', 'skagit', 'sound', 'spokane', 'twin', 'union gap', 'valley', 'whatcom', 'yakima']
    formal_report_list = ['Asotin County Transit', 'Ben Franklin Transit', 'Central Transit',
                               'Clallam Transit System', 'Columbia County Public Transportation',
                               'Community Transit', 'C-TRAN', 'RiverCities Transit', 'Everett Transit',
                               'Garfield County Transportation Authority', 'Grant Transit Authority',
                               'Grays Harbor Transportation Authority', 'Intercity Transit', 'Island Transit',
                               'Jefferson Transit Authority', 'King County Metro',
                               'Kitsap Transit', 'Link Transit', 'Mason County Transportation Authority', 'TranGo',
                               'Pacific Transit System', 'Pierce Transit', 'Pullman Transit',
                               'City of Selah Transportation Service', 'Skagit Transit', 'Sound Transit',
                               'Spokane Transit Authority', 'Twin Transit', 'Union Gap Transit',
                               'Valley Transit', 'Whatcom Transportation Authority', 'Yakima Transit']
    transit_dic = dict(zip(transit_list, formal_report_list))
    fareChangeDf = run_sql_script(sqlscripts.farebox_changes.format(yearOfReport), 'ptsummary_transit')
    agencyType = ['urban', 'small urban', 'rural']
    fareChangeDf['Agnc'] = fareChangeDf['Agnc'].apply(lambda x: transit_dic[x])
    fareChangeDf['PercentDiff'] = fareChangeDf['PercentDiff'].apply(lambda x: round(x, 1))
    count = 0
    increaseFareList = []
    decreaseFareList = []
    for atype in agencyType:
        sortedDf = fareChangeDf[fareChangeDf['agencytype'] == atype]
        maxrow = sortedDf.loc[sortedDf['PercentDiff'] == sortedDf['PercentDiff'].max()]
        minrow = sortedDf.loc[sortedDf['PercentDiff'] == sortedDf['PercentDiff'].min()]
        if count == 0:
            decreaseDf = pd.DataFrame(minrow)
            increaseDf = pd.DataFrame(maxrow)
            count +=1
        else:
            decreaseDf = pd.concat([decreaseDf, minrow], axis = 0)
            increaseDf = pd.concat([increaseDf, maxrow], axis = 0)
    increaseFareList.append("By classification, the following transit agencies showed the largest increases in farebox revenues, excluding vanpool farebox revenues")
    for index, value in increaseDf.iterrows():
        increaseFareList.append(value['agencytype'] + ": " + value['Agnc'] + ", {} percent".format(value['PercentDiff']))
    decreaseFareList.append(
        "By classification, the following transit agencies showed the largest decreases in farebox revenues, excluding vanpool farebox revenues")
    for index, value in decreaseDf.iterrows():
        decreaseFareList.append(value['agencytype']+ ": " + value['Agnc']+ ", {} percent".format(value['PercentDiff']))

    return increaseFareList, decreaseFareList



def main(otherRandomText, yearOfReport, path):
    randomTextDictionary = {'revenue vehicle hours': 'rvh', 'revenue vehicle miles': 'rvm', 'passenger trips': 'psgr', 'farebox revenues': 'rev', 'operating expenses': 'oex', 'farebox revenues':'rev'}
    previousYear = yearOfReport -1
    randomTextList = []
    for key, value in randomTextDictionary.items():
        text = generate_text(key, yearOfReport, previousYear, value)
        randomTextList.append(text)
    increaseFareText, decreaseFareText = find_fare_percent_changes((previousYear, yearOfReport))
    financialRandomText = revenue_and_investment_script((yearOfReport, previousYear))
    randomTextList = otherRandomText + randomTextList + financialRandomText + increaseFareText + decreaseFareText
    path = path + '\\' + 'randomtext.csv'
    to_csv(randomTextList, path)







if __name__ == "__main__":
    main(['some stuff'],2018, r'C:\Users\SchumeN\Documents\TPS\test')





