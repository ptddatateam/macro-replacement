import pandas as pd
import numpy as np
import pymysql.cursors
import itertools
import datetime
import os
# I imported a few things



class Datasheet():
    # this is the datasheet class; it contains all the methods for building a datasheet
    # initialized a set of cp specific modes
    mode_list = ['MB', 'CB', 'DR', 'IB']
    def __init__(self, agency, year1, year2, year3):
        self.agency = agency
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3

    def pull_from_db(self, agency, year1, year2, year3):
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        self.agency = agency
        connection = pymysql.connect(host='UCC1038029',
                                     user='nathans',
                                     password='shalom33',
                                     db='ptsummary_communityproviders',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            # Read a single record
            sql = """SELECT * from cpdata WHERE Agnc = '{}' and Yr in ('{}', '{}', '{}')""".format(agency, year1, year2, year3)
            cursor.execute(sql)
            result = cursor.fetchall()

        connection.close()
        return result

    def clean_dataframe(self, results,cp):
        self.results = results
        self.cp = cp
        df = pd.DataFrame.from_records(results)
        bad_data = ['desc'] # strips out some bad data categories, TODO should fix this in db design
        cols_to_drop = []
        for bad in bad_data:
            col_list  = df.columns[df.columns.str.contains(bad)]
            cols_to_drop.append(col_list)
        cols_to_drop = list(itertools.chain(*cols_to_drop)) # collapses each list into a single list
        cols_to_drop = cols_to_drop + ['Agnc', 'cpdataindex']
        #oth_cols = ['oth_OpExp', 'oth_SpPsgr', 'oth_fare', 'oth_psgr', 'oth_rvh', 'oth_rvm'] # may as well kill this bad other category while I am at it
        #cols_to_drop = cols_to_drop + oth_cols
        df = df.drop(cols_to_drop, axis =1 )
        df = df.set_index('Yr')
        df = df.transpose()
        df = self.empty_row_dropper(df)
        return df

    def empty_row_dropper(self, df):
        '''cuts out all of the empty rows from a dataframe'''
        self.df = df
        for index, row in df.iterrows():
            xrow = row.tolist()
            xrow = xrow[1:]
            for i in xrow:
                print(i)
            if sum(xrow) == 0.0:
                df = df.drop(index = index, axis = 0)
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


    def heading_inserter(self, df, year1, year2, year3):
        self.df = df
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        df = df.append(pd.Series(['Financial Information', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.str.contains('MB')].empty == False:
            df = df.append(pd.Series(['Bus Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
            df = df.append(pd.Series(['bus_services_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.str.contains('CB')].empty == False:
            df = df.append(pd.Series(['Commuter Bus Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
            df = df.append(pd.Series(['CB_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.str.contains('DR')].empty == False:
            df = df.append(pd.Series(['Demand Response Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
            df = df.append(pd.Series(['DR_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.str.contains('IB')].empty == False:
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

    def revenue_sum_formulas(self, df):
        '''This function builds sum formulas for calculated types of data'''
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
        df = self.sum_formula(df, 'Operating Local Sub-Total', ['op_far', 'op_don', 'op_con', 'op_loc', 'op_st', 'op_oth_dgf', 'op_oth'])
        df = self.sum_formula(df, 'Capital Local Sub-Total', ['cap_far', 'cap_don', 'cap_con', 'cap_loc', 'cap_st', 'cap_oth_dgf', 'cap_oth'])
        df = self.sum_formula(df, 'Operating Federal Sub-Total', ['fed_op_5309', 'fed_op_5310_spec', 'fed_op_5310_capop', 'fed_rur_op_5311',
            'fed_Tribe_op_5311', 'fed_op_5311_capop', 'fed_op_JARC', 'fed_op_5317', 'fed_op_5320', 'ARRA_op_5309', 'ARRA_op_5311',
            'ARRA_op_5311capop', 'ARRA_Tribe_op_5311', 'ARRA_op_GHG', 'fed_op_oth_FTA', 'fed_op_oth_FTA_capop', 'fed_op_oth'])
        df = self.sum_formula(df, 'Capital Federal Sub-Total', ['fed_cap_5309', 'fed_cap_5310_spec', 'fed_cap_5310_capop',
            'fed_rur_cap_5311', 'fed_Tribe_cap_5311', 'fed_cap_5311_capop', 'fed_cap_JARC', 'fed_cap_5317', 'fed_cap_5320',
            'ARRA_cap_5309', 'ARRA_cap_5311', 'ARRA_cap_5311capop', 'ARRA_Tribe_cap_5311', 'ARRA_cap_GHG', 'fed_cap_oth_FTA',
            'fed_cap_oth_FTA_capop', 'fed_cap_oth'])
        df = self.sum_formula(df, 'Total Federal Assistance', ['Operating Federal Sub-Total', 'Capital Federal Sub-Total'])
        df = self.sum_formula(df, 'Total Operating', ['Operating Local Sub-Total', 'Operating Federal Sub-Total'])
        df = self.sum_formula(df, 'Total Capital', ['Capital Local Sub-Total', 'Capital Federal Sub-Total'])
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
        return df




def main(year1, year2, year3, path):
    cp_list = ['Central Washington Airporter Gold', 'Central Washington Airporter Grape',
               'Coastal Community Action Program', 'Heckman Motors, Inc', 'Hopesource',
               'Klickitat County Senior Services',
               'Lower Columbia Community Action Council', 'Mt. Si Senior Center',
               'Northwest Stagelines Inc dba Northwestern Trailway',
               'Okanogan County Transportation & Nutrition',
               'People for People Moses Lake', 'People for People Yakima', 'Rural Resources Community Action',
               'Senior Services of Snohomish County', 'Skamania County Senior Services',
               'Smith6 LLC', 'Special Mobility Services', 'Thurston Regional Planning Council',
               'Wahkiakum County Health & Human Services', 'White Pass Community Services Coalition']
    for cp in cp_list:
        print(cp)
        ds = Datasheet(cp, year1, year2, year3)
        cp_df = ds.pull_from_db(cp, year1, year2, year3)
        cp_df = ds.clean_dataframe(cp_df, cp)
        cp_df = cp_df.fillna(0.0)
        cp_df = ds.revenue_sum_formulas(cp_df)
        cp_df = ds.empty_row_dropper(cp_df)
        cp_df = ds.percent_change_calculator(cp_df, year2, year3)
        cp_df = ds.pretty_formatting(cp_df, year1, year2, year3)
        cp_df['One Year Change (%)'] = cp_df['One Year Change (%)'].apply(lambda x: format(x, '.2f'))
        cp_df = ds.heading_inserter(cp_df, year1, year2, year3)
        cp_df = ds.template_sorter(cp_df)
        cp_df = ds.finalizing_datasheet(cp_df)
        cp_df = cp_df.rename(columns = {'category': 'Operating Information'})
        cp_df = cp_df.replace('$0.0', '$0')
        date = datetime.date.today().strftime("%m-%d")
        if os.path.exists(path + '\\community-providers-{}'.format(date)) == False:
            os.mkdir(path + '\\community-providers-{}'.format(date))
        cp_df.to_excel(path + '\\community-providers-{}\\'.format(date) + '{}.xlsx'.format(cp), index = False)


