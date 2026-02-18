"""Pytest fixtures for Hyperoptic integration tests."""

import random
import string
import uuid
from unittest.mock import MagicMock

import pytest

from custom_components.hyperoptic.coordinator import PackageWrapper


def _generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())


def _generate_name() -> str:
    """Generate a random name."""
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def _generate_email() -> str:
    """Generate a random email address."""
    name = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}@example.com"


@pytest.fixture
def mock_hyperoptic_client():
    """Create a mock Hyperoptic client."""
    client = MagicMock()

    # Generate random IDs and data
    customer_id = _generate_uuid()
    customer_identifier = random.randint(100000, 9999999)
    customer_name = _generate_name()
    customer_email = _generate_email()

    account_id = _generate_uuid()
    account_uprn = 100023336956

    package_id = _generate_uuid()
    package_identifier = random.randint(100000, 9999999)

    connection_id = _generate_uuid()

    # Mock customer
    customer = MagicMock()
    customer.id = customer_id
    customer.identifier = customer_identifier
    customer.full_name = customer_name
    customer.email = customer_email

    # Mock account
    account = MagicMock()
    account.id = account_id
    account.uprn = account_uprn
    account.bundle_name = "1Gb Fibre Connection - Broadband Only"
    account.order_status = "ACTIVE"
    account.have_hyperhub = True
    customer.accounts = [account]

    # Mock package
    package = MagicMock()
    package.id = package_id
    package.identifier = package_identifier
    package.status = "ACTIVE"
    package.bundle_name = "1Gb Fibre Connection - Broadband"
    package.download_speed = 1000
    package.upload_speed = 1000
    package.current_price = 16.0
    package.end_date = "2026-09-02"
    package.can_renew = True

    # Mock plan details with pricing information
    pricing_item_1 = {
        "from": None,
        "until": None,
        "price": "63.0",
    }
    pricing_item_2 = {
        "from": "2025-09-01",
        "until": "2026-05-01",
        "price": "16.0",
    }
    pricing_item_3 = {
        "from": "2026-05-01",
        "until": "2026-09-01",
        "price": "19.0",
    }

    plan_details = MagicMock()
    plan_details.pricing = [
        pricing_item_1,
        pricing_item_2,
        pricing_item_3,
    ]
    package.plan_details = plan_details

    # Mock connection
    connection = {
        "id": connection_id,
        "isInstalled": True,
        "premiseUprn": account_uprn,
    }

    client.get_customer = MagicMock(return_value=customer)
    client.get_my_packages = MagicMock(return_value=[package])
    client.get_my_connections = MagicMock(return_value=[connection])
    client.close = MagicMock()

    # Store generated IDs for test access
    client.test_customer_id = customer_id
    client.test_customer_name = customer_name
    client.test_customer_email = customer_email
    client.test_account_id = account_id
    client.test_account_uprn = account_uprn
    client.test_package_id = package_id
    client.test_connection_id = connection_id

    return client


@pytest.fixture
def mock_coordinator_data(mock_hyperoptic_client):
    """Create mock coordinator data."""
    uprn_str = str(mock_hyperoptic_client.test_account_uprn)
    package = mock_hyperoptic_client.get_my_packages.return_value[0]

    # Wrap the package with the calculated fields
    wrapped_package = PackageWrapper(package)
    wrapped_package.next_price_increase_date = "2026-05-01"
    wrapped_package.next_price_increase_price = "19.0"
    wrapped_package.current_price_tier = "Active Tier: £16.0/month"

    return {
        "customer": mock_hyperoptic_client.get_customer.return_value,
        "accounts": {
            uprn_str: {
                "account": (mock_hyperoptic_client.get_customer.return_value.accounts[0]),
                "packages": [wrapped_package],
                "connections": (mock_hyperoptic_client.get_my_connections.return_value),
            }
        },
    }
