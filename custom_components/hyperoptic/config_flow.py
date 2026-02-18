"""Config flow for Hyperoptic integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from hyperoptic import HyperopticClient

from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.EMAIL)
        ),
        vol.Required(CONF_PASSWORD): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
    }
)


def _validate_credentials(email: str, password: str) -> dict[str, Any]:
    """Validate credentials (blocking operation)."""
    client = HyperopticClient(email=email, password=password)
    try:
        customer = client.get_customer()
        return {
            "title": f"Hyperoptic - {customer.full_name}",
        }
    finally:
        client.close()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:  # noqa: E501
    """Validate the user input allows us to connect."""
    try:
        return await hass.async_add_executor_job(
            _validate_credentials,
            data[CONF_EMAIL],
            data[CONF_PASSWORD],
        )
    except Exception as err:
        _LOGGER.error("Error validating credentials: %s", err)
        if "401" in str(err) or "Unauthorized" in str(err):
            raise InvalidAuth from err
        raise CannotConnect from err


class HyperopticConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hyperoptic."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                description_placeholders={},
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error: %s", err)
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)  # noqa: E501

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={},
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication."""
