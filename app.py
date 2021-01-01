##### LOAD GEOJSON #####
import json
with open('data.geo/Phila_Political_Merged.geojson') as f:
    geo = json.load(f)


##### CODE FOR DATA LOADING #####
import pandas as pd
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

##### PIVOT DATA #####
pivoted_dataframes = {
    key + ' for ' + office: subdf.pivot_table(index='LOCATION',
                                              columns='PARTY',
                                              values='VOTES',
                                              aggfunc='sum')
    for key,df in dataframes.items()
    for office,subdf in df.groupby('OFFICE')}

for df in pivoted_dataframes.values():
    df['TOTAL'] = df.sum(axis=1)

# remove rows where TOTAL is zero
pivoted_dataframes = {
    key: df.loc[df['TOTAL']>0]
    for key,df in pivoted_dataframes.items()}

##### PREPARE MENU OPTIONS #####
party_colorscale = {
    'DEMOCRATIC': 'blues',
    'REPUBLICAN': 'reds',
    'GREEN':      'greens',
    'LIBERTARIAN': ['rgb(256,256,256)', 'rgb(255,232,11)'],
    'INDEPENDENT': 'greys',
}
party_comparison_colorscale = {
    'DEMOCRATIC': 'bluered_r',
    'REPUBLICAN': 'bluered'
}

years = sorted(set(k[:4] for k in dataframes.keys()), reverse=True)

def get_offices(df):
    offices = list(df.OFFICE.unique())
    offices.sort(key=lambda s: (
        1 if s.endswith(' DISTRICT') else 0,
        1 if 'GENERAL ASSEMBLY' in s else (-1 if 'CONGRESS' in s else 0),
        s))
    return offices
offices = {
    y: get_offices(dataframes[y+' general by ward'])
    for y in years}


##### PREPARE DASH APP #####
import os
mapbox_token = os.environ['MAPBOX_ACCESSTOKEN']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
github_ref = 'https://github.com/sigsmoore/phila-elections'

import dash
import dash_core_components as dcc
import dash_html_components as html
app = dash.Dash(__name__,
                title='Philadelphia General Elections',
                external_stylesheets=external_stylesheets
)
server = app.server

app.layout = html.Div([
    html.H2('Philadelphia General Elections'),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='year',
                options=[dict(label=y, value=y) for y in years],
                value=years[0],
                clearable=False,
            ),
            style={'width': '10%', 'display': 'inline-block', 'vertical-align': 'middle'},
        ),
        html.Div(
            ' general election for ',
            style={'display': 'inline'},
        ),
        html.Div(
            dcc.Dropdown(
                id='office',
                clearable=False,
            ),
            style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'middle'},
        ),
        html.Div(
            ' by ',
            style={'display': 'inline'},
        ),
        html.Div(
            dcc.Dropdown(
                id='division',
                options=[
                    dict(label='ward', value='ward'),
                    dict(label='voting district', value='precinct'),
                ],
                value='precinct',
                clearable=False,
            ),
            style={'width': '15%', 'display': 'inline-block', 'vertical-align': 'middle'},
        ),
    ]),

    html.Div([
        dcc.RadioItems(
            id='tile-values',
            options=[
                dict(label='Democratic percentage', value='DEMOCRATIC PERCENTAGE'),
                dict(label='Republican percentage', value='REPUBLICAN PERCENTAGE'),
            ],
            value='DEMOCRATIC PERCENTAGE',
            labelStyle={'display': 'inline'},
        ),
    ]),

    dcc.Graph(
        id='choropleth',
        style={'height': '80vh'},
    ),

    html.Table(
        html.Tr([
            html.Td('* voting districts may not be accurate for years prior to 2019',
                    style={'text-align': 'left'}),
            html.Td(html.A(github_ref, href=github_ref),
                    style={'text-align': 'right'}),
        ]),
        style={'font-size': 'small', 'width': '100%'},
    ),
])


##### CALLBACKS #####
from dash.dependencies import Input, Output, State

@app.callback(
    Output('office', 'options'),
    Output('office', 'value'),
    Input('year', 'value'),
    State('office', 'value'))
def set_office_options(year, old_val):
    new_val = old_val if old_val in offices[year] else offices[year][0]
    return [dict(label=r, value=r) for r in offices[year]], new_val

@app.callback(
    Output('tile-values', 'options'),
    Output('tile-values', 'value'),
    Input('office', 'value'),
    State('year', 'value'),
    State('division', 'value'),
    State('tile-values', 'value'))
def set_value_options(office, year, div, old_val):
    key = f"{year} general by {div} for {office}"
    df = pivoted_dataframes[key]
    opts = []
    for party in party_comparison_colorscale.keys():
        txt = party + ' percentage'
        opts.append(dict(
            label=txt.capitalize(),
            value=txt.upper(),
            disabled=(party not in df.columns)
        ))
    for party in party_colorscale.keys():
        txt = party + ' votes'
        opts.append(dict(
            label=txt.capitalize(),
            value=txt.upper(),
            disabled=(party not in df.columns)
        ))
    new_val = (old_val if not next(o for o in opts if o['value']==old_val)['disabled']
                       else next(o for o in opts if not o['disabled'])['value'])
    return opts, new_val

import plotly.graph_objects as go
@app.callback(
    Output('choropleth', 'figure'),
    Input('year', 'value'),
    Input('office', 'value'),
    Input('division', 'value'),
    Input('tile-values', 'value'))
def display_choropleth(year, office, div, vals):
    key = f"{year} general by {div} for {office}"
    df = pivoted_dataframes[key]
    args = dict(
        geojson=geo,
        locations=df.index,
        marker_line_color='rgba(128, 128, 128, 0.1)',
        marker_opacity=0.6,
        customdata=[
            '<br>'.join(party.title() + " votes: " + str(row[party]) for party in df.columns)
            for _,row in df.iterrows()
        ],
    )
    party,vtype = vals.split()
    if vtype=='PERCENTAGE':
        args.update(
            z=100*df[party]/df['TOTAL'],
            zmin=0,
            zmax=100,
            colorscale=party_comparison_colorscale[party],
            colorbar=dict(
                title=vals.title(),
                tickmode="array",
                tickvals=[0, 50, 100],
                ticktext=["0%", "50%", "100%"],
                ticks="outside"
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                + vals.capitalize() + ": %{z:.1f}%<br><br>"
                + "%{customdata}<extra></extra>"
            ),
        )
    else:
        args.update(
            z=df[party],
            zmin=0,
            colorscale=party_colorscale[party],
            colorbar=dict(title=vals.title()),
            hovertemplate="<b>%{text}</b><br><br>%{customdata}<extra></extra>",
        )
    args['text'] = (['Ward '+loc for loc in df.index] if div=='ward'
                    else [f"Ward {loc[:2]}, Division {loc[2:]}" for loc in df.index])
    fig = go.Figure(go.Choroplethmapbox(**args))
    fig.update_layout(
        # title_text=("Philadelphia " + year + " General Election by "
        #             + ("Ward" if div=='ward' else "Voting District")),
        mapbox_accesstoken=mapbox_token,
        mapbox_zoom=10, mapbox_center={"lat": 40.0, "lon": -75.1636},
        uirevision=1,
        margin=dict(l=40, r=80, b=0, t=40),
    )
    return fig


##### START SERVER #####
if __name__ == '__main__':
    app.run_server(debug=True)
