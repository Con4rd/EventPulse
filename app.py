from flask import Flask, render_template, send_from_directory, jsonify, request
import requests
import secrets
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

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


def fetch_ticketmaster_events(city, search_term=None):
    params = {
        'apikey': TICKETMASTER_API_KEY,
        'city': city,
        'countryCode': 'US',
        'keyword': search_term
    }
    response = requests.get(TICKETMASTER_API_URL, params=params)
    print(f"API Response: {response.json()}")  # Debugging statement
    return response.json()



def parse_event_data(events):
    if '_embedded' not in events or 'events' not in events['_embedded']:
        return []

    parsed_events = []
    for event in events['_embedded']['events']:
        venue_address = event['_embedded']['venues'][0]['address']['line1'] if '_embedded' in event and 'venues' in event['_embedded'] and 'address' in event['_embedded']['venues'][0] and 'line1' in event['_embedded']['venues'][0]['address'] else 'Unknown'

        start_time = event['dates']['start']['dateTime'] if 'dates' in event and 'start' in event['dates'] and 'dateTime' in event['dates']['start'] else 'Unknown'

        parsed_event = {
            'id': event['id'],
            'name': event['name'],
            'url': event['url'],
            'start_time': start_time,
            'status': event['dates']['status']['code'] if 'dates' in event and 'status' in event['dates'] else 'Unknown',
            'type': event['type'],
            'genre': event['classifications'][0]['genre']['name'] if 'classifications' in event and event['classifications'] else 'Unknown',
            'subgenre': event['classifications'][0]['subGenre']['name'] if 'classifications' in event and event['classifications'] else 'Unknown',
            'promoter': event['promoter']['name'] if 'promoter' in event else 'Unknown',
            'price_range': f"{event['priceRanges'][0]['min']} - {event['priceRanges'][0]['max']}" if 'priceRanges' in event else 'Unknown',
            'seatmap': event['seatmap']['staticUrl'] if 'seatmap' in event else 'None',
            'venue': event['_embedded']['venues'][0]['name'] if '_embedded' in event and 'venues' in event['_embedded'] else 'Unknown',
            'venue_address': venue_address,
            'city': event['_embedded']['venues'][0]['city']['name'] if '_embedded' in event and 'venues' in event['_embedded'] and 'city' in event['_embedded']['venues'][0] else 'Unknown',
            'state': event['_embedded']['venues'][0]['state']['stateCode'] if '_embedded' in event and 'venues' in event['_embedded'] and 'state' in event['_embedded']['venues'][0] else 'Unknown',
            'country': event['_embedded']['venues'][0]['country']['countryCode'] if '_embedded' in event and 'venues' in event['_embedded'] and 'country' in event['_embedded']['venues'][0] else 'Unknown',
            'images': [image['url'] for image in event['images']] if 'images' in event else []
        }
        parsed_events.append(parsed_event)
    return parsed_events



#Fecthing the events from TicketMaster API with dynamic city
@app.route('/api/events', methods=['GET'])
def get_events():
    city = request.args.get('city', 'Anchorage')
    search_term = request.args.get('search')
    events = fetch_ticketmaster_events(city, search_term)
    parsed_events = parse_event_data(events)
    return jsonify({'events': parsed_events})

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('search', '').strip()
    city = request.args.get('location', '').strip()

    if not city:
        # Handle case where location is not provided
        return render_template('page-listing-v3.html', events=[], search_term=search_term, city=city)

    events = fetch_ticketmaster_events(city, search_term)
    parsed_events = parse_event_data(events)

    if search_term:
        filtered_events = [event for event in parsed_events if
                           search_term.lower() in event['name'].lower() or
                           search_term.lower() in event['genre'].lower() or
                           search_term.lower() in event['subgenre'].lower() or
                           search_term.lower() in event['type'].lower()]
    else:
        filtered_events = parsed_events

    return render_template('page-listing-v3.html', events=filtered_events, search_term=search_term, city=city, event_count=len(filtered_events))


@app.route('/location', methods=['POST'])
def handle_location():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']

    # Process the location data as needed
    # You can store it in a database, perform reverse geocoding, etc.

    response = {'message': 'Location received successfully'}
    return jsonify(response)

@app.route('/')
def index():
    #Get the user's IP address
    user_ip = request.remote_addr

    #Get the user's location based on their IP address via geolocation API
    user_locale = get_user_location(user_ip) or 'Anchorage'

    #Fetch the events based on the user's location
    featured_events = fetch_featured_events(user_locale)

    return render_template('index.html', featured_events=featured_events)




def get_user_location(ip_address):
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(ip_address)
        return location.city if location else None
    except GeocoderServiceError as e:
        print(f"Error getting user location: {e}")
        return None
    except Exception as e:
        print(f"Error getting user location: {e}")
        return None


def fetch_featured_events(locale):
    #Fetch feature events based on the user's locale area
    params = {
        'apikey': TICKETMASTER_API_KEY,
        'city': locale,
        'countryCode': 'US',
        'size': 12
    }
    response = requests.get(TICKETMASTER_API_URL, params=params)
    events_data = response.json()
    featured_events = parse_event_data(events_data)
    return featured_events


@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    print("Visit http://localhost:5000/api/events to view the events")
    app.run(debug=True)


