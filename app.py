# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import pandas as pd
import csv
import numpy as np
import dash_table
import datetime
import io
import base64
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#fff',
    'text': '#111'
}
def generate_table(dataframe):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe)))
        ])
    ])

#app.scripts.config.serve_locally = True
#app.config.suppress_callback_exceptions = True
#app.server.config.suppress_callback_exceptions = True
#app.config[‘suppress_callback_exceptions’] = True

with open("1.csv", 'r') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    data = np.array(list(reader)).astype(float)

app.layout = html.Div(children=[
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    dcc.Graph(
        id='my-graph',
        figure=dict(
            data=[
                dict(
                    x=data[:,0],
                    y=data[:,1],
                    name='Rest of world',
                    mode=  'markers',
                    marker=dict(
                        color='rgb(55, 83, 109)',
                    line= {'width': 0.5, 'color': 'white'}
                    ),
                )
            ],
            layout= {
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    },
                },
            ),
    ),
    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    })
])

pre_style = {
    'whiteSpace': 'pre-wrap',
    'wordBreak': 'break-all',
    'whiteSpace': 'normal'
}

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return html.Div([
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            #editable=True,
            style_cell={
                'textAlign': 'left',
                'border': '1px solid grey',
            },
            style_header={
                'border': '1px solid black'},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            css=[
                {
                    'selector': 'table',
                    'rule': 'auto'
                }
            ],
            style_table={
                'maxHeight': '300px',
                'width': '50%',
                'overflowY': 'scroll',
                'border': 'thin lightgrey solid'
            },
            ),
        dcc.Graph(
            figure=dict(
                data=[
                dict(
                    x=df['x'],
                    y=df['y'],
                    name='Rest of world',
                    mode=  'markers',
                    marker=dict(
                        color='rgb(55, 83, 109)',
                        line= {'width': 0.5, 'color': 'white'},
                        size=df['size'],
                    ),
                )
            ],
                layout={
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    },
                },
            ),
        ),
        #html.H5(filename),
        #html.H6(datetime.datetime.fromtimestamp(date))
    ])

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)