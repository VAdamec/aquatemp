# AquaTemp

Home Assistant custom integration for AquaTemp heat pumps.

## Install with HACS

1. Open HACS in Home Assistant.
2. Open the menu for custom repositories.
3. Add this repository URL as a custom repository.
4. Select category `Integration`.
5. Find `AquaTemp` in HACS and install it.
6. Restart Home Assistant.

## Add the integration

1. Go to `Settings -> Devices & Services`.
2. Select `Add Integration`.
3. Search for `AquaTemp`.
4. Enter your AquaTemp cloud username and password.
5. Select your heat pump device.

## What it creates

- one climate entity for power, mode, and target temperature
- one number entity for DHW target temperature
- one switch for silent mode
- diagnostic and temperature sensors

## Notes

- This integration connects directly to the AquaTemp cloud API.
- The default polling interval is 30 seconds.
- The minimum supported polling interval is 20 seconds.
