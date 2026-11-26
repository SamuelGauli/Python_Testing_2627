"""Tests unitaires des vues, appelees directement dans un contexte Flask.

Pas de client HTTP ici : on pousse un contexte de requete, on appelle la
vue, on lit les messages flash, puis on ferme le contexte.
"""
from flask import get_flashed_messages, session

import server

FUTURE = 'Spring Festival'
PAST = 'CYBER.EX'
KATE = 'She Lifts'


def _purchase(app, data, logged_as=None):
    """POST /purchasePlaces isole : retourne (reponse, messages flash)."""
    with app.test_request_context(
            '/purchasePlaces', method='POST', data=data):
        if logged_as is not None:
            session['club'] = logged_as
        resp = server.purchasePlaces()
        messages = get_flashed_messages()
    return resp, messages


def _data(**overrides):
    data = {'competition': FUTURE, 'club': KATE, 'places': '2'}
    data.update(overrides)
    return data


def _comp(name):
    return next(c for c in server.competitions if c['name'] == name)


def _club(name):
    return next(c for c in server.clubs if c['name'] == name)


# ---------------------------------------------------------------- index
def test_index_renders_the_login_page(app):
    with app.test_request_context('/'):
        html = server.index()
    assert 'Secretary portal' in html
    assert 'GUDLFT' in html


# --------------------------------------------------------------- points
def test_points_renders_every_club_without_login(app):
    with app.test_request_context('/points'):
        html = server.points()
    assert 'No login required' in html
    for club in server.clubs:
        assert club['name'] in html


# ----------------------------------------------------------------- book
def test_book_renders_the_booking_form(app):
    with app.test_request_context('/'):
        session['club'] = KATE
        html = server.book(FUTURE, KATE)
    assert 'How many places?' in html
    assert FUTURE in html


def test_book_unknown_club_redirects_with_a_message(app):
    with app.test_request_context('/'):
        session['club'] = KATE
        resp = server.book(FUTURE, 'Ghost Club')
        messages = get_flashed_messages()
    assert resp.status_code == 302
    assert any('could not be found' in m for m in messages)


def test_book_for_another_club_is_refused(app):
    with app.test_request_context('/'):
        session['club'] = KATE
        resp = server.book(FUTURE, 'Simply Lift')
        messages = get_flashed_messages()
    assert resp.status_code == 302
    assert any('your own club' in m for m in messages)


def test_book_unknown_competition_redirects_with_a_message(app):
    with app.test_request_context('/'):
        session['club'] = KATE
        resp = server.book('No Such Cup', KATE)
        messages = get_flashed_messages()
    assert resp.status_code == 302
    assert any('competition could not be found' in m for m in messages)


def test_book_past_competition_is_refused(app):
    with app.test_request_context('/'):
        session['club'] = KATE
        resp = server.book(PAST, KATE)
        messages = get_flashed_messages()
    assert resp.status_code == 302
    assert any('already over' in m for m in messages)


# ------------------------------------------------------ purchasePlaces
def test_purchase_success_reduces_places_and_points(app):
    comp = _comp(FUTURE)
    club = _club(KATE)
    comp['numberOfPlaces'] = 12
    club['points'] = 12
    resp, messages = _purchase(app, _data(), logged_as=KATE)
    assert resp.status_code == 302
    assert 'showSummary' in resp.location
    assert any('Great-booking complete' in m for m in messages)
    assert comp['numberOfPlaces'] == 10
    assert club['points'] == 10


def test_purchase_is_persisted_to_disk(app):
    club = _club(KATE)
    club['points'] = 12
    _purchase(app, _data(places='3'), logged_as=KATE)
    reloaded = next(c for c in server.loadClubs() if c['name'] == KATE)
    assert reloaded['points'] == 9


def test_purchase_without_login_is_refused(app):
    resp, messages = _purchase(app, _data())
    assert resp.status_code == 302
    assert any('log in' in m.lower() for m in messages)


def test_purchase_with_a_non_numeric_value_is_refused(app):
    resp, messages = _purchase(app, _data(places='abc'), logged_as=KATE)
    assert any('valid number' in m for m in messages)


def test_purchase_with_zero_places_is_refused(app):
    resp, messages = _purchase(app, _data(places='0'), logged_as=KATE)
    assert any('at least one place' in m for m in messages)


def test_purchase_with_negative_places_is_refused(app):
    resp, messages = _purchase(app, _data(places='-3'), logged_as=KATE)
    assert any('at least one place' in m for m in messages)


def test_purchase_with_more_than_12_places_is_refused(app):
    resp, messages = _purchase(app, _data(places='13'), logged_as=KATE)
    assert any('more than 12' in m for m in messages)


def test_purchase_exceeding_available_places_is_refused(app):
    _comp(FUTURE)['numberOfPlaces'] = 3
    resp, messages = _purchase(app, _data(places='5'), logged_as=KATE)
    assert any('only 3 places are left' in m for m in messages)


def test_purchase_on_a_full_competition_is_refused(app):
    _comp(FUTURE)['numberOfPlaces'] = 0
    resp, messages = _purchase(app, _data(places='1'), logged_as=KATE)
    assert any('is full' in m for m in messages)


def test_purchase_without_enough_points_is_refused(app):
    _club(KATE)['points'] = 2
    resp, messages = _purchase(app, _data(places='5'), logged_as=KATE)
    assert any('only have 2 points' in m for m in messages)


def test_purchase_with_unknown_resources_is_refused(app):
    resp, messages = _purchase(
        app, _data(competition='Nope'), logged_as=KATE)
    assert any('not valid' in m for m in messages)


def test_purchase_for_another_club_is_refused(app):
    resp, messages = _purchase(
        app, _data(club='Simply Lift'), logged_as=KATE)
    assert any('your own club' in m for m in messages)


def test_purchase_on_a_past_competition_is_refused(app):
    resp, messages = _purchase(
        app, _data(competition=PAST), logged_as=KATE)
    assert any('already over' in m for m in messages)
