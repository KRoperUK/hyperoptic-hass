# Hyperoptic Home Assistant Integration

[![Tests](https://github.com/kroperuk/hyperoptic-hass/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/kroperuk/hyperoptic-hass/actions/workflows/tests.yaml)
[![codecov](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/kroperuk/hyperoptic-hass)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Flake8](https://img.shields.io/badge/lint-flake8-brightgreen)](https://flake8.pycqa.org/)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-informational)](http://www.mypy-lang.org/)

An unofficial **Home Assistant** integration that exposes your **Hyperoptic broadband** package data as sensors and binary sensors.

## Features

- 🌐 **Real-time Package Data**: Monitor your broadband package details including speed, pricing, and contract status
- 📊 **Binary Sensors**: Track connection installation status and package renewal eligibility
- ⚡ **Regular Updates**: Automatically updates data once per day
- 🔒 **Cloud Polling**: Polls your Hyperoptic account via cloud API
- 🎯 **Multi-Account Support**: Track multiple Hyperoptic accounts/premises
- 📱 **Easy Setup**: Simple config flow for credential entry

## Supported Entities

### Sensors

- **Download Speed** - Your current broadband download speed (Mbps)
- **Upload Speed** - Your current broadband upload speed (Mbps)
- **Current Price** - Current monthly price of your package (GBP)
- **Contract End Date** - Your package contract end date
- **Bundle Name** - Name of your broadband package
- **Order Status** - Current status of your order/service

### Binary Sensors

- **Has Hyperhub** - Whether you have a Hyperhub router installed
- **Connection Installed** - Whether your connection is fully installed
- **Can Renew** - Whether your package is eligible for renewal

## Installation

### Via HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations** tab
3. Click **Explore & Download Repositories**
4. Search for **Hyperoptic Broadband**
5. Click **Download**
6. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Extract to `custom_components/hyperoptic` in your Home Assistant config directory
3. Restart Home Assistant

## Configuration

### Setup via UI Config Flow

1. Go to **Settings** → **Devices & Services** → **Integrations**
2. Click **Create Integration**
3. Search for **Hyperoptic Broadband**
4. Enter your Hyperoptic email and password
5. Done! Entities will automatically be created for your account

### Entities Created

Entities are automatically created using the following naming convention:

- **Sensor entity IDs**: `sensor.{description_name}_{uprn}`
- **Binary sensor entity IDs**: `binary_sensor.{description_name}_{uprn}`

Where `{uprn}` is your property's UPRN (Unique Property Reference Number).

## Usage

Once set up, all sensors and binary sensors will be available in Home Assistant. You can:

- Create automations based on contract end dates
- Monitor your broadband speeds
- Track price changes
- Get alerts when you're eligible for renewal

### Example Automation

Monitor when you're eligible for package renewal:

```yaml
automation:
  - alias: "Notify when Hyperoptic package is renewable"
    trigger:
      platform: state
      entity_id: binary_sensor.can_renew_{uprn}
      to: "on"
    action:
      service: notify.notify
      data:
        message: "Your Hyperoptic package is eligible for renewal"
```

## Development

> **For detailed development instructions**, see [DEVELOPMENT.md](DEVELOPMENT.md) for setup, testing, and debugging guides.

### Prerequisites

- Python 3.13+
- Poetry
- Home Assistant dev environment

### Setup

```bash
# Clone the repository
git clone https://github.com/kroperuk/hyperoptic-hass.git
cd hyperoptic-hass

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components/hyperoptic

# Run specific test file
pytest tests/test_sensor.py
```

### Code Quality

```bash
# Format code with black
black custom_components/ tests/

# Lint with flake8
flake8 custom_components/ tests/ --max-line-length=79

# Type checking with mypy
mypy custom_components/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Project Structure

```
hyperoptic-hass/
├── custom_components/hyperoptic/
│   ├── __init__.py              # Integration setup and unload
│   ├── binary_sensor.py         # Binary sensor platform
│   ├── config_flow.py           # Configuration flow
│   ├── const.py                 # Constants and configuration
│   ├── coordinator.py           # Data update coordinator
│   ├── manifest.json            # Integration manifest
│   ├── sensor.py                # Sensor platform
│   └── strings.json             # Localization strings
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_binary_sensor.py    # Binary sensor tests
│   ├── test_config_flow.py      # Config flow tests
│   ├── test_coordinator.py      # Coordinator tests
│   ├── test_integration.py      # Integration tests
│   └── test_sensor.py           # Sensor tests
├── pyproject.toml               # Project configuration
├── pytest.ini                   # Pytest configuration
└── README.md                    # This file
```

## Testing

This project maintains 100% test coverage with comprehensive unit and integration tests. All tests use randomized fixture data to ensure robustness.

### Test Data Generation

Test fixtures automatically generate random:

- UUIDs for customer, account, package, and connection IDs
- Customer names and email addresses
- Numeric identifiers for accounts and packages

This ensures tests are independent and can be run multiple times without issues.

## Troubleshooting

### Integration not showing up

1. Ensure you've restarted Home Assistant after installation
2. Clear browser cache or try incognito mode
3. Check the logs under **Settings** → **System** → **Logs**

### Entities not appearing

1. Verify your email and password are correct
2. Check that your Hyperoptic account is active
3. Look for errors in the Home Assistant logs

### Debug Logging

#### Development Mode

For development and troubleshooting, enable Home Assistant's debug mode and asyncio logging. This helps detect blocking operations and other issues:

**configuration.yaml**:

```yaml
homeassistant:
  debug: true

logger:
  default: info
  logs:
    # Enable asyncio debug logging to detect blocking operations
    asyncio: debug

    # Enable Home Assistant core debug logging
    homeassistant.core: debug
    homeassistant.components.config: debug

    # Enable debug logging for the hyperoptic integration
    custom_components.hyperoptic: debug
    custom_components.hyperoptic.config_flow: debug
    custom_components.hyperoptic.coordinator: debug
```

A sample `configuration.yaml` is included in the repository.

#### Basic Debug Logging

For production use, you can enable just the integration's debug logging:

```yaml
logger:
  logs:
    custom_components.hyperoptic: debug
```

**Reference**: See [Home Assistant's asyncio blocking operations documentation](https://developers.home-assistant.io/docs/asyncio_blocking_operations/) for more information on detecting and fixing blocking operations in the event loop.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration and is not affiliated with Hyperoptic. Use at your own risk. The author assumes no responsibility for any issues, data loss, or service disruptions.

## Support

For issues, feature requests, or questions, please open an [issue](https://github.com/kroperuk/hyperoptic-hass/issues) on GitHub.

---

**Made with ❤️ by [@kroperuk](https://github.com/kroperuk)**
