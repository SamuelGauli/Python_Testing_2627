"""Tests fonctionnels : tous les chemins d'erreur (sad paths).

Chaque test pousse l'application jusqu'au message d'erreur attendu et
verifie qu'une page propre est rendue (jamais un 500).
"""
import server

FUTURE = 'Spring Festival'
KATE = 'She Lifts'
KATE_EMAIL = 'kate@shelifts.co.uk'


def _post_places(client, **overrides):
    data = {'competition': FUTURE, 'club': KATE, 'places': '2'}
    data.update(overrides)
    return client.post('/purchasePlaces', data=data,
                       follow_redirects=True)


def _login_as_kate(client):
    client.post('/showSummary', data={'email': KATE_EMAIL})


def test_unknown_email_on_login(client):
    resp = client.post('/showSummary',
                       data={'email': 'ghost@nowhere.fr'},
                       follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert 'find an account for that email' in html
    assert 'Secretary portal' in html


def test_more_than_12_places(client):
    club = next(c for c in server.clubs if c['name'] == KATE)
    club['points'] = 12
    _login_as_kate(client)
    html = _post_places(client, places='13').get_data(as_text=True)
    assert 'more than 12 places' in html


def test_zero_or_negative_places(client):
    _login_as_kate(client)
    zero = _post_places(client, places='0').get_data(as_text=True)
    assert 'at least one place' in zero
    negative = _post_places(client, places='-3').get_data(as_text=True)
    assert 'at least one place' in negative


def test_places_that_are_not_a_number(client):
    _login_as_kate(client)
    html = _post_places(client, places='abc').get_data(as_text=True)
    assert 'valid number' in html
    assert 'How many places?' in html


def test_more_places_than_available(client):
    comp = next(c for c in server.competitions
                if c['name'] == FUTURE)
    comp['numberOfPlaces'] = 3
    _login_as_kate(client)
    html = _post_places(client, places='5').get_data(as_text=True)
    assert 'only 3 places are left' in html


def test_a_full_competition(client):
    comp = next(c for c in server.competitions
                if c['name'] == FUTURE)
    comp['numberOfPlaces'] = 0
    _login_as_kate(client)
    html = _post_places(client, places='1').get_data(as_text=True)
    assert 'is full' in html


def test_not_enough_points(client):
    club = next(c for c in server.clubs if c['name'] == KATE)
    club['points'] = 2
    _login_as_kate(client)
    html = _post_places(client, places='5').get_data(as_text=True)
    assert 'only have 2 points' in html


def test_a_past_competition_is_not_bookable(client):
    _login_as_kate(client)
    page = client.get('/book/CYBER.EX/She%20Lifts',
                      follow_redirects=True)
    assert 'already over' in page.get_data(as_text=True)


def test_protected_pages_are_blocked_for_anonymous_users(client):
    summary = client.get('/showSummary', follow_redirects=True)
    assert 'Secretary portal' in summary.get_data(as_text=True)
    booking = client.get('/book/Spring%20Festival/She%20Lifts',
                         follow_redirects=True)
    assert 'Please log in' in booking.get_data(as_text=True)
    purchase = client.post('/purchasePlaces', data={
        'competition': FUTURE, 'club': KATE, 'places': '1'},
        follow_redirects=True)
    assert 'Please log in' in purchase.get_data(as_text=True)
