"""Tests d'integration de l'achat de places (/purchasePlaces)."""
import server


def test_purchase_happy_path_updates_summary_and_disk(client, login):
    club = next(c for c in server.clubs if c['name'] == 'She Lifts')
    comp = next(c for c in server.competitions
                if c['name'] == 'Spring Festival')
    club['points'] = 12
    comp['numberOfPlaces'] = 12

    login('kate@shelifts.co.uk')
    resp = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival', 'club': 'She Lifts',
        'places': '2'}, follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert 'Great-booking complete!' in html
    assert '<span class="points-big">10</span>' in html

    # persistance : relue depuis le disque (copie tmp isolee)
    on_disk = next(c for c in server.loadClubs()
                   if c['name'] == 'She Lifts')
    assert on_disk['points'] == 10
    comp_disk = next(c for c in server.loadCompetitions()
                     if c['name'] == 'Spring Festival')
    assert comp_disk['numberOfPlaces'] == 10


def test_purchase_requires_login(client):
    resp = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival', 'club': 'She Lifts',
        'places': '2'}, follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert 'Please log in to access this page.' in html


def test_purchase_with_text_places_shows_an_error(client, login):
    login('kate@shelifts.co.uk')
    resp = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival', 'club': 'She Lifts',
        'places': 'abc'}, follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert 'valid number' in html
    assert 'How many places?' in html


def test_purchase_with_unknown_resources_shows_an_error(client, login):
    login('kate@shelifts.co.uk')
    resp = client.post('/purchasePlaces', data={
        'competition': 'Nope', 'club': 'She Lifts', 'places': '1'},
        follow_redirects=True)
    assert 'not valid' in resp.get_data(as_text=True)
