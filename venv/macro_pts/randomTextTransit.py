import pandas as pd
import pymysql.cursors
import numpy as np
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


def generate_text(category, yearOfReport, previousYear, measure):
    script = populate_sql_script(measure, (yearOfReport,previousYear))
    df = run_sql_script(script, 'ptsummary_transit')
    if measure in ['rvh', 'psgr']:
        df = find_fixed_percentage((yearOfReport,previousYear), 'ptsummary_transit', df, measure)
    percentage = (df.loc[0][1] - df.loc[1][1]) / df.loc[1][1]
    print(percentage)
    percentage = round(percentage * 100, 1)
    df.iloc[:,1] = df.iloc[:,1].apply(lambda x: round(x/1000000, 4))
    df.iloc[:, 1] = df.iloc[:,1].apply(lambda x: float(str(x)[:-3]))
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: str(x).replace('.0', ''))
    if percentage > 0:
        percentage = modify_percentage(percentage)
        text = 'Total {} increased {} percent, from around {} million in {} to about {} million in {}.'.format(category, percentage, df.loc[0][1], int(df.loc[0][0]), df.loc[1][1], int(df.loc[1][0]))
    elif percentage < 0:
        percentage = modify_percentage(percentage)
        text = 'Total {} decreased {} percent, from around {} million in {} to about {} million in {}.'.format(category, percentage, df.loc[0][1], int(df.loc[0][0]), df.loc[1][1], int(df.loc[1][0]))
    # heres a separate bit of logic to produce the revenue vehicle hour text
    if measure in ['rvh', 'psgr']:
        if df.loc[0][3] > df.loc[1][3]:
            rvh_text = 'Fixed route services accounted for {} percent of total {} in {}, up from {} percent in {}.'.format(df.loc[0][3], category, int(df.loc[0][0]), df.loc[1][3], int(df.loc[1][0]))
        else:
            rvh_text = 'Fixed route services accounted for {} percent of total {} in {}, down from {} percent in {}.'.format(df.loc[0][3], category, int(df.loc[0][0]), df.loc[1][3], int(df.loc[1][0]))
        text = text + " "+ rvh_text
    return text





def main(yearOfReport, path):
    randomTextDictionary = {'revenue vehicle hours': 'rvh', 'revenue vehicle miles': 'rvm', 'passenger trips': 'psgr', 'farebox revenues': 'rev', 'operating expenses': 'oex'}
    previousYear = yearOfReport -1
    randomTextList = []
    for key, value in randomTextDictionary.items():
        text = generate_text(key, yearOfReport, previousYear, value)
        print(text)
        randomTextList.append(text)






if __name__ == "__main__":
    main(2017, r'C:\Users\SchumeN\Documents\ptstest\newtest\invest_test')





