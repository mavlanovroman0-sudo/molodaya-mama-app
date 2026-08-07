"""Абстрактный слой умного дома / Smart home provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any


class SmartHomeProvider(ABC):
    """Базовый провайдер — реализуйте для каждой платформы."""

    @abstractmethod
    async def list_devices(self) -> list[dict[str, Any]]:
        """Список устройств у провайдера."""

    @abstractmethod
    async def send_command(self, external_id: str, command: str, params: dict) -> dict:
        """Отправка команды устройству."""

    @abstractmethod
    async def get_state(self, external_id: str) -> dict:
        """Текущее состояние устройства."""


class HomeAssistantProvider(SmartHomeProvider):
    """Home Assistant REST API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    async def list_devices(self) -> list[dict]:
        # GET /api/states
        return [{"external_id": "light.kitchen", "name": "Кухня", "state": "off"}]

    async def send_command(self, external_id: str, command: str, params: dict) -> dict:
        # POST /api/services/{domain}/{service}
        return {"success": True, "external_id": external_id, "command": command}

    async def get_state(self, external_id: str) -> dict:
        return {"external_id": external_id, "state": "off"}


class YandexSmartHomeProvider(SmartHomeProvider):
    """Яндекс Умный дом OAuth API."""

    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token

    async def list_devices(self) -> list[dict]:
        return [{"external_id": "yandex:tea_kettle", "name": "Чайник", "state": "idle"}]

    async def send_command(self, external_id: str, command: str, params: dict) -> dict:
        return {"success": True, "provider": "yandex"}

    async def get_state(self, external_id: str) -> dict:
        return {"temperature": 22, "humidity": 45}


class GoogleHomeProvider(SmartHomeProvider):
    """Google Home / Matter через облако."""

    def __init__(self, project_id: str, credentials: dict):
        self.project_id = project_id
        self.credentials = credentials

    async def list_devices(self) -> list[dict]:
        return [{"external_id": "google:thermostat_nursery", "name": "Детская", "state": "heat"}]

    async def send_command(self, external_id: str, command: str, params: dict) -> dict:
        return {"success": True, "provider": "google"}

    async def get_state(self, external_id: str) -> dict:
        return {"temperature": 21.5, "target": 22}


def get_provider(protocol: str, config: dict) -> SmartHomeProvider:
    """Фабрика провайдеров по протоколу."""
    if protocol == "home_assistant":
        return HomeAssistantProvider(config.get("base_url", ""), config.get("token", ""))
    if protocol == "yandex":
        return YandexSmartHomeProvider(config.get("oauth_token", ""))
    if protocol == "google":
        return GoogleHomeProvider(config.get("project_id", ""), config.get("credentials", {}))
  # matter, zigbee, homekit — через Home Assistant как шлюз
    return HomeAssistantProvider(config.get("base_url", "http://localhost:8123"), config.get("token", ""))
