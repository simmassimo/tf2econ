from dash.dependencies import Input,Output,State
import time
import dash_bootstrap_components as dbc
from libraries import bptf
from dash import html
from datetime import datetime
from app import app

@app.callback(
    Output("output", "children"),
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

        ls = [f"{'🤖Bot' if l['isBot'] else '👨‍💼User'} {l['lastbump'] if not l['isBot'] else ''}  - {l['price']}" for l in paintListings[pName]]
        row_data.append(
            dbc.Col([         
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{pName}{pObj['emoji']}"),
                        dbc.ListGroup([dbc.ListGroupItem(l, href=f"https://next.backpack.tf/classifieds/{id}") for l in ls])
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