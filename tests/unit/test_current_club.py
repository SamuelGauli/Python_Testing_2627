"""Tests unitaires de currentClub (club courant via la session)."""
from flask import session

import server


def test_current_club_is_none_without_session(app):
    with app.test_request_context('/'):
        assert server.currentClub() is None


def test_current_club_returns_the_logged_club(app):
    with app.test_request_context('/'):
        session['club'] = 'Simply Lift'
        club = server.currentClub()
        assert club is not None
        assert club['email'] == 'john@simplylift.co'


def test_current_club_is_none_for_an_unknown_club_name(app):
    with app.test_request_context('/'):
        session['club'] = 'No Such Club'
        assert server.currentClub() is None


def test_current_club_is_none_for_an_empty_club_name(app):
    with app.test_request_context('/'):
        session['club'] = ''
        assert server.currentClub() is None
