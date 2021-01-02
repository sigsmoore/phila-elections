##### LOAD GEOJSON #####
import json
with open('data.geo/Phila_Political_Merged.geojson') as f:
    geo = json.load(f)


##### LOAD DATA #####
import pandas as pd

data = pd.HDFStore('data/pivoted_tables.h5', 'r')
years = list(data['years'])

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
    this_year_offices = list(data['offices/'+year])
    new_val = old_val if old_val in this_year_offices else this_year_offices[0]
    return [dict(label=r, value=r) for r in this_year_offices], new_val

@app.callback(
    Output('tile-values', 'options'),
    Output('tile-values', 'value'),
    Input('office', 'value'),
    State('year', 'value'),
    State('division', 'value'),
    State('tile-values', 'value'))
def set_value_options(office, year, div, old_val):
    key = f"{year} general by {div} for {office}"
    df = data[key]
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
    df = data[key]
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
