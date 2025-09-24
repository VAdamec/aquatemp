ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache curl mosquitto-clients jq
COPY scripts/ /
RUN chmod +x /run_loop.sh /monitor.sh

CMD ["/bin/bash", "/run_loop.sh"]