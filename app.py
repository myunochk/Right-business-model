# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq # ToggleSwitch
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
import numpy as np
import dash_table
import io
import base64
import random
import json
from datetime import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#fff',
    'text': '#111'
}
def generate_graph(dataframe):
    colorss=[]
    random.seed(datetime.now().time())
    for i in range(len(dataframe)):
        colorss.append('rgb('
                       f'{(dataframe["x"][i] * dataframe["y"][i])%random.randint(0,255)},'
                       f'{(dataframe["x"][i] * dataframe["y"][i])%random.randint(0,255)},'
                       f'{(dataframe["x"][i] * dataframe["y"][i])%random.randint(0,255)})')
    return dcc.Graph(
            figure=dict(
                data=[
                dict(
                    #TODO: Check for the existence of 'x' 'y' 'z' size.
                    #If they are not, then the first column will be x, the second y, etc.
                    x=dataframe['x'],
                    y=dataframe['y'],
                    name='Rest of world',
                    mode= 'markers',
                    marker=dict(
                        #color={'rgb(55, 83, 109)' if dataframe['x'][i]> 50 else 'rgb(15, 13, 19)' for i in range(len(dataframe['x']))},
                        color =colorss,
                        line= {'width': 0.5, 'color': 'white'},
                        size=abs(dataframe[list(dataframe)[-1]])/2,
                    ),
                ),
            ],
                layout={
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    },
                },
            ),
        )

def generate_table(dataframe):
    return dash_table.DataTable(
            data=dataframe.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in dataframe.columns],
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
            )

def parse_dataa(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df

#app.scripts.config.serve_locally = True
#app.config.suppress_callback_exceptions = True
#app.server.config.suppress_callback_exceptions = True
#app.config['suppress_callback_exceptions'] = True

data = pd.read_csv("1.csv")



app.layout = html.Div(children=(
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
    daq.ToggleSwitch(
        id='ToggleSwitch',
        label=['min', 'max'],
        style={'width': '250px', 'margin': 'auto'},
        value=False
    ),
    html.Div(id='asdddd', children="min"),
    html.Div(id='output-data-TS'),
    dcc.Dropdown(
        id='model-selector',
        value=""
    ),
    html.Div(id='output-data-pareto'),
    html.Div(id='output-data-table'),
    html.Div(id='output-data-upload'),
    html.Div(id='output-data-graph'),
    html.Div(id='aaasss'),
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    generate_graph(data),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    })
))

pre_style = {
    'whiteSpace': 'pre-wrap',
    'wordBreak': 'break-all',
    'whiteSpace': 'normal'
}
#TODO: Gently remove
def parse_contents(contents, filename):
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
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    #OutPareto = printPareto(Pareto)
    return html.Div([
        #generate_graph(df),
    ])

#
@app.callback(Output('model-selector', 'options'),
              [Input({'type': 'Pareto', 'index': ALL}, 'children')])
def chengeoption(a):
    return [{'label': str(a[i][0]), 'value': str(a[i][0])} for i in range(len(a))]

#TODO: Gently remove
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            parse_dataa(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        #return children

def optimalPareto(df, MN = 0):
    Pareto = []
    if MN == 0:
        MN=[False] * len(df)
    while len(df)>0:
        #dd = df.to_numpy()
        #dd[np.lexsort(np.fliplr(dd).T)]
        pareto = df[:]
        #c = [False,True]#[False]*len(df)
        #maybe rewite with [x >= y for i,x in enumerate(a) for j,y in enumerate(a) if i != j]
        for a in df:
            for b in df:
                ziplist = list(zip(a, b, MN))
                if (all(np.equal(x, y) for x, y, c in ziplist)):
                    continue
                if (all((np.greater_equal(x, y) and c) or
                        (np.less_equal(x ,y) and not c)
                        for x, y, c in ziplist)):
                    #print(a,b,c)
                    pareto = np.delete(pareto,np.where(np.all(pareto==b,axis=1)),axis=0)
        #print(f"Pareto: {pareto}")
        # Very slow
        # Difference between  df and pareto (df-pareto)
        df = np.array(list((set(map(tuple, df)).difference(set(map(tuple, pareto))))))
        Pareto.append(pareto)
    return Pareto
    #return printPareto(pareto,index)

#Out paretoList with data from uploaded files
@app.callback(Output('output-data-pareto', 'children'),
            [Input('upload-data', 'contents'),
             Input('upload-data', 'filename'),
            Input({'type': 'TS', 'index': ALL}, 'value')])
def printPareto(contents, filename, MN):
    paretoListDiv = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        pareto = parse_dataa(contents, filename)
        #Pareto.reverse()
        Pareto = optimalPareto(pareto.to_numpy(), MN)
        for index in range(len(Pareto)):
            paretoListDiv.append(
                html.Details(
                    [
                    html.Summary(
                        f'Pareto{index+1}'
                    ),
                    html.Div(
                        [f"{Pareto[index]}"],
                        id={'type': 'Pareto','index': index},
                        )
                    ],
                    open=False,
                    title="Pareto" + str(index + 1),
                ))
            print(f"{Pareto[index]}")
            print()
    #createCallback(len(paretoListDiv))
    return html.Div(paretoListDiv)

#Out table with data from uploaded files
@app.callback(Output('output-data-table', 'children'),
            [Input('upload-data', 'contents'),
             Input('upload-data', 'filename')])
def update_table(contents, filename):
    table = []
    if contents:
        children = [
            parse_dataa(c, n) for c, n in
            zip(contents, filename)]
        for i in range(len(children)):
            table.append(generate_table(children[i]))
    return table

#Out graph with data from uploaded files
@app.callback(Output('output-data-graph', 'children'),
            [Input('upload-data', 'contents'),
             Input('upload-data', 'filename')])
def update_graph(contents, filename):
    graph = []
    if contents:
        children = [
            parse_dataa(c, n) for c, n in
            zip(contents, filename)]
        for i in range(len(children)):
            graph.append(generate_graph(children[i]))
    return graph

@app.callback(Output('output-data-TS', 'children'),
            [Input('output-data-table', 'children')])
def TS(a):
    TSDiv = []
    if a:
        sizecolumns = len(a[0]['props']['columns'])

        print("Len: ", a[0]['props']['columns'])
        print("Len: ", sizecolumns)
        print("Len2: ", a[0]['props']['columns'][0])
        for i in range(sizecolumns):
            TSDiv.append(
                daq.ToggleSwitch(
                    id={'type': 'TS', 'index': i},
                    label=['min', 'max'],
                    style={
                        'display': 'flex',
                        'width': '10%',
                        'margin': '5px',
                        'margin-left': '30px',
                        'left' : '5%',
                        },
                    value=False
                )
            )
    return TSDiv

@app.callback(Output('aaasss', 'children'),
            [Input({'type': 'TS', 'index': ALL}, 'value')])
def valueTS(value):
    print()
    for i in range(len(value)):
        print(value[i])
    print()
    return html.Div()

@app.callback(Output('asdddd', 'children'),
            [Input('ToggleSwitch', 'value')])
def ass(v):
    if not v:
        return html.Div("min")

    return html.Div("max")

if __name__ == '__main__':
    app.run_server(debug=True)