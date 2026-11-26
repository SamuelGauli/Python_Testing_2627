"""Tests unitaires des sauvegardes JSON (saveClubs / saveCompetitions)."""
import json

import server


def test_save_clubs_writes_the_clubs_key():
    server.saveClubs()
    data = json.loads(server.CLUBS_FILE.read_text(encoding='utf-8'))
    assert 'clubs' in data
    assert data['clubs'] == server.clubs


def test_save_competitions_writes_the_competitions_key():
    server.saveCompetitions()
    data = json.loads(server.COMPETITIONS_FILE.read_text(encoding='utf-8'))
    assert data['competitions'] == server.competitions


def test_save_clubs_roundtrip_updates_points():
    before = server.clubs[0]['points']
    server.clubs[0]['points'] = before + 5
    server.saveClubs()
    assert server.loadClubs()[0]['points'] == before + 5


def test_save_competitions_roundtrip_updates_places():
    server.competitions[0]['numberOfPlaces'] = 3
    server.saveCompetitions()
    assert server.loadCompetitions()[0]['numberOfPlaces'] == 3


def test_save_clubs_preserves_non_ascii_characters():
    server.clubs.append(
        {'name': 'Équipe Accentuée', 'email': 'e@x.fr', 'points': 1}
    )
    server.saveClubs()
    raw = server.CLUBS_FILE.read_text(encoding='utf-8')
    assert 'Équipe Accentuée' in raw
