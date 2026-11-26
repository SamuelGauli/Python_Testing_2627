"""Tests d'integration du flux d'authentification (client HTTP complet)."""


def test_login_with_a_known_email_shows_the_summary(client, login):
    resp = login('kate@shelifts.co.uk')
    assert resp.status_code == 302
    assert 'showSummary' in resp.location
    page = client.get('/showSummary')
    html = page.get_data(as_text=True)
    assert page.status_code == 200
    assert 'Welcome back' in html
    assert 'kate@shelifts.co.uk' in html


def test_login_with_an_unknown_email_shows_an_error(client):
    resp = client.post('/showSummary',
                       data={'email': 'ghost@nowhere.fr'},
                       follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert 'find an account for that email' in html
    assert 'Secretary portal' in html


def test_summary_requires_login(client):
    resp = client.get('/showSummary', follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert 'Please log in to access this page.' in html
    assert 'Secretary portal' in html


def test_logout_clears_the_session(client, login):
    login('kate@shelifts.co.uk')
    resp = client.get('/logout', follow_redirects=True)
    assert 'You have been logged out.' in resp.get_data(as_text=True)
    page = client.get('/showSummary', follow_redirects=True)
    assert 'Secretary portal' in page.get_data(as_text=True)
