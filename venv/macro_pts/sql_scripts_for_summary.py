

sw_fin_exp_transit_data = '''SELECT Agnc, Sum(oex_do_fixed+ oex_pt_fixed+oex_do_CB+oex_pt_CB+oex_do_TB+oex_pt_TB+oex_do_RB +oex_pt_TB) AS Fixed_Route, Sum(oex_do_route+oex_pt_route) AS Route_Deviated,
Sum(oex_do_demand+oex_pt_demand+oex_pt_DT) As Demand_Response, oex_do_van as Vanpool,
Sum(oex_do_light+oex_pt_light+oex_do_SR+oex_pt_SR+oex_pt_com) As All_Rail_Modes FROM ptsummary_transit.transit_data where Yr = {} Group By Agnc order by Agnc'''

sw_fin_exp_revenues = '''Select Agnc, SUM(fta_5307_cg+fta_5309_cg+fta_5310_cg+fta_5311_cg+fta_5316_cg+Fstp_grnt_cg+
fed_other_grnt_cg+st_cg_rmg+st_cg_regmg+st_cg_sng+st_cg_ste+st_ct_van+st_cg_other) AS Capital_Expenses FROM ptsummary_transit.revenues where Yr = {} Group By Agnc order by Agnc'''

sw_fin_exp_expenses = '''Select Agnc, SUM(debt_ser_fund) As Debt_Service,  Otra_exp_num As Other, deprec AS Depreciation, local_cap From ptsummary_transit.expenses where Yr = {} Group By Agnc Order By Agnc'''

sw_fin_revs_revenues = '''SELECT Agnc, SUM(sales_tax+utility_tax+mvet) AS Sales_or_Local_Tax, SUM(fta_5307_op +fta_5307_prv +fta_5311_op +fta_5316_op +fta_other_op) As Federal_Operating_Revenue,
SUM(st_op_rmg+st_op_regmg+st_op_sng+st_op_stod+st_op_ste+st_op_other) AS State_Operating_Revenue, SUM(other_ad +other_int +other_gain +other_rev) AS Other_Operating_Revenue,
 Sum(fta_5307_cg+fta_5309_cg+fta_5310_cg+fta_5311_cg+fta_5316_cg +Fstp_grnt_cg +fed_other_grnt_cg) AS Federal_Capital_Revenue, Sum(st_cg_rmg+st_cg_regmg +st_cg_sng +st_cg_ste+st_ct_van +st_cg_other) As State_Capital_Revenue
FROM ptsummary_transit.revenues where Yr = {} group by Agnc Order by Agnc;'''

sw_fin_revs_transit_data ='''SELECT Agnc, rev_do_van AS Vanpool_Revenue, SUM(rev_do_fixed+rev_do_light+rev_do_route + rev_do_demand+rev_do_CB+rev_do_RB + rev_do_SR + rev_do_TB +rev_pt_fixed
+rev_pt_ferry +rev_pt_com + rev_pt_light + rev_pt_route + rev_pt_demand+rev_pt_CB +rev_pt_DT +rev_pt_RB) AS Fare_Revenues FROM ptsummary_transit.transit_data where Yr = {} group by Agnc order by Agnc;'''

