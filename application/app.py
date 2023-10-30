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
        api_key = '94e3fbf21ad242778aef5106d11e7cea'
        api_url = f'https://api.sl.se/api2/TravelplannerV3/trip.json?key={api_key}&originId={start}&destId={destination}'
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


# Realtid-sidan
@app.route('/realtid', methods=['GET', 'POST'])
def realtid():
    api_key = 'a8a250f2c2634381a8065817445217d5'
    api_url = f'https://api.sl.se/api2/realtimedeparturesV4.json?key={api_key}&siteid=DIN_SITE_ID&timewindow=DIN_TIME_WINDOW'
    return render_template('realtid.html')


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
