from bs4 import BeautifulSoup
import time,json
from requests_html import HTMLSession
import requests
from datetime import datetime

API_KEY = '628b33f45f92643cc307cb0e'

QUALITIES = {   
    1 : "Genuine",
    3 : "Vintage",
    6 : "Unique",
    11: "Strange",
    13: "Haunted"
}

def calc_timedelta(created, bump):
    # Calculate the time difference in seconds
    time_diff = abs(created - bump)

    # Convert the time difference to various units
    minutes, seconds = divmod(time_diff, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if hours <= 6:
        return f"{hours}h|{minutes}m"
    else:
        return "6+h"

class PAINTS:
    item_attribute = 142

    table = {
        '15132390': {
            'name': 'An Extraordinary Abundance of Tinge',
            'nicknames': ['Tinge', 'White'],
            'emoji': '🤍'
        },
        '16738740': {
            'name': 'Pink as Hell',
            'nicknames': ['Pink'],
            'emoji': '🎀'
        },
        '1315860': {
            'name': "A Distinctive Lack of Hue",
            'nicknames': ["Black", "Hue"],
            'emoji':'🖤'
        },
        '2960676': {
            'name': "After Eight",
            'nicknames': ["After8", "Eight", "8"],
            'emoji':'🏴'
        },
        '15185211': {
            'name': "Australium Gold",
            'nicknames': ["Gold", "Yellow"],
            'emoji':'💛'
        },
        '8208497': {
            'name': "A Deep Commitment to Purple",
            'nicknames': ["Purple"],
            'emoji': '💜'
        },
        '12073019': {
            'name': "Team Spirit",
            'nicknames': ["TS"],
            'emoji': '❤💙'
        },
        '3329330': {
            'name': "The Bitter Taste of Defeat and Lime",
            'nicknames': ["Lime"],
            'emoji':'💚'
        }
    }

    @staticmethod
    def byId(val):
        return PAINTS.table.get(val, -1)
    @staticmethod
    def byName(name):
        for k,v in PAINTS.table.items():
            if v["name"] == name or name in v["nicknames"] or name == v['emoji']:
                return k
        return None

SPELLS_ATTR = [1004,1005,1006,1007,1008,1009]

def update_itemlist():
    ses = HTMLSession()
    spreadsheet = ses.get("https://backpack.tf/spreadsheet")
    soup = BeautifulSoup(spreadsheet.content, 'html.parser')

    items = []

    pricelist = soup.find("table", id="pricelist")
    pricelist = pricelist.find("tbody")
    rows = pricelist.find_all("tr")
    for row in rows:
        uncraft = not bool(row["data-craftable"])
        cols = row.find_all("td")
        name = cols[0].get_text()
        itemType = cols[1].get_text()
        quals = []
        for i in range(2,7):
            q = cols[i]
            if q.get("abbr",0) != 0:
                if i == 3:
                    quals.append(1)
                elif i == 4:
                    quals.append(3)
                elif i == 5:
                    quals.append(6)
                elif i == 6:
                    quals.append(11)
                elif i == 7:
                    quals.append(13)
        items.append({
            "name":name,
            "type":itemType,
            "uncraft":uncraft,
            "qualities":quals
        })
    print(items)
    with open("bptf_items.json","w") as f:
        json.dump(items, f)

def fetch(name,quality,uncraft = False, ks_tier = 0, page_num = 0):
    params = {
        "key": API_KEY,
        "page_size":30,
        "page":page_num,
        "item":name,
        "craftable":0 if uncraft else 1,
        "quality":quality,
        "killstreak_tier":ks_tier
    }

    print("fetching....")
    get  = requests.get("https://backpack.tf/api/classifieds/search/v1", params=params)

    if get.status_code == 200:
        return get.json()
    elif get.status_code == 429:
        #too many requests
        print("HTTP Code 429: Too many requests.")
        time.sleep(10)
        return fetch(name,quality,uncraft,ks_tier)
    else:
        #unknown error
        raise Exception(f"Bad Request! HTTP Code: {get.status_code}")
    

def GetKeyPrices():
    data = fetch("Mann Co. Supply Crate Key",6)
    if data:
        return float(data["sell"]["listings"][0]["currencies"]["metal"])
    else:
        return float(50)
    
def NormalizeCurrency(curr):
    if not curr.get("keys") and not curr.get("metal"):
        return 0       
    return curr.get("keys",0) * 50 + curr.get("metal",0)

class ListingFilter:
    def __init__(self, listings):
        self.listings = listings

    def ByPrice(self, mode = "higher", val = 0.11):
        if mode == "higher":
            self.listings= [l for l in self.listings if l["price"] > val]
        elif mode == "lower":
            self.listings= [l for l in self.listings if l["price"] <= val]
        elif mode == "equals":
            self.listings= [l for l in self.listings if l["price"] == val]
        return self
        
    def ByPaint(self,paintName):
        def getPaintId(x):
            at = x.get("item", {}).get("attributes", {})
            for a in at:
                if a.get("defindex") == PAINTS.item_attribute:
                    return str(a["float_value"])
            return -1
        target = PAINTS.byName(paintName)
        self.listings = [l for l in self.listings if getPaintId(l) == target ]
        return self
    
    def OnlyPaints(self):
        self.listings = [l for l in self.listings if any(attr["defindex"] == '142' for attr in (l.get("item", {}).get("attributes") or []))]
        return self
    
    def HidePaints(self):
        self.listings = [l for l in self.listings if all(attr["defindex"] != '142' for attr in (l.get("item", {}).get("attributes") or []))]
        return self
    
    def HideSpells(self):
        self.listings = [l for l in self.listings if all(attr["defindex"] not in SPELLS_ATTR for attr in l.get("item",{}).get("attributes"))]
        return self

    def Finish(self):
        l = self.listings
        self.listings = {}
        return l
        

def GetListings(name, quality, uncraft = False, ks_tier = 0):
    i = 0
    results = {"buy":[],"sell":[]}
    while True:
        raw = fetch(name,quality,uncraft,ks_tier, page_num=i)
        if not raw["buy"]["listings"] and not raw["sell"]["listings"]:
            return results
        essential_keys = ["id","steamid","details","item","created"]

        raw_buys = raw["buy"]["listings"]
        for b in raw_buys:
            buy = {eskey : b[eskey] for eskey in essential_keys if eskey in b}
            buy["isBot"] = bool(b.get("automatic", False))
            buy["price"] = NormalizeCurrency(b.get("currencies"))
            buy["lastBump"] = calc_timedelta(b["created"], b["bump"])
            results["buy"].append(buy)
        
        raw_sells = raw["sell"]["listings"]
        for s in raw_sells:
            sell = {eskey : s[eskey] for eskey in essential_keys if eskey in s}
            sell["isBot"] = bool(s.get("automatic", False))
            sell["price"] = NormalizeCurrency(s.get("currencies"))
            sell["lastbump"] = calc_timedelta(s["created"], s["bump"])
            results["sell"].append(sell)
        i += 1