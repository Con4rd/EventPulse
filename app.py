from flask import Flask, render_template, send_from_directory, jsonify, request
import requests
import secrets

# In this example, we have a Flask application that serves static HTML files from the HTML_Files directory in the project.
# The HTML files are stored in the HTML_Files directory, and the Flask application is configured to serve these files using the send_from_directory function.
# The index route returns the index.html file, and the send_file route serves any static file from the HTML_Files directory based on the filename provided in the URL.
# This allows us to create a simple Flask application that serves static HTML files without the need to create routes for each individual file.
# To run the application, we can execute the app.py file and access the index.html file in the browser:
# $ python app.py
# The application will be running on a development server, and we can access the index.html file by visiting http:// http://127.0.0.1:5000/ in the browser.


app = Flask(__name__, static_folder='HTML_Files', template_folder='HTML_Files')
app.secret_key = secrets.token_hex(32)  # Random secret key for session management


# Configuration for TicketMaster API
TICKETMASTER_API_KEY = 'qDV0IOLql9ch2aHpyV5ThqHeXjG5Glcg'
TICKETMASTER_API_URL = 'https://app.ticketmaster.com/discovery/v2/events.json'


def fetch_ticketmaster_events():
    params = {
        'apikey': TICKETMASTER_API_KEY,
        'city': 'Anchorage',
        'countryCode': 'US'
    }
    response = requests.get(TICKETMASTER_API_URL, params=params)
    return response.json()


def fetch_ticketmaster_events(city):
    params = {
        'apikey': TICKETMASTER_API_KEY,
        'city': city,
        'countryCode': 'US'
    }
    response = requests.get(TICKETMASTER_API_URL, params=params)
    return response.json()

def parse_event_data(events):
    if '_embedded' not in events or 'events' not in events['_embedded']:
        return []

    parsed_events = []
    for event in events['_embedded']['events']:
        parsed_event = {
            'id': event['id'],
            'name': event['name'],
            'url': event['url'],
            'start_time': event['dates']['start']['dateTime'],
            'status': event['dates']['status']['code'],
            'type': event['type'],
            'genre': event['classifications'][0]['genre']['name'] if 'classifications' in event and event['classifications'] else 'Unknown',
            'subgenre': event['classifications'][0]['subGenre']['name'] if 'classifications' in event and event['classifications'] else 'Unknown',
            'promoter': event['promoter']['name'] if 'promoter' in event else 'Unknown',
            'price_range': f"{event['priceRanges'][0]['min']} - {event['priceRanges'][0]['max']}" if 'priceRanges' in event else 'Unknown',
            'seatmap': event['seatmap']['staticUrl'] if 'seatmap' in event else 'None',
            'venue': event['_embedded']['venues'][0]['name'] if '_embedded' in event and 'venues' in event['_embedded'] else 'Unknown',
            'venue_address': event['_embedded']['venues'][0]['address']['line1'] if '_embedded' in event and 'venues' in event['_embedded'] and 'address' in event['_embedded']['venues'][0] else 'Unknown',
            'city': event['_embedded']['venues'][0]['city']['name'] if '_embedded' in event and 'venues' in event['_embedded'] and 'city' in event['_embedded']['venues'][0] else 'Unknown',
            'state': event['_embedded']['venues'][0]['state']['stateCode'] if '_embedded' in event and 'venues' in event['_embedded'] and 'state' in event['_embedded']['venues'][0] else 'Unknown',
            'country': event['_embedded']['venues'][0]['country']['countryCode'] if '_embedded' in event and 'venues' in event['_embedded'] and 'country' in event['_embedded']['venues'][0] else 'Unknown',
            'images' : [image['url'] for image in event['images']] if 'images' in event else []
        }
        parsed_events.append(parsed_event)
    return parsed_events



#Fecthing the events from TicketMaster API with dynamic city
@app.route('/api/events', methods=['GET'])
def get_events():
    city = request.args.get('city', 'Anchorage')
    events = fetch_ticketmaster_events(city)
    parsed_events = parse_event_data(events)
    return jsonify({'events': parsed_events})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    print("Visit http://localhost:5000/api/events to view the events")
    app.run(debug=True)


