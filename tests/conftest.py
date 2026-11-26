"""Fixtures partagees : isolation des JSON, client Flask, helper de login.

Chaque test travaille sur des COPIES de clubs.json et competitions.json
placer dans un tmp_path pytest : les vrais fichiers du projet ne sont
jamais ecrits, et les listes en memoire sont restaurees apres chaque test.
"""
import copy
import shutil

import pytest

import server


@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    """Copie les donnees dans tmp_path et coupe les chemins du serveur."""
    clubs_copy = tmp_path / 'clubs.json'
    comps_copy = tmp_path / 'competitions.json'
    shutil.copy(server.CLUBS_FILE, clubs_copy)
    shutil.copy(server.COMPETITIONS_FILE, comps_copy)
    monkeypatch.setattr(server, 'CLUBS_FILE', clubs_copy)
    monkeypatch.setattr(server, 'COMPETITIONS_FILE', comps_copy)
    clubs_backup = copy.deepcopy(server.clubs)
    comps_backup = copy.deepcopy(server.competitions)
    yield
    server.clubs.clear()
    server.clubs.extend(clubs_backup)
    server.competitions.clear()
    server.competitions.extend(comps_backup)


@pytest.fixture
def app():
    """Application en mode test (exceptions remontees, pas de 500 cache)."""
    server.app.config['TESTING'] = True
    return server.app


@pytest.fixture
def client(app):
    """Client HTTP de Flask (cookies de session conserves entre requetes)."""
    return app.test_client()


@pytest.fixture
def login(client):
    """Se connecter via POST /showSummary avec l'email d'un club."""

    def _login(email):
        return client.post('/showSummary', data={'email': email})

    return _login