ser_mode_rev = '''select Yr, SUM(rev_do_fixed +rev_pt_fixed+rev_do_TB+ rev_do_RB+ rev_pt_RB+ rev_pt_TB+rev_do_CB+rev_pt_CB) as Fixed_Route, SUM(rev_do_route+rev_pt_route) As Route_Deviated, SUM(rev_do_demand + rev_pt_demand + rev_pt_DT) as Demand, SUM(rev_do_van) As Vanpool, Sum(rev_pt_com) As Commuter_Rail, SUM(rev_do_light + rev_pt_light+rev_do_SR+rev_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_rvh  = '''select Yr, SUM(rvh_do_fixed+rvh_pt_fixed+rvh_do_TB+ rvh_pt_TB+rvh_do_CB+rvh_pt_CB+rvh_do_RB +rvh_pt_RB) as Fixed_Route, SUM(rvh_do_route+rvh_pt_route) As Route_Deviated, SUM(rvh_do_demand + rvh_pt_demand + rvh_pt_DT) as Demand, SUM(rvh_do_van) As Vanpool, Sum(rvh_pt_com) As Commuter_Rail, SUM(rvh_do_light + rvh_pt_light+rvh_do_SR+rvh_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;'''

ser_mode_rvm = '''select Yr, SUM(rvm_do_fixed+rvm_pt_fixed+rvm_do_TB+ rvm_pt_TB+rvm_do_CB+rvm_pt_CB+rvm_do_RB +rvm_pt_RB) as Fixed_Route, SUM(rvm_do_route+rvm_pt_route) As Route_Deviated, SUM(rvm_do_demand + rvm_pt_demand + rvm_pt_DT) as Demand, SUM(rvm_do_van) As Vanpool, Sum(rvm_pt_com) As Commuter_Rail, SUM(rvm_do_light + rvm_pt_light+rvm_do_SR+rvm_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_psgr = '''select Yr, SUM(psgr_do_fixed+psgr_pt_fixed+psgr_do_TB+ psgr_pt_TB+psgr_do_CB+psgr_pt_CB +psgr_do_RB +psgr_pt_RB) as Fixed_Route, SUM(psgr_do_route+psgr_pt_route) As Route_Deviated, SUM(psgr_do_demand + psgr_pt_demand + psgr_pt_DT) as Demand, SUM(psgr_do_van) As Vanpool, Sum(psgr_pt_com) As Commuter_Rail, SUM(psgr_do_light + psgr_pt_light+psgr_do_SR+psgr_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_psgr_per_rvh = '''select Yr, SUM(psgr_do_fixed+psgr_pt_fixed+psgr_do_TB+ psgr_pt_TB+psgr_do_CB+psgr_pt_CB +psgr_do_RB +psgr_pt_RB)/SUM(rvh_do_fixed+rvh_pt_fixed+rvh_do_TB+ rvh_pt_TB+rvh_do_CB+rvh_pt_CB+rvh_do_RB +rvh_pt_RB) as Fixed_Route, SUM(psgr_do_route+psgr_pt_route)/SUM(rvh_do_route+rvh_pt_route) As Route_Deviated, SUM(psgr_do_demand + psgr_pt_demand + psgr_pt_DT)/SUM(rvh_do_demand + rvh_pt_demand + rvh_pt_DT) as Demand, SUM(psgr_do_van)/SUM(rvh_do_van) As Vanpool, Sum(psgr_pt_com)/Sum(rvh_pt_com) As Commuter_Rail, SUM(psgr_do_light + psgr_pt_light+psgr_do_SR+psgr_pt_SR)/SUM(rvh_do_light + rvh_pt_light+rvh_do_SR+rvh_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_psgr_per_rvm = '''select Yr, SUM(psgr_do_fixed+psgr_pt_fixed+psgr_do_TB+ psgr_pt_TB+psgr_do_CB+psgr_pt_CB +psgr_do_RB +psgr_pt_RB)/SUM(rvm_do_fixed+rvm_pt_fixed+rvm_do_TB+ rvm_pt_TB+rvm_do_CB+rvm_pt_CB+rvm_do_RB +rvm_pt_RB) as Fixed_Route, SUM(psgr_do_route+psgr_pt_route)/SUM(rvm_do_route+rvm_pt_route) As Route_Deviated, SUM(psgr_do_demand + psgr_pt_demand + psgr_pt_DT)/SUM(rvm_do_demand + rvm_pt_demand + rvm_pt_DT) as Demand, SUM(psgr_do_van)/SUM(rvm_do_van) As Vanpool, Sum(psgr_pt_com)/Sum(rvm_pt_com) As Commuter_Rail, SUM(psgr_do_light + psgr_pt_light+psgr_do_SR+psgr_pt_SR)/SUM(rvm_do_light + rvm_pt_light+rvm_do_SR+rvm_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_oex = '''select Yr, SUM(oex_do_fixed +oex_pt_fixed+oex_do_TB+ oex_do_RB+ oex_pt_RB+ oex_pt_TB+oex_do_CB+oex_pt_CB) as Fixed_Route, SUM(oex_do_route+oex_pt_route) As Route_Deviated, SUM(oex_do_demand + oex_pt_demand + oex_pt_DT) as Demand, SUM(oex_do_van) As Vanpool, Sum(oex_pt_com) As Commuter_Rail, SUM(oex_do_light + oex_pt_light+oex_do_SR+oex_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_oex_per_rvh = '''select Yr, SUM(oex_do_fixed+oex_pt_fixed+oex_do_TB+ oex_pt_TB+oex_do_CB+oex_pt_CB +oex_do_RB +oex_pt_RB)/SUM(rvh_do_fixed+rvh_pt_fixed+rvh_do_TB+ rvh_pt_TB+rvh_do_CB+rvh_pt_CB+rvh_do_RB +rvh_pt_RB) as Fixed_Route, SUM(oex_do_route+oex_pt_route)/SUM(rvh_do_route+rvh_pt_route) As Route_Deviated, SUM(oex_do_demand + oex_pt_demand + oex_pt_DT)/SUM(rvh_do_demand + rvh_pt_demand + rvh_pt_DT) as Demand, SUM(oex_do_van)/SUM(rvh_do_van) As Vanpool, Sum(oex_pt_com)/Sum(rvh_pt_com) As Commuter_Rail, SUM(oex_do_light + oex_pt_light+oex_do_SR+oex_pt_SR)/SUM(rvh_do_light + rvh_pt_light+rvh_do_SR+rvh_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_oex_per_rvm = '''select Yr, SUM(oex_do_fixed+oex_pt_fixed+oex_do_TB+ oex_pt_TB+oex_do_CB+oex_pt_CB +oex_do_RB +oex_pt_RB)/SUM(rvm_do_fixed+rvm_pt_fixed+rvm_do_TB+ rvm_pt_TB+rvm_do_CB+rvm_pt_CB+rvm_do_RB +rvm_pt_RB) as Fixed_Route, SUM(oex_do_route+oex_pt_route)/SUM(rvm_do_route+rvm_pt_route) As Route_Deviated, SUM(oex_do_demand + oex_pt_demand + oex_pt_DT)/SUM(rvm_do_demand + rvm_pt_demand + rvm_pt_DT) as Demand, SUM(oex_do_van)/SUM(rvm_do_van) As Vanpool, Sum(oex_pt_com)/Sum(rvm_pt_com) As Commuter_Rail, SUM(oex_do_light + oex_pt_light+oex_do_SR+oex_pt_SR)/SUM(rvm_do_light + rvm_pt_light+rvm_do_SR+rvm_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_oex_per_psgr = '''select Yr, SUM(oex_do_fixed+oex_pt_fixed+oex_do_TB+ oex_pt_TB+oex_do_CB+oex_pt_CB +oex_do_RB +oex_pt_RB)/SUM(psgr_do_fixed+psgr_pt_fixed+psgr_do_TB+ psgr_pt_TB+psgr_do_CB+psgr_pt_CB+psgr_do_RB +psgr_pt_RB) as Fixed_Route, SUM(oex_do_route+oex_pt_route)/SUM(psgr_do_route+psgr_pt_route) As Route_Deviated, SUM(oex_do_demand + oex_pt_demand + oex_pt_DT)/SUM(psgr_do_demand + psgr_pt_demand + psgr_pt_DT) as Demand, SUM(oex_do_van)/SUM(psgr_do_van) As Vanpool, Sum(oex_pt_com)/Sum(psgr_pt_com) As Commuter_Rail, SUM(oex_do_light + oex_pt_light+oex_do_SR+oex_pt_SR)/SUM(psgr_do_light + psgr_pt_light+psgr_do_SR+psgr_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_farebox_recovery = '''select Yr, SUM(rev_do_fixed+rev_pt_fixed+rev_do_TB+ rev_pt_TB+rev_do_CB+rev_pt_CB +rev_do_RB +rev_pt_RB)/SUM(oex_do_fixed+oex_pt_fixed+oex_do_TB+ oex_pt_TB+oex_do_CB+oex_pt_CB+oex_do_RB +oex_pt_RB)*100 as Fixed_Route, SUM(rev_do_route+rev_pt_route)/SUM(oex_do_route+oex_pt_route)*100 As Route_Deviated, SUM(rev_do_demand + rev_pt_demand + rev_pt_DT)/SUM(oex_do_demand + oex_pt_demand + oex_pt_DT)*100 as Demand, SUM(rev_do_van)/SUM(oex_do_van)*100 As Vanpool, Sum(rev_pt_com)/Sum(oex_pt_com)*100 As Commuter_Rail, SUM(rev_do_light + rev_pt_light+rev_do_SR+rev_pt_SR)/SUM(oex_do_light + oex_pt_light+oex_do_SR+oex_pt_SR)*100 AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;
'''

ser_mode_rvh_per_employee = '''select Yr, SUM(rvh_do_fixed+rvh_pt_fixed+rvh_do_TB+ rvh_pt_TB+rvh_do_CB+rvh_pt_CB+rvh_do_RB +rvh_pt_RB)/SUM(fte_do_fixed+fte_pt_fixed+fte_do_TB+ fte_pt_TB+fte_do_CB+fte_pt_CB+fte_do_RB +fte_pt_RB) as Fixed_Route, SUM(rvh_do_route+rvh_pt_route)/SUm(fte_do_route + fte_pt_route) As Route_Deviated, SUM(rvh_do_demand + rvh_pt_demand + rvh_pt_DT)/SUM(fte_do_demand + fte_pt_demand + fte_pt_DT) as Demand, SUM(rvh_do_van)/SUM(fte_do_van) As Vanpool, Sum(rvh_pt_com)/Sum(fte_pt_com) As Commuter_Rail, SUM(rvh_do_light + rvh_pt_light+rvh_do_SR+rvh_pt_SR)/SUM(fte_do_light+fte_pt_light + fte_do_SR+fte_pt_SR) AS Light_Rail from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('small urban', 'urban', 'rural') and t1.Yr in {} Group By Yr;'''

sw_op_stats_fixed = '''select Agnc, t2.agencytype, sum(rvh_do_fixed + rvh_pt_fixed) as Revenue_Vehicle_Hours, sum(tvh_do_fixed + tvh_pt_fixed) as Total_Vehicle_Hours,
sum(rvm_do_fixed + rvm_pt_fixed) as Revenue_Vehicle_Miles, sum(tvm_do_fixed + tvm_pt_fixed) as Total_Vehicle_Miles, sum(psgr_do_fixed + psgr_pt_fixed) as Passenger_Trips,
Sum(fte_do_fixed + fte_pt_fixed) as Employees_FTEs, Sum(oex_do_fixed + oex_pt_fixed) as Operating_Expenses, sum(rev_do_fixed + rev_pt_fixed) as Farebox_Revenues,
Sum(psgr_do_fixed + psgr_pt_fixed)/Sum(rvh_do_fixed + rvh_pt_fixed) AS Passenger_Trips_Revenue_Hour, Sum(psgr_do_fixed + psgr_pt_fixed)/Sum(rvm_do_fixed + rvm_pt_fixed) as Passenger_Trips_per_Revenue_Mile,
Sum(rvh_do_fixed + rvh_pt_fixed)/Sum(fte_do_fixed + fte_pt_fixed) as Revenue_Hours_Per_Employee, Sum(oex_do_fixed + oex_pt_fixed)/Sum(rvh_do_fixed + rvh_pt_fixed) As Operating_Expenses_per_Revenue_Vehicle_Hour,
sum(oex_do_fixed + oex_pt_fixed)/sum(rvm_do_fixed + rvm_pt_fixed) Operating_Expense_per_Revenue_Vehicle_Mile, sum(oex_do_fixed + oex_pt_fixed)/sum(psgr_do_fixed + psgr_pt_fixed) as Operating_Expense_per_Passenger_Trip, 
(sum(rev_do_fixed + rev_pt_fixed)/sum(oex_do_fixed + oex_pt_fixed))*100 As Farebox_Recovery_Ratio from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr = {} Group by Agnc Order By Agnc;'''

sw_op_stats_demand = '''select Agnc, t2.agencytype, sum(rvh_do_demand + rvh_pt_demand+rvh_pt_DT) as Revenue_Vehicle_Hours, sum(tvh_do_demand + tvh_pt_demand+tvh_pt_DT) as Total_Vehicle_Hours,
sum(rvm_do_demand + rvm_pt_demand+rvm_pt_DT) as Revenue_Vehicle_Miles, sum(tvm_do_demand + tvm_pt_demand+tvm_pt_DT) as Total_Vehicle_Miles, sum(psgr_do_demand + psgr_pt_demand+psgr_pt_DT) as Passenger_Trips,
Sum(fte_do_demand + fte_pt_demand + fte_pt_DT) as Employees_FTEs, Sum(oex_do_demand + oex_pt_demand+oex_pt_DT) as Operating_Expenses, sum(rev_do_demand + rev_pt_demand+rev_pt_DT) as Farebox_Revenues,
Sum(psgr_do_demand + psgr_pt_demand+psgr_pt_DT)/Sum(rvh_do_demand + rvh_pt_demand+rvh_pt_DT) AS Passenger_Trips_Revenue_Hour, Sum(psgr_do_demand + psgr_pt_demand+psgr_pt_DT)/Sum(rvm_do_demand + rvm_pt_demand+rvm_pt_DT) as Passenger_Trips_per_Revenue_Mile,
Sum(rvh_do_demand + rvh_pt_demand+rvh_pt_DT)/Sum(fte_do_demand + fte_pt_demand+fte_pt_DT) as Revenue_Hours_Per_Employee, Sum(oex_do_demand + oex_pt_demand+oex_pt_DT)/Sum(rvh_do_demand + rvh_pt_demand+rvh_pt_DT) As Operating_Expenses_per_Revenue_Vehicle_Hour,
sum(oex_do_demand + oex_pt_demand+oex_pt_DT)/sum(rvm_do_demand + rvm_pt_demand + rvm_pt_DT) as Operating_Expense_per_Revenue_Vehicle_Mile, sum(oex_do_demand + oex_pt_demand + oex_pt_DT)/sum(psgr_do_demand + psgr_pt_demand + psgr_pt_DT) as Operating_Expense_per_Passenger_Trip, 
(sum(rev_do_demand + rev_pt_demand + rev_pt_DT)/sum(oex_do_demand + oex_pt_demand + oex_pt_DT))*100 As Farebox_Recovery_Ratio from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr = {} Group by Agnc Order By Agnc;
'''

sw_op_stats_van = '''select Agnc, t2.agencytype, rvh_do_van as Revenue_Vehicle_Hours, tvh_do_van as Total_Vehicle_Hours,
rvm_do_van as Revenue_Vehicle_Miles, tvm_do_van as Total_Vehicle_Miles, psgr_do_van as Passenger_Trips,
fte_do_van as Employees_FTEs, oex_do_van as Operating_Expenses,rev_do_van as Farebox_Revenues,
psgr_do_van/rvh_do_van AS Passenger_Trips_Revenue_Hour, psgr_do_van/rvm_do_van as Passenger_Trips_per_Revenue_Mile,
rvh_do_van/fte_do_van as Revenue_Hours_Per_Employee, oex_do_van/rvh_do_van As Operating_Expenses_per_Revenue_Vehicle_Hour,
oex_do_van/rvm_do_van as Operating_Expense_per_Revenue_Vehicle_Mile, oex_do_van/psgr_do_van as Operating_Expense_per_Passenger_Trip, 
(rev_do_van/oex_do_van)*100 As Farebox_Recovery_Ratio from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr = {} Group by Agnc Order By Agnc;
'''

sw_op_stats_com = '''select Agnc, t2.agencytype, rvh_pt_com as Revenue_Vehicle_Hours, tvh_pt_com as Total_Vehicle_Hours,
rvm_pt_com as Revenue_Vehicle_Miles, tvm_pt_com as Total_Vehicle_Miles, psgr_pt_com as Passenger_Trips,
fte_pt_com as Employees_FTEs, oex_pt_com as Operating_Expenses,rev_pt_com as Farebox_Revenues,
psgr_pt_com/rvh_pt_com AS Passenger_Trips_Revenue_Hour, psgr_pt_com/rvm_pt_com as Passenger_Trips_per_Revenue_Mile,
rvh_pt_com/fte_pt_com as Revenue_Hours_Per_Employee, oex_pt_com/rvh_pt_com As Operating_Expenses_per_Revenue_Vehicle_Hour,
oex_pt_com/rvm_pt_com as Operating_Expense_per_Revenue_Vehicle_Mile, oex_pt_com/psgr_pt_com as Operating_Expense_per_Passenger_Trip, 
(rev_pt_com/oex_pt_com)*100 As Farebox_Recovery_Ratio from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr = {} Group by Agnc Order By Agnc;
'''


sw_invest_rev = '''SELECT Yr, SUM(sales_tax+utility_tax+mvet) AS Local_Tax, SUM(other_ad+ other_int + other_gain + other_rev) AS Other_Local_Revenue, SUM(fta_5307_op +fta_5307_prv +fta_5311_op +fta_5316_op +fta_other_op+fta_5307_cg+fta_5309_cg+fta_5310_cg+fta_5311_cg+fta_5316_cg +Fstp_grnt_cg +fed_other_grnt_cg) As Federal_Revenues,
SUM(st_op_rmg+st_op_regmg+st_op_sng+st_op_stod+st_op_ste+st_op_other+st_cg_rmg+st_cg_regmg +st_cg_sng +st_cg_ste+st_ct_van +st_cg_other) AS State_Revenues, SUM(other_ad +other_int +other_gain +other_rev) AS Other_Operating_Revenue,
 Sum(fta_5307_cg+fta_5309_cg+fta_5310_cg+fta_5311_cg+fta_5316_cg +Fstp_grnt_cg +fed_other_grnt_cg) AS Federal_Capital_Investment, Sum(st_cg_rmg+st_cg_regmg +st_cg_sng +st_cg_ste+st_ct_van +st_cg_other) As State_Capital_Investment
FROM ptsummary_transit.revenues as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} group by Yr;'''

sw_invest_td = '''Select Yr, SUM(oex_do_fixed+ oex_pt_fixed+oex_do_RB+oex_pt_RB+oex_do_CB+oex_pt_CB+oex_do_TB+oex_pt_TB+oex_pt_com+oex_do_light+oex_pt_light+oex_do_SR+oex_pt_SR
+oex_do_route+oex_pt_route+oex_do_demand+oex_pt_demand+oex_pt_DT+oex_do_van) as Operating_Investments, SUM(rev_do_van +rev_do_fixed+rev_do_light+rev_do_route + rev_do_demand+rev_do_CB+rev_do_RB + rev_do_SR + rev_do_TB +rev_pt_fixed +rev_pt_com + rev_pt_light + rev_pt_route + rev_pt_demand+rev_pt_CB +rev_pt_DT +rev_pt_RB+ rev_pt_SR) as Farebox_Revenues FROM ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} group by Yr;'''

sw_invest_exp = '''Select Yr, Sum(local_cap) as Local_Capital_Investment, SUM(Otra_exp_num + interest + principal) as Other_Capital_Investment from ptsummary_transit.expenses as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group by Yr;'''


random_text_local_tax = '''SELECT Yr, sum(sales_tax + mvet+utility_tax) as Local_Tax FROM ptsummary_transit.revenues as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} group by Yr'''

random_text_local_tax_sound = '''SELECT Yr, sum(sales_tax + mvet+utility_tax) as Sound FROM ptsummary_transit.revenues where Agnc = 'sound' and Yr in {} Group By Yr;'''

fares = '''SELECT Yr, SUM(rev_do_van +rev_do_fixed+rev_do_light+rev_do_route + rev_do_demand+rev_do_CB+rev_do_RB + rev_do_SR + rev_do_TB +rev_pt_fixed +rev_pt_com + rev_pt_light + rev_pt_route + rev_pt_demand+rev_pt_CB +rev_pt_DT +rev_pt_RB+ rev_pt_SR) as Fares from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;'''

operating_revenues = '''Select Yr, SUM(sales_tax+utility_tax+mvet+fta_5307_op +fta_5307_prv +fta_5311_op +fta_5316_op +fta_other_op+st_op_rmg+st_op_regmg+st_op_sng+st_op_stod+st_op_ste+st_op_other+other_ad +other_int +other_gain +other_rev) as Operating_Revenues from ptsummary_transit.revenues as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Yr;'''

fare_changes = '''SELECT Yr, t1.Agnc, agencytype, SUM(rev_do_van +rev_do_fixed+rev_do_light+rev_do_route + rev_do_demand+rev_do_CB+rev_do_RB + rev_do_SR + rev_do_TB +rev_pt_fixed +rev_pt_com + rev_pt_light + rev_pt_route + rev_pt_demand+rev_pt_CB +rev_pt_DT +rev_pt_RB+ rev_pt_SR) as Fares from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and t1.Yr in {} Group By Agnc, Yr;'''

farebox_changes = '''With summary_table AS (SELECT Yr, Agnc, t2.agencytype, SUM(rev_do_fixed+rev_do_light+rev_do_route + rev_do_demand+rev_do_CB+rev_do_RB + rev_do_SR + rev_do_TB +rev_pt_fixed +rev_pt_com + rev_pt_light
 + rev_pt_route + rev_pt_demand+rev_pt_CB +rev_pt_DT +rev_pt_RB) As Fares
from ptsummary_transit.transit_data as t1 inner join ptsummary_transit.agencytype as t2 on t1.Agnc = t2.Agency where t2.agencytype in ('urban', 'rural', 'small urban') and
 t1.Yr in {} Group By Agnc, Yr)  
 
 Select A.*, 
	Case WHen (A.Fares IS NULL or B.Fares IS Null or B.Fares = 0) Then 0 Else (A.Fares - B.Fares)*100/B.Fares End As PercentDiff
    From summary_table A Left Join summary_table B
    On A.Yr = (B.Yr+1) and A.Agnc = B.Agnc'''
