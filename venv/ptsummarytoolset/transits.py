import pymysql.cursors
import pandas as pd
import numpy as np

# TODO group all utility functions together; place each function in the order that they are representd in the main function


class Datasheet():
    mode_list = ['do_fixed', 'pt_fixed', 'do_RB', 'pt_RB', 'do_CB', 'pt_CB', 'do_TB', 'pt_TB', 'pt_com', 'do_light',
                 'pt_light', 'do_SR', 'pt_SR', 'do_route', 'pt_route', 'do_demand', 'pt_demand', 'pt_DT', 'do_van']
    transit_list = ['asotin', 'ben franklin', 'Central Transit', 'clallam', 'columbia', 'community', 'ctran',
                         'CUBS', 'everett', 'garfield',
                         'grant', 'grays', 'intercity', 'island', 'jefferson', 'king', 'kitsap', 'link', 'mason',
                         'Okanogan County Transit Authority', 'pacific', 'pierce', 'pullman',
                         'selah', 'skagit', 'sound', 'spokane', 'twin', 'union gap', 'valley', 'whatcom', 'yakima']
    def __init__(self, agency, year1, year2, year3):
        self.agency = agency
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        print('This is the constructor for {}'.format(agency))
    def clean_dataframe(self, xdf, agency):
        self.agency = agency
        self.xdf = xdf
        xdf = xdf[xdf['Agnc'] == agency]
        xdf = xdf.drop(['Comments', 'revenueindex'], axis = 1)
        return xdf
    def template_sorter(self, xdf):
        # sifts through the transit data and organizes it to fit the report
        self.xdf = xdf
        columns = pd.read_excel(r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\columnorderspreadsheet.xlsx')
        order = columns['columnorder'].tolist()
        xdf = xdf.reindex(columns = order)
        xdf = xdf.transpose()
        xdf.columns = xdf.loc['Yr']
        cols = xdf.columns.sort_values(ascending=True)
        xdf = xdf[cols]
        # rearranges the columns so that they are in the right order
        xdf = xdf.fillna(0)
        xdf = xdf.drop('Yr', axis = 0)
        return xdf
    def empty_column_adder(self, xdf, years):
        # adds an empty column with a certain number of years in it
        self.xdf = xdf
        self.years  = years
        if len(xdf.columns) < 3:
            missing_years =[year for year in years if year not in xdf.columns]
            for yr in missing_years:
                xdf[yr] = np.nan
            xdf = xdf[sorted(xdf.columns)]
            xdf = xdf.fillna(0)
            return xdf, missing_years
        else:
            missing_years = 'empty'
            return xdf, missing_years
    def revenue_expense_formulas(self, xdf):
        #TODO there's a more pythonic way to make this work
        self.xdf = xdf
        # section isolates all revenues and appends them together to build the farebox revenue category
        xdf = xdf.reset_index()
        xdf = xdf.rename(columns ={'index': 'category'})
        xdf = self.sum_formula(xdf, 'Other Operating Sub-Total', ['other_ad', 'other_int', 'other_gain', 'other_rev'])
        xdf = self.sum_formula(xdf, 'Vanpooling Revenue', ['rev_do_van'])
        xdf = self.sum_formula(xdf, 'Total Farebox Revenues', ['rev_do_fixed', 'rev_pt_fixed', 'rev_do_RB', 'rev_pt_RB', 'rev_do_CB', 'rev_pt_CB', 'rev_do_TB', 'rev_pt_com', 'rev_do_light', 'rev_pt_light',
        'rev_do_SR', 'rev_pt_SR', 'rev_do_route', 'rev_pt_route', 'rev_do_demand', 'rev_pt_demand', 'rev_pt_DT'])
        xdf = self.sum_formula(xdf, 'Total (Excludes Capital Revenues)', ['sales_tax', 'utility_tax', 'mvet', 'Total Farebox Revenues', 'Vanpooling Revenue', 'fta_5307_op', 'fta_5307_prv', 'fta_5311_op',
         'fta_5316_op',  'fta_other_op', 'st_op_rmg', 'st_op_regmg', 'st_op_sng', 'st_op_stod', 'st_op_ste', 'st_op_other', 'Other Operating Sub-Total'])
        xdf = self.sum_formula(xdf, 'Total Federal Capital', ['fta_5307_cg', 'fta_5309_cg', 'fta_5310_cg', 'fta_5311_cg', 'fta_5316_cg', 'Fstp_grnt_cg', 'fed_other_grnt_cg'])
        xdf = self.sum_formula(xdf, 'Total State Capital', ['st_cg_rmg', 'st_cg_regmg', 'st_cg_sng', 'st_cg_ste', 'st_ct_van', 'st_cg_other'])
        xdf = self.sum_formula(xdf, 'Total Local Capital', ['local_cap'])
        xdf = self.sum_formula(xdf, 'Total Debt Service', ['interest', 'principal'])
        xdf = self.sum_formula(xdf, 'Total', ['gen_fund', 'unrest_cash', 'oper_res', 'work_cap', 'cap_res_fund', 'cont_res', 'debt_ser_fund', 'insur_fund', 'other_balace'])
        xdf = self.sum_formula(xdf, 'Local Revenues', ['sales_tax', 'utility_tax', 'mvet', 'Total Farebox Revenues', 'Vanpooling Revenue', 'Other Operating Sub-Total'])
        xdf = self.sum_formula(xdf, 'State Revenues', ['Total State Capital', 'st_op_rmg', 'st_op_regmg', 'st_op_sng', 'st_op_stod', 'st_op_ste', 'st_op_other'])
        xdf = self.sum_formula(xdf, 'Federal Revenues', ['fta_5307_op', 'fta_5307_prv', 'fta_5311_op', 'fta_5316_op',  'fta_other_op', 'Total Federal Capital'])
        xdf = self.sum_formula(xdf, 'Total Revenues (all sources)', ['Local Revenues', 'State Revenues', 'Federal Revenues'])
        xdf = self.sum_formula(xdf, 'Operating Investment', ['oex_do_fixed', 'oex_pt_fixed', 'oex_do_RB', 'oex_pt_RB', 'oex_do_CB', 'oex_pt_CB', 'oex_do_TB', 'oex_pt_TB', 'oex_pt_com', 'oex_do_light',
                                                        'oex_pt_light', 'oex_do_SR', 'oex_pt_SR', 'oex_do_route', 'oex_pt_route', 'oex_do_demand', 'oex_pt_demand', 'oex_pt_DT', 'oex_do_van'])
        xdf = self.sum_formula(xdf, 'Local Capital Investment', ['Total Local Capital'])
        xdf = self.sum_formula(xdf, 'State Capital Investment', ['Total State Capital'])
        xdf = self.sum_formula(xdf, 'Federal Capital Investment', ['Total Federal Capital'])
        xdf = self.sum_formula(xdf, 'Other Investment', ['Otra_exp_num', 'Total Debt Service'])
        xdf = self.sum_formula(xdf, 'Total Investment', ['Operating Investment', 'Local Capital Investment', 'State Capital Investment', 'Federal Capital Investment', 'Other Investment'])
        return xdf

    def sum_formula(self, xdf, category_name, category_list):
        self.xdf = xdf
        self.category_name = category_name
        self.category_list = category_list
        sumcategory = xdf[xdf.category.isin(category_list)].sum(axis = 0)
        sumcategory['category'] = category_name
        if type(sumcategory) == 'pandas.core.frame.DataFrame':
            sumcategory = sumcategory.iloc[0, :]
            xdf = xdf.append(sumcategory, ignore_index = True)
        else:
            xdf = xdf.append(sumcategory, ignore_index = True)
        return xdf

    def mode_cutter(self, xdf, mode_list):
        self.xdf = xdf
        self.mode_list = mode_list
        for mode in mode_list:
            mode_dataframe = xdf[xdf.category.str.contains(mode)]
            modes_sums = mode_dataframe.sum(axis=1)
            mode_dataframe = pd.concat([mode_dataframe, modes_sums], axis = 1)
            mode_dataframe = mode_dataframe.rename(columns = {0:'sums'})
            if mode_dataframe['sums'].sum() == 0.0:
                xdf = xdf[~xdf.category.str.contains(mode)]
        return xdf

    def percent_change_calculator(self, xdf):
        self.xdf = xdf
        # built this to be pretty resilient, so it's able to handle weird shit like zero division errors, etc. this means its kind of slow, and I didn't use good pandas functionality
        current_year = xdf.iloc[:,3].tolist()
        previous_year = xdf.iloc[:,2].tolist()
        zipped = zip(current_year, previous_year)
        one_year_change = []
        for curr, prev in zipped:
            if (prev == 0 and curr != 0):
                one_year_change.append(1.00)
            elif (prev == 0 and curr == 0):
                one_year_change.append(0.00)
            else:
                percent_change = (curr - prev)/prev
                one_year_change.append(percent_change)
        xdf['One Year Change (%)'] = one_year_change
        xdf['One Year Change (%)'] = xdf['One Year Change (%)'].fillna(0.0)
        xdf['One Year Change (%)'] =   xdf['One Year Change (%)']*100
        xdf = xdf.replace(np.inf, 100.00)
        xdf['One Year Change (%)'] = xdf['One Year Change (%)'].apply(lambda x: round(x, 2))
        return xdf

    def empty_row_dropper(self, xdf):
        self.xdf = xdf
        for index, row in xdf.iterrows():
            xrow = row.tolist()
            xrow = xrow[1:]
            if sum(xrow) == 0.0:
                xdf = xdf.drop(index = index, axis = 0)
        return xdf


    def heading_inserter(self, xdf, year1, year2, year3):
        self.xdf = xdf
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        header = pd.read_excel(r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\headerdictionary.xlsx')
        abbr = header['Abbreviation'].tolist()
        heading = header['Heading'].tolist()
        headerdic = dict(zip(abbr, heading))
        for key in headerdic.keys():
           if xdf[xdf.category.str.contains(key)].empty == False:
               xdf = xdf.append(pd.Series([headerdic[key], '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index = True)
        xdf = xdf.append(pd.Series(['Financial Information', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index = True)
        xdf = xdf.append(pd.Series(['Operating Related Revenues', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Other Expenditures', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Debt Service', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Ending Balances, December 31', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append(pd.Series(['Total Funds by Source', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Revenues', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Investments', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        return xdf

    def final_template_sorter(self, xdf):
        self.xdf = xdf
        columns = pd.read_excel(
            r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\finalcolumnorderspreadsheet.xlsx')
        order = columns['columnorder1'].tolist()
        xdfcategoryorder = xdf.category.tolist()
        adjustedorder = [i for i in order if i in xdfcategoryorder]
        xdf = xdf.set_index('category')
        xdf = xdf.reindex(index = adjustedorder)
        xdf = xdf.reset_index()
        nwo = columns['columnorder2'].tolist()
        orderdict = dict(zip(order, nwo))
        xdf.category = xdf.category.apply(lambda x: orderdict[x])
        return xdf

    def final_template_sorter_sw(self, xdf):
        self.xdf = xdf
        columns = pd.read_excel(
            r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\finalcolumnorderspreadsheet_sw.xlsx')
        order = columns['columnorder1'].tolist()
        xdfcategoryorder = xdf.category.tolist()
        adjustedorder = [i for i in order if i in xdfcategoryorder]
        xdf = xdf.set_index('category')
        xdf = xdf.reindex(index = adjustedorder)
        xdf = xdf.reset_index()
        nwo = columns['columnorder2'].tolist()
        orderdict = dict(zip(order, nwo))
        xdf.category = xdf.category.apply(lambda x: orderdict[x])
        return xdf



    def mode_aggregator(self, finaldf, mode_list):
        self.finaldf = finaldf
        self.mode_list = mode_list
        finaldf = finaldf.set_index('category')
        mode_list = ['do_fixed', 'pt_fixed', 'do_RB', 'pt_RB', 'do_CB', 'pt_CB', 'do_TB', 'pt_TB', 'pt_com', 'do_light',
                     'pt_light', 'do_SR', 'pt_SR', 'do_route', 'pt_route', 'do_demand', 'pt_demand', 'pt_DT', 'do_van']
        fixed_list = ['pt_fixed', 'do_CB', 'pt_CB', 'do_TB', 'pt_TB', 'do_RB', 'pt_RB']
        for mode in fixed_list:
            finaldf.index = finaldf.index.str.replace(mode, 'do_fixed')
        light_rail = ['pt_light', 'do_SR', 'pt_SR']
        for mode in light_rail:
            finaldf.index = finaldf.index.str.replace(mode, 'do_light')
        finaldf.index = finaldf.index.str.replace('pt_route', 'do_route')
        finaldf.index = finaldf.index.str.replace('pt_demand', 'do_demand')
        finaldf.index = finaldf.index.str.replace('pt_DT', 'do_demand')
        finaldf = finaldf.reset_index()
        finaldf =finaldf.groupby('category').sum()
        finaldf = finaldf.reset_index()
        return finaldf


    def fin_opp_sum_category_names(self, finaldf):
        # for the operations summary, this function provides the appropriate titles for categories
        self.finaldf = finaldf
        finaldf.category = finaldf.category.str.replace('Fixed Route Services', 'Fixed Route Services (Fixed Route, Bus Rapid Transit, Commuter Bus and Trolley Bus)')
        finaldf.category = finaldf.category.str.replace(' \(Purchased Transportation\)', '')
        finaldf.category = finaldf.category.str.replace('Light Rail Services ', 'Light Rail Services (Includes Streetcar Rail)')
        finaldf.category = finaldf.category.str.replace(' \(Direct Operated\)', '')
        finaldf.category = finaldf.category.str.replace('\(Direct Operated\)', '')
        return finaldf

    def heading_inserter_for_sw(self, xdf, year1, year2, year3):
        self.xdf = xdf
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        header = pd.read_excel(r'I:\Public_Transportation\Data_Team\PT_Summary\PythonFiles\headerdictionary.xlsx')
        abbr = header['Abbreviation'].tolist()
        heading = header['Heading'].tolist()
        headerdic = dict(zip(abbr, heading))
        for key in headerdic.keys():
           if xdf[xdf.category.str.contains(key)].empty == False:
               xdf = xdf.append(pd.Series([headerdic[key], '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index = True)
        xdf = xdf.append(pd.Series(['Financial Information', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index = True)
        xdf = xdf.append(pd.Series(['Operating Related Revenues', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Other Expenditures', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Debt Service', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Ending Balances, December 31', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append(pd.Series(['Total Funds by Source', year1, year2, year3, 'One Year Change (%)'], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Revenues', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['Investments', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append(pd.Series(['frs_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['crs_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['lrs_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append( pd.Series(['rds_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['drs_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append(pd.Series(['vans_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['fed_cap_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['state_cap_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append( pd.Series(['loc_cap_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['other_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append(pd.Series(['debt_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['ending_bal_empty_row', '', '', '', ''],['category', year1, year2, year3, 'One Year Change (%)']), ignore_index=True)
        xdf = xdf.append(pd.Series(['revenue_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        xdf = xdf.append(pd.Series(['investments_empty_row', '', '', '', ''], ['category', year1, year2, year3, 'One Year Change (%)']),ignore_index=True)
        return xdf

    def fix_floating_zero(self, j):
        '''low level function to cut out the .0 that comes with converting from float to string'''
        self.j = j
        if len(j) > 4:
            j = j.replace('.00', '')
        return j


    def pretty_formatting(self, xdf, year1, year2, year3):
        '''method to make the dataframe have commas and dollar signs'''
        # variable initiation in a semi-anonymous manner
        self.xdf = xdf
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        # adding a comma after every three numbers
        xdf[year1] = xdf[year1].apply(lambda x:  "{:,}".format(x))
        xdf[year2] = xdf[year2].apply(lambda x: "{:,}".format(x))
        xdf[year3] = xdf[year3].apply(lambda x: "{:,}".format(x))
        # have to make this substitution because it was messing stuff up
        xdf.category = xdf.category.str.replace('other_rev', 'other_rv')
        # converts to string
        xdf[[year1, year2, year3]] = xdf[[year1, year2, year3]].astype(str)
        # builds an index set for oex and rev numbers to find dollars
        rev_index = xdf[xdf.category.str.contains('rev')].index.tolist()
        oex_index = xdf[xdf.category.str.contains('oex')].index.tolist()
        # max rev and max oex are the points at which everything following is financial info, also almost all aggregate categories are in dollars
        # complex set of try/excepts as a means of getting around the fact that some of the tribes don't report financial data
        try:
            max_rev = max(rev_index)
        except ValueError:
            try:
                max_rev = max(oex_index)
            except ValueError:
                return xdf
        others = xdf.loc[max_rev:].index.tolist()
        # makes an indice list
        indices = rev_index + oex_index + others
        # hits each individual column
        cols = [year1, year2, year3]
        # filters out anything from the indice list that is actually 0.0
        for col in cols:
            # turns them into dollars
            xdf[col].loc[indices] = xdf[col].loc[indices].apply(lambda x: "${}".format(x))
            # fixes the floating zero function
            xdf[col] = xdf[col].map(self.fix_floating_zero)
            # returns the dataframe
        return xdf


    def pretty_formatting_sw(self, xdf, year1, year2, year3):
        '''method to make the dataframe have commas and dollar signs'''
        # variable initiation in a semi-anonymous manner
        self.xdf = xdf
        self.year1 = year1
        self.year2 = year2
        self.year3 = year3
        # adding a comma after every three numbers
        xdf[year1] = xdf[year1].apply(lambda x:  "{:,.2f}".format(x))
        xdf[year2] = xdf[year2].apply(lambda x: "{:,.2f}".format(x))
        xdf[year3] = xdf[year3].apply(lambda x: "{:,.2f}".format(x))
        # have to make this substitution because it was messing stuff up
        xdf.category = xdf.category.str.replace('other_rev', 'other_rv')
        # converts to string
        xdf[[year1, year2, year3]] = xdf[[year1, year2, year3]].astype(str)
        # builds an index set for oex and rev numbers to find dollars

        index_list = ['Federal Capital Investment','Federal Revenues','Fstp_grnt_cg','Local Capital Investment','Local Revenues','Operating Investment',
        'Other Investment','Other Operating Sub-Total','Otra_exp_num','State Capital Investment','State Revenues','Total','Total (Excludes Capital Revenues)',
    'Total Debt Service','Total Farebox Revenues','Total Federal Capital','Total Local Capital','Total Revenues (all sources)','Total State Capital', 'Vanpooling Revenue', 'cap_res_fund',
     'cont_res','debt_ser_fund','deprec','fed_other_grnt_cg','fta_5307_cg','fta_5307_op','fta_5307_prv','fta_5309_cg','fta_5310_cg','fta_5311_cg','fta_5311_op',
    'fta_5316_op','fta_other_op','gen_fund','insur_fund','interest','local_cap','mvet','oex_do_demand','oex_do_fixed','oex_do_light','oex_do_route','oex_do_van',
    'oex_pt_com','oper_res','other_ad','other_balace','other_gain','other_int','other_rev','principal','rev_do_demand','rev_do_fixed','rev_do_light','rev_do_route',
    'rev_do_van','rev_pt_com','sales_tax','st_cg_other','st_cg_regmg','st_cg_rmg','st_cg_sng','st_cg_ste','st_ct_van','st_op_other','st_op_regmg','st_op_rmg','st_op_sng',
    'st_op_ste','st_op_stod','unrest_cash','utility_tax','work_cap']
        indices = xdf[xdf.category.isin(index_list)].index.tolist()
        # hits each individual column
        cols = [year1, year2, year3]
        # filters out anything from the indice list that is actually 0.0
        for col in cols:
            # turns them into dollars
            xdf[col].loc[indices] = xdf[col].loc[indices].apply(lambda x: "${}".format(x))
            # fixes the floating zero function
            xdf[col] = xdf[col].map(self.fix_floating_zero)
            # returns the dataframe
        return xdf

def pull_from_db(table_name, year1, year2, year3):
    connection = pymysql.connect(host='UCC1038029',
                             user='nathans',
                             password='shalom33',
                             db='ptsummary_transit',
                             cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        # Read a single record
        sql = """SELECT * from {} WHERE Yr in ('{}', '{}', '{}')""".format(table_name, year1, year2, year3)
        cursor.execute(sql)
        result = cursor.fetchall()


    connection.close()

    count = 0
    for i in result:
        if count == 0:
            df = pd.DataFrame.from_dict(i, orient= 'index')
            count +=1
        else:
            newdf = pd.DataFrame.from_dict(i, orient = 'index')
            df = pd.concat([df, newdf], axis = 1)
    df = df.transpose()
    df = df.set_index('AgencyYr')
    return df

def dataset_builder(year1, year2, year3):
    # function to build out the transit datasets so that they can be transposed into a singular dataframe
    tables = ['revenues', 'expenses', 'transit_data']
    count = 0
    # iterates over the various table types and combines them
    for table in tables:
        if count == 0:
            df = pull_from_db(table, year1, year2, year3)
            count +=1
        else:
            newdf  = pull_from_db(table, year1, year2, year3)
            newdf = newdf.drop(['rpKey', 'Agnc', 'Yr', 'Comments'], axis = 1)
            df = pd.concat([newdf, df], axis = 1)
    return df

def fix_up_agencylist(agencylist):
    # functions that very specifically clean up the agency list for use in the broader macro/ class
    # it ends up being easier to write things in this rather definitive way because the data doesnt change much
    agencylist = [i for i in agencylist if i != 'Testing agency']
    return agencylist


def main(year1, year2, year3):
    print('Hurry up and get your coffee, because this program is fast')
    # pulls the dataframe out of the aether, and constructs an original dataset
    df = dataset_builder(year1, year2, year3)
    # builds a unique list of agencies to cycle through
    agencylist = df.Agnc.unique().tolist()
    # some aesthetic problems, such as the existence of the testing agency ( a relic of the macro
    agencylist = fix_up_agencylist(agencylist)
    # makes a list of unique years
    years = df.Yr.unique()
    # a count device, because the first dataframe needs to be treated differently than the rest; it's a recurring feature of my code
    count = 0
    # iterates through the agency list
    # there are parallel tracks here for statewide and individual agencies, xdf signifies an individual agency, finaldf signifies a sw agency
    #TODO make the df appelation better reflective of sw vs. individual agency
    for agnc in agencylist:
        # initializes the Datasheet class object, from which all the methods are pulled
       ds = Datasheet(agnc, year1, year2, year3)
       # a few cleaning processes
       xdf = ds.clean_dataframe(df, agnc)
        # sorts and formats based on template
       xdf = ds.template_sorter(xdf)
        # checks to make sure there are no missing year columns; necessary since we have lots of tribes who report intermittently
       xdf, missing_years = ds.empty_column_adder(xdf, years)
        # checks to see if the agency is a transit, so that it can feed it into the state wide operations financial summary loop
       if agnc in ds.transit_list:
           if count == 0:
               finaldf = xdf
               count +=1
           else:
               newdf = xdf
               cols = [year1,year2, year3]
               for i in cols:
                   finaldf[i] =finaldf[i].add(newdf[i], axis = 0)
       # this part of the loop starts to build the Statewide Operations Financial Summary, takes the generated individual data and uses it to build the op finn sum, which is a larger version of individual agency sheets
        # builds out the datasheet for individual agencies by creating a list of composite financial categories
       xdf = ds.revenue_expense_formulas(xdf)

        # axes any modes that aren't represented by a particular transit agency, accepts the variable mode list as a guide to finding these modes
       xdf = ds.mode_cutter(xdf, ds.mode_list)
        # calculates the percent change for year over year
       xdf = ds.percent_change_calculator(xdf)
        # mode cutter is pretty general, and doesn't do financials, so need another means of cutting things that are empty
       xdf = ds.empty_row_dropper(xdf)
        # checks to make sure that the dataframe isnt empty; if it is, it drops it
       if xdf.empty == True:
           continue
        # puts headings in to the output
       xdf['One Year Change (%)'] = xdf['One Year Change (%)'].apply(lambda x: format(x, '.2f'))
       xdf = ds.pretty_formatting(xdf, year1, year2, year3)
       xdf = ds.heading_inserter(xdf, year1, year2, year3)
        # sorts the final template based on a saved style sheet
       xdf = ds.final_template_sorter(xdf)
        # renames the category column to '' so that it is readable
       xdf = xdf.rename(columns = {'category': 'Annual Operating Information'})
       xdf = xdf.replace('$0.0', '$0')
        # outputs to a file path
        # TODO anonynmize this so that a path can be passed through the main function
       xdf.to_excel('I:\\Public_Transportation\\Data_Team\\PT_Summary\\PythonFiles\\testfolder\\{}.xlsx'.format(agnc), index = False)
    finaldf = ds.revenue_expense_formulas(finaldf)
    finaldf = ds.empty_row_dropper(finaldf)
    finaldf = ds.mode_aggregator(finaldf, ds.mode_list)
    finaldf = ds.percent_change_calculator(finaldf)
    finaldf['One Year Change (%)'] = finaldf['One Year Change (%)'].apply(lambda x: format(x, '.2f'))
    finaldf = ds.pretty_formatting_sw(finaldf, year1, year2, year3)
    finaldf = ds.heading_inserter_for_sw(finaldf, year1, year2, year3)
    finaldf = ds.final_template_sorter_sw(finaldf)
    finaldf = ds.fin_opp_sum_category_names(finaldf)
    finaldf = finaldf.rename(columns={'category': ''})
    finaldf = finaldf.replace('$0.0', '$0')
    finaldf.to_excel('I:\\Public_Transportation\\Data_Team\\PT_Summary\\PythonFiles\\testfolder\\{} SW Fin Summ.xlsx'.format(year3), index = False)
if __name__ == "__main__":
    main(2015, 2016, 2017)