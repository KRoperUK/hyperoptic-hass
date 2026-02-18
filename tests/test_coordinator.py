"""Tests for Hyperoptic coordinator."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.hyperoptic.coordinator import (
    HyperopticCoordinator,
)


@pytest.mark.asyncio
async def test_coordinator_update_data(hass: HomeAssistant, mock_hyperoptic_client):
    """Test coordinator successfully fetches and transforms data."""
    uprn_str = str(mock_hyperoptic_client.test_account_uprn)

    with patch(
        "custom_components.hyperoptic.coordinator.HyperopticClient",
        return_value=mock_hyperoptic_client,
    ):
        coordinator = HyperopticCoordinator(
            hass,
            email="test@example.com",
            password="password",
        )

        data = await coordinator._async_update_data()

        assert data is not None
        assert "customer" in data
        assert "accounts" in data
        assert uprn_str in data["accounts"]
        assert "account" in data["accounts"][uprn_str]
        assert "packages" in data["accounts"][uprn_str]
        assert "connections" in data["accounts"][uprn_str]


@pytest.mark.asyncio
async def test_coordinator_update_data_auth_error(hass: HomeAssistant):
    """Test coordinator handles auth errors."""
    mock_client = MagicMock()
    mock_client.get_customer = MagicMock(side_effect=Exception("401 Unauthorized"))

    with patch(
        "custom_components.hyperoptic.coordinator.HyperopticClient",
        return_value=mock_client,
    ):
        coordinator = HyperopticCoordinator(
            hass,
            email="test@example.com",
            password="wrongpassword",
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_update_data_api_error(hass: HomeAssistant):
    """Test coordinator handles API errors."""
    mock_client = MagicMock()
    mock_client.get_customer = MagicMock(side_effect=Exception("API error"))

    with patch(
        "custom_components.hyperoptic.coordinator.HyperopticClient",
        return_value=mock_client,
    ):
        coordinator = HyperopticCoordinator(
            hass,
            email="test@example.com",
            password="password",
        )

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_shutdown(hass: HomeAssistant):
    """Test coordinator shutdown completes successfully."""
    coordinator = HyperopticCoordinator(
        hass,
        email="test@example.com",
        password="password",
    )

    # Should complete without errors
    await coordinator.async_shutdown()
