'''function for building statewide community provider rollups
by Nathan Schumer
replacing the macro for the summary of public transportation
'''

import pandas as pd
import numpy as np
import pymysql.cursors
import itertools
import csv
# I imported a few things


class statewide_cp_Datasheet():
    def __init__(self, year1, year2, year3):
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
    def pull_from_db(self, year1, year2, year3):
        '''this function provides the names of columns in the dataframe'''
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        connection = pymysql.connect(host='UCC1038029',
                                     user='nathans',
                                     password='shalom33',
                                     db='ptsummary_communityproviders',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            # Read a single record
            sql = """SELECT * from cpdata WHERE Yr in ('{}', '{}', '{}')""".format(year1, year2, year3)
            cursor.execute(sql)
            result = cursor.fetchall()

        connection.close()
        return result


    def clean_results(self, results):
        self.results = results
        df = pd.DataFrame.from_records(results)
        bad_data = ['DT', 'VP', 'RB', 'desc']  # strips out some bad data categories, TODO should fix this in db design
        cols_to_drop = []
        for bad in bad_data:
            col_list = df.columns[df.columns.str.contains(bad)]
            cols_to_drop.append(col_list)
        cols_to_drop = list(itertools.chain(*cols_to_drop))  # collapses each list into a single list
        cols_to_drop = cols_to_drop + ['Agnc', 'cpdataindex']
        oth_cols = ['oth_OpExp', 'oth_SpPsgr', 'oth_fare', 'oth_psgr', 'oth_rvh',
                    'oth_rvm', 'Yr']  # may as well kill this bad other category while I am at it
        cols_to_drop = cols_to_drop + oth_cols
        df = df.drop(cols_to_drop, axis=1)
        cols = df.columns.tolist()
        return cols

    def empty_row_dropper(self, df):
        '''cuts out all of the empty rows from a dataframe'''
        self.df = df
        for index, row in df.iterrows():
            xrow = row.tolist()
            xrow = xrow[1:]
            if sum(xrow) == 0.0:
                df = df.drop(index=index, axis=0)
        return df

    def sql_sums(self, columns, year1, year2, year3):
        self.columns = columns
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        df_list = []
        for col in columns:
            connection = pymysql.connect(host='UCC1038029',
                                         user='nathans',
                                         password='shalom33',
                                         db='ptsummary_communityproviders',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                # Read a single record
                sql = """SELECT Yr, Sum({}) AS {} from cpdata inner join cp_data_type on cpdata.Agnc = cp_data_type.Agency WHERE cp_data_type.Agency_Type ='CP' and Yr in ('{}', '{}', '{}') Group By Yr Order by Yr""".format(col, col, year1, year2, year3)
                cursor.execute(sql)
                result = cursor.fetchall()
            connection.close()
            res = pd.DataFrame.from_records(result)
            res = res.set_index('Yr')
            df_list.append(res)
        df = pd.concat(df_list, axis = 1)
        df = df.transpose()
        return df

    def build_calculated_fields(self, df):
        '''this function constructs the calculated field categories'''
        self.df = df
        df = df.reset_index()
        df = df.rename(columns={'index': 'category'})
        df = self.sum_formula(df, 'Revenue Vehicle Miles', ['MB_rvm', 'CB_rvm', 'DR_rvm', 'IB_rvm'])
        df = self.sum_formula(df, 'Revenue Vehicle Hours', ['MB_rvh', 'CB_rvh', 'DR_rvh'])
        df = self.sum_formula(df, 'Regular Unlinked Passenger Trips', ['MB_psgr', 'CB_psgr', 'DR_psgr', 'IB_psgr'])
        try:
            locs = df.loc[['MB_SpPsgr', 'CB_SpPsgr', 'DR_Sp_Psgr']]
            df = self.sum_formula(df, 'Sponsored Unlinked Passenger Trips', ['MB_SpPsgr', 'CB_SpPsgr', 'DR_Sp_Psgr'])
        except KeyError:
            pass
        df = self.sum_formula(df, 'Operating Local Sub-Total',
                              ['op_far', 'op_don', 'op_con', 'op_loc', 'op_st', 'op_oth_dgf', 'op_oth'])
        df = self.sum_formula(df, 'Capital Local Sub-Total',
                              ['cap_far', 'cap_don', 'cap_con', 'cap_loc', 'cap_st', 'cap_oth_dgf', 'cap_oth'])
        df = self.sum_formula(df, 'Operating Federal Sub-Total',
                              ['fed_op_5309', 'fed_op_5310_spec', 'fed_op_5310_capop', 'fed_rur_op_5311',
                               'fed_Tribe_op_5311', 'fed_op_5311_capop', 'fed_op_JARC', 'fed_op_5317', 'fed_op_5320',
                               'ARRA_op_5309', 'ARRA_op_5311',
                               'ARRA_op_5311capop', 'ARRA_Tribe_op_5311', 'ARRA_op_GHG', 'fed_op_oth_FTA',
                               'fed_op_oth_FTA_capop', 'fed_op_oth'])
        df = self.sum_formula(df, 'Capital Federal Sub-Total',
                              ['fed_cap_5309', 'fed_cap_5310_spec', 'fed_cap_5310_capop',
                               'fed_rur_cap_5311', 'fed_Tribe_cap_5311', 'fed_cap_5311_capop', 'fed_cap_JARC',
                               'fed_cap_5317', 'fed_cap_5320',
                               'ARRA_cap_5309', 'ARRA_cap_5311', 'ARRA_cap_5311capop', 'ARRA_Tribe_cap_5311',
                               'ARRA_cap_GHG', 'fed_cap_oth_FTA',
                               'fed_cap_oth_FTA_capop', 'fed_cap_oth'])
        df = self.sum_formula(df, 'Total Federal Assistance',
                              ['Operating Federal Sub-Total', 'Capital Federal Sub-Total'])
        df = self.sum_formula(df, 'Total Operating', ['Operating Local Sub-Total', 'Operating Federal Sub-Total'])
        df = self.sum_formula(df, 'Total Capital', ['Capital Local Sub-Total', 'Capital Federal Sub-Total'])
        return df

    def sum_formula(self, df, category_name, category_list):
        self.df = df
        self.category_name = category_name
        self.category_list = category_list
        sumcategory = df[df.category.isin(category_list)].sum(axis = 0)
        if sum(sumcategory.iloc[1:]) == 0.0:
            return df
        else:
            sumcategory['category'] = category_name
            if type(sumcategory) == 'pandas.core.frame.DataFrame':
                sumcategory = sumcategory.iloc[0, :]
                df = df.append(sumcategory, ignore_index = True)
            else:
                df = df.append(sumcategory, ignore_index = True)
            return df

    def percent_change_calculator(self, df, year2, year3):
        self.df = df
        self.year2 = year2
        self.year3 = year3
        # built this to be pretty resilient, so it's able to handle weird shit like zero division errors, etc. this means its kind of slow, and I didn't use good pandas functionality
        current_year = df[year3].tolist()
        previous_year = df[year2].tolist()
        zipped = zip(current_year, previous_year)
        one_year_change = []
        for curr, prev in zipped:
            if (prev == 0 and curr != 0):
                one_year_change.append(1.00)
            elif (prev == 0 and curr == 0):
                one_year_change.append(0.00)
            else:
                percent_change = (curr - prev) / prev
                one_year_change.append(percent_change)
        df['One Year Change (%)'] = one_year_change
        df['One Year Change (%)'] = df['One Year Change (%)'].fillna(0.0)
        df['One Year Change (%)'] = df['One Year Change (%)'] * 100
        df = df.replace(np.inf, 100.00)
        df['One Year Change (%)'] = df['One Year Change (%)'].apply(lambda x: round(x, 2))
        return df

    def fix_floating_zero(self, j):
        '''low level function to cut out the .0 that comes with converting from float to string'''
        self.j = j
        if len(j) > 4:
            j = j.replace('.0', '')
        return j

    def pretty_formatting(self, df, year1, year2, year3):
        self.df = df
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        # adding a comma after every three numbers
        df[year1] = df[year1].apply(lambda x:  "{:,}".format(x))
        df[year2] = df[year2].apply(lambda x: "{:,}".format(x))
        df[year3] = df[year3].apply(lambda x: "{:,}".format(x))
        df[[year1, year2, year3]] = df[[year1, year2, year3]].astype(str)
        rvm = df[df.category.str.contains('rvm')].index.tolist()
        psgr = df[df.category.str.contains('psgr')].index.tolist()
        SpPsgr = df[df.category.str.contains('SpPsgr')].index.tolist()
        rvh = df[df.category.str.contains('rvh')].index.tolist()
        other_list = ['Revenue Vehicle Miles', 'Revenue Vehicle Hours', 'Regular Unlinked Passenger Trips', 'Sponsored Unlinked Passenger Trips']
        other_veh = ['tot_fleet', 'ada_fleet', 'num_vehs', 'num_drivers']
        other_veh_indice_list = []
        for i in other_veh:
            if df[df.category.str.contains(i)].empty == False:
                ix = df[df.category == i].index
                other_veh_indice_list.append(ix)
        other_list_indices = []
        for cat in other_list:
            other_list_indices.append(df[df.category == cat].index.tolist())
        list_indices = list(itertools.chain(*other_list_indices))
        indices = rvm + psgr + SpPsgr + rvh + list_indices + other_veh_indice_list
        cols = [year1, year2, year3]
        df_indices = df.index.tolist()
        df_indices = [x for x in df_indices if x not in indices]
        for col in cols:
            # turns them into dollars
            df[col].loc[df_indices] = df[col].loc[df_indices].apply(lambda x: "${}".format(x))
            df[col] = df[col].map(self.fix_floating_zero)
        return df



    def heading_inserter(self, df, year1, year2, year3):
        self.df = df
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        df = df.append(pd.Series(['Financial Information', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Bus Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['bus_services_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Commuter Bus Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['CB_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Demand Response Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['DR_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Intercity Bus Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        df = df.append(pd.Series(['IB_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Source of Revenue Funds Expended', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Operating_Local', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Total of All Service Modes', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Capital_Local', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Federal Assistance', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Operating_Federal', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Capital_Federal', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Vehicles', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Other Resources', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['operating_info_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['total_services_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['source_of_revenue_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['federal_assistance_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['total_federal_assistance_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['total_capital_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['other_resources_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        return df


    def sort_keys(self, headerdic, value):
        '''this function makes it simple to switch out the '''
        self.value = value
        self.headerdic = headerdic
        if value in headerdic.keys():
            return headerdic[value]
        else:
            return value

    def finalizing_datasheet(self, df):
        '''this function does some final formatting and replacing'''
        self.df = df
        header = pd.read_excel(
            r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\cp_formatting_sheets\cp_header_dictionary.xlsx')
        abbr = header['Abbreviation'].tolist()
        heading = header['Heading'].tolist()
        headerdic = dict(zip(abbr, heading))
        df.category = df.category.map(lambda x: self.sort_keys(headerdic, x))
        empty_row_list = df[df.category.str.contains('empty_row')].index.tolist()
        df.category.loc[empty_row_list] = ''
        subtotals = ['Operating Local Sub-Total', 'Capital Local Sub-Total', 'Capital Federal Sub-Total' 'Operating Federal Sub-Total', 'Operating Federal Sub-Total']
        for sub in subtotals:
            df.category = df.category.str.replace(sub, 'Sub-Total')
        df.category = df.category.str.replace('Capital_Local', 'Capital')
        df.category = df.category.str.replace('Capital_Federal', 'Capital')
        df.category = df.category.str.replace('Operating_Local', 'Operating')
        df.category = df.category.str.replace('Operating_Federal', 'Operating')
        df.category = df.category.str.replace('Capital Federal Sub-Total', 'Sub-Total')
        return df


    def translate_headings(self, df):
        self.df = df
        header = pd.read_excel(
            r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\cp_formatting_sheets\cp_header_dictionary.xlsx')
        abbr = header['Abbreviation'].tolist()
        heading = header['Heading'].tolist()
        headerdic = dict(zip(abbr, heading))
        df.category = df.category.map(lambda x: headerdic[x])
        return df

    def template_sorter(self, df):
        self.df = df
        columns = pd.read_excel(
            r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\cp_formatting_sheets\cp_template_sheet.xlsx')
        order = columns['columnorder'].tolist()
        dfcategoryorder = df.category.tolist()
        adjustedorder = [i for i in order if i in dfcategoryorder]
        df = df.set_index('category')
        df = df.reindex(index=adjustedorder)
        df = df.reset_index()
        return df

    def round(self, df, year1, year2, year3):
        self.df = df
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        cols = [year1, year2, year3]
        for col in cols:
            df[col] = df[col].apply(lambda x: round(x, 0 ))
        return df


    def random_text_generator(self, year3):
        self.year3 = year3
        connection = pymysql.connect(host='UCC1038029',
                                     user='nathans',
                                     password='shalom33',
                                     db='ptsummary_communityproviders',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            # Read a single record
            sql1 = '''SELECT SUM(MB_psgr+ DR_psgr + CB_psgr) as Passenger_Trips, Sum(MB_rvh+CB_rvh + DR_rvh) As Revenue_Vehicle_Hours, Sum(MB_rvm + CB_rvm + CB_rvm) as Revenue_Vehicle_Miles 
         FROM cpdata Where Yr = {} Group BY Yr;'''.format(year3)
            sql2 = '''SELECT Count(Distinct(Agnc)) AS Number FROM cpdata inner join cp_data_type on cpdata.Agnc = cp_data_type.Agency where cp_data_type.Agency_Type ='CP' and Yr = {};'''.format(year3)

            cursor.execute(sql1)
            result = cursor.fetchall()
            cursor.execute(sql2)
            agency_nums = cursor.fetchall()
        connection.close()
        count = agency_nums[0]['Number']
        result = result[0]
        res = list(result.values())
        res = ["{:,}".format(i) for i in res]
        res = [i.replace('.0', '') for i in res]
        psgr = 'In {}, the {} community transportation providers reported a total of {} passenger trips.'.format(year3, count, res[0])
        rvh = 'The {} community transportation providers reported {} hours of vehicle revenue service for the {} reporting year.'.format(count, res[1], year3)
        rvm = 'The {} community transportation providers drove {} revenue vehicle miles in {}.'.format(count, res[2], year3)
        final_list = [(psgr,), (rvh,), (rvm,)]
        return final_list

    def to_csv(self, a_list, path):
        self.a_list = a_list
        self.path = path
        with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=',')
                for item in a_list:
                    writer.writerow(item)

class IB_SW_Rollup():
    def __init__(self, year1, year2, year3):
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
    def ib_sql_sums(self, year1, year2, year3):
        columns = ['IB_rvm', 'IB_psgr', 'fed_rur_op_5311']
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        df_list = []
        for col in columns:
            connection = pymysql.connect(host='UCC1038029',
                                         user='nathans',
                                         password='shalom33',
                                         db='ptsummary_communityproviders',
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                # Read a single record
                sql = """SELECT Yr, Sum({}) AS {} from cpdata inner join cp_data_type on cpdata.Agnc = cp_data_type.Agency WHERE cp_data_type.Agency_Type ='IB' and Yr in ('{}', '{}', '{}') Group By Yr Order by Yr""".format(
                    col, col, year1, year2, year3)
                cursor.execute(sql)
                result = cursor.fetchall()
            connection.close()
            res = pd.DataFrame.from_records(result)
            res = res.set_index('Yr')
            df_list.append(res)
        df = pd.concat(df_list, axis=1)
        df = df.transpose()
        return df

    def build_calculated_fields(self, df):
        '''this function constructs the calculated field categories'''
        self.df = df
        df = df.reset_index()
        df = df.rename(columns={'index': 'category'})
        df = self.sum_formula(df, 'Revenue Vehicle Miles', ['MB_rvm', 'CB_rvm', 'DR_rvm', 'IB_rvm'])
        df = self.sum_formula(df, 'Regular Unlinked Passenger Trips', ['MB_psgr', 'CB_psgr', 'DR_psgr', 'IB_psgr'])
        df = self.sum_formula(df, 'Total Federal Assistance', ['fed_rur_op_5311'])
        df = self.sum_formula(df, 'Total Operating', ['fed_rur_op_5311'])
        return df

    def sum_formula(self, df, category_name, category_list):
        self.df = df
        self.category_name = category_name
        self.category_list = category_list
        sumcategory = df[df.category.isin(category_list)].sum(axis=0)
        if sum(sumcategory.iloc[1:]) == 0.0:
            return df
        else:
            sumcategory['category'] = category_name
            if type(sumcategory) == 'pandas.core.frame.DataFrame':
                sumcategory = sumcategory.iloc[0, :]
                df = df.append(sumcategory, ignore_index=True)
            else:
                df = df.append(sumcategory, ignore_index=True)
            return df

    def call_sw_cp_class_methods(self, year1, year2, year3, df):
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        self.df = df
        df = statewide_cp_Datasheet.percent_change_calculator(self, df, year2, year3)
        df = statewide_cp_Datasheet.round(self, df, year1, year2, year3)
        df = statewide_cp_Datasheet.pretty_formatting(self, df, year1, year2, year3)
        return df

    def ib_heading_inserter(self, df, year1, year2, year3):
        self.df = df
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        df = df.append(pd.Series(['Financial Information', year1, year2, year3, 'One Year Change (%)'],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Intercity Bus Services', '', '', '', ''],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(
            pd.Series(['IB_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),
            ignore_index=True)
        df = df.append(pd.Series(['Total of All Service Modes', '', '', '', ''],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Federal Assistance', '', '', '', ''],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Operating_Federal', '', '', '', ''],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['total_services_empty_row', '', '', '', ''],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['federal_assistance_empty_row', '', '', '', ''],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['total_federal_assistance_empty_row', '', '', '', ''],
                                 ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        return df

    def call_more_sw_cp_class_methods(self, year1, year2, year3, df):
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        self.df = df
        df = statewide_cp_Datasheet.template_sorter( self, df)
        df = statewide_cp_Datasheet.finalizing_datasheet(self, df)
        return df

    def fix_floating_zero(self, j):
        '''low level function to cut out the .0 that comes with converting from float to string'''
        self.j = j
        if len(j) > 4:
            j = j.replace('.0', '')
        return j

    def sort_keys(self, headerdic, value):
        '''this function makes it simple to switch out the '''
        self.value = value
        self.headerdic = headerdic
        if value in headerdic.keys():
            return headerdic[value]
        else:
            return value


def main(year1, year2, year3):
    sw_cp_ds =statewide_cp_Datasheet(year1, year2, year3)
    results = sw_cp_ds.pull_from_db(year1, year2, year3)
    columns_to_pull = sw_cp_ds.clean_results(results)
    df = sw_cp_ds.sql_sums(columns_to_pull, year1, year2, year3)
    df = sw_cp_ds.build_calculated_fields(df)
    df = sw_cp_ds.empty_row_dropper(df)
    df = sw_cp_ds.percent_change_calculator(df, year2, year3)
    df = sw_cp_ds.round(df, year1, year2, year3 )
    df = sw_cp_ds.pretty_formatting(df, year1, year2, year3)
    df['One Year Change (%)'] = df['One Year Change (%)'].apply(lambda x: format(x, '.2f'))
    df = sw_cp_ds.heading_inserter(df, year1, year2, year3)
    df = sw_cp_ds.template_sorter(df)
    df = sw_cp_ds.finalizing_datasheet(df)
    df = df.rename(columns={'category': 'Annual Operating Information'})
    df = df.replace('$0.0', '$0')
    df.to_excel(r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\testfolder\cp\{} CP Compiled Years.xlsx'.format(year3),
                   index=False, columns=None)
    random_text = sw_cp_ds.random_text_generator(year3)
    sw_cp_ds.to_csv(random_text, r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\testfolder\cp\CP {} Random Text.csv'.format(year3))
    isr = IB_SW_Rollup(year1, year2, year3)
    df = isr.ib_sql_sums(year1, year2, year3)
    df = isr.build_calculated_fields(df)
    df = isr.call_sw_cp_class_methods(year1, year2, year3, df)
    df['One Year Change (%)'] = df['One Year Change (%)'].apply(lambda x: format(x, '.2f'))
    df = isr.ib_heading_inserter(df, year1, year2, year3)
    df = isr.call_more_sw_cp_class_methods(year1, year2, year3, df)
    df = df.rename(columns={'category': 'Annual Operating Information'})
    df = df.replace('$0.0', '$0')
    df.to_excel(
        r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\testfolder\cp\{} IB Compiled Years.xlsx'.format(
            year3),index=False, columns=None)








if __name__ == "__main__":
    main(2015, 2016, 2017)