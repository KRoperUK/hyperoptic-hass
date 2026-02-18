"""Tests for Hyperoptic binary sensor platform."""

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.hyperoptic.binary_sensor import (
    BINARY_SENSOR_DESCRIPTIONS,
    HyperopticBinarySensorEntity,
)


@pytest.mark.asyncio
async def test_binary_sensor_has_hyperhub(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test has hyperhub binary sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)

    sensor = HyperopticBinarySensorEntity(
        coordinator=coordinator,
        description=BINARY_SENSOR_DESCRIPTIONS["has_hyperhub"],
        uprn=uprn,
        entity_type="account",
    )

    assert sensor.is_on is True


@pytest.mark.asyncio
async def test_binary_sensor_is_installed(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test connection installed binary sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    connection_id = mock_hyperoptic_client.test_connection_id

    sensor = HyperopticBinarySensorEntity(
        coordinator=coordinator,
        description=BINARY_SENSOR_DESCRIPTIONS["is_installed"],
        uprn=uprn,
        entity_type="connection",
        entity_id=connection_id,
    )

    assert sensor.is_on is True


@pytest.mark.asyncio
async def test_binary_sensor_can_renew(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test can renew binary sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticBinarySensorEntity(
        coordinator=coordinator,
        description=BINARY_SENSOR_DESCRIPTIONS["can_renew"],
        uprn=uprn,
        entity_type="package",
        entity_id=package_id,
    )

    assert sensor.is_on is True


@pytest.mark.asyncio
async def test_binary_sensor_unique_id(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test binary sensor unique ID is properly generated."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)

    sensor = HyperopticBinarySensorEntity(
        coordinator=coordinator,
        description=BINARY_SENSOR_DESCRIPTIONS["has_hyperhub"],
        uprn=uprn,
        entity_type="account",
    )

    assert sensor._attr_unique_id == (f"hyperoptic_{uprn}_account_{uprn}")


@pytest.mark.asyncio
async def test_binary_sensor_unique_id_with_entity_id(
    hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data
):
    """Test binary sensor unique ID with entity_id."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    connection_id = mock_hyperoptic_client.test_connection_id

    sensor = HyperopticBinarySensorEntity(
        coordinator=coordinator,
        description=BINARY_SENSOR_DESCRIPTIONS["is_installed"],
        uprn=uprn,
        entity_type="connection",
        entity_id=connection_id,
    )

    assert sensor._attr_unique_id == (f"hyperoptic_{uprn}_connection_{connection_id}")


@pytest.mark.asyncio
async def test_binary_sensor_no_coordinator_data(hass: HomeAssistant):
    """Test binary sensor handles no coordinator data."""
    coordinator = MagicMock()
    coordinator.data = None

    sensor = HyperopticBinarySensorEntity(
        coordinator=coordinator,
        description=BINARY_SENSOR_DESCRIPTIONS["has_hyperhub"],
        uprn="10007888137",
        entity_type="account",
    )

    # Should return None when coordinator data is None
    assert sensor.is_on is None


@pytest.mark.asyncio
async def test_binary_sensor_missing_connection(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test binary sensor handles missing connection."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)

    sensor = HyperopticBinarySensorEntity(
        coordinator=coordinator,
        description=BINARY_SENSOR_DESCRIPTIONS["is_installed"],
        uprn=uprn,
        entity_type="connection",
        entity_id="nonexistent-id",
    )

    # Should return None if connection not found
    assert sensor.is_on is None
