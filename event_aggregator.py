import requests
from datetime import datetime
import json

class UnifiedEvent:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.description = ""
        self.start_time = ""
        self.end_time = ""
        self.venue = {
            "name": "",
            "address": "",
            "city": "",
            "state": "",
            "country": "",
            "zip_code": ""
        }
        self.category = ""
        self.price = {
            "min": None,
            "max": None
        }
        self.image_url = ""
        self.ticket_url = ""
        self.attending_count = 0
        self.interested_count = 0
        self.source = []

    def populate_from_ticketmaster(self, tm_event):
        self.id = tm_event.get('id', '')
        self.name = tm_event.get('name', '')
        self.description = tm_event.get('description', '')
        self.start_time = tm_event.get('dates', {}).get('start', {}).get('dateTime', '')
        self.end_time = tm_event.get('dates', {}).get('end', {}).get('dateTime', '')

        if '_embedded' in tm_event and 'venues' in tm_event['_embedded']:
            venue = tm_event['_embedded']['venues'][0]
            self.venue = {
                "name": venue.get('name', ''),
                "address": venue.get('address', {}).get('line1', ''),
                "city": venue.get('city', {}).get('name', ''),
                "state": venue.get('state', {}).get('name', ''),
                "country": venue.get('country', {}).get('name', ''),
                "zip_code": venue.get('postalCode', '')
            }

        self.category = tm_event.get('classifications', [{}])[0].get('segment', {}).get('name', '')

        if 'priceRanges' in tm_event:
            self.price = {
                "min": tm_event['priceRanges'][0].get('min'),
                "max": tm_event['priceRanges'][0].get('max')
            }

        self.image_url = tm_event.get('images', [{}])[0].get('url', '')
        self.ticket_url = tm_event.get('url', '')
        self.source.append("Ticketmaster")

    def populate_from_yelp(self, yelp_event):
        self.id = yelp_event.get('id', '')
        self.name = yelp_event.get('name', '')
        self.description = yelp_event.get('description', '')
        self.start_time = yelp_event.get('time_start', '')
        self.end_time = yelp_event.get('time_end', '')

        self.venue = {
            "name": yelp_event.get('business_id', ''),
            "address": yelp_event.get('location', {}).get('address1', ''),
            "city": yelp_event.get('location', {}).get('city', ''),
            "state": yelp_event.get('location', {}).get('state', ''),
            "country": yelp_event.get('location', {}).get('country', ''),
            "zip_code": yelp_event.get('location', {}).get('zip_code', '')
        }

        self.category = yelp_event.get('category', '')

        if yelp_event.get('cost') is not None:
            self.price = {
                "min": yelp_event.get('cost'),
                "max": yelp_event.get('cost_max')
            }

        self.image_url = yelp_event.get('image_url', '')
        self.ticket_url = yelp_event.get('event_site_url', '')
        self.attending_count = yelp_event.get('attending_count', 0)
        self.interested_count = yelp_event.get('interested_count', 0)
        self.source.append("Yelp")

    def merge(self, other_event):
        # Merge data, preferring non-empty values
        for attr, value in vars(other_event).items():
            if getattr(self, attr) == "" or getattr(self, attr) is None:
                setattr(self, attr, value)

        # Merge sources
        self.source = list(set(self.source + other_event.source))

def fetch_ticketmaster_events(api_key, location):
    city = location.split(", ")[0]  # Just use the city name
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={api_key}&city={city}"

    print(f"Ticketmaster API URL: {url}")  # Add this line for debugging

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        events = data.get('_embedded', {}).get('events', [])
        print(f"Ticketmaster API returned {len(events)} events")  # Add this line
        return events
    else:
        print(f"Error fetching Ticketmaster data: {response.status_code}")
        print(f"Response content: {response.text}")  # Add this line
        return []

def fetch_yelp_events(api_key, location):
    headers = {'Authorization': f'Bearer {api_key}'}
    url = "https://api.yelp.com/v3/events"
    now = int(datetime.now().timestamp())  # Convert to Unix timestamp
    params = {'location': location, 'limit': 50, 'start_date': now}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('events', [])
    else:
        print(f"Error fetching Yelp data: {response.status_code}")
        print(f"Response content: {response.text}")  # Add this line
        return []

def aggregate_events(tm_events, yelp_events):
    aggregated = []

    for event in tm_events:
        aggregated.append({
            'id': event.get('id'),
            'name': event.get('name'),
            'description': event.get('description'),
            'start_time': event.get('dates', {}).get('start', {}).get('dateTime'),
            'end_time': event.get('dates', {}).get('end', {}).get('dateTime'),
            'venue': event.get('_embedded', {}).get('venues', [{}])[0],
            'category': event.get('classifications', [{}])[0].get('segment', {}).get('name'),
            'price': event.get('priceRanges', [{}])[0],
            'image_url': event.get('images', [{}])[0].get('url'),
            'ticket_url': event.get('url'),
            'source': ['Ticketmaster']
        })

    for event in yelp_events:
        aggregated.append({
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
            'source': ['Yelp']
        })

    return aggregated

def main():
    tm_api_key = 'your_ticketmaster_api_key'
    yelp_api_key = 'your_yelp_api_key'
    city = 'New York'

    tm_events = fetch_ticketmaster_events(tm_api_key, city)
    yelp_events = fetch_yelp_events(yelp_api_key, city)

    aggregated_events = aggregate_events(tm_events, yelp_events)

    # Output results
    for event in aggregated_events:
        print(f"Event: {event.name}")
        print(f"Date: {event.start_time}")
        print(f"Venue: {event.venue['name']}")
        print(f"Sources: {', '.join(event.source)}")
        print("---")

    print(f"Total events aggregated: {len(aggregated_events)}")

if __name__ == "__main__":
    main()