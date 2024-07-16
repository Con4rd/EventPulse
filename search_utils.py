from difflib import SequenceMatcher

# Expanded category mappings and synonyms
category_mappings = {
    'music': {
        'ticketmaster': ['KnvZfZ7vAkJ', 'KnvZfZ7vAeA', 'KnvZfZ7vAvF', 'KnvZfZ7vAv6', 'KnvZfZ7vAvv', 'KnvZfZ7vAve', 'KnvZfZ7vAvd', 'KnvZfZ7vAva', 'KnvZfZ7vAv1', 'KnvZfZ7vAvJ', 'KnvZfZ7vAvE', 'KnvZfZ7vAJ6', 'KnvZfZ7vAvI', 'KnvZfZ7vAvt', 'KnvZfZ7vAvn', 'KnvZfZ7vAvl', 'KnvZfZ7vAev', 'KnvZfZ7vAee', 'KnvZfZ7vAed', 'KnvZfZ7vAe7', 'KnvZfZ7vAeF'],
        'yelp': ['music'],
        'synonyms': ['concert', 'gig', 'live performance', 'recital', 'show', 'band', 'orchestra', 'dj set', 'album release', 'tour']
    },
    'sports': {
        'ticketmaster': ['KZFzniwnSyZfZ7v7nE'],
        'yelp': ['sports'],
        'synonyms': ['game', 'match', 'tournament', 'championship', 'league', 'competition', 'athletics']
    },
    'arts': {
        'ticketmaster': ['KZFzniwnSyZfZ7v7na'],
        'yelp': ['visualarts', 'artmuseums'],
        'synonyms': ['exhibition', 'gallery', 'museum', 'painting', 'sculpture']
    },
    'theatre': {
        'ticketmaster': ['KnvZfZ7v7l1'],
        'yelp': ['theater'],
        'synonyms': ['play', 'drama', 'musical', 'broadway', 'performance', 'stage']
    },
    'comedy': {
        'ticketmaster': ['KnvZfZ7vAe1'],
        'yelp': ['comedyclubs'],
        'synonyms': ['standup', 'improv', 'sketch', 'comedian']
    },
    'film': {
        'ticketmaster': ['KZFzniwnSyZfZ7v7nn'],
        'yelp': ['movietheaters', 'filmfestivals'],
        'synonyms': ['movie', 'cinema', 'screening', 'premiere']
    },
    'food': {
        'ticketmaster': ['KnvZfZ7vAAI'],
        'yelp': ['food', 'restaurants'],
        'synonyms': ['dining', 'culinary', 'tasting', 'gastronomy']
    }
}

def expand_search_terms(search_term):
    expanded_terms = [search_term.lower()]
    for category, data in category_mappings.items():
        if search_term.lower() in data['synonyms'] or search_term.lower() == category:
            expanded_terms.extend(data['synonyms'])
            expanded_terms.append(category)
    return list(set(expanded_terms))

def get_category_score(event, search_terms):
    score = 0
    event_category = event.get('category', '').lower()

    print(f"Event category: {event_category}")
    print(f"Search terms: {search_terms}")

    for category, data in category_mappings.items():
        if event_category in data['ticketmaster'] or event_category in data['yelp']:
            if any(term in search_terms for term in data['synonyms'] + [category]):
                score += 10  # High score for direct category match
                print(f"Category match found: {category}")  # Add this line
                break

    return score

def get_description_score(event, search_terms):
    if event is None:
        return 0
    description = event.get('description', '')
    if description is None:
        return 0
    description = description.lower()
    score = sum(2 for term in search_terms if term in description)
    return score

def search_events(events, search_term):
    expanded_search_terms = expand_search_terms(search_term.lower())

    scored_events = []
    for event in events:
        if event is None:
            continue
        category_score = get_category_score(event, expanded_search_terms)
        description_score = get_description_score(event, expanded_search_terms)
        total_score = category_score + description_score

        if total_score > 0:
            scored_events.append((event, total_score))

    # Sort events by score in descending order
    scored_events.sort(key=lambda x: x[1], reverse=True)

    # Return only the events, not the scores
    return [event for event, score in scored_events]