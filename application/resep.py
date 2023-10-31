import json
from urllib.request import urlopen

api = "70441b322dc24df7bdc70cb278ed4192"

# namn översättning till siteId

# få station1 (från) siteId
station1 = input("från: ")
url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station1
first_station = urlopen(url1)
first_station_data = json.loads(first_station.read().decode("utf-8"))
first_station_result = first_station_data["ResponseData"]
start_pos = first_station_result[0]['SiteId']

# print för att kontrollera att det är korrekt
print(first_station_result[0]['SiteId'])

# få station2 (till) siteId
station2 = input("till: ")
url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station2
second_station = urlopen(url1)
second_station_data = json.loads(second_station.read().decode("utf-8"))
second_station_result = second_station_data["ResponseData"]
destination = second_station_result[0]['SiteId']

# print för att kontrollera att det är korrekt
print(second_station_result[0]['SiteId'])


# --------------------------------
# reseplanerare 


