import requests
import json
import jsonpickle
from pymaybe import maybe
from os.path import exists
from colorama import Fore, Back, Style

class Bolt:
    def __init__(self,b):
        self.year = b["year"]
        self.price = maybe(b["pricing"]["cash"])["summary"]["gross"][0]["value"].or_else(-1)
        self.msrp = maybe(b["pricing"]["cash"])["summary"]["items"][0]["value"].or_else(-1)
        self.dealer = b["dealer"]["name"]
        self.avail = maybe(b.get("vehicleAvailabilityStatus",None))["displayStatus"].or_else("battery?")
    def __str__(self):
        return f'Bolt(year={self.year},price={self.price},dealer={self.dealer},avail={self.avail}'
    def __eq__(self, other) -> bool:
        if isinstance(other,Bolt):
            return self.year == other.year and self.price==other.price and self.msrp==other.msrp and self.dealer==other.dealer and self.avail==other.avail
        return super().__eq__(other)


def getCurrentBolts():    
    url = "https://www.chevrolet.com/electric/shopping/api/drp-cp-api/p/v1/vehicles"
    headers = {
            "content-type":"application/json", 
            "accept": "application/json"
    }    
    data = json.dumps({
    "name": "DrpInventory",
    "filters": [
        {
        "field": "paymentType",
        "operator": "IN",
        "values": [
            "CASH"
        ],
        "key": "paymentType"
        },
        {
        "field": "model",
        "operator": "IN",
        "values": [
            "Bolt EUV"
        ],
        "key": "model"
        },
        {
        "field": "year",
        "operator": "IN",
        "values": [
            "2023",
            "2022"
        ],
        "key": "year"
        },
        {
        "field": "packages",
        "operator": "IN",
        "values": [
            "WPT"
        ],
        "key": "packages"
        },
        {
        "field": "cash",
        "operator": "IN",
        "values": [
            "60000"
        ],
        "key": "cash"
        },
        {
        "field": "radius",
        "operator": "IN",
        "values": [
            250
        ],
        "key": "radius"
        },
        {
        "field": "zipcode",
        "operator": "IN",
        "values": [
            "83815"
        ],
        "key": "zipcode"
        }
    ],
    "sort": [
        {
        "field": "availability",
        "order": "DESC"
        }
    ],
    "pageInfo": {
        "rows": 20
    },
    "searchText": ""
    })

    response = requests.post(url, headers=headers,data=data)
    boltsJson = response.json()
    return [Bolt(b) for b in boltsJson["data"]["listResponse"]]

def getSavedBolts():
    if exists("saved.json"):
        with open("saved.json","r") as read:
            allLines = read.read()
            return jsonpickle.decode(allLines)
    else:
        return {}

def saveBolts(bolts):
    encoded = jsonpickle.encode(bolts)
    with open("saved.json", "w") as write:
        write.writelines(encoded)

def printDifferences(bolts,state):
    if bolts != None and len(bolts):
        print(Fore.RED+f"Bolt change detected: {state}"+Style.RESET_ALL)
        for item in bolts:
            print(item)

savedBolts = getSavedBolts()
currentBolts = getCurrentBolts()

newBolts = [n for n in currentBolts if n not in savedBolts]
printDifferences(newBolts,"New")
removedBolts = [n for n in savedBolts if n not in currentBolts]
printDifferences(removedBolts,"Removed")

if not len(newBolts) and not len(removedBolts):
    print(Fore.GREEN+"No updates")
    
saveBolts(currentBolts)