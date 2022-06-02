#!/bin/bash

source .env

docker run -d --cgroupns host \
            -p 8125:8125/udp \
            -p 8126:8126 \
            -v $PWD/datadog/datadog-agent/conf.d:/etc/datadog-agent/conf.d \
            -v $PWD/datadog/datadog-agent/checks.d:/etc/datadog-agent/checks.d \
            -v $PWD/datadog/datadog-agent/run:/opt/datadog-agent/run:rw \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v /proc/:/host/proc/:ro \
            -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
            -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
            -v /etc/passwd:/etc/passwd:ro \
            -e DD_PROCESS_AGENT_ENABLED=true \
            -e DD_API_KEY="${DD_API_KEY}" \
            -e DD_SITE="${DD_SITE}" \
            -e DD_ENV="${DD_ENV}" \
            -e DD_HOSTNAME="iris-datadog-example" \
            -e DD_APM_ENABLED=true \
            -e DD_CONTAINER_EXCLUDE="name:datadog-agent-docker" \
            -e DD_APM_NON_LOCAL_TRAFFIC=true \
            -e DD_LOGS_ENABLED=true \
            -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true \
            --network datadog-example \
            --name datadog-agent-docker \
            gcr.io/datadoghq/agent:latest-jmx
