"""Tests d'integration du classement public (/points)."""


def test_points_page_is_public_and_lists_all_clubs(client):
    page = client.get('/points')
    html = page.get_data(as_text=True)
    assert page.status_code == 200
    assert 'No login required' in html
    for expected in ('Simply Lift', 'Iron Temple', 'She Lifts'):
        assert expected in html
