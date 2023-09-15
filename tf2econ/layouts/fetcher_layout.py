from dash import html,dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
            dbc.Row(dbc.Col(html.H1("This is the Fetcher."))),
            dbc.Row(
                [
                    dbc.Col(html.Div("One of three columns")),
                    dbc.Col(html.Div("One of three columns")),
                    dbc.Col(dbc.Button("Update Item List",color="primary", id="update_bptf_items")),
                ]
            ),
            
            dbc.Toast(
                [html.P("bptf_items.json has been updated", className="mb-0")],
                id="updated_itemlist_toast",
                header="Itemlist Updated!",
                is_open=False,
                dismissable=True,
                icon="success",
                duration=3000,
                # top: 66 positions the toast below the navbar
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            ),
        ])