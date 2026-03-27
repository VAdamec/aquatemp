#!/bin/bash

set -euo pipefail

path="$(cd "$(dirname "$0")" && pwd)"
settings_file="$path/settings"

setting()
{
	awk -F '\t' -v key="$1" '$1 == key { print $2; exit }' "$settings_file"
}

require_setting()
{
	local value="$1"
	local key="$2"

	if [[ -z "$value" ]]; then
		echo "Missing $key in $settings_file" >&2
		exit 1
	fi
}

is_number()
{
	[[ "$1" =~ ^[0-9]+([.][0-9]+)?$ ]]
}

run_heatpump()
{
	"$path/heatpump" "$@" >/dev/null
}

refresh_state()
{
	"$path/heatpump" info >/dev/null
}

run_and_refresh()
{
	if run_heatpump "$@"; then
		if ! refresh_state; then
			echo "Failed to refresh state after: $*" >&2
		fi
	else
		echo "Heatpump command failed: $*" >&2
	fi
}

set_temperature()
{
	run_and_refresh temp "$1"
}

set_dwh_temperature()
{
	run_and_refresh setdwhtemp "$1"
}

set_silent()
{
	local state

	state=$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')

	case "$state" in
		ON|OFF)
			run_and_refresh silent "$state"
			;;
	esac
}

set_mode()
{
	case "$1" in
		off)
			run_and_refresh off
			;;
		heat|cool|auto)
			if run_heatpump on && run_heatpump mode "$1"; then
				if ! refresh_state; then
					echo "Failed to refresh state after mode change: $1" >&2
				fi
			else
				echo "Heatpump mode command failed: $1" >&2
			fi
			;;
		*)
			return
			;;
	esac
}

subscribe()
{
	local -a cmd
	local topic

	cmd=(mosquitto_sub -v -R -h "$mqtt" -p "$mqttport")

	if [[ -n "$mqttuser" && "$mqttuser" != "none" ]]; then
		cmd+=(-u "$mqttuser")
	fi

	if [[ -n "$mqttpass" && "$mqttpass" != "none" ]]; then
		cmd+=(-P "$mqttpass")
	fi

	for topic in \
		"$temperature_topic" \
		"$legacy_temperature_topic" \
		"$dwh_temperature_topic" \
		"$silent_topic" \
		"$mode_topic" \
		"$legacy_mode_topic"
	do
		cmd+=(-t "$topic")
	done

	"${cmd[@]}"
}

mqtt=$(setting mqttserver)
mqttuser=$(setting mqttuser)
mqttpass=$(setting mqttpass)
mqttport=$(setting mqttport)
name=$(setting hassname)

require_setting "$mqtt" "mqttserver"
require_setting "$mqttport" "mqttport"
require_setting "$name" "hassname"

temperature_topic="homeassistant/climate/${name}/temperature/set"
legacy_temperature_topic="homeassistant/sensor/${name}_settemp/state"
dwh_temperature_topic="homeassistant/sensor/${name}_setdwhtemp/state"
silent_topic="homeassistant/switch/${name}_silent/set"
mode_topic="homeassistant/climate/${name}/mode/set"
legacy_mode_topic="homeassistant/sensor/${name}_mode_set/state"

subscribe | while IFS= read -r line
do
	topic="${line%% *}"
	payload="${line#* }"

	case "$topic" in
		"$temperature_topic" | "$legacy_temperature_topic")
			if is_number "$payload"; then
				echo "Set heat temperature: $payload"
				set_temperature "$payload"
			fi
			;;
		"$dwh_temperature_topic")
			if is_number "$payload"; then
				echo "Set DWH temperature: $payload"
				set_dwh_temperature "$payload"
			fi
			;;
		"$silent_topic")
			if [[ -n "$payload" ]]; then
				echo "Set silent mode: $payload"
				set_silent "$payload"
			fi
			;;
		"$mode_topic" | "$legacy_mode_topic")
			case "$payload" in
				off|heat|cool|auto)
					echo "Set mode: $payload"
					set_mode "$payload"
					;;
			esac
			;;
	esac
done
