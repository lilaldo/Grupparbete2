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

        # Hämta alternativen från API-svaret
        station_options = [station['Name'] for station in data.get('ResponseData', [])]

        return render_template('reseplanerare.html', station_options=station_options)

    return render_template('reseplanerare.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Hantera POST-förfrågan (om det behövs)
        pass
    else:
        results = request.args.get('results')
        return render_template('search.html', results=results)


# Realtid-sidan
@app.route('/realtid')
def realtid():
    # Lägg till logik för Realtid-sidan här
    return render_template('realtid.html')


# Priser-sidan
@app.route('/priser')
def priser():
    # Lägg till logik för Priser-sidan här
    return render_template('priser.html')


# Trafikläge-sidan
@app.route('/trafiklage')
def trafiklage():
    # Lägg till logik för Trafikläge-sidan här
    return render_template('trafiklage.html')


if __name__ == '__main__':
    app.run(debug=True)
