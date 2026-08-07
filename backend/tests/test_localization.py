"""Тесты локализации / Localization tests."""

from app.services.localization import language_from_country, parse_accept_language
from app.models import AppLanguage


def test_language_russia():
    assert language_from_country("RU") == AppLanguage.ru


def test_language_kazakhstan():
    assert language_from_country("KZ") == AppLanguage.kk


def test_language_kazakhstan_russian_fallback():
    assert language_from_country("KZ", "ru-RU,ru") == AppLanguage.ru


def test_language_uzbekistan():
    assert language_from_country("UZ") == AppLanguage.uz


def test_parse_accept_language():
    assert parse_accept_language("kk-KZ,kk;q=0.9,ru;q=0.8") == AppLanguage.kk
