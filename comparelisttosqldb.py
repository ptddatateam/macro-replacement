import pandas as pd
import pypyodbc
from fuzzywuzzy import fuzz
import re
import itertools
import csv
from nltk.corpus import stopwords


def read_data(path):
    try:
        df = pd.read_csv(path)
    except:
        df = pd.read_excel(path)
    return df

def connect_to_sql(companyname):
    companyname = str(companyname)
    company = companyname.split(" ")
    company = [j for j in company if j not in stopwords.words('english')]
    matches = []
    for companyname in company:
        companyname = replace_commmon_words(companyname)
        companyname = companyname.replace("'", "")
        sqlscript = prep_sql_script(companyname)
        cnxn = pypyodbc.connect(driver='{SQL Server}', server = 'HQOLYMSQL09P', database = 'CTRSurvey')
        cursor = cnxn.cursor()
        cursor.execute(sqlscript)
        tables = cursor.fetchall()
        tables = [list(j) for j in tables]
        tables = list(itertools.chain(*tables))
        matches.append(tables)
    tables = list(itertools.chain(*matches))
    return tables

def normalize(strng):
    strng = strng.lower()
    strng = replace_commmon_words(strng)
    strng = regex(strng)
    return strng

def regex(x):
    x = re.sub('\W+', '', x)
    return x

def fuzz_match(text1, text2):
    score = fuzz.partial_ratio(text1, text2)
    return score
def fuzz_match_full(text1, text2):
    score = fuzz.ratio(text1, text2)
    return score

def replace_commmon_words(text):
    text = text.replace('inc', "")
    text = text.replace('corporation', '')
    text = text.replace('llc', '')
    text = text.replace('group', '')
    text = text.replace('company', '')
    text = text.replace('com', '')
    text = text.replace('technologies', '')
    text = text.replace('solutions', '')
    text = text.replace('international', '')
    text = text.replace('health', '')
    return text

def fuzz_tokenize(text1, text2):
    score = fuzz.token_set_ratio(text1, text2)
    return score

def prep_sql_script(fragment):
    sqlscript = '''SELECT Organization.OrganizationName
  FROM [CTRSurvey].[dbo].[Organization]
  WHERE OrganizationName Like '%' + '{}' + '%' '''.format(fragment)
    return sqlscript


def to_csv(res, path):
    with open(path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter = ',')
        try:
            writer.writerows([res])
        except:
            pass

def fuzzy_string_match(company, tables):
    for table in tables:
        if table == []:
            continue
        ncompany = normalize(company)
        ntable = normalize(table)
        score1 = fuzz_match_full(ncompany, ntable)
        score2 = fuzz_match(ncompany, ntable)
        score3 = fuzz_tokenize(ncompany, ntable)
        aggscore = (score2 + score3)/2
        if score2 > 89 and aggscore > 50:
            to_csv([company, table, aggscore], r'C:\Users\SchumeN\Documents\CTR\webscraping\morecompanies\testmatch.csv')








def Main(path):
    df = read_data(path)
    df.name = df.name.astype(str)
    companies = df.name.tolist()
    for company in companies:
        tables = connect_to_sql(company)
        fuzzy_string_match(company, tables)




if __name__ == "__main__":
    Main(r'C:\Users\SchumeN\Documents\CTR\webscraping\morecompanies\nonseattlebased.xlsx')