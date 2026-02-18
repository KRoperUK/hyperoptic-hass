# Development Guide

This guide explains how to set up and test the Hyperoptic Home Assistant integration during development.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+
- Virtual environment tool (venv/poetry)

### Running Home Assistant with the Integration

1. **Start the Home Assistant Docker container**:

```bash
# Mount the custom_components directory and use the included configuration
docker run -d \
  --name homeassistant \
  --privileged \
  -e TZ=UTC \
  -v $(pwd)/custom_components:/config/custom_components \
  -v $(pwd)/configuration.yaml:/config/configuration.yaml \
  -p 8123:8123 \
  homeassistant/home-assistant:latest
```

2. **Access Home Assistant**:

   - Open browser to `http://localhost:8123`
   - Complete onboarding
   - Navigate to **Settings** → **Devices & Services** → **Integrations**
   - Click **Create Integration**
   - Search for "Hyperoptic Broadband"
   - Enter your Hyperoptic credentials

3. **Monitor logs**:

```bash
docker logs -f homeassistant
```

4. **Stop the container**:

```bash
docker stop homeassistant
docker rm homeassistant
```

## Debug Mode

### Enabling Debug Logging

The included `configuration.yaml` has debug mode enabled by default. This includes:

- **asyncio debug logging** - Detects blocking operations in the event loop
- **Home Assistant core debug logging** - Core integration debugging
- **Integration-specific logging** - Hyperoptic integration logs

Debug logs will appear when you:

- Run the config flow
- Add the integration
- Interact with sensors/binary sensors

### Understanding Debug Output

Look for warnings about "blocking calls" in the logs. These indicate operations that should be run in a thread pool executor rather than directly in the event loop.

Example warning:

```
WARNING (MainThread) [homeassistant.util.loop] Detected blocking call to load_verify_locations ...
```

**Solution**: Use `hass.async_add_executor_job()` to run blocking operations. See [Home Assistant's asyncio documentation](https://developers.home-assistant.io/docs/asyncio_blocking_operations/).

## Testing

### Run Unit Tests

```bash
# Activate virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt

# Run tests
pytest

# Run with coverage
pytest --cov=custom_components/hyperoptic

# Watch mode (requires pytest-watch)
ptw
```

### Test Specific Components

```bash
# Test config flow
pytest tests/test_config_flow.py -v

# Test coordinators
pytest tests/test_coordinator.py -v

# Test sensors
pytest tests/test_sensor.py -v

# Test binary sensors
pytest tests/test_binary_sensor.py -v
```

## Code Quality

### Lint with flake8

```bash
flake8 custom_components/ tests/ --max-line-length=79
```

### Format with black

```bash
black custom_components/ tests/
```

### Type checking with mypy

```bash
mypy custom_components/
```

### Pre-commit hooks

```bash
pre-commit run --all-files
```

## Common Issues

### Integration Not Showing

1. Check that custom_components are mounted correctly in Docker
2. Reload browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Restart Home Assistant container
4. Check logs for import errors

### Blocking Operation Warnings

If you see warnings about blocking operations:

1. Check the offending file and line number
2. Wrap blocking calls in `hass.async_add_executor_job()`
3. Wrap blocking library operations in a separate function
4. Run tests to verify the fix

**Example**:

```python
# ❌ Wrong - blocking in event loop
async def async_something(self, hass):
    result = blocking_io_call()
    return result

# ✅ Correct - blocking in executor
def _blocking_operation():
    return blocking_io_call()

async def async_something(self, hass):
    result = await hass.async_add_executor_job(_blocking_operation)
    return result
```

### Connection Issues

1. Verify your Hyperoptic account is active
2. Test credentials with the hyperoptic-py library directly
3. Check network connectivity
4. Review error logs in Home Assistant

## Architecture

### Integration Flow

1. **Config Flow** (`config_flow.py`)

   - User enters credentials
   - Validates credentials via executor job
   - Creates config entry

2. **Coordinator** (`coordinator.py`)

   - Runs in executor to fetch Hyperoptic API data
   - Organizes data by account UPRN
   - Updates on interval

3. **Platforms**
   - **Sensor** (`sensor.py`) - Speed, price, status data
   - **Binary Sensor** (`binary_sensor.py`) - Installation and renewal status

### Async Pattern

All blocking operations use `hass.async_add_executor_job()`:

```python
# In config_flow.py
result = await hass.async_add_executor_job(
    _validate_credentials,
    email,
    password,
)

# In coordinator.py - Already handled in DataUpdateCoordinator
# The coordinator framework automatically runs _async_update_data
```

## Git Workflow

1. Create a feature branch
2. Make changes and test
3. Run linters and tests
4. Commit with descriptive messages
5. Create a pull request

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Asyncio Blocking Operations](https://developers.home-assistant.io/docs/asyncio_blocking_operations/)
- [Integration Architecture](https://developers.home-assistant.io/docs/integration_architecture)
- [Creating a Custom Component](https://developers.home-assistant.io/docs/creating_component/)

## Questions?

Open an issue on [GitHub](https://github.com/kroperuk/hyperoptic-hass/issues) with:

- Description of the issue
- Debug logs from the container
- Steps to reproduce
- Your environment details
