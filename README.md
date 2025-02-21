# aquatemp

Bash scripts for integration of AquaTemp wifi module to Home Assistant using mqtt autodiscovery

requirement of mosquitto_pub and mosquitto_sub and jq
(sudo apt-get install mosquitto-clients jq)

first run

1.	edit settings file for your needs
2.	./heatpump install
3.	add control.sh and status.sh to systemd
	(you could use the script "setup_systemd install" to add and enable the service "ubuntu"
	the service name will be aquatemp_control and aquatemp_status)

uninstall

1.	./heatpump uninstall (removes the entities from Home Assistant)
2.	remove control.sh and status.sh from systemd
	(you could use the script "setup_systemd uninstall" to remove and disable the service "ubuntu")


Poll intervall for the app is 20s, so i recommend to not set this to lower value than 20s 

# Warmlink update
- API calls from iOS app wireshark data, object camelcased, different auth URI

## TODO
- No idea about password hash mechanism yes - hash taken from wireshark and use as a password in settings
- Some parameters doesn't exists, there are others which are not covered yet
- Changing temperature not solved 

![plot](./example.png)

