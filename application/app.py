from flask import Flask, render_template, request, jsonify
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)


# Första sidan
@app.route('/')
def index():
    return render_template('index.html')

from flask import Flask, render_template, request, jsonify


@app.route('/')
@app.route('/reseplanerare', methods=['GET', 'POST'])
def reseplanerare():
    if request.method == 'POST':
        api_key = '8fa2feecea3240138c2474a4d9a83845'
        origin = request.form.get('origin')
        destination = request.form.get('destination')

        # Använd SL:s API för att hämta reseplanen
        api_url = f'https://api.sl.se/api2/TravelplannerV3/trip.json?key={api_key}&originId={origin}&destId={destination}'
        response = requests.get(api_url)
        data = response.json()

        # Hantera API-svar och skapa en användbar reseplan
        # Du måste anpassa detta beroende på API-svaret och ditt användningsfall.

        return jsonify(data)

    return render_template('reseplanerare.html')


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

# Sökrutin för reseplanerare-sidan


if __name__ == '__main__':
    app.run(debug=True)
