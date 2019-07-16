import pandas as pd
import pymysql.cursors
import numpy as np
import sql_scripts_for_summary as sqlscripts
from xlsxwriter.utility import xl_rowcol_to_cell
pd.options.display.float_format = '{:,}'.format


class statewide_rollup_sheets():

    def __init__(self, year_of_report):
        self.year_of_report = year_of_report
        self.transit_list = ['asotin', 'ben franklin', 'Central Transit', 'clallam', 'columbia', 'community', 'ctran', 'CUBS', 'everett', 'garfield',
                    'grant', 'grays', 'intercity', 'island', 'jefferson', 'king', 'kitsap', 'link', 'mason', 'Okanogan County Transit Authority', 'pacific', 'pierce', 'pullman',
                             'selah', 'skagit', 'sound', 'spokane', 'twin', 'union gap', 'valley', 'whatcom', 'yakima']
        self.formal_report_list = ['Asotin County Transit', 'Ben Franklin Transit', 'Central Transit', 'Clallam Transit System', 'Columbia County Public Transportation',
        'Community Transit', 'C-TRAN', 'RiverCities Transit', 'Everett Transit', 'Garfield County Transportation Authority',  'Grant Transit Authority',
        'Grays Harbor Transportation Authority', 'Intercity Transit', 'Island Transit', 'Jefferson Transit Authority', 'King County Metro',
        'Kitsap Transit',  'Link Transit', 'Mason County Transportation Authority', 'TranGo', 'Pacific Transit System', 'Pierce Transit', 'Pullman Transit',
        'City of Selah Transportation Service',  'Skagit Transit', 'Sound Transit', 'Spokane Transit Authority', 'Twin Transit', 'Union Gap Transit',
        'Valley Transit', 'Whatcom Transportation Authority', 'Yakima Transit']
        self.transit_dic = dict(zip(self.transit_list, self.formal_report_list))
        print('It begins')

    def populate_sql_script(self, year, script):
        self.year = year
        self.scrip =script
        script = script.format(year)
        return script


    def run_sql_script(self, sql_script):
        self.sql_script = sql_script
        connection = pymysql.connect(host='UCC1038029',
                                     user='nathans',
                                     password='shalom33',
                                     db='ptsummary_transit',
                                     cursorclass=pymysql.cursors.DictCursor)
        df = pd.read_sql(sql_script, con=connection)
        return df
    def deduplicate(self, df):
        self.df = df
        df = df.transpose()
        df = df.drop_duplicates()
        df = df.transpose()
        return  df

    def formulate_total_and_sub_total(self, df):
        self.df = df
        sounddata = df[df.Agnc == 'Sound Transit']
        totals = df.sum(axis = 0)
        totals.Agnc = 'Statewide Obligation Totals'
        df = df[df.Agnc != 'Sound Transit']
        subtotals = df.sum(axis =0 )
        subtotals.Agnc = 'Sub-Totals'
        df = df.append(subtotals, ignore_index = True)
        df =pd.concat([df, sounddata], axis = 0)
        df = df.append(totals, ignore_index = True)
        return df


    def sql_script(self, year_of_report, script):
        self.year_of_report = year_of_report
        self.script = script
        script = self.populate_sql_script(year_of_report, script)
        df = self.run_sql_script(script)
        return df


    def generate_year_list(self, year, length):
        year_list = []
        while length >= 0:
            adjyear = year -length
            year_list.append(adjyear)
            length = length -1
        return year_list
    def fix_floating_zero_single(self, j):
        '''low level function to cut out the .00 that comes with converting from float to string'''
        self.j = j
        j = j.replace('.0', '')
        return j


    def sw_invest_table(self, year_of_report, df, path):
        self.df = df
        self.year_of_report = year_of_report
        inv_df = df[['Yr', 'Operating_Investments', 'Local_Capital_Investment', 'State_Capital_Investment', 'Federal_Capital_Investment', 'Other_Investment']]
        inv_df = inv_df.set_index('Yr')
        inv_df = inv_df.transpose()
        sorted_columns = inv_df.columns.sort_values(ascending=True)
        inv_df = inv_df[sorted_columns]
        sums = inv_df.sum(axis=0)
        inv_df = inv_df.reset_index()
        inv_df = inv_df.append(sums, ignore_index=True)
        inv_df['index'] = inv_df['index'].fillna('Total')
        inv_df = inv_df.rename(columns={'index': 'Total Investments'})
        percent_of_total = inv_df[year_of_report].loc[:4].tolist()
        percent_of_total = [i / inv_df[year_of_report].loc[5] for i in percent_of_total]
        percent_of_total = [round(i * 100, 2) for i in percent_of_total]
        percent_of_total.append(np.nan)
        inv_df['% of Total'] = percent_of_total
        inv_df = inv_df.fillna('')
        inv_df['Total Investments'] = inv_df['Total Investments'].str.replace('_', ' ')
        cols = inv_df.columns.tolist()
        cols = cols[1:7]
        for col in cols:
            inv_df[col] = inv_df[col].apply(lambda x: "{:,}".format(x))
            inv_df[col] = inv_df[col].apply(lambda x: "${}".format(x))
            inv_df[col] = inv_df[col].map(self.fix_floating_zero_single)
        inv_cols = inv_df.columns.tolist()
        inv_cols[1:7] = [int(i) for i in inv_cols[1:7]]
        inv_df.columns = inv_cols
        inv_df.to_excel(path + '\\{} SW Investments.xlsx'.format(year_of_report), index=False)


    def sw_rev_table(self, year_of_report, path):
        self.year_of_report = year_of_report
        year_list = self.generate_year_list(year_of_report, 5)
        # convert the list to a tuple
        year_list = tuple(year_list)
        inv_rev = self.populate_sql_script(year_list, sqlscripts.sw_invest_rev)
        df_rev = self.run_sql_script(inv_rev)
        inv_td = self.populate_sql_script(year_list, sqlscripts.sw_invest_td)
        df_td = self.run_sql_script(inv_td)
        inv_exp = self.populate_sql_script(year_list, sqlscripts.sw_invest_exp)
        df_exp = self.run_sql_script(inv_exp)
        df = pd.concat([df_td, df_exp, df_rev], axis=1)
        df = self.deduplicate(df)
        self.sw_invest_table(year_of_report, df, path) # rolled this all into a separate function, when I come and clean it up, I may put revenues in their own function as well
        df['Local_Revenues'] = df['Farebox_Revenues'] + df['Local_Tax']
        rev_df = df[['Local_Revenues', 'State_Revenue', 'Federal_Revenue', 'Yr']]
        rev_df =rev_df.set_index('Yr')
        rev_df = rev_df.transpose()
        sorted_columns = rev_df.columns.sort_values(ascending=True)
        rev_df = rev_df[sorted_columns]
        sums = rev_df.sum(axis = 0)
        rev_df = rev_df.reset_index()
        rev_df = rev_df.append(sums, ignore_index = True)
        rev_df['index'] = rev_df['index'].fillna('Total')
        rev_df =rev_df.rename(columns = {'index':'Total Revenues'})
        percent_of_total = rev_df[year_of_report].loc[:2].tolist()
        percent_of_total = [i/rev_df[year_of_report].loc[3] for i in percent_of_total]
        percent_of_total = [round(i*100, 2) for i in percent_of_total]
        percent_of_total.append(np.nan)
        rev_df['% of Total'] = percent_of_total
        rev_df = rev_df.fillna('')
        rev_df['Total Revenues'] = rev_df['Total Revenues'].str.replace('_', ' ')
        cols = rev_df.columns.tolist()
        cols = cols[1:7]
        for col in cols:
            rev_df[col] = rev_df[col].apply(lambda x: "{:,}".format(x))
            rev_df[col] = rev_df[col].apply(lambda x: "${}".format(x))
            rev_df[col] = rev_df[col].map(self.fix_floating_zero_single)
        rev_cols = rev_df.columns.tolist()
        rev_cols[1:7] = [int(i) for i in rev_cols[1:7]]
        rev_df.columns = rev_cols
        rev_df.to_excel(path +'\\{} SW Revenues.xlsx'.format(year_of_report), index=False)


    def sw_fin_exps_stats(self, year_of_report, transit_list, transit_dic, path):
        self.transit_dic = transit_dic
        self.transit_list = transit_list
        self.year_of_report = year_of_report
        fexp_td = self.populate_sql_script(year_of_report, sqlscripts.sw_fin_exp_transit_data)
        df_td = self.run_sql_script(fexp_td)
        fexp_rev = self.populate_sql_script(year_of_report, sqlscripts.sw_fin_exp_revenues)
        df_rev = self.run_sql_script(fexp_rev)
        fexp_exp = self.populate_sql_script(year_of_report, sqlscripts.sw_fin_exp_expenses)
        df_exp = self.run_sql_script(fexp_exp)
        df = pd.concat([df_td, df_exp, df_rev], axis = 1)
        df = self.deduplicate(df)
        df['Capital_Expenses'] = df['Capital_Expenses'] + df['local_cap']
        df = df.drop('local_cap', axis  =1)
        df = df[df['Agnc'].isin(transit_list)]
        df['Total_Annual_Expenses'] = df['Fixed_Route'] + df['Route_Deviated'] + df['Demand_Response'] + df['Vanpool'] + df['All_Rail_Modes'] + df['Capital_Expenses'] + df['Other']
        columns = ['Agnc', 'Fixed_Route', 'Route_Deviated', 'Demand_Response', 'Vanpool',
       'All_Rail_Modes', 'Debt_Service', 'Other',
       'Capital_Expenses', 'Total_Annual_Expenses', 'Depreciation']
        df = df[columns]
        df.columns = df.columns.str.replace('_', ' ')
        df.Agnc = df.Agnc.apply(lambda x: transit_dic[x])
        df = self.formulate_total_and_sub_total(df)
        cols = df.columns.tolist()
        cols = cols[1:]
        for col in cols:
            df[col] = df[col].apply(lambda x: "{:,}".format(x))
            df[col] = df[col].apply(lambda x: "${}".format(x))
            df[col] = df[col].map(self.fix_floating_zero_single)
        df = df.rename(columns = {'Agnc': 'Operating and Capital Expenses'})
        df.to_excel(path + '\\{} SW Fin Exps Stats.xlsx'.format(year_of_report), index=False)

    def sw_fin_rev_stats(self, year_of_report, transit_list, transit_dic, path):
        self.year_of_report = year_of_report
        self.transit_list = transit_list
        self.transit_dic = transit_dic
        script_rev = self.populate_sql_script(year_of_report, sqlscripts.sw_fin_revs_revenues)
        df_rev = self.run_sql_script(script_rev)
        script_td = self.populate_sql_script(year_of_report, sqlscripts.sw_fin_revs_transit_data)
        df_td = self.run_sql_script(script_td)
        df = pd.concat([df_rev, df_td], axis = 1)
        df = self.deduplicate(df)
        totalrev = df.iloc[:, 1:].sum(axis  =1).tolist()
        df['Total Revenue'] = totalrev
        df = df[df['Agnc'].isin(transit_list)]
        cols = ['Agnc', 'Sales_or_Local_Tax', 'Fare_Revenues', 'Vanpool_Revenue', 'Federal_Operating_Revenue', 'State_Operating_Revenue', 'Other_Operating_Revenue', 'Federal_Capital_Revenue',
                   'State_Capital_Revenue', 'Total Revenue']
        df = df[cols]
        df.columns = df.columns.str.replace('_', ' ')
        df.Agnc = df.Agnc.apply(lambda x: transit_dic[x])
        df = df.sort_values('Agnc') #sorting because RiverCites ends up in a weird palce
        df = self.formulate_total_and_sub_total(df)
        cols = df.columns.tolist()
        cols = cols[1:]
        for col in cols:
            df[col] = df[col].apply(lambda x: "{:,}".format(x))
            df[col] = df[col].apply(lambda x: "${}".format(x))
            df[col] = df[col].map(self.fix_floating_zero_single)
        df = df.rename(columns = {'Agnc': 'Revenues', 'Fare Revenues': 'Fare Revenues (all modes except vanpool)'})
        df.to_excel(path + '\\{} SW Fin Revs Stats.xlsx'.format(year_of_report), index=False)

    # TODO need to add in fastest growing mode for each one of these
    def ser_mode(self, year_of_report, path):
        self.year_of_report = year_of_report
        year_list = self.generate_year_list(year_of_report, 5)
        year_list = tuple(year_list)
        script_list = [sqlscripts.ser_mode_rev, sqlscripts.ser_mode_rvh, sqlscripts.ser_mode_rvm, sqlscripts.ser_mode_psgr, sqlscripts.ser_mode_oex, sqlscripts.ser_mode_psgr_per_rvh, sqlscripts.ser_mode_psgr_per_rvm,
                       sqlscripts.ser_mode_oex_per_rvh, sqlscripts.ser_mode_oex_per_rvm, sqlscripts.ser_mode_oex_per_psgr, sqlscripts.ser_mode_rvh_per_employee, sqlscripts.ser_mode_farebox_recovery]
        mode_dict = {'ser_mode_rev':'Farebox Revenues by Service Mode', 'ser_mode_rvh': 'Revenue Vehicle Hours by Service Mode', 'ser_mode_rvm': 'Revenue Vehicle Miles by Service Mode', 'ser_mode_psgr':'Passenger Trips by Service Mode',
                     'ser_mode_oex':'Operating Expenses by Passenger Mode', 'ser_mode_psgr_per_rvh': 'Passenger Trips per Revenue Vehicle Hour', 'ser_mode_psgr_per_rvm':'Passenger Trips per Revenue Vehicle Mile',
                     'ser_mode_oex_per_rvh':'Operating Costs per Revenue Vehicle Hour', 'ser_mode_oex_per_rvm':'Operating Costs per Revenue Vehicle Mile', 'ser_mode_oex_per_psgr':'Operating Costs per Passenger Trip',
                     'ser_mode_rvh_per_employee':'Revenue Vehicle Hours per Employee','ser_mode_farebox_recovery':'Farebox Recovery/Vanpool Revenue Recovery'}
        zipped = zip(script_list, mode_dict.keys())
        count = 0
        for script, title in zipped:
            scripted = self.populate_sql_script(year_list, script)
            df = self.run_sql_script(scripted)
            df = df.set_index('Yr')
            df = df.sort_index(ascending=True)
            df = df.transpose()
            df.index = df.index.str.replace('_', ' ')
            df = df.reset_index()
            title = mode_dict[title]
            df = df.rename(columns={'index': title})
            if 'by' in title:
                totals = []
                cols = df.iloc[:, 1:].columns.tolist()
                for col in cols:
                    total = df[col].sum()
                    totals.append(total)
                totals.insert(0, 'Total')
                df = df.append(dict(zip(df.columns.tolist(), totals)), ignore_index = True)
            prev_year = year_of_report - 1
            df['One Year Percent Change (%)'] = (df[year_of_report] - df[prev_year]) / df[prev_year]
            df['One Year Percent Change (%)'] = df['One Year Percent Change (%)'] * 100
            df.loc[-1] = df.columns.tolist()  # adding a row
            df.index = df.index + 1  # shifting index
            df = df.sort_index()
            df = df.rename(columns={title: 'table_name'})
            if count == 0:
                df = self.pretty_formatting(df)
                finaldf = df
                count +=1
            else:
                df = self.pretty_formatting(df)
                emptylist = ['']*len(finaldf.columns)
                finaldf = finaldf.append(dict(zip(finaldf.columns.tolist(), emptylist)), ignore_index = True)
                finaldf = pd.concat([finaldf, df], axis = 0)

                finaldf.to_excel(path + '\\{} Ser Mode Tables.xlsx'.format(year_of_report), index = False, header = False)

    def pretty_formatting(self, df):
        self.df = df
        table_name = df['table_name'].loc[0]
        revenue_list = ['Farebox Revenues by Service Mode', 'Operating Expenses by Passenger Mode', 'Operating Costs per Revenue Vehicle Hour', 'Operating Costs per Revenue Vehicle Mile', 'Operating Costs per Passenger Trip']
        col_list = df.columns.tolist()
        col_list = col_list[1:]
        col_list.pop()
        for col in col_list:
            df[col].loc[1:] = df[col].loc[1:].apply(lambda x: "{:,.2f}".format(x))
            if table_name in revenue_list:
                df[col].loc[1:] = df[col].loc[1:].apply(lambda x: "${}".format(x))
                df[col].loc[1:] = df[col].loc[1:].map(self.fix_floating_zero)
            elif table_name == 'Farebox Recovery/Vanpool Revenue Recovery':
                df[col].loc[1:] = df[col].loc[1:].apply(lambda x: "{}%".format(x))
        df['One Year Percent Change (%)'].loc[1:] = df['One Year Percent Change (%)'].loc[1:].apply(lambda x: format(x, '.2f'))
        return df

    def fix_floating_zero(self, j):
        '''low level function to cut out the .00 that comes with converting from float to string'''
        self.j = j
        j = j.replace('.00', '')
        return j

    def filter_out_empty_rows(self, df):
        self.df = df
        sums = df.iloc[:, 2:].sum(axis=1)
        sums = pd.DataFrame(sums)
        sums = sums[sums[0] != 0]
        sum_index = sums.index.tolist()
        df = df[df.index.isin(sum_index)]
        return df

    def aggregate_mode_data(self, df, mode):
        totals = ['Revenue_Vehicle_Hours', 'Total_Vehicle_Hours', 'Revenue_Vehicle_Miles', 'Total_Vehicle_Miles',
                  'Passenger_Trips', 'Employees_FTEs', 'Operating_Expenses', 'Farebox_Revenues']
        averages = ['Passenger_Trips_Revenue_Hour', 'Passenger_Trips_per_Revenue_Mile', 'Revenue_Hours_Per_Employee',
                    'Operating_Expenses_per_Revenue_Vehicle_Hour', 'Operating_Expense_per_Revenue_Vehicle_Mile',
                    'Operating_Expense_per_Passenger_Trip', 'Farebox_Recovery_Ratio']
        self.df = df
        self.mode = mode
        agtype = ['Urban', 'Small Urban', 'Rural']
        if len(df) < 3:
            totals_row = df[totals].sum(axis=0).tolist() + df[averages].mean(axis=0).tolist()
            totals_row.insert(0, 'Totals')
            totals_row.insert(0, 'Statewide '.format(mode))
            df = df.append(dict(zip(df.columns.tolist(), totals_row)), ignore_index=True)
            return df
        else:
            for form in agtype:
                filtereddf = df[df['agencytype'] == form]
                totals_row = filtereddf[totals].sum(axis=0).tolist() + filtereddf[averages].mean(axis=0).tolist()
                totals_row.insert(0, 'Totals/Averages')
                totals_row.insert(0, form)
                df = df.append(dict(zip(df.columns.tolist(), totals_row)), ignore_index=True)
            totals_row = df[totals].sum(axis=0).tolist() + df[averages].mean(axis=0).tolist()
            totals_row.insert(0, 'Totals')
            totals_row.insert(0, 'Statewide '.format(mode))
            df = df.append(dict(zip(df.columns.tolist(), totals_row)), ignore_index=True)
            return df

    def format_data(self, df):
        ## TODO figure out how to print out commas in the thousands place
        self.df = df
        df = df.fillna(0)
        dollars_list = ['Operating_Expenses', 'Farebox_Revenues', 'Operating_Expenses_per_Revenue_Vehicle_Hour','Operating_Expense_per_Revenue_Vehicle_Mile','Operating_Expense_per_Passenger_Trip']
        cols = df.columns.tolist()
        cols = cols[2:]
        for col in cols:
            if col in dollars_list:
                df[col] = df[col].apply(lambda x: "${:,.2f}".format(x))
                large_numbers = ['Operating_Expenses', 'Farebox_Revenues']
                if col in large_numbers:
                    df[col] = df[col].map(self.fix_floating_zero)
            elif col == 'Employees_FTEs':
                df[col] = df[col].apply(lambda x: "{:,.1f}".format(x))
            elif col == 'Farebox_Recovery_Ratio':
                #df['Farebox_Recovery_Ratio'] = df['Farebox_Recovery_Ratio'].apply(lambda x: round(x,2))
                df['Farebox_Recovery_Ratio'] = df['Farebox_Recovery_Ratio'].apply(lambda x: '{:.2f}%'.format(x))
            else:
                df[col] = df[col].apply(lambda x: '{:,.2f}'.format(x))
                df[col] = df[col].map(self.fix_floating_zero)
        return df


    def sw_op_stats(self, year, transit_dic, path):
        self.year = year
        self.transit_dic = transit_dic
        modes = ['fixed', 'CB', 'TB', 'route', 'demand', 'van', 'com', 'light', 'SR']
        fancy_mode_name = ['Fixed Route', 'Commuter Bus', 'Trolley Bus', 'Route Deviated', 'Demand Response', 'Vanpool', 'Commuter Rail', 'Light Rail', 'Streetcar Rail']

        mode_dict = dict(zip(modes, fancy_mode_name))
        count = 0 # have to set up count as a variable outside the for loop so that it can be disposed of
        for mode in modes:
            if mode == 'demand':
                script = self.populate_sql_script(year, sqlscripts.sw_op_stats_demand)
                df = self.run_sql_script(script)
            elif mode == 'com':
                script = self.populate_sql_script(year, sqlscripts.sw_op_stats_com)
                df = self.run_sql_script(script)
            elif mode == 'van':
                script = self.populate_sql_script(year, sqlscripts.sw_op_stats_van)
                df = self.run_sql_script(script)
                df['Farebox_Recovery_Ratio'] = df['Farebox_Recovery_Ratio']*0
                df['Farebox_Revenues'] = df['Farebox_Revenues']*0
            else:
                script = self.populate_sql_script(year, sqlscripts.sw_op_stats_fixed)
                script = script.replace('fixed', mode)
                df = self.run_sql_script(script)
            df = df.set_index('Agnc')
            df = self.filter_out_empty_rows(df)
            df.agencytype = df.agencytype.str.title()
            df = df.reset_index()
            df.Agnc = df.Agnc.apply(lambda x: transit_dic[x])
            df = self.aggregate_mode_data(df, mode)
            df = self.format_data(df)
            df.columns = df.columns.str.replace('_', ' ')
            mode = mode_dict[mode]
            df = df.rename(columns = {'Agnc': mode, 'agencytype': 'System Category'})
            df.loc[-1] = df.columns.tolist()  # adding a row
            df.index = df.index + 1  # shifting index
            df = df.sort_index()
            df = df.rename(columns={mode: 'table_name'})
            if count == 0:
                finaldf = df
                count += 1
            else:
                emptylist = [''] * len(finaldf.columns)
                finaldf = finaldf.append(dict(zip(finaldf.columns.tolist(), emptylist)), ignore_index=True)
                finaldf = pd.concat([finaldf, df], axis=0)
            finaldf.to_excel(path + '\\{} SW Op Stats.xlsx'.format(year), index=False, header = False, sheet_name='Sheet1')


    def random_text(self, year_of_report):
        random_text_list = []
        previous_year = year_of_report-1
        # local tax


        local_tax_sql_script = "SELECT Yr, Sum(sales_tax+utility_tax+mvet) As Total_Local_Funds FROM ptsummary_transit.revenues join agencytype on revenues.Agnc = agencytype.Agency where Yr in ({}, {}) and agencytype.agencytype in ('urban', 'small urban', 'rural') Group By Yr".format(year_of_report, previous_year)
        local_tax = self.run_sql_script(local_tax_sql_script)
        local_tax['Total_Local_Funds'] = local_tax['Total_Local_Funds']*.0000000001
        random_text_list.append('Local Funding')
        local_taxes = 'Local tax revenues for {} totaled nearly ${} billion ($ {} billion in {}), accounting for XXX percent ' \
                      'of all revenues (both operating and capital) for public transit systems'.format(local_tax['Yr'].loc[0], )



def main(year_of_report, path):
    srs = statewide_rollup_sheets(year_of_report)
    srs.sw_fin_exps_stats(year_of_report, srs.transit_list, srs.transit_dic, path)
    srs.sw_fin_rev_stats(year_of_report, srs.transit_list, srs.transit_dic, path)
    srs.ser_mode(year_of_report, path)
    srs.sw_op_stats(year_of_report, srs.transit_dic, path)
    srs.sw_rev_table(year_of_report, path)
    #srs.random_text(year_of_report, path)



if __name__ == "__main__":
    main(2017, r'C:\Users\SchumeN\Documents\ptstest\newtest\invest_test')