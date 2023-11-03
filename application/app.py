from flask import Flask, request, render_template, make_response
import requests, json
from urllib.request import urlopen
from urllib.parse import quote
from datetime import datetime
import pandas as pd

app = Flask(__name__)
search_history = []

# Cookies -

#############################################################################################
# Förstasidan samt reseplaneraren.
# Endpoints '/'
@app.route('/')
@app.route('/reseplanerare', methods=['GET', 'POST'])
def reseplanerare():
    if request.method == 'POST':
        # Anropa SL:s API för att hämta alternativ baserat på användarens inmatning
        start = request.form.get('origin')
        # Hämta destinationsstation från användarens inmatning
        destination = request.form.get('destination')
        # API-nyckel för SL
        rese_apikey = '94e3fbf21ad242778aef5106d11e7cea'
        # Skapa API-anrops-URL med användarinformation
        api_url = f'https://api.sl.se/api2/TravelplannerV3/trip.json?key={rese_apikey}&originId={start}&destId={destination}'
        # Gör ett GET-anrop till SL:s API
        response = requests.get(api_url)
        # Konvertera API-svaret till JSON-format
        data = response.json()

        # Extrahera stationernas namn från API-svaret
        station_options = [station['Name'] for station in data.get('ResponseData', [])]
        # Rendera HTML-sidan med stationernas namn
        return render_template('reseplanerare.html', station_options=station_options)
    # Rendera HTML-sidan om det inte är en POST-förfrågan (t.ex., när användaren öppnar sidan)
    return render_template('reseplanerare.html')

"""Reseplanereraren är ganska lik SL:s egna, dock i ett simplare format. När användaren skriver in önskad start & slut-destination
 så visas nästkommande resa och hur personen ska ta sig dit"""
@app.route('/search', methods=['GET', 'POST'])
def search():
    global search_history  # Tillåt att använda en global variabel 'search_history'

    if request.method == 'POST':
        start_pos = request.form.get('origin')  # Hämta startstation från användarens inmatning
        end_pos = request.form.get('destination')  # Hämta destinationsstation från användarens inmatning

        # Omvandla tecken i stationernas namn för att hantera särskilda tecken
        station1 = start_pos.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace(" ", "")
        station2 = end_pos.replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace(" ", "")

        # Skapa URL för att söka den första stationen
        url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station1
        first_station = urlopen(url1)
        first_station_data = json.loads(first_station.read().decode("utf-8"))
        first_station_result = first_station_data["ResponseData"]
        start_loc = first_station_result[0]['SiteId']

        # Skapa URL för att söka den andra stationen
        url2 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station2
        second_station = urlopen(url2)
        second_station_data = json.loads(second_station.read().decode("utf-8"))
        second_station_result = second_station_data["ResponseData"]
        end_loc = second_station_result[0]['SiteId']

        # Skapa en sökfråga och lägg till den i sökhistoriken
        search_query = f"From: {start_pos}, To {end_pos}"
        search_history.append(search_query)

        # Utför reseplanering med hjälp av SL:s API
        api = "70441b322dc24df7bdc70cb278ed4192"
        url = f"https://api.sl.se/api2/TravelplannerV3_1/trip.json?key={api}&originExtId={start_loc}&destExtId={end_loc}"
        trip = urlopen(url)
        trip_data = json.loads(trip.read().decode("utf-8"))
        antal = trip_data["Trip"][0]["LegList"]["Leg"]
        count = len(antal)
        # En lista för att lagra reseinformation
        travel_results = []

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

        # Skapa ett HTTP-svar med resultatet och uppdatera sökhistoriken som en cookie
        resp = make_response(render_template('search.html', travel_results=travel_results))
        resp.set_cookie('search_history', json.dumps(search_history))

        return resp

    # Läs sökhistoriken från en cookie om det finns någon
    search_history = json.loads(request.cookies.get('search_history', '[]'))

    return render_template('search.html', search_history=search_history)

"""Resultaten visas för användaren i text-format och berätta hur användaren tar sig från punkt a till b. Cookies sparar även tidigare sökta resor som visas för användaren nere i vänstra hörnet."""
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

"""Hade stora utmaningar med att få fram SiteId från SL:s api då man delvis var tvungen att ha en api för
 att hämta alla hållplatser och sedan en annan för att hämta avgångar och sedan kombinera dessa två.
 Med dessa behöver sedan url:en med de olika nyckelvärden ändras beroende på vad användaren matar in"""
##############################################################################################

# Priser-sidan
@app.route('/priser')
def priser():
    return render_template('priser.html')

"""Vi hade andra visioner för denna sidan men tiden räckte inte till för det. 
Till en början var tanken att vi skulle kombinera SL och polisen men efter att vi insett hur många olika api:er
vi skulle behöva ha att göra med så stannade vi vid SL enbart."""
##############################################################################################
# Trafikläge-sidan
@app.route('/trafiklage', methods=['POST', 'GET'])
def trafiklage():
    error_message = ""  # error_message == tom sträng
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

"""Här ser användaren de stora trafikläget som SL går ut med. Mindre förseningar och andra fel som inte påverkar den större allmänheten visas inte här."""

if __name__ == '__main__':
    app.run(debug=True)
