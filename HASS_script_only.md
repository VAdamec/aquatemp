# HASS cfg
* /homeassistant/configuration.yaml
```shell
shell_command:
  heatpump_set_temperature: /bin/bash /config/scripts/heatpump_set_temperature {{ states("input_number.heatpumptemperature") }}
```

* heatpump_set_temperature
```shell
#!/bin/bash
#
# Use token from main integration
#

token=$(cat /homeassistant/heatpump/tmp/token)
cloudurl="https://cloud.linked-go.com:449/crmservice/api/app"
temperature=${1:-30}

device=$(curl -s -H "Content-Type: application/json; charset=utf-8" \
        -H "x-token: ${token}" -X POST "${cloudurl}/device/deviceList?lang=en" |
        jq -r '.objectResult[]."device_code"')

curl -s -H "Content-Type: application/json; charset=utf-8" \
        -H "x-token: ${token}" \
          -d '{"appId": "16","param":[{"deviceCode":"'$device'","protocolCode":"R02","value":"'$temperature'"}]}' \
    -X POST "${cloudurl}/device/control?lang=en"
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