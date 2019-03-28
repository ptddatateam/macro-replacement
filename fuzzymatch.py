import pandas as pd
from fuzzywuzzy import fuzz
import os
import re
import csv
import itertools

def read_datasets(path1, path2):
    df1 = pd.read_excel(path1)
    df2 = pd.read_csv(path2, encoding = 'latin1')
    return df1, df2


def normalize_text(df):
    df['name']  = df['name'].astype(str)
    df['normaltext'] = df['name'].apply(lambda x: x.lower())
    df['normaltext'] = df['normaltext'].apply(lambda x: regex(x))
    return df


def regex(x):
    x = re.sub('\W+', '', x)
    return x

def fuzz_match(text1, text2):
    score = fuzz.token_set_ratio(text1, text2)
    return score
def fuzz_match_full(text1, text2):
    score = fuzz.ratio(text1, text2)
    return score


def match_stuff(df1, df2):
    scrapename = df1['normaltext'].tolist()
    for name in scrapename:
        for index, row in df2.iterrows():
            namescore = fuzz_match(name, row['normaltext'])
            if namescore > 80:
                matchvalues = df1[df1.normaltext == name]
                scrapelist = matchvalues.values.tolist()
                dblist = df2[df2.normaltext == row['normaltext']]
                dblist = dblist.name.tolist()
                namescore = str(namescore)
                dblist.append(namescore)
                scrapelist.extend(dblist)
                scrapedlist = list(itertools.chain(*scrapelist))
                to_csv(scrapedlist, )


def to_csv(res, path):
    with open(path, 'a', newline='') as file:
        writer = csv.writer(file, delimiter = ',')
        writer.writerows([res])

def Main(path1, path2):
    df1, df2 = read_datasets(path1, path2)
    df1 = normalize_text(df1)
    df2 = normalize_text(df2)
    match_stuff(df1, df2)

if __name__ == "__main__":
    Main()
