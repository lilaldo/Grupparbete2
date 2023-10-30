from flask import Flask, request, render_template, jsonify  # Ensure you import jsonify
import requests

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

siteid_dict = {}

@app.route('/realtid', methods=['POST','GET'])
def realtid():
    if request.method == 'POST':
        # Hämta användarens inmatning från api
        station = request.form.get('station')

        # Kontrollera om stationen redan finns i siteid
        if station in siteid_dict:
            siteid = siteid_dict[station]
        else:
            # Gör en API-förfrågan för att hämta siteid
            api_key = '045de5f58ee24c00ae94d24c4c958908'
            station_input = station  # Användarens inmatning
            api_url = f'https://api.sl.se/api2/LineData.json?model=site&key={api_key}&stopAreaName={station}'
            response = requests.get(api_url)
            data = response.json()

            if 'ResponseData' in data and data['ResponseData']:
                # Extrahera siteid från API-svaret
                siteid = data['ResponseData'][0]['SiteId']
                # Lagra siteid i din dictionary
                siteid_dict[station] = siteid
            else:
                # Om ingen data hittades för stationen, led om användaren
                return redirect(url_for('realtid'))


        real_apikey = 'a8a250f2c2634381a8065817445217d5'
        real_api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={real_apikey}&siteid={siteid}'
        response = requests.get(real_api_url)
        realtidsdata = response.json()

        return render_template('realtid.html', realtidsdata=realtidsdata)

    return render_template('realtid.html')

@app.route('/realtid_result', methods=['POST','GET'])
def realtid_result():
    station = request.args.get('station') '

    real_apikey = 'a8a250f2c2634381a8065817445217d5'
    api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={real_apikey}&siteid={station}'  # Ta bort '&timewindow={timewindow}'
    response = requests.get(api_url)
    realtidsdata = response.json()

    # Returnera realtidsdatan till en resultatvy
    return render_template('realtid_result.html', realtidsdata=realtidsdata)


####################################################################################################

# Priser-sidan
@app.route('/priser')
def priser():
    # KOD
    return render_template('priser.html')


# Trafikläge-sidan
@app.route('/trafiklage')
def trafiklage():
    # KOD
    return render_template('trafiklage.html')


if __name__ == '__main__':
    app.run(debug=True)
