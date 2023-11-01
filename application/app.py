from flask import Flask, request, render_template, jsonify  # Ensure you import jsonify
import requests, json
from urllib.request import urlopen
import json
from urllib.parse import quote
from datetime import datetime

app = Flask(__name__)


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
        pass
    else:
        results = request.args.get('results')
        return render_template('search.html', results=results)

##############################################################################################

# Dict för att lagra SiteId.
siteid_dict = {}

# Endpoint för realtid via navbar.
@app.route('/realtid', methods=['POST','GET'])
def realtid():
    # Hämtar användarens inmatning i sökfältey.
    if request.method == 'POST':
        # Svaret hämtas och lagras i variabeln.
        station = request.form.get('station')
        az_station = quote(station, safe='')

        url1 = "https://api.sl.se/api2/typeahead.json?key=460343b3030c4ed9a213f0727f858052&searchstring=" + station
        stat = urlopen(url1)
        stat1 = json.loads(stat.read().decode("utf-8"))
        stat2 = stat1["ResponseData"]
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
            # ... Och läser dessa om json.
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


# Endpoint för resultat av realtids-sökningen.
@app.route('/realtid_result', methods=['POST','GET'])
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

    # Returnera realtidsdatan till en resultatvy.
    return render_template('realtid_result.html', realtidsdata=realtidsdata)


# Vad som behövs göras/Problem som stötts på:
# - Fixa så att SiteId hämtas korrekt
# - Endpoint ska ändras till SiteId och inte angivet sökord.
# - Pandas för snyggare utskrift?
# - Centrerad text/sortering av resehåll/fordon?
# - Cookies?
####################################################################################################

# Priser-sidan
@app.route('/priser')
def priser():
    # KOD
    return render_template('priser.html')


# Trafikläge-sidan
@app.route('/trafiklage', methods=['POST','GET'])
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
