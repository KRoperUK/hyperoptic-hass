"""Tests for Hyperoptic sensor platform."""

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.hyperoptic.sensor import (
    SENSOR_DESCRIPTIONS,
    HyperopticSensorEntity,
)


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "email": "test@example.com",
        "password": "password",
    }
    return entry


@pytest.mark.asyncio
async def test_sensor_entity_download_speed(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test download speed sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["download_speed"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == 1000
    assert sensor._attr_name == f"Download Speed {uprn}"


@pytest.mark.asyncio
async def test_sensor_entity_upload_speed(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test upload speed sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["upload_speed"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == 1000


@pytest.mark.asyncio
async def test_sensor_entity_current_price(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test current price sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["current_price"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == 16.0


@pytest.mark.asyncio
async def test_sensor_entity_contract_end_date(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test contract end date sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["contract_end_date"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == "2026-09-02"


@pytest.mark.asyncio
async def test_sensor_entity_bundle_name(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test bundle name sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["bundle_name"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == "1Gb Fibre Connection - Broadband"


@pytest.mark.asyncio
async def test_sensor_entity_order_status(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test order status sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["order_status"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == "ACTIVE"


@pytest.mark.asyncio
async def test_sensor_entity_unique_id(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test sensor unique ID is properly generated."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["download_speed"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor._attr_unique_id == (f"hyperoptic_{uprn}_{package_id}_download_speed")


@pytest.mark.asyncio
async def test_sensor_no_coordinator_data(hass: HomeAssistant):
    """Test sensor handles no coordinator data."""
    coordinator = MagicMock()
    coordinator.data = None

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["download_speed"],
        uprn="10007888137",
        package_id="185a6934-e37a-4da7-90be-4fe65e30c9bd",
    )

    # Should return None when coordinator data is None
    assert sensor.native_value is None


@pytest.mark.asyncio
async def test_sensor_entity_next_price_increase_date(
    hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data
):
    """Test next price increase date sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["next_price_increase_date"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == "2026-05-01"


@pytest.mark.asyncio
async def test_sensor_entity_next_price_increase_amount(
    hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data
):
    """Test next price increase amount sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["next_price_increase_amount"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == "19.0"


@pytest.mark.asyncio
async def test_sensor_entity_current_price_tier(hass: HomeAssistant, mock_hyperoptic_client, mock_coordinator_data):
    """Test current price tier sensor."""
    coordinator = MagicMock()
    coordinator.data = mock_coordinator_data
    uprn = str(mock_hyperoptic_client.test_account_uprn)
    package_id = mock_hyperoptic_client.test_package_id

    sensor = HyperopticSensorEntity(
        coordinator=coordinator,
        description=SENSOR_DESCRIPTIONS["current_price_tier"],
        uprn=uprn,
        package_id=package_id,
    )

    assert sensor.native_value == "Active Tier: £16.0/month"
