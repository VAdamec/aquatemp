#!/bin/bash
path=$(dirname "$0":)
mqtt=$(grep mqttserver "${path}"/settings | cut -f2)
mqttuser=`cat $path/settings | grep mqttuser | cut -f2`
mqttpass=`cat $path/settings | grep mqttpass | cut -f2`
mqttport=$(grep mqttport "${path}"/settings | cut -f2)
name=$(grep hassname "${path}"/settings | cut -f2)

check()
{
"${path}"/heatpump info
}

mosquitto_sub -v -R -h "${mqtt}" -p "${mqttport}" -u "$mqttuser" -P "$mqttpass" -t homeassistant/# | while read line
do
	settemp=$(echo "${line}" | perl -lne '/my_heatpump_settemp\/state\s([0-9]*)/ and print ${1}')
	mode=$(echo "${line}" | perl -lne '/my_heatpump_mode_set\/state\s([0-9]*)/ and print ${1}')
	silent=$(echo "${line}" | perl -lne '/my_heatpump_silent\/set\s(.*)/ and print ${1}')
	if [[ -n "${settemp}" ]]; then
		"${path}"/heatpump temp "${settemp}"
		check
	fi
	if [[ -n "${silent}" ]]; then
		"${path}"/heatpump silent "${silent}"
		check
	fi	
	if [[ -n $mode ]]; then
		echo "${line}"
		if [[ $mode = "off" ]]; then
			"${path}"/heatpump off
			check
		elif [[ $mode = "heat" ]]; then
			"${path}"/heatpump on
			"${path}"/heatpump mode heat
			check
		elif [[ $mode = "auto" ]]; then
			"${path}"/heatpump on
			"${path}"/heatpump mode auto
			check
		elif [[ $mode = "cool" ]]; then
			"${path}"/heatpump on
			"${path}"/heatpump mode cool
			check
		fi
	fi

done
