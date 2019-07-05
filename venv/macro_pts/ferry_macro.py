import pandas as pd
import numpy as np
import pymysql.cursors
import itertools
import csv



class Datasheet():
    # this is the datasheet class; it contains all the methods for building a datasheet
    # initialized a set of cp specific modes
    def __init__(self, agency, year1, year2, year3):
        self.agency = agency
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3

    def pull_from_db(self, agency, year1, year2, year3):
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        connection = pymysql.connect(host='UCC1038029',
                                     user='nathans',
                                     password='shalom33',
                                     db='ptsummary_ferries',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            # Read a single record
            sql = """SELECT * from ferrydata WHERE Yr in ('{}', '{}', '{}') And Agnc = '{}'""".format(year1, year2, year3, agency)
            cursor.execute(sql)
            result = cursor.fetchall()

        connection.close()
        return result

    def clean_dataframe(self, results,cp):
        self.results = results
        self.cp = cp
        df = pd.DataFrame.from_records(results)
        df = df.drop(['Agnc', 'ferryindex'], axis = 1)
        df = df.set_index('Yr')
        df = df.transpose()
        df = self.empty_row_dropper(df)
        return df

    def empty_row_dropper(self, df):
        '''cuts out all of the empty rows from a dataframe'''
        self.df = df
        for index, row in df.iterrows():
            xrow = row.tolist()
            if sum(xrow) == 0.0:
                df = df.drop(index=index, axis=0)
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

    def revenue_sum_formulas(self, df):
        '''This function builds sum formulas for calculated types of data'''
        self.df = df
        df = df.reset_index()
        df = df.rename(columns={'index': 'category'})
        df = self.sum_formula(df, 'Farebox Revenues (Passenger, Auto & Driver Fares)', ['fare', 'rev'])
        df = self.sum_formula(df, 'Other Operating Sub-Total', ['other_advertising', 'oth_gas_tax', 'oth_rev', 'oth_prop_tax', 'other_int', 'other_rev'])
        df = self.sum_formula(df, 'Total (Excludes Capital Revenues)', ['sales_tax', 'dgf_prop_tax','ut_tax', 'mvet', 'Farebox Revenues (Passenger, Auto & Driver Fares)',
            'fta_5307_op' ,'fta_5307_prv', 'fta_5311_op', 'fta_5316_op', 'fta_other_op', 'def_grnt', 'st_op_rmg',  'st_op_regmg',
            'st_op_sng', 'st_op_ste', 'st_op_other', 'st_gas_tax', 'st_oth_tax', 'Other Operating Sub-Total', 'deficitreim_grnt'])
        df = self.sum_formula(df, 'Farebox Revenues', ['rev'])
        df = self.sum_formula(df, 'Total Federal Capital',['fta_5307_grnt', 'fta_5309_grnt', 'fta_5310_grnt', 'fta_5311_grnt',
                                                           'fta_5337_grnt', 'fta_5316_grnt', 'Fstp_grnt', 'fed_other_grnt'])
        df = self.sum_formula(df, 'Total State Capital',
                              ['st_cg_rmg', 'st_cg_regmg', 'st_cg_sng', 'st_cg_ste', 'st_ct_van', 'st_cg_other'])
        df = self.sum_formula(df, 'Total Local Capital',['local_cap_invest', 'oth_loc_cap'])
        df = self.sum_formula(df, 'Total Other Expenditures', ['ls_rent_ag', 'oth_recon'])
        df = self.sum_formula(df, 'Total Local Revenues', ['Other Operating Sub-Total','sales_tax', 'dgf_prop_tax',
        'ut_tax', 'mvet', 'Farebox Revenues'])
        df = self.sum_formula(df, 'Total State Revenues', ['def_grnt', 'st_op_rmg', 'st_op_regmg', 'st_op_sng',
            'st_op_ste', 'st_op_other', 'st_gas_tax', 'st_oth_tax'])
        df = self.sum_formula(df, 'Total Federal Revenues', ['fta_5307_op', 'fta_5307_prv', 'fta_5311_op', 'fta_5316_op',
        'fta_other_op'])
        df = self.sum_formula(df, 'Total Operating',['Total Local Revenues', 'Total State Revenues', 'Total Federal Revenues'])
        df = self.sum_formula(df, 'Total Local Investment', ['Total Local Capital'])
        df = self.sum_formula(df, 'Total State Investment', ['Total State Capital'])
        df = self.sum_formula(df, 'Total Federal Investment', ['Total Federal Capital'])
        df = self.sum_formula(df, 'Total Capital', ['Total Local Investment', 'Total State Investment', 'Total Federal Investment'])
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
        df[year1] = df[year1].apply(lambda x: round(x, 0))
        df[year2] = df[year2].apply(lambda x: round(x, 0))
        df[year3] = df[year3].apply(lambda x: round(x, 0))
        df[year1] = df[year1].apply(lambda x:  "{:,}".format(x))
        df[year2] = df[year2].apply(lambda x: "{:,}".format(x))
        df[year3] = df[year3].apply(lambda x: "{:,}".format(x))
        df[[year1, year2, year3]] = df[[year1, year2, year3]].astype(str)
        bad_indices = ['rvh', 'tvh', 'rvm', 'tvm', 'psgrtrips', 'vehtrips', 'dfc', 'bdfc', 'fte']
        df_indices = df.index.tolist()
        df_indices = [x for x in df_indices if x not in bad_indices]
        cols = [year1, year2, year3]
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

    def heading_inserter(self, df, year1, year2, year3):
        self.df = df
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        df = df.append(pd.Series(['Financial Information', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Passenger Ferry Services', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        df = df.append(pd.Series(['ferry_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Operating Related Revenues', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        federal = ['fta_5307_grnt', 'fta_5309_grnt', 'fta_5310_grnt', 'fta_5311_grnt','fta_5337_grnt', 'fta_5316_grnt', 'Fstp_grnt', 'fed_other_grnt']
        if df[df.category.isin(federal)].empty == False:
            df = df.append(pd.Series(['Federal Capital Grant Revenues', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.isin(['st_cg_rmg', 'st_cg_regmg', 'st_cg_sng', 'st_cg_ste', 'st_ct_van', 'st_cg_other'])].empty == False:
            df = df.append(pd.Series(['State Capital Grant Revenues', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.isin(['local_cap_invest', 'oth_loc_cap'])].empty == False:
            df = df.append(pd.Series(['Local Capital Expenditures', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.isin(['ls_rent_ag', 'oth_recon'])].empty == False:
            df = df.append(pd.Series(['Other Expenditures', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Operating', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        if df[df.category.isin(['Total Local Investment', 'Total State Investment', 'Total Federal Investment'])].empty == False:
            df = df.append(pd.Series(['Capital', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Total Funds by Source', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['Other Resources', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['operating_info_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['operating_related_revenues_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['fed_cap_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['state_cap_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['local_cap_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['total_other_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['operating_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        df = df.append(pd.Series(['capital_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        return df


    def template_sorter(self, df):
        self.df = df
        columns = pd.read_excel(
            r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\ferry_formatting_sheets\ferrytemplates.xlsx')
        order = columns['columnorder'].tolist()
        dfcategoryorder = df.category.tolist()
        adjustedorder = [i for i in order if i in dfcategoryorder]
        df = df.set_index('category')
        df = df.reindex(index=adjustedorder)
        df = df.reset_index()
        return df

    def finalizing_datasheet(self, df):
        '''this function does some final formatting and replacing'''
        self.df = df
        header = pd.read_excel(
            r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\ferry_formatting_sheets\ferry_header_dictionary.xlsx')
        abbr = header['Abbreviation'].tolist()
        heading = header['Heading'].tolist()
        headerdic = dict(zip(abbr, heading))
        df.category = df.category.map(lambda x: self.sort_keys(headerdic, x))
        empty_row_list = df[df.category.str.contains('empty_row')].index.tolist()
        df.category.loc[empty_row_list] = ''
        subtotals = ['Operating Local Sub-Total', 'Capital Local Sub-Total',
                 'Capital Federal Sub-Total' 'Operating Federal Sub-Total', 'Operating Federal Sub-Total']
        for sub in subtotals:
            df.category = df.category.str.replace(sub, 'Sub-Total')
        df.category = df.category.str.replace('Capital_Local', 'Capital')
        df.category = df.category.str.replace('Capital_Federal', 'Capital')
        df.category = df.category.str.replace('Operating_Local', 'Operating')
        df.category = df.category.str.replace('Operating_Federal', 'Operating')
        return df



    def random_text_generator(self, df, year2, year3, ferry):
        self.df = df
        self.year2 = year2
        self.year3 = year3
        self.ferry = ferry

        fancy_ferry_dictionary = {'Guemes': 'Guemes Island Ferry', 'Lummi': 'Lummi Island Ferry', 'Keller': 'Keller Ferry', 'King': 'King County Water Taxi', 'Kitsap': 'Kitsap Transit Foot Ferry',
                                  'Pierce': 'Pierce County Ferry System', 'Wahkiakum': 'Wahkiakum Ferry', 'WSF': 'Washington State Ferries'}


        ferry = fancy_ferry_dictionary[ferry]
        psgr = df.loc['psgrtrips'][year3]
        psgrtrip_change = df.loc['psgrtrips']['One Year Change (%)']
        try:
            vehtrips = df.loc['vehtrips'][year3]
            vehtrip_change = df.loc['vehtrips']['One Year Change (%)']
            if (psgrtrip_change > 0) and (vehtrip_change > 0):
                random_text = "In {}, the {} provided service to {} passengers (up {} percent from {}) and {} vehicles (up {} percent from {}).".format(
                    year3,
                    ferry, psgr, psgrtrip_change, year2, vehtrips, vehtrip_change, year2)
                return random_text
            else:
                random_text = "In {}, the {} provided service to {} passengers (down {} percent from {}) and {} vehicles (down {} percent from {}).".format(
                    year3,
                    ferry, psgr, psgrtrip_change, year2, vehtrips, vehtrip_change, year2)
                return random_text
        except KeyError:
            if psgrtrip_change > 0:
                random_text  ="In {}, the {} provided service to {} passengers (up {} percent from {}).".format(year3, ferry, psgr, psgrtrip_change, year2)
                return random_text
            else:
                random_text = "In {}, the {} provided service to {} passengers (down {} percent from {}).".format(year3, ferry, psgr, psgrtrip_change, year2)
                return random_text





def main(year1, year2, year3, path):
    ferry_list = ['Guemes', 'Keller', 'King', 'Kitsap', 'Pierce', 'Lummi', 'Wahkiakum', 'WSF']
    random_text_list = []
    for ferry in ferry_list:
        print(ferry)
        ds = Datasheet(ferry, year1, year2, year3)
        df = ds.pull_from_db(ferry, year1, year2, year3)
        df = ds.clean_dataframe(df, ferry)
        df = ds.revenue_sum_formulas(df)
        df = ds.percent_change_calculator(df, year2, year3)
        df = df.set_index('category')
        df = ds.pretty_formatting(df, year1, year2, year3)
        random_text = ds.random_text_generator(df, year2, year3, ferry)
        random_text_list.append(random_text)
        df = df.reset_index()
        df['One Year Change (%)'] = df['One Year Change (%)'].apply(lambda x: format(x, '.2f'))
        df = ds.heading_inserter(df, year1, year2, year3)
        df = ds.template_sorter(df)
        df = ds.finalizing_datasheet(df)
        df = df.rename(columns={'category': 'Operating Information'})
        df = df.replace('$0.0', '$0')
        df.to_excel(path + '\\'+ '{}.xlsx'.format(ferry), index = False)
    randomtext = pd.DataFrame(random_text_list)
    randomtext.to_excel(path + '\\'+ '{} Random Text.xlsx'.format(year3), index = False)


if __name__ == "__main__":
    main(2015, 2016, 2017, r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\testfolder\ferry')