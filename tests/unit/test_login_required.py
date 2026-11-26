"""Tests unitaires du decorateur loginRequired."""
from flask import get_flashed_messages, session

import server


def _protected_view():
    return 'SECRET VIEW'


def test_login_required_redirects_anonymous_users(app):
    wrapped = server.loginRequired(_protected_view)
    with app.test_request_context('/'):
        resp = wrapped()
        assert resp.status_code == 302
        assert resp.location.endswith('/')


def test_login_required_flashes_a_login_message(app):
    wrapped = server.loginRequired(_protected_view)
    with app.test_request_context('/'):
        wrapped()
        messages = get_flashed_messages()
        assert messages
        assert 'log in' in messages[0].lower()


def test_login_required_lets_logged_clubs_through(app):
    wrapped = server.loginRequired(_protected_view)
    with app.test_request_context('/'):
        session['club'] = 'Simply Lift'
        assert wrapped() == 'SECRET VIEW'


def test_login_required_keeps_the_original_function_name(app):
    wrapped = server.loginRequired(_protected_view)
    assert wrapped.__name__ == '_protected_view'
