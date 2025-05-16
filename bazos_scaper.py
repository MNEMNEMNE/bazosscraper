import requests
import argparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description="Bazos scraper", epilog="example: bazos_scaper.py -m \"https://teams.szn.cz/hooks/xxxxxxxxx\"  \"https://pc.bazos.cz/?hledat=rtx+4060&rubriky=pc&hlokalita=&humkreis=25&cenaod=&cenado=6000&order=&crp=&kitx=ano\" 4060")
parser.add_argument("url", help="Exact link to bazos.cz including the filtering get parameters")
parser.add_argument("search_string", help="Search string in advert title")
parser.add_argument("-m", dest="mm_hook", help="Webhook to mattermost")
args = parser.parse_args()

# create the today and yesterday string in "d.m." format

today = datetime.now()
yesterday = today - timedelta(days=1)
dates = {f"{today.day}.{today.month}.", f"{yesterday.day}.{yesterday.month}."}

# Read the page
try:

    response = requests.get(args.url, headers={"User-Agent": "Mozilla/5.0"} )
except:
    print("Error reading the page from: ", args.url)
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# find the main adverts section
adverts = soup.find_all("div", class_="inzeraty inzeratyflex")

# header of text message to mattermost
text = "Nadpis | Datum | Lokalita | Cena\n---|---|---|---\n"

count = 0 
# Loop through each advert
for advert in adverts:
    title = advert.find("div", class_="inzeratynadpis")
    if not title:
        continue

    datum_span = title.find("span", class_="velikost10")
    if datum_span and any(date in datum_span.text for date in dates):
        nadpis_elem = advert.find("h2", class_="nadpis")
        lokalita_elem = advert.find("div", class_="inzeratylok")
        cena_elem = advert.find("div", class_="inzeratycena")

        # checkt whether the advert title contain the search string
        if args.search_string in nadpis_elem.text:
            
            count += 1
            new_text = f"{nadpis_elem.text.strip() if nadpis_elem else 'N/A'} | {datum_span.text.strip() if datum_span else 'N/A'} | {lokalita_elem.text.strip() if lokalita_elem else 'N/A'} | {cena_elem.text.strip() if cena_elem else 'N/A'}"
            print(new_text)
            text += f"{new_text}\n"


if count > 0:
    # Sent the message to mattermost
    if args.mm_hook:
        payload = { "text": text}
        resp = requests.post(args.mm_hook, json=payload, headers={"Content-Type": "application/json"})
        if resp.status_code != 200:
            print("Error send the mattermost hook:", resp.status_code,  resp.text)

