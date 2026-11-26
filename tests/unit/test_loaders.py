"""Tests unitaires des chargeurs JSON (loadClubs / loadCompetitions)."""
import json

import server


def test_load_clubs_returns_a_list():
    clubs = server.loadClubs()
    assert isinstance(clubs, list)
    assert len(clubs) >= 3


def test_load_clubs_entries_have_required_keys():
    for club in server.loadClubs():
        assert {'name', 'email', 'points'} <= set(club)


def test_load_clubs_contains_demo_accounts():
    emails = {c['email'] for c in server.loadClubs()}
    assert 'john@simplylift.co' in emails
    assert 'admin@irontemple.com' in emails
    assert 'kate@shelifts.co.uk' in emails


def test_load_clubs_reads_the_patched_file():
    custom = {'clubs': [{'name': 'X Club', 'email': 'x@y.z', 'points': 7}]}
    server.CLUBS_FILE.write_text(json.dumps(custom), encoding='utf-8')
    assert server.loadClubs() == custom['clubs']


def test_load_competitions_returns_a_list():
    comps = server.loadCompetitions()
    assert isinstance(comps, list)
    assert len(comps) >= 1


def test_load_competitions_entries_have_required_keys():
    for comp in server.loadCompetitions():
        assert {'name', 'date', 'numberOfPlaces'} <= set(comp)


def test_load_competitions_reads_the_patched_file():
    custom = {'competitions': [{
        'name': 'Cup', 'date': '2030-01-01 00:00:00', 'numberOfPlaces': 5,
    }]}
    server.COMPETITIONS_FILE.write_text(json.dumps(custom), encoding='utf-8')
    assert server.loadCompetitions() == custom['competitions']
