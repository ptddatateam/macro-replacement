import pandas as pd
import pypyodbc




def connecttodb(org):
    sqlquery = '''select OrganizationName FROM Organization Where OrganizationName LIKE '%' + '{}' + '%' '''.format(org)
    cnxn = pypyodbc.connect(driver='{SQL Server}', server = 'HQOLYMSQL09P', database = 'CTRSurvey')
    cursor = cnxn.cursor()
    cursor.execute(sqlquery)
    results = cursor.fetchall()
    cursor.close()
    reslist = [org, results]
    return reslist


df = pd.read_csv(r'C:\Users\SchumeN\Documents\CTR\webscraping\scrape.csv')

orgs = df.name.tolist()
resultlist = []

for org in orgs:
    org = org.replace("'", '')
    results = connecttodb(org)
    resultlist.append(results)
df['queries'] = resultlist

df.to_csv(r'C:\Users\SchumeN\Documents\CTR\webscraping\scrape.csv')