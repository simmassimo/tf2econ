from libraries.bptf import *
from libraries import scraptf,bptf
import json


def FindOpportunities(threshold = 0.11):
    items = scraptf.update_pricelist()
    for i in items:
        listings = bptf.GetListings(i["name"],6, quick=True)
        if(len(listings["buy"]) > 0):
            bprice = listings["buy"][0]["price"]
            if bprice - i["sell"] >= threshold:
                print(f"Found for {i['name']} (BP:{bprice})-(Scrap:{i['sell']})")

FindOpportunities(0.33)