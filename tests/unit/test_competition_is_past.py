"""Tests unitaires de competitionIsPast (regle : concours a venir)."""
from datetime import datetime, timedelta

import server


def test_a_past_competition_is_past():
    comp = {'name': 'Old Cup', 'date': '2020-01-01 00:00:00'}
    assert server.competitionIsPast(comp) is True


def test_a_future_competition_is_not_past():
    comp = {'name': 'Future Cup', 'date': '2099-12-31 23:59:59'}
    assert server.competitionIsPast(comp) is False


def test_an_invalid_date_does_not_crash_and_is_not_past():
    # bug d'origine : ValueError non attrape -> on exige False, pas un crash
    comp = {'name': 'Broken', 'date': 'not-a-date'}
    assert server.competitionIsPast(comp) is False


def test_an_empty_date_does_not_crash_and_is_not_past():
    comp = {'name': 'Empty', 'date': ''}
    assert server.competitionIsPast(comp) is False


def test_a_competition_ending_tomorrow_is_not_past():
    tomorrow = datetime.now() + timedelta(days=1)
    comp = {'name': 'Tomorrow', 'date': tomorrow.strftime('%Y-%m-%d %H:%M:%S')}
    assert server.competitionIsPast(comp) is False
