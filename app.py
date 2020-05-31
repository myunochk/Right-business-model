# -*- coding: utf-8 -*-
#TODO: add more logs, add more exceptions
#TODO: If first col have naming then Rebuild Full Logic
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq # ToggleSwitch
from dash.dependencies import Input, Output, ALL
import pandas as pd
import numpy as np
import dash_table
import io
import os
import base64
import random
import flask
from datetime import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server,external_stylesheets=external_stylesheets)

colors = {
    'background': '#fff',
    'text': '#111'
}

tabs_styles = {
    'height': '84px'
}
tab_style = {
    'borderBottom': '2px solid #236604',
    'borderTop': '2px solid #236604',
    'padding': '6px',
}

tab_selected_style = {
    'borderBottom': '2px solid #e17dfa',
    #'background': 'linear-gradient(135deg, orange, orange 60%, cyan)',
    #'background': 'linear-gradient(to right,red,orange,yellow,green,blue,pink)',
#'background': 'radial-gradient(center, ellipse cover, rgba(255,175,75,1) 0%, rgba(0,0,0,1) 100%)',
    'color': 'black',
    'fontWeight': 'bold',
    'padding': '6px'
}

def generate_graph(dataframe, TS = 0, RS = [[0,0],[0,0]], names = []):
    random.seed(datetime.now())
    Pareto = optimalPareto(pd.DataFrame(dataframe).to_numpy(), TS = TS, RS = RS)
    dates = []
    for i in range(len(Pareto)):
        P = Pareto[i]
        X, Y, Size = [], [], []
        for j in range(len(P)):
            X.append(P[j][0])
            Y.append(P[j][1])
            Size.append(abs(P[j][2])+10 if len(P[j])>2 else 20)
        dates.append(
            dict(
                # TODO: Check for the existence of 'x' 'y' 'z' size.
                #If they are not, then the first column will be x, the second y, etc.
                x=X,
                y=Y,
                name=f'Pareto {i+1}',
                mode='markers',
                hover_data=names,
                marker=dict(
                    line={'width': 0.5, 'color': 'white'},
                    size=Size,
                ),
            )
        )
    return dcc.Graph(
        figure=dict(
            data = dates,
            layout={
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                },
            },
        )
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
            #'width': '50%',
            'overflowY': 'scroll',
            'border': 'thin lightgrey solid'
        },
    )

def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        names = []
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+' added an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
        if not pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull().all():
            names = df.iloc[:, 0]
            df = df.iloc[:, 1:]
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df, names

def parse_df_name(df):
    names = []
    if df['columns'][0]['name'] == 'name':
        for x in df['data']:
            names.append(x.get('name'))
            x.pop('name', None)
        del df['columns'][0]
    return df, names
#app.scripts.config.serve_locally = True
#app.config.suppress_callback_exceptions = True
#app.server.config.suppress_callback_exceptions = True
#app.config['suppress_callback_exceptions'] = True

#data = pd.read_csv("1.csv")



app.layout = html.Div(children=(
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            #'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    dcc.Dropdown(
        id='model-selector',
        value=""
    ),
    dcc.Tabs([
        dcc.Tab(label='Pareto',
                children=[
                    html.Div(id='output-data-TS'),
                    html.Div(id='output-data-pareto'),
                ],
                style=tab_style, selected_style=tab_selected_style,
                ),
        dcc.Tab(label='Table',
                children=html.Div(id='output-data-table'),
                style=tab_style, selected_style=tab_selected_style,
                ),
    ]
    ),
    html.Div(id='output-data-graph'),
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children='Dash: A web application framework for Python.',
             style={
                 'textAlign': 'center',
                 'color': colors['text']
             }
             )
)
)
pre_style = {
    'whiteSpace': 'pre-wrap',
    'wordBreak': 'break-all',
    'whiteSpace': 'normal'
}
@app.callback(Output('model-selector', 'options'),
              [Input({'type': 'Pareto', 'index': ALL}, 'children')])
def chengeoption(a):
    return [{'label': str(a[i][0]), 'value': str(a[i][0])} for i in range(len(a))]

def optimalPareto(df, TS = 0, RS = [[0,0],[0,0]]):
    Pareto = []
    while len(df)>0:
        pareto = df[:]
        #maybe rewite with [x >= y for i,x in enumerate(a) for j,y in enumerate(a) if i != j]
        for a in df:
            try:
                for indexcolumn in range(len(a)):
                    if len(RS)==len(a) and  not (a[indexcolumn] >= RS[indexcolumn][0]
                                                 and a[indexcolumn] <= RS[indexcolumn][1]):
                        df = np.delete(df, np.where(np.all(df == a, axis=1)), axis=0)
                        if len(pareto) > 0 and a in pareto:
                            pareto = np.delete(pareto, np.where(np.all(pareto == a, axis=1)), axis=0)
                        continue
            except Exception as e:
                print(e)
            for b in df:
                try:
                    ziplist = list(zip(a, b, TS, RS))
                    if (all(np.equal(x, y) for x, y, TS, RS in ziplist)):
                        continue
                    if (all(((np.greater_equal(x, y) and TS) or
                            (np.less_equal(x ,y) and not TS))
                            for x, y, TS, RS in ziplist)):
                        pareto = np.delete(pareto,np.where(np.all(pareto==b,axis=1)),axis=0)
                except Exception as e:
                    print(e)
        # Very slow
        # Difference between  df and pareto (df-pareto)
        df = np.array(list((set(map(tuple, df)).difference(set(map(tuple, pareto))))))
        if len(pareto):
            Pareto.append(pareto)
    return Pareto
    #return printPareto(pareto,index)

