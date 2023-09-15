from dash import html,dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Input(id="item-name", type="text", placeholder="Enter item name"),
            dbc.Button("Submit", id="submit-button", color="primary", className="mr-2"),
        ])
    ]),
    dbc.Row([
        dbc.Spinner(
            color="primary",
            children=html.Div(id="output")
        )
    ])
])