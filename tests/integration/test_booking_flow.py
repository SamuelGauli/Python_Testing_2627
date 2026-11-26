"""Tests d'integration de la page de reservation (/book)."""


def test_booking_page_is_reachable_after_login(client, login):
    login('kate@shelifts.co.uk')
    page = client.get('/book/Spring%20Festival/She%20Lifts')
    html = page.get_data(as_text=True)
    assert page.status_code == 200
    assert 'How many places?' in html


def test_booking_for_another_club_is_refused(client, login):
    login('john@simplylift.co')
    resp = client.get('/book/Spring%20Festival/She%20Lifts',
                      follow_redirects=True)
    assert 'your own club' in resp.get_data(as_text=True)


def test_booking_requires_login(client):
    resp = client.get('/book/Spring%20Festival/She%20Lifts',
                      follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert 'Please log in to access this page.' in html
    assert 'Secretary portal' in html
