# WarmLink Agent Notes

## Project State

- This repository is a Home Assistant custom integration only.
- Legacy MQTT/bash bridge files were removed on purpose.
- The integration domain is `warmlink`.
- The package path is `custom_components/warmlink`.
- The repository is prepared for HACS custom repository installation.

## Current Versioning

- Current integration version: `0.3.1`
- Keep `custom_components/warmlink/manifest.json` and `README.md` version text in sync.
- When releasing:
  1. update manifest version
  2. update README version line
  3. commit
  4. push `main`
  5. create and push matching git tag
  6. create GitHub release from the tag

## Important Mappings

- DHW target temperature: `R01`
- DHW actual temperature: `T08`
- Main heating target temperature: `R02`
- Operating modes:
  - `water` -> `Mode=1`
  - `heat` -> `Mode=2`
  - `dhw` -> `Mode=3`

## Entity Model

- Climate entity is used for:
  - power on/off
  - target temperature
  - preset mode (`water`, `heat`, `dhw`)
- Separate select entity exists for operating mode.
- Separate number entity exists for DHW target temperature.
- Separate sensors exist for DHW actual and DHW target temperature.

## Diagnostics

- Additional diagnostic sensors were added and are intentionally disabled by default.
- They are meant for safe read-only inspection before promoting anything to a normal entity or writable control.
- Current diagnostic expansion includes:
  - mute timer values
  - compensation slope/offset
  - zone temperatures/targets
  - smart grid status
  - fault registers

## HACS / CI Notes

- `hacs.json` is intentionally minimal.
- HACS workflow currently ignores:
  - `brands`
  - `description`
  - `issues`
  - `topics`
- If GitHub repository metadata is improved later, those ignores can be reduced.

## Validation

- Quick local validation:
  - `python3 -m compileall custom_components/warmlink`
- Hassfest is checked in GitHub Actions.

## Editing Guidance

- Do not reintroduce MQTT, `nohup` scripts, or old shell bridge logic.
- Prefer adding new metrics as read-only diagnostics first.
- Be careful with protocol-code assumptions unless confirmed by observed values on the device.
