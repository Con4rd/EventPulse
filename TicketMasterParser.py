from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Configuration
TICKETMASTER_API_KEY = 'YOUR_TICKETMASTER_API_KEY'
TICKETMASTER_API_URL = 'https://app.ticketmaster.com/discovery/v2/events.json'

def fetch_ticketmaster_events():
    params = {
        'apikey': TICKETMASTER_API_KEY,
        'countryCode': 'US',  # You can change this to your preferred country code
        'size': 10  # Number of events to fetch
    }
    response = requests.get(TICKETMASTER_API_URL, params=params)
    return response.json()

@app.route('/api/events', methods=['GET'])
def get_events():
    events = fetch_ticketmaster_events()
    parsed_events = parse_event_data(events)
    return jsonify({'events': parsed_events})

def parse_event_data(events):
    if '_embedded' not in events or 'events' not in events['_embedded']:
        return []

    parsed_events = []
    for event in events['_embedded']['events']:
        parsed_event = {
            'name': event['name'],
            'description': event.get('info', 'No description available'),
            'start_time': event['dates']['start']['dateTime'],
            'url': event['url'],
            'venue': event['_embedded']['venues'][0]['name']
        }
        parsed_events.append(parsed_event)
    return parsed_events

if __name__ == '__main__':
    app.run(debug=True)
