# perform pivots on electon data tables and store in HDFStore

import pandas as pd

##### CODE FOR DATA LOADING #####
type_col_variants = ['TYPE','VOTE TYPE']
office_col_variants = ['OFFICE','CATEGORY']
candidate_col_variants = ['CANDIDATE','NAME','SELECTION']
vote_col_variants = ['VOTES','VOTE COUNT']
csv_dtypes = dict(
    WARD=int,
    DIVISION=int,
    PARTY=str,
    **{c: str for c in type_col_variants},
    **{c: str for c in office_col_variants},
    **{c: str for c in candidate_col_variants},
    **{c: int for c in vote_col_variants},
)
read_csv_opts = dict(dtype=csv_dtypes, encoding='latin1')

def rename_cols(df):
    type_col = next((c for c in type_col_variants if c in df.columns), None)
    office_col = next((c for c in office_col_variants if c in df.columns), None)
    candidate_col = next((c for c in candidate_col_variants if c in df.columns), None)
    vote_col = next((c for c in vote_col_variants if c in df.columns), None)
    return df.rename(
        columns={type_col: 'TYPE',
                 office_col: 'OFFICE',
                 candidate_col: 'CANDIDATE',
                 vote_col: 'VOTES'
        })

def collapse_types(df):
    return df.drop(columns=['TYPE'])\
             .groupby([c for c in df.columns if c not in ['TYPE','VOTES']], as_index=False)\
             .sum()

def collapse_divisions(df):
    return df.drop(columns=['DIVISION'])\
             .groupby([c for c in df.columns if c not in ['DIVISION','VOTES']], as_index=False)\
             .sum()

##### LOAD DATA #####
dataframes = {
    '2020 general by precinct': rename_cols(pd.read_csv('data/2020_general.csv', **read_csv_opts)),
    '2019 general by precinct': rename_cols(pd.read_csv('data/2019_general.csv', **read_csv_opts)),
    '2018 general by precinct': rename_cols(pd.read_csv('data/2018_general.csv', **read_csv_opts)),
    '2017 general by precinct': rename_cols(pd.read_csv('data/2017_general.csv', **read_csv_opts)),
    '2016 general by precinct': rename_cols(pd.read_csv('data/2016_general.csv', **read_csv_opts)),
}

dataframes = {key: collapse_types(df) for key,df in dataframes.items()}

import re
dataframes.update({
    re.sub(r' by precinct$', ' by ward', key): collapse_divisions(df)
    for key,df in dataframes.items()})

for k,df in dataframes.items():
    year = k[:4]
    div  = k.split()[-1]
    if div == 'ward':
        df['LOCATION'] = df['WARD'].map(str)
    elif div == 'precinct':
        df['LOCATION'] = df.apply(lambda row: "{:02d}{:02d}".format(row['WARD'],row['DIVISION']), axis=1)
    else:
        raise ValueError("invalid division: "+div)


##### CREATE HDFSTORE #####
import warnings
import tables
# we're going to have "unnatural" key values
warnings.simplefilter('ignore', tables.NaturalNameWarning)

data = pd.HDFStore('data/pivoted_tables.h5')

##### PIVOT DATA #####
for key,df in dataframes.items():
    for office,subdf in df.groupby('OFFICE'):
        pivdf = subdf.pivot_table(index='LOCATION',
                                  columns='PARTY',
                                  values='VOTES',
                                  aggfunc='sum')
        pivdf['TOTAL'] = pivdf.sum(axis=1)
        # remove rows where TOTAL is zero
        pivdf = pivdf.loc[pivdf['TOTAL']>0]

        data[key + ' for ' + office] = pivdf


years = sorted(set(k[:4] for k in dataframes.keys()), reverse=True)
data['years'] = pd.Series(years)

def get_offices(df):
    offices = list(df.OFFICE.unique())
    offices.sort(key=lambda s: (
        1 if s.endswith(' DISTRICT') else 0,
        1 if 'GENERAL ASSEMBLY' in s else (-1 if 'CONGRESS' in s else 0),
        s))
    return offices

for y in years:
    data['offices/'+y] = pd.Series(get_offices(dataframes[y+' general by ward']))

data.close()
