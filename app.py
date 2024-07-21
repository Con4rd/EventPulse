from flask import Flask, render_template, send_from_directory, jsonify, request, json
import secrets
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
from event_aggregator import aggregate_events, fetch_ticketmaster_events, fetch_yelp_events
from difflib import SequenceMatcher
from datetime import datetime
import random
from search_utils import search_events
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create a Flask application instance
app = Flask(__name__, static_folder='HTML_Files', template_folder='HTML_Files')
app.secret_key = secrets.token_hex(32)


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["300 per day"],
    storage_uri="memory://",
)


# Configuration for APIs
TICKETMASTER_API_KEY = 'qDV0IOLql9ch2aHpyV5ThqHeXjG5Glcg'
YELP_API_KEY = 'QMNqEjuHC8KV88qoIn8iPAa-ByvTljO7eCIzLK5Fka_eqHHJK_hi7mfOHj-95t8KWvucWoEh1OIF9PgePSIMW_rf1eWzOvCrgvV4ooOPopxqA-NKZYXIPYmWzDGTZnYx'



def log_event(event):
    """Print detailed event information"""
    print(f"Event ID: {event.id}")
    print(f"Name: {event.name}")
    print(f"Description: {event.description[:100]}...")  # First 100 characters
    print(f"Start Time: {event.start_time}")
    print(f"End Time: {event.end_time}")
    print(f"Venue: {event.venue}")
    print(f"Category: {event.category}")
    print(f"Price: {event.price}")
    print(f"Image URL: {event.image_url}")
    print(f"Ticket URL: {event.ticket_url}")
    print(f"Attending Count: {event.attending_count}")
    print(f"Interested Count: {event.interested_count}")
    print(f"Source: {', '.join(event.source)}")
    print("-" * 50)

@app.route('/api/events', methods=['GET'])
@limiter.limit("300 per day", error_message="Daily request exceeded. Please try again tomorrow.")
def get_events():
    city = request.args.get('city', 'Anchorage')
    search_term = request.args.get('search', '').lower()

    # Fetch events from Ticketmaster and Yelp APIs
    tm_events = fetch_ticketmaster_events(TICKETMASTER_API_KEY, city)
    yelp_events = fetch_yelp_events(YELP_API_KEY, city)

    # Aggregate events from both APIs
    aggregated_events = aggregate_events(tm_events, yelp_events)

    # Filter events based on the search term if provided
    if search_term:
        filtered_events = search_events(aggregated_events, search_term)
    else:
        filtered_events = aggregated_events

    # Prepare the event data for response
    events_data = [
        {
            'id': event['id'],
            'name': event['name'],
            'description': event['description'],
            'start_time': event['start_time'],
            'end_time': event['end_time'],
            'venue': event['venue'],
            'category': event['category'],
            'price': event['price'],
            'image_url': event['image_url'],
            'ticket_url': event['ticket_url'],
            'source': event['source']
        }
        for event in filtered_events
    ]

    return jsonify({'events': events_data})

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('search', '').strip()
    city = request.args.get('location', '').strip()

    if not city:
        return render_template('page-listing-v3.html', events=[], search_term=search_term, city=city, event_count=0)

    # Attempt to get state and country information
    user_locale = get_user_location(request.remote_addr)
    if user_locale:
        city, state, country = user_locale
        location = f"{city}, {state}, {country}"
    else:
        location = city

    # Fetch events from Ticketmaster and Yelp APIs
    tm_events = fetch_ticketmaster_events(TICKETMASTER_API_KEY, location)
    yelp_events = fetch_yelp_events(YELP_API_KEY, location)

    # Aggregate events from both APIs
    aggregated_events = aggregate_events(tm_events, yelp_events)

    # Filter events based on the search term if provided
    if search_term:
        filtered_events = search_events(aggregated_events, search_term)
    else:
        filtered_events = aggregated_events

    return render_template('page-listing-v3.html', events=filtered_events, search_term=search_term, city=city, event_count=len(filtered_events))

@app.route('/location', methods=['POST'])
def handle_location():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']

    response = {'message': 'Location received successfully'}
    return jsonify(response)

@app.route('/')
def index():
    user_ip = request.remote_addr
    print(f"User IP: {user_ip}")
    user_locale = get_user_location(user_ip)
    print(f"User locale: {user_locale}")

    if user_locale:
        city, state, country = user_locale
        featured_events = fetch_featured_events(city, state, country)
    else:
        print("Using default location: Anchorage, AK, USA")
        featured_events = fetch_featured_events("Anchorage", "AK", "USA")

    print(f"Number of featured events: {len(featured_events)}")
    return render_template('index.html', featured_events=featured_events)


def get_user_location(ip_address):
    try:
        geolocator = Nominatim(user_agent="EventPulseApp")
        location = geolocator.geocode(ip_address, language="en")
        if location:
            address = location.raw['address']
            city = address.get('city') or address.get('town') or address.get('village')
            state = address.get('state')
            country = address.get('country')
            return city, state, country
        return None
    except GeocoderServiceError as e:
        print(f"Error getting user location: {e}")
        return None
    except Exception as e:
        print(f"Error getting user location: {e}")
        if '418' in str(e):
            print("Received 418 status code. This might be due to rate limiting or IP restrictions.")
        return None


