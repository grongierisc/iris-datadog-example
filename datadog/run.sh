#!/bin/bash

docker run -d --cgroupns host \
            -v /var/run/docker.sock:/var/run/docker.sock:ro \
            -v /proc/:/host/proc/:ro \
            -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
            -v /etc/passwd:/etc/passwd:ro \
            -e DD_SYSTEM_PROBE_ENABLED=true \
            -e DD_PROCESS_AGENT_ENABLED=true \
            -e DD_API_KEY="81948d9a5ad70e30ec46fe69b3cc2eaf" \
            -e DD_SITE="datadoghq.eu" \
            -e DD_LOG_LEVEL="debug" \
            -e DD_LOGS_ENABLED=true \
            -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true \
            -e DD_CONTAINER_EXCLUDE="name:datadog-agent" \
            --network pex-demo_default \
            --name datadog-agent-docker \
            gcr.io/datadoghq/agent:latest 
            