"""Tests fonctionnels : parcours complets du secretaire, bout en bout."""
import server


def test_full_secretary_journey(client):
    club = next(c for c in server.clubs if c['name'] == 'She Lifts')
    comp = next(c for c in server.competitions
                if c['name'] == 'Spring Festival')
    club['points'] = 12
    comp['numberOfPlaces'] = 12

    # 1. page d'accueil
    page = client.get('/')
    assert 'Secretary portal' in page.get_data(as_text=True)

    # 2. connexion -> resume du club
    resp = client.post('/showSummary',
                       data={'email': 'kate@shelifts.co.uk'})
    assert resp.status_code == 302
    summary = client.get('/showSummary')
    html = summary.get_data(as_text=True)
    assert 'Welcome back' in html
    assert '12 places left' in html
    assert 'Finished' in html

    # 3. ouverture de la page de reservation
    booking = client.get('/book/Spring%20Festival/She%20Lifts')
    assert 'How many places?' in booking.get_data(as_text=True)

    # 4. achat de 2 places -> confirmation + solde a jour
    bought = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival', 'club': 'She Lifts',
        'places': '2'}, follow_redirects=True)
    html = bought.get_data(as_text=True)
    assert 'Great-booking complete!' in html
    assert '<span class="points-big">10</span>' in html

    # 5. le classement public reste consultable sans connexion
    standings = client.get('/points')
    assert standings.status_code == 200
    assert 'She Lifts' in standings.get_data(as_text=True)


def test_standings_then_login_then_logout_journey(client):
    # classement visible sans connexion
    page = client.get('/points')
    assert page.status_code == 200

    # connexion puis affichage du resume
    client.post('/showSummary', data={'email': 'john@simplylift.co'})
    summary = client.get('/showSummary')
    assert 'john@simplylift.co' in summary.get_data(as_text=True)

    # deconnexion -> retour a la page de connexion
    client.get('/logout')
    again = client.get('/showSummary', follow_redirects=True)
    assert 'Secretary portal' in again.get_data(as_text=True)
