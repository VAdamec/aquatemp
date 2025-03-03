# HASS cfg
* /homeassistant/configuration.yaml
```shell
shell_command:
  heatpump_set_temperature: /bin/bash /config/scripts/heatpump_set_temperature {{ states("input_text.heatpumplogin") }} {{ states("input_text.heatpumppass") }} {{ states("input_number.heatpumptemperature") }}
```

* heatpump_set_temperature
```shell
#!/bin/bash
#
# Use token from main integration
#

cloudurl="https://cloud.linked-go.com:449/crmservice/api/app"
login=${1}
pass=$(echo -n "${2}" | openssl dgst -md5 | awk '{print $2}')
temperature=${1:-30}

token=$(curl -s -H "Content-Type: application/json; charset=utf-8" -X POST \
  -d '{"password": "'$pass'","loginSource": "IOS","areaCode": "en","appId": "16","type": "2","userName": "'$login'"}' \
  "${cloudurl}/user/login?lang=en" | jq -r '.objectResult."x-token"')

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