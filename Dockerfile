ARG BUILD_FROM
FROM $BUILD_FROM

# Install curl and the MQTT client tools
RUN apk add --no-cache curl mosquitto-clients

# Copy your scripts and config into the container
COPY run_loop.sh monitor.sh config.conf /

# Make the scripts executable
RUN chmod +x /run_loop.sh /monitor.sh

# This defines the command that will be run when the container starts
CMD ["/bin/bash", "/run_loop.sh"]
