"""Автоопределение языка по стране / Language detection from country."""

from app.models import AppLanguage

# Маппинг страна → язык / Country to language mapping
COUNTRY_LANGUAGE_MAP: dict[str, AppLanguage] = {
    "RU": AppLanguage.ru,
    "KZ": AppLanguage.kk,
    "UZ": AppLanguage.uz,
    "TJ": AppLanguage.tg,
    "GE": AppLanguage.ka,
    "KG": AppLanguage.ky,
}

# Казахстан: казахский по умолчанию, русский как fallback через Accept-Language
KZ_FALLBACK = AppLanguage.ru


def language_from_country(country_code: str, accept_language: str | None = None) -> AppLanguage:
    """Определяет язык по коду страны ISO 3166-1 alpha-2."""
    code = country_code.upper()
    if code == "KZ" and accept_language:
        al = accept_language.lower()
        if "ru" in al and "kk" not in al:
            return KZ_FALLBACK
    return COUNTRY_LANGUAGE_MAP.get(code, AppLanguage.ru)


def parse_accept_language(header: str | None) -> AppLanguage | None:
    """Парсит Accept-Language заголовок браузера."""
    if not header:
        return None
    mapping = {
        "ru": AppLanguage.ru,
        "kk": AppLanguage.kk,
        "uz": AppLanguage.uz,
        "tg": AppLanguage.tg,
        "ka": AppLanguage.ka,
        "ky": AppLanguage.ky,
    }
    for part in header.split(","):
        lang = part.strip().split(";")[0].split("-")[0].lower()
        if lang in mapping:
            return mapping[lang]
    return None
