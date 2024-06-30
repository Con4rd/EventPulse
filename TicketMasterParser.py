from flask import Flask, jsonify, request, session, redirect
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Random secret key for session management

# Configuration
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


#Fecthing the events from TicketMaster API with dynamic city
@app.route('/api/events', methods=['GET'])
def get_events():
    city = request.args.get('city', 'Anchorage')
    events = fetch_ticketmaster_events(city)
    parsed_events = parse_event_data(events)
    return jsonify({'events': parsed_events})

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

if __name__ == '__main__':
    print("Visit http://localhost:5000/api/events to view the events")
    app.run(debug=True)
