"""Binary sensor platform for Hyperoptic integration."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICON_CONNECTION, ICON_ROUTER
from .coordinator import HyperopticCoordinator

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_DESCRIPTIONS = {
    "has_hyperhub": BinarySensorEntityDescription(
        key="has_hyperhub",
        name="Has Hyperhub",
        icon=ICON_ROUTER,
    ),
    "is_installed": BinarySensorEntityDescription(
        key="is_installed",
        name="Connection Installed",
        icon=ICON_CONNECTION,
    ),
    "can_renew": BinarySensorEntityDescription(
        key="can_renew",
        name="Can Renew",
    ),
}


class HyperopticBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Base class for Hyperoptic binary sensor entities."""

    def __init__(
        self,
        coordinator: HyperopticCoordinator,
        description: BinarySensorEntityDescription,
        uprn: str,
        entity_type: str,
        entity_id: str | None = None,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._uprn = uprn
        self._entity_type = entity_type
        self._entity_id = entity_id

        self._attr_name = f"{description.name} {uprn}"
        unique_id_suffix = entity_id if entity_id else uprn
        self._attr_unique_id = f"hyperoptic_{uprn}_{entity_type}_{unique_id_suffix}"  # noqa: E501

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        if self.coordinator.data is None:
            return None

        account_data = self.coordinator.data["accounts"].get(self._uprn)
        if not account_data:
            return None

        key = self.entity_description.key

        if key == "has_hyperhub":
            account = account_data["account"]
            return account.have_hyperhub

        if key == "is_installed":
            connection = next(
                (conn for conn in account_data["connections"] if conn.get("id") == self._entity_id),
                None,
            )
            if connection:
                return connection.get("isInstalled", False)
            return None

        if key == "can_renew":
            package = next(
                (pkg for pkg in account_data["packages"] if pkg.id == self._entity_id),
                None,
            )
            if package:
                return package.can_renew
            return None

        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hyperoptic binary sensors from a config entry."""
    coordinator: HyperopticCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []

    if coordinator.data is None:
        return

    for uprn, account_data in coordinator.data["accounts"].items():
        # Add has_hyperhub sensor for each account
        entities.append(
            HyperopticBinarySensorEntity(
                coordinator=coordinator,
                description=BINARY_SENSOR_DESCRIPTIONS["has_hyperhub"],
                uprn=uprn,
                entity_type="account",
            )
        )

        # Add is_installed sensor for each connection
        for connection in account_data["connections"]:
            entities.append(
                HyperopticBinarySensorEntity(
                    coordinator=coordinator,
                    description=BINARY_SENSOR_DESCRIPTIONS["is_installed"],
                    uprn=uprn,
                    entity_type="connection",
                    entity_id=connection.get("id"),
                )
            )

        # Add can_renew sensor for each package
        for package in account_data["packages"]:
            entities.append(
                HyperopticBinarySensorEntity(
                    coordinator=coordinator,
                    description=BINARY_SENSOR_DESCRIPTIONS["can_renew"],
                    uprn=uprn,
                    entity_type="package",
                    entity_id=package.id,
                )
            )

    async_add_entities(entities)
