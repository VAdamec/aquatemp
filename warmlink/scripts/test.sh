#!/bin/bash
#
# bash test.sh login pass
# just test login, get some data and test temperature setup
# bash, curl and jq is needed
#

cloudurl="https://cloud.linked-go.com:449/crmservice/api/app"
login=$1
pass=$(echo -n "${2}" | openssl dgst -md5 | awk '{print $2}')

token=$(curl -s -H "Content-Type: application/json; charset=utf-8" -X POST \
  -d '{"password": "'$pass'","loginSource": "IOS","areaCode": "en","appId": "16","type": "2","userName": "'$login'"}' \
  "${cloudurl}/user/login?lang=en" | jq -r '.objectResult."x-token"')

device=$(curl -s -H "Content-Type: application/json; charset=utf-8" \
	-H "x-token: ${token}" -X POST "${cloudurl}/device/deviceList?lang=en" |
	jq -r '.objectResult[]."device_code"')

echo "heatPump ID: ${device}"

curl -s -H "Content-Type: application/json; charset=utf-8" \
	-H "x-token: ${token}" \
	-d '{"appId":"16","deviceCode":"'${device}'"}' \
	-X POST "${cloudurl}/device/getDeviceStatus?lang=en" > tmp/status

curl -s -H "Content-Type: application/json; charset=utf-8" \
	-H "x-token: ${token}" \
	-d '{"deviceCode": "'${device}'","appId": "16","protocalCodes": ["Power", "Mode", "ModeState", "O01~014", "O01~023", "H21", "R01", "R02", "R03", "T39", "T04", "T01", "T08", "T09", "T02", "H25", "H28", "H31", "H22", "hanControl", "R08", "R09", "R10", "R11", "R36", "R37", "R70", "R71", "R72", "R73", "R74", "H01", "H05", "MainBoard Version", "code_version", "R35", "H07", "H10", "H18", "H20", "H27", "H29", "H30", "H32", "H33", "H35", "H36", "H37", "H40", "H41", "H42", "H43", "H45", "A03", "A04", "A05", "A06", "A11", "A21", "A22", "A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A32", "A33", "A34", "A35", "A38", "A39", "A40", "F01", "F02", "F03", "F05", "F06", "F10", "F18", "F19", "F21", "F22", "F23", "F25", "F26", "F27", "F28", "F29", "D01", "D02", "D03", "D04", "D05-1", "D05-2", "D07", "D08", "D09", "D10", "D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24", "D25", "D26", "D30", "E01", "E02", "E03", "E07", "E08", "E09", "E10", "E13", "E14", "E17", "E18", "E19", "E03-1", "E03-2", "E03-3", "E03-4", "E03-5", "E07-1", "E07-2", "E07-3", "E07-4", "E07-5", "R04", "R05", "R06", "R07", "R15", "R16", "R17", "R29", "R30", "R31", "R32", "R33", "R34", "R39", "R40", "R41", "R42", "R43", "R44", "R45", "R46", "R60", "R61", "R62", "P01", "P02", "P03", "P05", "P06", "P08", "P09", "P10", "P11", "P12", "P13", "P14", "P15", "P16", "G01", "G02", "G03", "G04", "G05", "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "O15", "O17", "S01~S10", "T03", "T05", "T06", "T07", "T13", "T15", "T10", "T11", "T12", "T27", "T28", "T29", "T30", "T31", "T32", "T33", "T34", "T35", "T36", "T37", "T38", "T40", "T41", "T42", "T43", "T44", "T46", "T47", "T48", "Fault1", "Fault5", "Fault6", "1250", "1256", "1257", "1258", "1259", "1260", "1261", "1262", "1263", "1264", "1265", "1266", "1267", "1268", "1269", "KG1", "KG2", "KG3", "KG4", "KG5", "KG6", "KG7", "KG8", "KG9", "KG10", "KG11", "KG12", "KG13~KG28", "KG29~KG44", "KG45~KG60", "Timer_Mute_On_En", "TimerMuteOnHour", "TimerMuteOnMinute", "Timer_Mute_Off_En", "TimerMuteOffHour", "TimerMuteOffMinute", "2014", "compensate_slope", "compensate_offset", "InputCurrent1", "Z01", "Z17", "Zone 2 Water Target", "Zone 2 Cure Slope", "Zone 2 Curve Offset", "Zone 1 Room Temp", "Zone 2 Room Temp", "Zone 2 Mixing Temp", "Z02", "Z03", "Z05", "Z06", "Z04", "Z07", "Z08", "Z09", "Z10", "Z11", "Z12", "Z13", "Z14", "Z15", "Z19", "Z20", "M1 Start", "M1 End", "M2 Start", "M2 End", "M3 Start", "M3 End", "M4 Start", "M4 End", "M5 Start", "M5 End", "M6 Start", "M6 End", "M1_2 Enalbe", "M3_4 Enalbe", "M5_6 Enalbe", "M1 Mode", "M2 Mode", "M3 Mode", "M4 Mode", "M5 Mode", "M6 Mode", "M1 Hot Water Target", "M1 Heating Target", "M1 Cooling Target", "M2 Hot Water Target", "M2 Heating Target", "M2 Cooling Target", "M3 Hot Water Target", "M3 Heating Target", "M3 Cooling Target", "M4 Hot Water Target", "M4 Heating Target", "M4 Cooling Target", "M5 Hot Water Target", "M5 Heating Target", "M5 Cooling Target", "M6 Hot Water Target", "M6 Heating Target", "M6 Cooling Target", "M1 Max. Power", "M2 Max. Power", "M3 Max. Power", "M4 Max. Power", "M5 Max. Power", "M6 Max. Power", "SG01", "SG Status", "SG02", "SG03", "SG04", "SG05", "SG06", "SG07", "SG08"]}' \
	-X POST "${cloudurl}/device/getDataByCode?lang=en" > tmp/info

power=`cat tmp/info | jq '.objectResult[] | select(.code=="Power")' | jq -r '.value'`
readtemp=`cat tmp/info | jq '.objectResult[] | select(.code=="Set_Temp")' | jq -r '.value'`

inlettemp=`cat tmp/info | jq '.objectResult[] | select(.code=="T02")' | jq -r '.value'`
outlettemp=`cat tmp/info | jq '.objectResult[] | select(.code=="T03")' | jq -r '.value'`
coiltemp=`cat tmp/info | jq '.objectResult[] | select(.code=="T04")' | jq -r '.value'`
ambienttemp=`cat tmp/info | jq '.objectResult[] | select(.code=="T05")' | jq -r '.value'`

mode=`cat tmp/info | jq '.objectResult[] | select(.code=="Mode")' | jq -r '.value'`

echo "
-----------------------
HeatPump mode: ${mode}
Power: ${power}
-----------------------
---- Temperature ${readtemp} ------
Inlet/outlet: ${inlettemp} / ${outlettemp}
Coil/ambient: ${coiltemp}  / ${ambienttemp}
"

# Set temp to 35
SetTemp=$(curl -s -H "Content-Type: application/json; charset=utf-8" \
	-H "x-token: ${token}" \
	  -d '{"appId": "16","param":[{"deviceCode":"'$device'","protocolCode":"R02","value":"20"}]}' \
    -X POST "${cloudurl}/device/control?lang=en" > tmp/temp_status)

# Show set response
jq -r . tmp/temp_status
