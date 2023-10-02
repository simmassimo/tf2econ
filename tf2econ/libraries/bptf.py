from bs4 import BeautifulSoup
import time,json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlencode
import time
from requests_html import HTMLSession

API_KEY = '6507fb3065ea1a68900e9c74'

QUALITIES = {   
    1 : "Genuine",
    3 : "Vintage",
    6 : "Unique",
    11: "Strange",
    13: "Haunted"
}

CurrentKeyPrice = 0

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
            "name":name.strip(),
            "type":itemType.strip(),
            "uncraft":uncraft,
            "qualities":quals
        })
    print(items)
    with open("bptf_items.json","w") as f:
        json.dump(items, f)


def InitializeSession():
# Initialize WebDriver
    options = webdriver.EdgeOptions()
    session = webdriver.Edge(options=options)

    # Navigate to Steam login page
    session.get('https://steamcommunity.com/login/home')


    login_form = WebDriverWait(session, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "newlogindialog_LoginForm_3Tsg9"))
    )

    # Locate username and password fields
    username_field = login_form.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > input') 
    password_field = login_form.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > input') # Replace with the actual ID or name
    
    # Input username and password
    username_field.send_keys('goleador815')
    password_field.send_keys('manIcodiscOpa12')
    password_field.send_keys(Keys.ENTER)
    WebDriverWait(session, 10).until(EC.url_contains("profiles"))
    print("INITIALIZED SESSION")
    return session

def LinkBackpackTF(session):
    session.get('https://backpack.tf/login')   
    login = WebDriverWait(session,10).until(EC.presence_of_element_located((By.ID, "imageLogin")))
    login.click()
    WebDriverWait(session,10).until(EC.url_contains("backpack"))
    print("CONNECTED TO BP.TF")
    return session

def NormalizeCurrency(curr:str):
    global CurrentKeyPrice
    if not curr or  curr == '':
        return -1
    if curr.find("key") != -1:
        spl = curr.split("key")
        if spl[1] and spl[1] != '':
            ref = spl[1]
            ref = ref.strip("s,").replace("ref","")
            if ref:
                ref = float(ref)
            else:
                ref = 0
        else:
            ref = 0
        key = int(spl[0])
        
    else:
        key = 0
        ref = float(curr.strip().replace("ref",""))
    return round(key * CurrentKeyPrice + ref,2)

def fetch(session: WebDriver,name: str,quality: int,uncraft: bool = False, ks_tier: int = 0, page_num: int = 1):
    
    params = {
        "item":name,
        "quality":quality,
        "page":page_num,
        "craftable": -1 if uncraft else 0
    }
    params = urlencode(params)

    response = {
        "buy":[],
        "sell":[]
    }
    session.get(f"https://backpack.tf/classifieds?{params}")
    listings = WebDriverWait(session,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "media-list")))  
    sell_listings = listings[0]
    sells = sell_listings.find_elements(By.CLASS_NAME, "listing")
    if len(sells) > 0:
        for s in sells:
            it = s.find_element(By.CLASS_NAME, "listing-item").find_element(By.TAG_NAME, "div")
            pr = NormalizeCurrency(it.get_attribute("data-listing_price"))
            if pr == -1:
                continue
            sell = {
                "steamid":it.get_attribute("data-listing_account_id"),
                "details":it.get_attribute("data-listing_comment"),
                "tradeUrl":it.get_attribute("data-listing_offers_url"),
                "price": pr
            }
            sell["attribute"] = "paint" if it.get_attribute("data-paint_name") else "spell" if it.get_attribute("data-spell_1") else "pure"
            bd = s.find_element(By.CSS_SELECTOR, "div.listing-body")
            bump = bd.find_element(By.CSS_SELECTOR, "span > span.data1 > time")
            sell["bumped"] = datetime.fromisoformat(bump.get_attribute("datetime"))
            listed = bd.find_element(By.CSS_SELECTOR, "span > span.data2 > time")
            sell["listed"] = datetime.fromisoformat(listed.get_attribute("datetime"))

            response["sell"].append(sell)
 


    buy_listings = listings[1]
    buys = buy_listings.find_elements(By.CLASS_NAME, "listing")
    if len(buys) > 0:
        for b in buys:
            it = b.find_element(By.CLASS_NAME, "listing-item").find_element(By.TAG_NAME, "div")
            pr = NormalizeCurrency(it.get_attribute("data-listing_price"))
            if pr == -1:
                continue
            buy = {
                "steamid":it.get_attribute("data-listing_account_id"),
                "details":it.get_attribute("data-listing_comment"),
                "tradeUrl":it.get_attribute("data-listing_offers_url"),
                "price": pr
            }
            if it.get_attribute("data-paint_name"):
                buy["attribute"] = "paint"  
            elif it.get_attribute("data-spell_1"):
                buy["attribute"] = "spell" 
            elif it.get_attribute("data-part_name_1"): 
                buy["attribute"] = "parts"
            else:
                buy["attribute"] = "pure"
            bd = b.find_element(By.CSS_SELECTOR, "div.listing-body")
            bump = bd.find_element(By.CSS_SELECTOR, "span > span.data1 > time")
            buy["bumped"] = datetime_object = datetime.fromisoformat(bump.get_attribute("datetime"))
            listed = bd.find_element(By.CSS_SELECTOR, "span > span.data2 > time")
            buy["listed"] = datetime.fromisoformat(listed.get_attribute("datetime"))

            response["buy"].append(buy)

    return response

def GetKeyPrices(ses):
    global CurrentKeyPrice
    data = fetch(ses,"Mann Co. Supply Crate Key",6)
    if data:
        CurrentKeyPrice = float(data["sell"][0]["price"])

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
        
def GetListings(session:WebDriver,name:str,quality:str,uncraft:bool = False, ks_tier:int = 0, quick:bool = False):

    results = {"buy":[],"sell":[]}   
    if quick:
        return fetch(session,name,quality,uncraft,ks_tier)
    else:
        i = 1
        while True:
            if i == 1:
                raw = fetch(session,name,quality,uncraft,ks_tier, page_num=i)
                i=2
                continue
            page = fetch(session,name,quality,uncraft,ks_tier, page_num=i)          
            if not page["buy"]and not page["sell"]:
                break
            else:
                raw["buy"].extend(page["buy"])
                raw["sell"].extend(page["sell"])
            i += 1
    return raw

def FindOpportunities(ses:WebDriver):
    print("STARTING")
    with open(r"C:\Users\Simon\Desktop\TF2Econ\tf2econ\bptf_items.json","r") as f:
        items = json.load(f)
        GetKeyPrices(ses)
        print("ITEMS LOADED")
        for i in items:
            if i["type"] == "Type" or i["type"] =="Cosmetic":
                for q in i["qualities"]:
                    listings = GetListings(ses,i["name"],q, False, quick=True)
                    if listings["buy"] and listings["sell"]:
                        bprice = None
                        for b in listings["buy"]:
                            if b["attribute"] == "pure":
                                bprice = b["price"]
                                break
                        if not bprice:
                            continue
                        sprice = None
                        for s in listings["sell"]:
                            if s["attribute"] == "pure":
                                sprice = s["price"]
                                break
                        if not sprice:
                            continue
                        if bprice > sprice:
                            print(f"Opportunity for {QUALITIES[q]} {i['name']} S {sprice}ref - B {bprice}ref [{round(bprice-sprice,2)} PROFIT ({round(((sprice - bprice)/bprice),2)*100}%)]")
    return ses
