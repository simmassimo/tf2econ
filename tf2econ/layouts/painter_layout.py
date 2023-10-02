from dash import html,dcc
import dash_bootstrap_components as dbc

layout = dbc.Row([
    dbc.Col(
        dbc.Tabs(
        [
            dbc.Tab(label="Paint Analysis", tab_id="tab-analysis"),
            dbc.Tab(label="Negotiation Analysis", tab_id="tab-negotiate"),
        ],
        style={"flex-direction":"column"},
        id="tabs"
        ),
        width=2),
    dbc.Col(
        html.Div(id="tab-content"),
        width=10)
])


