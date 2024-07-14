import requests
import json

api_key = 'QMNqEjuHC8KV88qoIn8iPAa-ByvTljO7eCIzLK5Fka_eqHHJK_hi7mfOHj-95t8KWvucWoEh1OIF9PgePSIMW_rf1eWzOvCrgvV4ooOPopxqA-NKZYXIPYmWzDGTZnYx'  # Your full API key here
headers = {
    'Authorization': f'Bearer {api_key}',
}

params = {
    'location': 'New York, NY',
    'term': 'concert',
    'limit': 20,  # Requesting 20 events
    'sort_on': 'popularity'
}

url = 'https://api.yelp.com/v3/events'

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    events = response.json()
    print(json.dumps(events, indent=2))  # Pretty print the entire response
    print(f"\nTotal events returned: {len(events['events'])}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)