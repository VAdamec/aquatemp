# HASS cfg
* /homeassistant/configuration.yaml
```shell
shell_command:
  heatpump_set_temperature: /bin/bash /config/scripts/heatpump_set_temperature {{ states("input_number.heatpumptemperature") }}
```

# Helper
* `input_number.heatpumptemperature`

# Automation

```shell
alias: Nastaveni teploty tepelneho cerpadla
description: HeatPump temperature setup
triggers:
  - trigger: state
    entity_id:
      - input_number.heatpumptemperature
conditions: []
actions:
  - action: shell_command.heatpump_set_temperature
    metadata: {}
    data: {}
mode: single

```