from flask import Flask, request, render_template, make_response
import requests, json
from urllib.request import urlopen
from urllib.parse import quote
from datetime import datetime
import pandas as pd

app = Flask(__name__)


# Cookies -

#############################################################################################
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
        start_pos = request.form.get('origin')
        end_pos = request.form.get('destination')
        station1 = start_pos
        station1 = station1.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace(" ", "")
        url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station1
        first_station = urlopen(url1)
        first_station_data = json.loads(first_station.read().decode("utf-8"))
        first_station_result = first_station_data["ResponseData"]
        start_loc = first_station_result[0]['SiteId']

        # print för att kontrollera att det är korrekt
        # print(first_station_result[0]['SiteId'])

        # få station2 (till) siteId
        station2 = end_pos
        station2 = station2.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace(" ", "")
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


        return render_template('search.html', travel_results=travel_results)

    return render_template('search.html')


##############################################################################################

# Dict för att lagra SiteId.
siteid_dict = {}


# Endpoint för realtid via navbar.
@app.route('/realtid', methods=['POST', 'GET'])
def realtid():
    # Kollar om användaren skickat in ett post-form.
    if request.method == 'POST':
        # Hämtar användarens inmatning från sök.
        station = request.form.get('station')
        # Skapar url för att göra en GET från SL:s api och hämtar rätt data beroende på vad användaren skriver in.
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

        # Lagring av API-key för att hämta realtids tidtabell.
        real_apikey = 'a8a250f2c2634381a8065817445217d5'
        # Skapa URL för att göra en GET-förfrågan till SL API för realtidsavgångar.
        real_api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={real_apikey}&siteid={station_id}'
        # Gör en GET-förfrågan till det angivna URL för att hämta realtidsdata.
        response = requests.get(real_api_url)
        # Konvertera svaret från JSON till ett Python-dictionary som innehåller realtidsinformation.
        realtidsdata = response.json()

        # Resultat av svaret hämtat från api.
        return render_template('realtid.html', realtidsdata=realtidsdata)
    # # Om ingen datat hittas så skickar användaren tillbaka.
    return render_template('realtid.html')


##############################################################################################

# Endpoint för resultat av realtids-sökningen.
@app.route('/realtid_result', methods=['POST', 'GET'])
def realtid_result():
    # Kontrollerar att stationen finns innan programmet körs vidare.
    station = request.args.get('station')

    try:
        if station is not None:
            # Ignorerar tecken som inte kan hanteras i ASCII.
            station = station.encode('ascii', 'ignore').decode('ascii')
            """ Problem/fixat: endpoint svarar inte på mellanrum. Ordnat nu."""
            station = quote(station)
            """# Problem/fixat: endpoint svarar inte å, ä, ö. Kod för att ersätta dessa har lagts till och därmed resulterat i 200 :)"""
            station = station.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace(" ", "")
            # Hämta SiteId för den sökta stationen från SL API.
            url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station
            stat = urlopen(url1)
            stat1 = json.loads(stat.read().decode("utf-8"))
            stat2 = stat1["ResponseData"]
            station_id = stat2[0]['SiteId']
            # En GET-förfrågan görs till SL API med hjälp av SiteId. Omvandlas sedan till json och lagras i realtidsdata.
            real_apikey = 'a8a250f2c2634381a8065817445217d5'
            api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={real_apikey}&siteid={station_id}'
            response = requests.get(api_url)
            # Det vill säga här.
            realtidsdata = response.json()
            # Skapar en Pandas DataFrame som innehåller realtidsinformationen från API-svaret.
            # Som sammanfogas i en enda DataFrame.
            realtids_df = pd.DataFrame(
                realtidsdata["ResponseData"]["Metros"] + realtidsdata["ResponseData"]["Buses"] +
                realtidsdata["ResponseData"][
                    "Trains"])

            # Skapar DataFrames för -:- baserat på informationen om realtid från API.
            tunnelbana_df = realtids_df[realtids_df["TransportMode"] == "METRO"]
            buss_df = realtids_df[realtids_df["TransportMode"] == "BUS"]
            pendel_df = realtids_df[realtids_df["TransportMode"] == "TRAIN"]

            # Konvertera DataFrames till listor med dictionaries.
            tunnelbana_data = tunnelbana_df.to_dict(orient="records")
            buss_data = buss_df.to_dict(orient="records")
            pendel_data = pendel_df.to_dict(orient="records")

            # De konverterade datalistorna skickas som variabler till HTML-filer som sedan visas på sidan.
            return render_template('realtid_result.html', tunnelbana_data=tunnelbana_data, buss_data=buss_data,
                                   pendel_data=pendel_data)
    except IndexError:
        # Hantera fallet där det uppstår ett IndexError, till exempel om stationen inte finns.
        return render_template('realtid.html')  # Returnerar ett felmeddelande om ogiltig station.


# - Cookies?
##############################################################################################

# Priser-sidan
@app.route('/priser')
def priser():
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
