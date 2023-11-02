from flask import Flask, request, render_template, jsonify  # Ensure you import jsonify
import requests, json
from urllib.request import urlopen
from urllib.parse import quote
from datetime import datetime
import pandas as pd

app = Flask(__name__)



# Cookies -

##############################################################################################
# Förstasidan samt reseplaneraren.
@app.route('/')
@app.route('/reseplanerare', methods=['GET', 'POST'])
def reseplanerare():
    if request.method == 'POST':
        # Anropa SL:s API för att hämta alternativ baserat på användarens inmatning
        start = request.form.get('origin')
        destination = request.form.get('destination')
        rese_apikey = '94e3fbf21ad242778aef5106d11e7cea'
        api_url = f'https://api.sl.se/api2/TravelplannerV3/trip.json?key={rese_apikey}&originId={start}&destId={destination}'
        response = requests.get(api_url)
        data = response.json()

        # KOD
        station_options = [station['Name'] for station in data.get('ResponseData', [])]

        return render_template('reseplanerare.html', station_options=station_options)

    return render_template('reseplanerare.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get user inputs for start and destination stations
        start_pos = request.form.get('origin')
        end_pos = request.form.get('destination')

        # Translate station names to SiteIds (you can include your code here)
        station1 = start_pos
        station1 = station1.replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
        url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station1
        first_station = urlopen(url1)
        first_station_data = json.loads(first_station.read().decode("utf-8"))
        first_station_result = first_station_data["ResponseData"]
        start_loc = first_station_result[0]['SiteId']

        # print för att kontrollera att det är korrekt
        # print(first_station_result[0]['SiteId'])

        # få station2 (till) siteId
        station2 = end_pos
        station2 = station2.replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
        url2 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station2
        second_station = urlopen(url2)
        second_station_data = json.loads(second_station.read().decode("utf-8"))
        second_station_result = second_station_data["ResponseData"]
        end_loc = second_station_result[0]['SiteId']

        # Perform the trip planning
        api = "70441b322dc24df7bdc70cb278ed4192"
        url = f"https://api.sl.se/api2/TravelplannerV3_1/trip.json?key={api}&originExtId={start_loc}&destExtId={end_loc}"
        trip = urlopen(url)
        trip_data = json.loads(trip.read().decode("utf-8"))
        antal = trip_data["Trip"][0]["LegList"]["Leg"]
        count = len(antal)
        travel_results = []  # A list to store the trip results

        for stopp in range(count):
            if trip_data["Trip"][0]["LegList"]["Leg"][stopp]["type"] != "WALK":
                start_name = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["name"]
                start_time = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["time"]
                destination_name = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["name"]
                destination_time = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["time"]
                product_name = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Product"]["catOutL"]
                direction = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["direction"]

                result = f"Du tar {product_name} klockan {start_time} från {start_name} stationen som åker mot {direction} och går av i {destination_name} klockan {destination_time}"
            else:
                start_walk_str = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["time"]
                start_walk_pos = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Origin"]["name"]
                end_walk_str = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["time"]
                end_walk_pos = trip_data["Trip"][0]["LegList"]["Leg"][stopp]["Destination"]["name"]
                start_time = datetime.strptime(start_walk_str, "%H:%M:%S")
                end_time = datetime.strptime(end_walk_str, "%H:%M:%S")
                time_diff = end_time - start_time
                min_diff = time_diff.total_seconds() / 60
                result = f"Du promenerar från {start_walk_pos} till {end_walk_pos} som tar {int(min_diff)} minuter"

            travel_results.append(result)

        # Render the results in the 'search_results.html' template
        return render_template('search.html', travel_results=travel_results)

    return render_template('search.html')  # Replace with the actual template name

##############################################################################################

# Dict för att lagra SiteId.
siteid_dict = {}


# Endpoint för realtid via navbar.
@app.route('/realtid', methods=['POST', 'GET'])
def realtid():
    # Hämtar användarens inmatning i sökfältet.
    if request.method == 'POST':
        # Svaret hämtas och lagras i variabeln.
        station = request.form.get('station')
        # Variabel som gör att koden kan hantera mellanrum m.m
        az_station = quote(station, safe='')

        # Skapar url för att göra en GET från SL:s api och hämtar rätt value beroende på vad användaren skriver in.
        url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station
        # urlopen används för att öppna och hämta resultat för url1.
        stat = urlopen(url1)
        # Läser json-data från api-svaret sedan omvandlas json till python dict som sedan lagras i variabeln.
        stat1 = json.loads(stat.read().decode("utf-8"))
        # Relevant del av svaret från api läses av och lagras i en ny variabel.
        stat2 = stat1["ResponseData"]
        # SiteId lagras i variabel:
        station_id = stat2[0]['SiteId']

        # kontrollerar om stationen redan finns i dict.
        if station in siteid_dict:
            siteid = siteid_dict[station]
        # Om inte så görs en förfrågan till api för att hämta SiteId
        else:
            # Lagring av api-key för att hämta alla hållplatser.
            api_key = '045de5f58ee24c00ae94d24c4c958908'
            station_input = station
            api_url = f'https://api.sl.se/api2/LineData.json?model=site&key={api_key}&stopAreaName={station_id}'
            # ... Och läser dessa som json.
            response = requests.get(api_url)
            data = response.json()

            # Kontrollerar att giltig 'SiteId' finns i api.
            if 'SiteId' in data:
                siteid = data['SiteId']
                siteid_dict['SiteId'] = siteid
            else:

                # Om ingen datat hittas så skickar användaren tillbaka.
                return redirect('/realtid')

        # Lagring av api-key för att hämta tidtabell i realtid.
        real_apikey = 'a8a250f2c2634381a8065817445217d5'
        real_api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={real_apikey}&siteid={station_id}'
        response = requests.get(real_api_url)
        realtidsdata = response.json()

        # Resultat av svaret hämtat från api.
        return render_template('realtid.html', realtidsdata=realtidsdata)
    # # Om ingen datat hittas så skickar användaren tillbaka.
    return render_template('realtid.html')


##############################################################################################
# TEST - sortera efter avgångstid.
"""def convert_display_time(display_time):
    if display_time == "Nu":
        return 0
    elif "min" in display_time:
        return int(display_time.split()[0])
    else:
        time_obj = datetime.strptime(display_time, "%H:%M")
        return time_obj.hour * 60 + time_obj.minute"""

# Endpoint för resultat av realtids-sökningen.
@app.route('/realtid_result', methods=['POST', 'GET'])
def realtid_result():
    station = request.args.get('station')
    # Problem/fixat: endpoint svarar inte på mellanrum. Ordnat nu.
    station = quote(station)
    # Problem/fixat: endpoint svarar inte å, ä, ö. Kod för att ersätta dessa har lagts till och därmed resulterat i 200 :)
    station = station.replace('å', 'a').replace('ä', 'a').replace('ö', 'o')
    url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station
    stat = urlopen(url1)
    stat1 = json.loads(stat.read().decode("utf-8"))
    stat2 = stat1["ResponseData"]
    station_id = stat2[0]['SiteId']
    # Api för att hämta realtids-svaret och leverera denna igen på denna endpoint, fast hämtat.
    real_apikey = 'a8a250f2c2634381a8065817445217d5'
    api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={real_apikey}&siteid={station_id}'
    response = requests.get(api_url)
    realtidsdata = response.json()

    realtids_df = pd.DataFrame(
        realtidsdata["ResponseData"]["Metros"] + realtidsdata["ResponseData"]["Buses"] + realtidsdata["ResponseData"][
            "Trams"]
    )

    # Skapa DataFrames för varje färdmedelstyp
    tunnelbana_df = realtids_df[realtids_df["TransportMode"] == "METRO"]
    buss_df = realtids_df[realtids_df["TransportMode"] == "BUS"]
    sparvagn_df = realtids_df[realtids_df["TransportMode"] == "TRAM"]

    # Sortera DataFrames efter tid (DisplayTime)
    tunnelbana_df = tunnelbana_df.sort_values(by="DisplayTime")
    buss_df = buss_df.sort_values(by="DisplayTime")
    sparvagn_df = sparvagn_df.sort_values(by="DisplayTime")

    # Konvertera DataFrames till listor med dictionaries
    tunnelbana_data = tunnelbana_df.to_dict(orient="records")
    buss_data = buss_df.to_dict(orient="records")
    sparvagn_data = sparvagn_df.to_dict(orient="records")

    # TEST - sortera efter avgångstid.
    tunnelbana_data.sort(key=lambda x: x["DisplayTime"])
    buss_data.sort(key=lambda x: x["DisplayTime"])
    sparvagn_data.sort(key=lambda x: x["DisplayTime"])

    return render_template('realtid_result.html', tunnelbana_data=tunnelbana_data, buss_data=buss_data, sparvagn_data=sparvagn_data)

    # test för sortering av tider.
    """tunnelbana_data.sort(key=lambda x: convert_display_time(x["DisplayTime"]))
    buss_data.sort(key=lambda x: convert_display_time(x["DisplayTime"]))
    sparvagn_data.sort(key=lambda x: convert_display_time(x["DisplayTime"]))

    return render_template('realtid_result.html', tunnelbana_data=tunnelbana_data, buss_data=buss_data,
                           sparvagn_data=sparvagn_data)"""

# Vad som behövs göras/Problem som stötts på:
# - Pandas för snyggare utskrift? ///
# - Cookies?
##############################################################################################

# Priser-sidan
@app.route('/priser')
def priser():
    # KOD
    return render_template('priser.html')

##############################################################################################
# Trafikläge-sidan
@app.route('/trafiklage', methods=['POST', 'GET'])
def trafiklage():
    error_message = ""  # Initsierar error_message som en tom sträng
    # Ange API-endpointen för trafikinformation (exempel)
    trinfo_apikey = '854b0bee7c2841dfbcb36e421c4616f0'
    api_url = f'https://api.sl.se/api2/trafficsituation.json?key={trinfo_apikey}'

    # Gör en HTTP-förfrågan till trafikinformationstjänsten
    response = requests.get(api_url)

    # Kontrollera om förfrågan var framgångsrik (HTTP-statuskod 200)
    if response.status_code == 200:
        traffic_data = response.json()  # Förutsatt att svaret är i JSON-format
    else:
        error_message = "Kunde inte hämta trafikinformation."
        traffic_data = None

    return render_template('trafiklage.html', traffic_data=traffic_data, error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)
