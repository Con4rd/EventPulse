from flask import Flask, redirect, request, jsonify, session
import requests

IBWQA7U7G6676YYYP46L

app = Flask(__name__)
app.secret_key = b'i\x9c\xac\t\xcd\xa7nM\xc3\x91\xd7\xbd\xa9b+\xefYgNj\x97\x0b\xfb\xd4'

# Configuration
EVENTBRITE_CLIENT_ID = 'XLMYVXWAPWGJQZGGL4'
EVENTBRITE_CLIENT_SECRET = 'C6DOGY2FVVGYJEAEQH4TBQ3E2LMQWAEP5M7HWSKX2ER66D77HI'
REDIRECT_URI = 'http://localhost:5000/oauth/callback'
EVENTBRITE_API_URL = 'https://www.eventbriteapi.com/v3/events/search/'

@app.route('/authorize')
def authorize():
    authorization_url = (
        f"https://www.eventbrite.com/oauth/authorize"
        f"?response_type=code"
        f"&client_id={EVENTBRITE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(authorization_url)

@app.route('/oauth/callback')
def oauth_callback():
    code = request.args.get('code')
    if code:
        token_response = get_token(code)
        session['access_token'] = token_response.get('access_token')
        print(session.get('access_token'))  # Print the access token to verify it's set
        return jsonify(token_response)
    else:
        return 'Authorization failed.'

def get_token(code):
    token_url = 'https://www.eventbrite.com/oauth/token'
    payload = {
        'grant_type': 'authorization_code',
        'client_id': EVENTBRITE_CLIENT_ID,
        'client_secret': EVENTBRITE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(token_url, data=payload, headers=headers)
    return response.json()

def fetch_eventbrite_events(access_token, query='technology'):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'q': query  # General search term
    }
    response = requests.get(EVENTBRITE_API_URL, headers=headers, params=params)
    print(response.json())  # Print the response from Eventbrite API to debug
    return response.json()

@app.route('/api/events', methods=['GET'])
def get_events():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/authorize')  # Redirect to authorization if no token is available
    query = request.args.get('query', 'technology')  # Default to 'technology' if not provided
    events = fetch_eventbrite_events(access_token, query)
    parsed_events = parse_event_data(events)
    return jsonify({'events': parsed_events})

def parse_event_data(events):
    if 'events' not in events:
        return []

    parsed_events = []
    for event in events['events']:
        parsed_event = {
            'name': event['name']['text'],
            'description': event['description']['text'],
            'start_time': event['start']['local'],
            'end_time': event['end']['local'],
            'url': event['url']
        }
        parsed_events.append(parsed_event)
    return parsed_events

if __name__ == '__main__':
    print("Visit http://localhost:5000/authorize to start the OAuth process")
    app.run(debug=True)
