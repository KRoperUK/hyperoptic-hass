"""Integration tests for Hyperoptic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.hyperoptic import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.hyperoptic.const import DOMAIN


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
async def test_async_setup_entry(hass: HomeAssistant, mock_hyperoptic_client, mock_config_entry):
    """Test async setup entry."""
    hass.data[DOMAIN] = {}

    with patch("custom_components.hyperoptic.HyperopticCoordinator") as mock_coordinator_class:
        mock_coordinator = MagicMock()
        mock_coordinator.data = {
            "customer": mock_hyperoptic_client.get_customer.return_value,
            "accounts": {},
        }
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator_class.return_value = mock_coordinator

        with patch.object(
            hass.config_entries,
            "async_forward_entry_setups",
            new_callable=AsyncMock,
        ):
            result = await async_setup_entry(hass, mock_config_entry)

            assert result is True
            assert mock_config_entry.entry_id in hass.data[DOMAIN]
            assert "coordinator" in hass.data[DOMAIN][mock_config_entry.entry_id]


@pytest.mark.asyncio
async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry):
    """Test async unload entry."""
    mock_coordinator = MagicMock()
    mock_coordinator.async_shutdown = AsyncMock()

    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "coordinator": mock_coordinator,
        }
    }

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        new_callable=AsyncMock,
        return_value=True,
    ):
        result = await async_unload_entry(hass, mock_config_entry)

        assert result is True
        assert mock_config_entry.entry_id not in hass.data[DOMAIN]
        mock_coordinator.async_shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_async_unload_entry_unload_failed(hass: HomeAssistant, mock_config_entry):
    """Test async unload entry when unload fails."""
    mock_coordinator = MagicMock()
    mock_coordinator.async_shutdown = AsyncMock()

    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "coordinator": mock_coordinator,
        }
    }

    with patch.object(
        hass.config_entries,
        "async_unload_platforms",
        new_callable=AsyncMock,
        return_value=False,
    ):
        result = await async_unload_entry(hass, mock_config_entry)

        assert result is False
        assert mock_config_entry.entry_id in hass.data[DOMAIN]
        mock_coordinator.async_shutdown.assert_not_called()
