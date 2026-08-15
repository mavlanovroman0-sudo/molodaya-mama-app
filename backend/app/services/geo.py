"""Геолокация: IP + reverse geocoding / Geo detection service."""

import httpx

from app.config import settings
from app.models import AppLanguage
from app.schemas import GeoDetectResponse
from app.services.localization import language_from_country, parse_accept_language


async def detect_by_ip(ip: str | None) -> dict:
    """Определение страны/города по IP через ip-api.com (бесплатный tier)."""
    if not ip or ip in ("127.0.0.1", "::1"):
        return {"countryCode": "RU", "city": "Москва", "lat": 55.7558, "lon": 37.6173}
    url = f"{settings.ip_geo_api_url}/{ip}?fields=status,countryCode,city,lat,lon,district"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(url)
            data = resp.json()
            if data.get("status") == "success":
                return data
        except Exception:
            pass
    return {"countryCode": "RU", "city": None, "lat": None, "lon": None}


async def reverse_geocode(latitude: float, longitude: float) -> dict:
    """Определение района через Nominatim (OpenStreetMap)."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "accept-language": "ru",
        "addressdetails": 1,
    }
    headers = {"User-Agent": "HomeEase/2.0"}
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            data = resp.json()
            addr = data.get("address", {})
            return {
                "city": addr.get("city") or addr.get("town") or addr.get("village"),
                "district": addr.get("suburb") or addr.get("city_district") or addr.get("district"),
                "microdistrict": addr.get("neighbourhood") or addr.get("quarter"),
                "country_code": addr.get("country_code", "ru").upper(),
            }
        except Exception:
            return {}


async def detect_location(
    ip: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    accept_language: str | None = None,
) -> GeoDetectResponse:
    """Комбинированное автоопределение языка и района."""
    country_code = "RU"
    city = None
    district = None
    microdistrict = None
    lat = latitude
    lon = longitude

    if latitude is not None and longitude is not None:
        geo = await reverse_geocode(latitude, longitude)
        city = geo.get("city")
        district = geo.get("district")
        microdistrict = geo.get("microdistrict")
        country_code = geo.get("country_code", "RU")
    else:
        ip_data = await detect_by_ip(ip)
        country_code = ip_data.get("countryCode", "RU")
        city = ip_data.get("city")
        lat = ip_data.get("lat")
        lon = ip_data.get("lon")
        if lat and lon:
            geo = await reverse_geocode(lat, lon)
            district = geo.get("district")
            microdistrict = geo.get("microdistrict")

    lang = language_from_country(country_code, accept_language)
    if accept_language:
        parsed = parse_accept_language(accept_language)
        if parsed and country_code not in ("KZ",):
            lang = parsed

    return GeoDetectResponse(
        language=lang,
        country_code=country_code,
        city=city,
        district=district,
        microdistrict=microdistrict,
        latitude=lat,
        longitude=lon,
    )
