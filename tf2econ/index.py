from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
import libraries
from layouts import home_layout, fetcher_layout, painter_layout
from callbacks import fetcher_callbacks, painter_callback

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Refresh", href="/fetcher")),
        ],
        brand="My Finance App",
    ),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/fetcher':
        return fetcher_layout.layout
    elif pathname == "/painter":
        return painter_layout.layout
    else:
        return home_layout.layout

if __name__ == '__main__':
    app.run_server(debug=True)