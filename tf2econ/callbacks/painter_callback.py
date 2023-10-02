from dash.dependencies import Input,Output,State
import time
import dash_bootstrap_components as dbc
from libraries import bptf
from dash import html
from datetime import datetime
from app import app

@app.callback(
    Output("analysis-output", "children"),
    [Input("submit-button", "n_clicks")],
    [State("item-name", "value")]
)
def update_output(n_clicks, value):
    if n_clicks is None:
        return ""

    test = bptf.GetListings(value,6)

    paintListings = {}
    res = []
    row_data = []
    res.append(html.H2("Selling Orders:"))
    for pObj in bptf.PAINTS.table.values():
        print("ADDING")
        pName = pObj["name"]
        print(pName)
        paintListings[pName] = bptf.ListingFilter(test["sell"]).ByPaint(pName).Finish()

        
        
        listEls = []
        for l in paintListings[pName]:
            label = f"{'🤖Bot' if l['isBot'] else '👨‍💼User'} {l['lastbump'] if not l['isBot'] else ''}  - {l['price']}"
            sid = l["steamid"]
            listEls.append(dbc.ListGroupItem(label, href=f"https://backpack.tf/u/{sid}"))
        row_data.append(
            dbc.Col([         
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{pName}{pObj['emoji']}"),
                        dbc.ListGroup(listEls)
                    ])
                ])
            ], width=4)
        )
        print("added col")
        if len(row_data) > 2:
            print("adding row")
            res.append(dbc.Row(row_data))
            row_data = []
    if row_data:
        print("adding remaining cols in a row")
        res.append(dbc.Row(row_data))

    #BUYING ORDERS
    res.append(html.H2("Buying Orders:"))
    paintBuyListings = bptf.ListingFilter(test["buy"]).OnlyPaints().Finish()
    res.append(dbc.Col([
        dbc.ListGroup([dbc.ListGroupItem(l["details"]) for l in paintBuyListings])
    ]))
    return res



@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab')]
)
def update_tab(at):
    if at == 'tab-analysis':
        return tab1_content
    elif at == 'tab-negotiate':
        return tab2_content
    return "This shouldn't ever be displayed..."


tab1_content = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Input(id="item-name", type="text", placeholder="Enter item name"),
            dbc.Button("Submit", id="submit-button", color="primary", className="mr-2"),
        ])
    ]),
    dbc.Row([
        dbc.Spinner(
            color="primary",
            children=html.Div(id="analysis-output")
        )
    ])
])

tab2_content = dbc.Container([
    dbc.Row([
        dbc.Button("Research Potential Negotiations", id="submit-button", color="primary", className="mr-2"),
    ]),
    dbc.Row([
        dbc.Spinner(
            color="primary",
            children=html.Div(id="negotiate-output")
        )
    ])
])