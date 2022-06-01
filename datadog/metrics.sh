#!/bin/bash

docker run -d --cgroupns host \
            -v /var/run/docker.sock:/var/run/docker.sock:ro \
            -v /proc/:/host/proc/:ro \
            -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
            -e DD_API_KEY="81948d9a5ad70e30ec46fe69b3cc2eaf" \
            -e DD_SITE="datadoghq.eu" \
            -e DD_LOG_LEVEL="debug" \
            -e DD_CONTAINER_EXCLUDE="name:datadog-agent" \
            --network datadog-example \
            --name datadog-agent-metrics \
            gcr.io/datadoghq/agent:7
            