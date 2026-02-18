"""Constants for the Hyperoptic integration."""

from datetime import timedelta

DOMAIN = "hyperoptic"
PLATFORMS = ["sensor", "binary_sensor"]
SCAN_INTERVAL = timedelta(days=1)

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# Data keys for coordinator
DATA_CUSTOMER = "customer"
DATA_ACCOUNTS = "accounts"
DATA_PACKAGES = "packages"
DATA_CONNECTIONS = "connections"

# Sensor device classes and units
ICON_DOWNLOAD = "mdi:download"
ICON_UPLOAD = "mdi:upload"
ICON_MONEY = "mdi:pound"
ICON_CALENDAR = "mdi:calendar"
ICON_STATUS = "mdi:information"
ICON_ROUTER = "mdi:router-wireless"
ICON_CONNECTION = "mdi:cable-data"

# Entity ID format
ENTITY_ID_FORMAT = "{domain}.{name}"

# Timeouts
TIMEOUT_SECONDS = 10
