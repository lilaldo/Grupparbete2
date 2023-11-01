import json
from urllib.request import urlopen

api = "70441b322dc24df7bdc70cb278ed4192"

# namn översättning till siteId

# få station1 (från) siteId
station1 = input("från: ")
station1 = station1.replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station1
first_station = urlopen(url1)
first_station_data = json.loads(first_station.read().decode("utf-8"))
first_station_result = first_station_data["ResponseData"]
start_pos = first_station_result[0]['SiteId']

# print för att kontrollera att det är korrekt
# print(first_station_result[0]['SiteId'])

# få station2 (till) siteId
station2 = input("till: ")
station2 = station2.replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
url2 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station2
second_station = urlopen(url2)
second_station_data = json.loads(second_station.read().decode("utf-8"))
second_station_result = second_station_data["ResponseData"]
destination = second_station_result[0]['SiteId']

# print för att kontrollera att det är korrekt
# print(second_station_result[0]['SiteId'])


# --------------------------------
# reseplanerare 
url = f"https://api.sl.se/api2/TravelplannerV3_1/trip.json?key={api}&originExtId={start_pos}&destExtId={destination}"
trip = urlopen(url)
trip_data = json.loads(trip.read().decode("utf-8"))
antal = trip_data["Trip"][0]["LegList"]["Leg"]
count = len(antal)
for stopp in  range(count):
    if trip_data["Trip"][0]["LegList"]["Leg"][stopp]["type"] != "WALK":
        start_name = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["name"]
        start_time = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["time"]
        destination_name = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["name"]
        destination_time = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["time"]
        product_name = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Product"]["catOutL"]
        direction = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["direction"]

        print(f"Du tar {product_name} klockan {start_time} från {start_name} stationen som åker mot {direction} och går av i {destination_name} klockan {destination_time}")
    else:
        start_walk = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["time"]
        start_walk_pos = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["name"]
        end_walk = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["time"]
        end_walk_pos = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["name"]
        print(f"Du promenerar från {start_walk_pos} klockan {start_walk} till {end_walk_pos} klockan {end_walk}")


#for trip in trip_result:
 #   print(f"Du tar ")
