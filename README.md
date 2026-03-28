# WarmLink

Home Assistant custom integration for WarmLink heat pumps.

Current version: `0.3.1`

## Install with HACS

1. Open HACS in Home Assistant.
2. Open the menu for custom repositories.
3. Add this repository URL as a custom repository.
4. Select category `Integration`.
5. Find `WarmLink` in HACS and install it.
6. Restart Home Assistant.

## Add the integration

1. Go to `Settings -> Devices & Services`.
2. Select `Add Integration`.
3. Search for `WarmLink`.
4. Enter your WarmLink cloud username and password.
5. Select your heat pump device.

## What it creates

- one climate entity for power, mode, and target temperature
- one number entity for DHW target temperature
- one switch for silent mode
- diagnostic and temperature sensors

## Notes

- This integration connects directly to the WarmLink cloud API.
- The default polling interval is 30 seconds.
- The minimum supported polling interval is 20 seconds.
