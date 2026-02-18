"""Tests for Hyperoptic config flow."""

from unittest.mock import patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult, FlowResultType

from custom_components.hyperoptic.config_flow import (
    HyperopticConfigFlow,
)


@pytest.fixture
def mock_setup_entry():
    """Mock setup entry."""
    with patch("custom_components.hyperoptic.async_setup_entry", return_value=True) as mock:
        yield mock


async def test_config_flow_user_valid(hass: HomeAssistant, mock_hyperoptic_client):
    """Test config flow with valid credentials."""
    test_email = mock_hyperoptic_client.test_customer_email
    test_name = mock_hyperoptic_client.test_customer_name
    mock_customer = mock_hyperoptic_client.get_customer.return_value

    def mock_validate(email, password):
        """Mock validation function."""
        return {"title": f"Hyperoptic - {mock_customer.full_name}"}

    with patch(
        "custom_components.hyperoptic.config_flow._validate_credentials",
        side_effect=mock_validate,
    ):
        flow = HyperopticConfigFlow()
        flow.hass = hass
        flow.context = {"source": SOURCE_USER, "unique_id": None}

        result: FlowResult = await flow.async_step_user(
            {
                "email": test_email,
                "password": "password",
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == f"Hyperoptic - {test_name}"
        assert result["data"] == {
            "email": test_email,
            "password": "password",
        }


async def test_config_flow_user_invalid_auth(hass: HomeAssistant):
    """Test config flow with invalid credentials."""
    with patch(
        "custom_components.hyperoptic.config_flow._validate_credentials",
        side_effect=Exception("401 Unauthorized"),
    ):
        flow = HyperopticConfigFlow()
        flow.hass = hass
        flow.context = {"source": SOURCE_USER, "unique_id": None}

        result: FlowResult = await flow.async_step_user(
            {
                "email": "invalid@example.com",
                "password": "wrongpassword",
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "invalid_auth"}


async def test_config_flow_user_cannot_connect(hass: HomeAssistant):
    """Test config flow with connection error."""
    with patch(
        "custom_components.hyperoptic.config_flow._validate_credentials",
        side_effect=Exception("Connection error"),
    ):
        flow = HyperopticConfigFlow()
        flow.hass = hass
        flow.context = {"source": SOURCE_USER, "unique_id": None}

        result: FlowResult = await flow.async_step_user(
            {
                "email": "test@example.com",
                "password": "password",
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}


async def test_config_flow_user_initial(hass: HomeAssistant):
    """Test config flow initial step."""
    flow = HyperopticConfigFlow()
    flow.hass = hass
    flow.context = {"source": SOURCE_USER, "unique_id": None}

    result: FlowResult = await flow.async_step_user()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
