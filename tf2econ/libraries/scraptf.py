from bs4 import BeautifulSoup
import time,json
from requests_html import HTMLSession

def NormalizeCurrency(curr:str):
    if curr.find("key") != -1:
        spl = curr.split("key")
        if spl[1]:
            ref = spl[1]
            ref = ref.strip("s,").replace("refined","")
            if ref:
                ref = float(ref)
            else:
                ref = 0
        else:
            ref = 0
        key = int(spl[0])
        
    else:
        key = 0
        ref = float(curr.strip().replace("refined",""))
    return round(key * 50 + ref,2)

def update_pricelist():
    ses = HTMLSession()
    spreadsheet = ses.get("https://scrap.tf/items")
    soup = BeautifulSoup(spreadsheet.content, 'html.parser')

    items = []

    pricelist = soup.find("table", id="itembanking-list").find("tbody")

    rows = pricelist.find_all("tr")

    for r in rows:
        cols = r.find_all("td")
        if(cols[4].find("div").text[0] == '0'):
            continue
        name = cols[1].text.strip()
        psell = NormalizeCurrency(cols[2].text.strip())
        pbuy = NormalizeCurrency(cols[3].text.strip())

        

        items.append({
            "name":name,
            "sell":psell,
            "buy":pbuy
        })
    return items
