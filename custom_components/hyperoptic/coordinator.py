"""Data coordinator for Hyperoptic integration."""

import logging
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from hyperoptic import HyperopticClient

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PackageWrapper:
    """Wrapper for Package objects to store calculated fields."""

    def __init__(self, package: Any) -> None:
        """Initialize the wrapper."""
        self._package = package
        self.next_price_increase_date: str | None = None
        self.next_price_increase_price: str | None = None
        self.current_price_tier: str | None = None

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the wrapped package."""
        return getattr(self._package, name)


def _get_current_price_tier(package: Any) -> str | None:
    """Get the current applicable price tier from pricing schedule.

    Evaluates pricing tiers based on date ranges, preferring more specific
    entries (with both from/until or just until) over the default (both null).

    Returns:
        Human-readable current price tier description or None.
    """
    try:
        if not hasattr(package, "plan_details"):
            return None

        plan_details = package.plan_details
        if not hasattr(plan_details, "pricing"):
            return None

        pricing_list = plan_details.pricing
        if not pricing_list:
            return None

        today = datetime.now().date()
        default_price = None
        applicable_prices = []

        for pricing in pricing_list:
            from_date_str = (
                pricing.get("from") if isinstance(pricing, dict) else getattr(pricing, "from_date", None)  # noqa: E501
            )
            until_date_str = (
                pricing.get("until") if isinstance(pricing, dict) else getattr(pricing, "until", None)  # noqa: E501
            )
            price = pricing.get("price") if isinstance(pricing, dict) else getattr(pricing, "price", None)

            # Skip if no price
            if not price:
                continue

            # If both from and until are null, this is the default price
            if from_date_str is None and until_date_str is None:
                default_price = price
                continue

            # Try to parse dates
            from_date = None
            until_date = None

            if from_date_str:
                try:
                    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue

            if until_date_str:
                try:
                    until_date = datetime.strptime(until_date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue

            # Check if this entry applies to today
            # It applies if: from <= today < until (or from is None, or until is None)
            applies = True
            if from_date is not None and today < from_date:
                applies = False
            if until_date is not None and today >= until_date:
                applies = False

            if applies and until_date is not None:
                # Entries with an until date are more specific
                applicable_prices.append((until_date, price))

        # Use the most specific applicable price (smallest until date)
        if applicable_prices:
            applicable_prices.sort(key=lambda x: x[0])
            return f"Active Tier: £{applicable_prices[0][1]}/month"

        # Fall back to default price
        if default_price:
            return f"Default Price: £{default_price}/month"

        return None

    except Exception as err:
        _LOGGER.debug("Error parsing current price tier: %s", err)
        return None


def _get_next_price_increase(
    package: Any,
) -> tuple[str | None, str | None]:
    """Get next price increase date and amount from package pricing.

    The next price increase happens at the end of the current pricing period.

    Returns:
        Tuple of (increase_date, new_price) or (None, None) if no increase.
    """
    try:
        if not hasattr(package, "plan_details"):
            return None, None

        plan_details = package.plan_details
        if not hasattr(plan_details, "pricing"):
            return None, None

        pricing_list = plan_details.pricing
        if not pricing_list:
            return None, None

        today = datetime.now().date()

        # Get all entries with until dates and parse them
        entries_with_until = []
        for pricing in pricing_list:
            until_date_str = (
                pricing.get("until") if isinstance(pricing, dict) else getattr(pricing, "until", None)  # noqa: E501
            )
            price = pricing.get("price") if isinstance(pricing, dict) else getattr(pricing, "price", None)

            if until_date_str and price:
                try:
                    until_date = datetime.strptime(until_date_str, "%Y-%m-%d").date()
                    entries_with_until.append((until_date, str(price), pricing))
                except ValueError:
                    continue

        if not entries_with_until:
            return None, None

        # Sort by until date
        entries_with_until.sort(key=lambda x: x[0])

        # Find the index of the current applicable entry
        current_index = None
        for i, (until_date, _, _) in enumerate(entries_with_until):
            if until_date > today:
                current_index = i
                break

        # If we found a current entry and there's a next one, return it
        if current_index is not None and current_index < len(entries_with_until) - 1:
            # The next price increase is at the current entry's until date
            current_until_date = entries_with_until[current_index][0]
            next_price = entries_with_until[current_index + 1][1]
            return str(current_until_date), str(next_price)

        # No next price increase found
        return None, None

    except Exception as err:
        _LOGGER.debug("Error parsing price increase: %s", err)
        return None, None


def _fetch_hyperoptic_data(email: str, password: str) -> tuple[Any, Any, Any]:
    """Fetch data from Hyperoptic API (blocking operation)."""
    client = HyperopticClient(email=email, password=password)
    try:
        customer = client.get_customer()
        packages = client.get_my_packages()
        connections = client.get_my_connections()
        return customer, packages, connections
    finally:
        client.close()


class HyperopticCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Hyperoptic data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        email: str,
        password: str,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.email = email
        self.password = password

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Hyperoptic API."""
        try:
            # Run blocking operations in executor
            customer, packages, connections = await self.hass.async_add_executor_job(
                _fetch_hyperoptic_data,
                self.email,
                self.password,
            )

            # Transform data: organize by account UPRN
            accounts_data: dict[str, Any] = {}

            for account in customer.accounts:
                uprn = account.uprn

                account_connections = [conn for conn in connections if conn.get("premiseUprn") == uprn]

                # Add pricing info to each package
                packages_with_pricing = []
                for package in packages:
                    next_increase_date, next_increase_price = _get_next_price_increase(package)
                    current_price_tier = _get_current_price_tier(package)
                    # Wrap package to store calculated pricing info
                    wrapped_package = PackageWrapper(package)
                    wrapped_package.next_price_increase_date = next_increase_date
                    wrapped_package.next_price_increase_price = next_increase_price
                    wrapped_package.current_price_tier = current_price_tier
                    packages_with_pricing.append(wrapped_package)

                accounts_data[str(uprn)] = {
                    "account": account,
                    "packages": packages_with_pricing,
                    "connections": account_connections,
                }

            return {
                "customer": customer,
                "accounts": accounts_data,
            }

        except Exception as err:
            _LOGGER.error("Error updating Hyperoptic data: %s", err)
            if "401" in str(err) or "Unauthorized" in str(err):
                raise ConfigEntryAuthFailed("Invalid email or password") from err
            raise UpdateFailed(f"Error communicating with API: {err}") from err
