"""Sensor platform for Hyperoptic integration."""

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ICON_CALENDAR,
    ICON_DOWNLOAD,
    ICON_MONEY,
    ICON_UPLOAD,
)
from .coordinator import HyperopticCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = {
    "download_speed": SensorEntityDescription(
        key="download_speed",
        name="Download Speed",
        icon=ICON_DOWNLOAD,
        native_unit_of_measurement="Mbps",
    ),
    "upload_speed": SensorEntityDescription(
        key="upload_speed",
        name="Upload Speed",
        icon=ICON_UPLOAD,
        native_unit_of_measurement="Mbps",
    ),
    "current_price": SensorEntityDescription(
        key="current_price",
        name="Current Price",
        icon=ICON_MONEY,
        native_unit_of_measurement="GBP",
    ),
    "current_price_tier": SensorEntityDescription(
        key="current_price_tier",
        name="Current Price Tier",
        icon=ICON_MONEY,
    ),
    "contract_end_date": SensorEntityDescription(
        key="contract_end_date",
        name="Contract End Date",
        icon=ICON_CALENDAR,
    ),
    "bundle_name": SensorEntityDescription(
        key="bundle_name",
        name="Bundle Name",
    ),
    "order_status": SensorEntityDescription(
        key="order_status",
        name="Order Status",
    ),
    "next_price_increase_date": SensorEntityDescription(
        key="next_price_increase_date",
        name="Next Price Increase Date",
        icon=ICON_CALENDAR,
    ),
    "next_price_increase_amount": SensorEntityDescription(
        key="next_price_increase_amount",
        name="Next Price Increase Amount",
        icon=ICON_MONEY,
        native_unit_of_measurement="GBP",
    ),
}


class HyperopticSensorEntity(CoordinatorEntity, SensorEntity):
    """Base class for Hyperoptic sensor entities."""

    def __init__(
        self,
        coordinator: HyperopticCoordinator,
        description: SensorEntityDescription,
        uprn: str,
        package_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._uprn = uprn
        self._package_id = package_id

        self._attr_name = f"{description.name} {uprn}"
        self._attr_unique_id = f"hyperoptic_{uprn}_{package_id}_{description.key}"

    @property
    def native_value(self) -> int | str | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None

        account_data = self.coordinator.data["accounts"].get(self._uprn)
        if not account_data:
            return None

        package = next(
            (pkg for pkg in account_data["packages"] if pkg.id == self._package_id),
            None,
        )
        if not package:
            return None

        key = self.entity_description.key

        if key == "download_speed":
            return package.download_speed
        elif key == "upload_speed":
            return package.upload_speed
        elif key == "current_price":
            return package.current_price
        elif key == "current_price_tier":
            return getattr(package, "current_price_tier", None)
        elif key == "contract_end_date":
            return package.end_date
        elif key == "bundle_name":
            return package.bundle_name
        elif key == "order_status":
            account = account_data["account"]
            return account.order_status
        elif key == "next_price_increase_date":
            return getattr(package, "next_price_increase_date", None)
        elif key == "next_price_increase_amount":
            return getattr(package, "next_price_increase_price", None)

        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hyperoptic sensors from a config entry."""
    coordinator: HyperopticCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []

    # Create sensors for each account/package combo
    if coordinator.data is None:
        return

    for uprn, account_data in coordinator.data["accounts"].items():
        for package in account_data["packages"]:
            for description in SENSOR_DESCRIPTIONS.values():
                entities.append(
                    HyperopticSensorEntity(
                        coordinator=coordinator,
                        description=description,
                        uprn=uprn,
                        package_id=package.id,
                    )
                )

    async_add_entities(entities)
