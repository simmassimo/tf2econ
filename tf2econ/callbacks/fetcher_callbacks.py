from dash.dependencies import Input,Output
from app import app
from libraries import bptf
import dash
import dash_bootstrap_components as dbc

@app.callback(
     [Output('updated_itemlist_toast', 'is_open')],
    [Input('update_bptf_items', 'n_clicks')],
)
def update_bptf_itemlist(n_clicks):
    if n_clicks is not None and  n_clicks > 0:
        print("I HAVE BEEN CLICKED")
        bptf.update_itemlist()
        print("DONE")
        return True
    
    return False