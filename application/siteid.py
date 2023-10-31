import json
from urllib.request import urlopen

def main():
        # Station
        station = input("Vilken station vill du se tidstabell från: ")
        url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station
        stat = urlopen(url1)
        stat1 = json.loads(stat.read().decode("utf-8"))
        stat2 = stat1["ResponseData"]
        valet = stat2[0]
        print("Du valde station", stat2[0]['Name'])
        print(stat2[0]['SiteId'])

if __name__ == "__main__":
    main()