def fetch_featured_events(city, state, country):
    location = f"{city}, {state}, {country}"
    print(f"Fetching featured events for location: {location}")

    tm_events = fetch_ticketmaster_events(TICKETMASTER_API_KEY, location)
    yelp_events = fetch_yelp_events(YELP_API_KEY, location)

    print(f"Raw Ticketmaster events: {len(tm_events)}")
    print(f"Raw Yelp events: {len(yelp_events)}")

    # Process Ticketmaster events
    filtered_tm_events = []
    for event in tm_events:
        if isinstance(event, dict):
            filtered_tm_events.append({
                'id': event.get('id'),
                'name': event.get('name'),
                'description': event.get('description'),
                'start_time': event.get('dates', {}).get('start', {}).get('dateTime'),
                'end_time': event.get('dates', {}).get('end', {}).get('dateTime'),
                'venue': event.get('_embedded', {}).get('venues', [{}])[0],
                'category': event.get('classifications', [{}])[0].get('segment', {}).get('name'),
                'price': event.get('priceRanges', [{}])[0] if event.get('priceRanges') else {},
                'image_url': event.get('images', [{}])[0].get('url') if event.get('images') else None,
                'ticket_url': event.get('url'),
                'source': 'Ticketmaster'
            })

    # Process Yelp events
    filtered_yelp_events = []
    for event in yelp_events:
        if isinstance(event, dict):
            filtered_yelp_events.append({
                'id': event.get('id'),
                'name': event.get('name'),
                'description': event.get('description'),
                'start_time': event.get('time_start'),
                'end_time': event.get('time_end'),
                'venue': event.get('location', {}),
                'category': event.get('category'),
                'price': {'min': event.get('cost'), 'max': event.get('cost_max')},
                'image_url': event.get('image_url'),
                'ticket_url': event.get('event_site_url'),
                'source': 'Yelp'
            })

    print(f"Filtered Ticketmaster events: {len(filtered_tm_events)}")
    print(f"Filtered Yelp events: {len(filtered_yelp_events)}")

    # Ensure equal representation
    max_events_per_source = 10  # Adjust this number as needed
    tm_events_sample = random.sample(filtered_tm_events, min(max_events_per_source, len(filtered_tm_events)))
    yelp_events_sample = random.sample(filtered_yelp_events, min(max_events_per_source, len(filtered_yelp_events)))

    # Combine and shuffle the events
    all_events = tm_events_sample + yelp_events_sample
    random.shuffle(all_events)



    # Select up to 12 events
    featured_events = all_events[:12]

    print(f"Fetched featured events for {location}")
    print(f"Ticketmaster events: {len(tm_events_sample)}")
    print(f"Yelp events: {len(yelp_events_sample)}")
    print(f"Sample events: {len(featured_events) - len(tm_events_sample) - len(yelp_events_sample)}")
    print(f"Total featured events: {len(featured_events)}")

    return featured_events

@app.route('/all_events', methods=['GET'])
def all_events():
    """Display all event data in the browser"""
    city = request.args.get('city', 'New York')

    tm_events = fetch_ticketmaster_events(TICKETMASTER_API_KEY, city)
    yelp_events = fetch_yelp_events(YELP_API_KEY, city)

    aggregated_events = aggregate_events(tm_events, yelp_events)

    events_data = [
        {
            'id': event.get('id', ''),
            'name': event.get('name', ''),
            'description': event.get('description', ''),
            'start_time': event.get('start_time', ''),
            'end_time': event.get('end_time', ''),
            'venue': event.get('venue', {}),
            'category': event.get('category', ''),
            'price': event.get('price', {}),
            'image_url': event.get('image_url', ''),
            'ticket_url': event.get('ticket_url', ''),
            'attending_count': event.get('attending_count', 0),
            'interested_count': event.get('interested_count', 0),
            'source': event.get('source', [])
        }
        for event in aggregated_events
    ]

    return f"<pre>{json.dumps(events_data, indent=2)}</pre>"


def calculate_relevance_score(event, search_terms):
    if event is None:
        return 0

    score = 0
    searchable_fields = [
        str(event.get('name', '')).lower(),
        str(event.get('description', '')).lower(),
        str(event.get('category', '')).lower(),
    ]

    for term in search_terms:
        term_score = 0
        for field in searchable_fields:
            if term in field:
                term_score += 1
            # Add extra score for exact matches
            if term == field:
                term_score += 2
            # Add partial matching score
            term_score += SequenceMatcher(None, term, field).ratio()

        # Only add to the total score if this term contributed something
        if term_score > 0:
            score += term_score

    # Set a minimum threshold for relevance
    min_threshold = 0.5 * len(search_terms)

    return score if score > min_threshold else 0


@app.template_filter('datetime')
def format_datetime(value):
    if value:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").strftime("%B %d, %Y")
    return ''

@app.template_filter('time')
def format_time(value):
    if value:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").strftime("%I:%M %p")
    return ''


@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    print("Visit http://localhost:5000/api/events to view the aggregated events")
    print("Visit http://localhost:5000/all_events to see all event data in the browser")
    print("Visit http://localhost:5000/api/events?city=Los+Angeles to see events in Los Angeles")
    print("Visit http://localhost:5000/location to test the location endpoint")
    app.run(debug=True)