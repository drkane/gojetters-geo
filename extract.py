import requests
from bs4 import BeautifulSoup
import dateparser
import json

PAGE_URL = "/wiki/Go_Jetters"


def get_episodes(page_url, url_base="https://en.wikipedia.org"):
    request = requests.get(url_base + page_url)
    soup = BeautifulSoup(request.text, 'html.parser')
    tables = soup.find_all('table')
    episodes = []

    for index, table in enumerate(tables):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells)==4:
                links = cells[1].find_all('a')
                place_url = None
                country = []
                for link in links:
                    if link.find("img"):
                        country.append(link.get("href").replace("/wiki/", ""))
                    else:
                        place_url = url_base + link.get("href")

                air_date = None
                if cells[3].text.strip()!="":
                    air_date = dateparser.parse(cells[3].text.strip())
                episode = {
                    "series": index,
                    "episode": int(cells[0].text.strip()),
                    "title": cells[1].text.strip(),
                    "synopsis": cells[2].text.strip(),
                    "air_date": air_date,
                    "place_link": place_url if country else None,
                    "country": country,
                }
                episodes.append(episode)
    return episodes


def get_lat_long(link):
    if not link:
        return
    request = requests.get(link)
    soup = BeautifulSoup(request.text, 'html.parser')
    try:
        geo = soup.find("span", class_="geo").text
        geo = [float(g.strip()) for g in geo.split(";")]
        return [geo[1], geo[0]]
    except:
        pass



def main():
    episodes = get_episodes(PAGE_URL)
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    for episode in episodes:
        if "place_link" not in episode:
            continue
        if not episode["place_link"]:
            continue
        lat_long = get_lat_long(episode["place_link"])
        if not lat_long:
            continue
        if episode["air_date"]:
            episode["air_date"] = episode["air_date"].isoformat()
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": lat_long
            },
            "properties": episode
        }
        geojson["features"].append(feature)
    with open("gojetters.geojson", "w") as f:
        f.write(json.dumps(geojson, indent=4))
    print(geojson)

if __name__ == '__main__':
    main()