#Out paretoList with data from uploaded file(s)
@app.callback(Output('output-data-pareto', 'children'),
              [Input('output-data-table', 'children'),
               Input({'type': 'TS', 'index': ALL}, 'value'),
               Input({'type': 'RS', 'index': ALL}, 'value')])
def printPareto(dataframe, TS, RS):
    paretoListDiv = []
    if len(dataframe):
        dataframe = dataframe[0]['props']
        #Pareto.reverse()
        dataframe, names = parse_df_name(dataframe)
        listvalues = [list(d.values()) for d in dataframe['data'][0:]]
        Pareto = optimalPareto(pd.DataFrame(dataframe['data']).to_numpy(), TS = TS, RS = RS)
        lenPareto = len(Pareto)
        for index in range(lenPareto):
            #print(listvalues)
            nameParetoDiv = Pareto[index]
            if len(names):
                nameParetoDiv = []
                for inParetoindex in range(len(Pareto[index])):
                    nameParetoDiv.append(names[listvalues.index(list(Pareto[index][inParetoindex]))])
            #print(set(dataframe['data'][:]))
            #print(set(Pareto[index][0]))
            paretoListDiv.append(
                html.Details(
                    [
                    html.Summary(
                        f'Pareto{index+1}'
                    ),
                    html.Div(
                        [f"{nameParetoDiv}"],
                        id={'type': 'Pareto','index': index},
                        )
                    ],
                    open=False,
                    title="Pareto" + str(index + 1),
                )
            )
            #print(f"{Pareto[index]}")
            #print()
    #createCallback(len(paretoListDiv))
    return html.Div(paretoListDiv)

#Out table with data from uploaded file(s)
@app.callback(Output('output-data-table', 'children'),
            [Input('upload-data', 'contents'),
             Input('upload-data', 'filename')])
def update_table(contents, filename):
    table = []
    if contents:
        tablecontent, names = parse_data(contents, filename)
        if len(names):
            tablecontent.insert(loc=0, column='name', value=names)
        table.append(generate_table(tablecontent))
    return table

#Out graph with data from uploaded file(s)
@app.callback(Output('output-data-graph', 'children'),
            [Input('output-data-table', 'children'),
             Input({'type': 'TS', 'index': ALL}, 'value'),
             Input({'type': 'RS', 'index': ALL}, 'value')])
def update_graph(dataframe, TS, RS):
    graph = []
    if len(dataframe):
        dataframe = dataframe[0]['props']
        dataframe, names = parse_df_name(dataframe)
        dataframe = dataframe['data']
        graph.append(generate_graph(dataframe, TS = TS, RS = RS, names = names))
    return graph

@app.callback(Output('output-data-TS', 'children'),
            [Input('output-data-table', 'children')])
def TS(dataframe):
    TSDiv = []
    if dataframe:
        dataframe = dataframe[0]['props']
        dataframe, names = parse_df_name(dataframe)
        sizecolumns = len(dataframe['columns'])
        for i in range(sizecolumns):
            columnname = str(dataframe['columns'][i]['name'])
            minvalue = dataframe['data'][0][columnname]
            maxvalue = minvalue
            step = 1#abs(dataframe[0]['props']['data'][1][columnname] - minvalue)
            for j in range(len(dataframe['data'])):
                value = dataframe['data'][j][columnname]
                minvalue = min(minvalue,value)
                maxvalue = max(maxvalue,value)
                #if j:
                #    step = min(step,abs(value-dataframe[0]['props']['data'][j-1][columnname]))
            marks = []
            if max(step,int(abs(maxvalue-minvalue)/20)):
                for mark in range(minvalue,maxvalue,max(step,int(abs(maxvalue-minvalue)/20))):
                    marks.append(mark)
            marks.append(maxvalue)
            TSDiv.append(
                html.Div([
                    html.Div(children=columnname,
                             style={
                                 'position': 'relative',
                                 'margin-left': '60px',
                                 'margin-top': '10px'
                             }
                             ),
                    daq.ToggleSwitch(
                        id={'type': 'TS', 'index': i},
                        label=['min', 'max'],
                        style={
                            'position': 'relative',
                            'display': 'flex',
                        },
                        value=False
                    ),
                    dcc.RangeSlider(
                        id={'type': 'RS', 'index': i},
                        min=minvalue,
                        max=maxvalue,
                        step=step,
                        value=[minvalue, maxvalue],
                        marks={str(marks[h]) : {'label' : str(marks[h])} for h in range(len(marks))},
                    ),
                ]
                )
            )
    return TSDiv

if __name__ == '__main__':
    app.run_server(debug=True)