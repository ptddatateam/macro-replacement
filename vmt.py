    def cvm(row):
        if (row['carpool_days']>0) & (row['vanpool_days']==0) & (row['motorcycle_days']==0):
            val = 1
        elif (row['carpool_days']==0) & (row['vanpool_days']>0) & (row['motorcycle_days']==0):
            val = 2
        elif (row['carpool_days']==0) & (row['vanpool_days']==0) & (row['motorcycle_days']>0):
            val = 3
        elif (row['carpool_days']>0) & (row['vanpool_days']>0) & (row['motorcycle_days']==0):
            val = 4
        elif (row['carpool_days']>0) & (row['vanpool_days']==0) & (row['motorcycle_days']>0):
            val = 5
        elif (row['carpool_days']==0) & (row['vanpool_days']>0) & (row['motorcycle_days']>0):
            val = 6
        elif (row['carpool_days']>0) & (row['vanpool_days']>0) & (row['motorcycle_days']>0):
            val = 7
        else:
            val = np.nan
        return val
    df['cvm'] = df.apply(cvm, axis=1)

    def carpoolOccupancy(row):
        if (row['cvm'] == 1) | (row['cvm'] == 4) | (row['cvm'] == 5) | (row['cvm'] == 7):
            val = row['cvm_occupancy']
        else:
            val = np.nan
        return val
    df['carpool_occ'] = df.apply(carpoolOccupancy, axis=1)

    def carpoolOccupancyImpute(row):
        if row['carpool_occ'] < 2:
            val = 2
        else:
            val = row['carpool_occ']
        return val
    df['carpool_occ_impute'] = df.apply(carpoolOccupancyImpute, axis=1)

    def vanpoolOccupancy(row):
        if (row['cvm'] == 2) | (row['cvm'] == 4) | (row['cvm'] == 6) | (row['cvm'] == 7):
            val = row['cvm_occupancy']
        else:
            val = np.nan
        return val
    df['vanpool_occ'] = df.apply(vanpoolOccupancy, axis=1)

    def vanpoolOccupancyImpute(row):
        if row['vanpool_occ'] < 2:
            val = 7
        else:
            val = row['vanpool_occ']
        return val
    df['vanpool_occ_impute'] = df.apply(vanpoolOccupancyImpute, axis=1)

    def motorcycleOccupancy(row):
        if (row['cvm'] == 3) | (row['cvm'] == 5) | (row['cvm'] == 6) | (row['cvm'] == 7):
            val = row['cvm_occupancy']
        else:
            val = np.nan
        return val
    df['motorcycle_occ'] = df.apply(motorcycleOccupancy, axis=1)

    def motorcycleOccupancyImpute(row):
        if row['motorcycle_occ'] > 2:
            val = 1
        else:
            val = row['motorcycle_occ']
        return val
    df['motorcycle_occ_impute'] = df.apply(motorcycleOccupancyImpute, axis=1)

    df['carpool_adj_trips'] = (df['carpool_days'] / df['carpool_occ']).fillna(0)
    df['vanpool_adj_trips'] = (df['vanpool_days'] / df['vanpool_occ']).fillna(0)
    df['motorcycle_adj_trips'] = (df['motorcycle_days'] / df['motorcycle_occ']).fillna(0)
    df['adjusted_trips'] = df['drv_alone_days'] + df['carpool_adj_trips'] + df['vanpool_adj_trips'] + df['motorcycle_adj_trips']
    df['potential_trips'] = df['drv_alone_days'] + df['carpool_days'] + df['vanpool_days'] + \
                            df['motorcycle_days'] + df['bus_days'] + df['bike_days'] + df['walk_days'] + \
                            df['telework_days'] + df['other_days'] + df['train_days'] + df['cww_days'] + \
                            df['ferry_w_ vehicle_days'] + df['ferry_walkon_days']
    df['vmt_oneway_correct'] = (df['adjusted_trips'] / df['potential_trips']) * df['commute_dist']
    df['avg_vmt_oneway_ctr_method'] = (df['adjusted_trips'].sum()/df['potential_trips'].sum()) * (df['commute_dist'].sum()/df['commute_dist'].count())
    return df