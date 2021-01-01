import os

import dash
import dash_core_components as dcc
import dash_html_components as html

years = ['2020','2019','2018']

mapbox_token = os.environ['MAPBOX_ACCESSTOKEN']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
github_ref = 'https://github.com/sigsmoore/phila-elections'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
            html.Td('* voting divisions may not be accurate for years prior to 2019',
                    style={'text-align': 'left'}),
            html.Td(html.A(github_ref, href=github_ref),
                    style={'text-align': 'right'}),
        ]),
        style={'font-size': 'small', 'width': '100%'},
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
