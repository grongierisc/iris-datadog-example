# 1. IRIS DataDog Example
Demo showcasing InterSystems IRIS, Flask, Kafka and Postgres monitoring with DataDog.

![DataDog_macro excalidraw](https://user-images.githubusercontent.com/47849411/171481830-56d358de-79b5-41b3-8e38-b8de6df5a41d.png)

- [1. IRIS DataDog Example](#1-iris-datadog-example)
- [2. IRIS + Kafka](#2-iris--kafka)
- [3. Flask and Postgres](#3-flask-and-postgres)
- [4. Running the demo](#4-running-the-demo)
- [5. Demo DataDog](#5-demo-datadog)
  - [5.1. datadog-agent](#51-datadog-agent)
    - [5.1.1. Configrations](#511-configrations)
      - [5.1.1.1. Agent](#5111-agent)
      - [5.1.1.2. AutoDiscovery](#5112-autodiscovery)
    - [5.1.2. Datadog status](#512-datadog-status)
  - [5.2. datadog-agent-apm](#52-datadog-agent-apm)
    - [5.2.1. Configuration](#521-configuration)
      - [5.2.1.1. Agent](#5211-agent)
      - [5.2.1.2. Postgres](#5212-postgres)
      - [5.2.1.3. .Net Core](#5213-net-core)
      - [5.2.1.4. Java](#5214-java)
      - [5.2.1.5. Python Gateway](#5215-python-gateway)
    - [5.2.2. Python flask](#522-python-flask)
    - [5.2.3. Datadog status](#523-datadog-status)
- [6. What's inside](#6-whats-inside)
  - [6.1. UI](#61-ui)

# 2. IRIS + Kafka

IRIS is a database and a middleware, for this demo we mainly use it as a middleware. It makes use of PEX to manage an Kafka Produceur, an Kafka Consumer and a Python code to stimulate the Kafka Producer.

The Production EXtension (PEX) framework provides you with a choice of implementation languages when you are developing interoperability productions. Interoperability productions enable you to integrate systems with different message formats and communication protocols. If you are not familiar with interoperability productions, see [Introduction to Productions](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=EGIN_intro#EGIN_productions).

As of January 2022, PEX supports Python, Java, and .NET (C#) languages. PEX provides flexible connections between business services, processes, and operations that are implemented in PEX-supported languages or in InterSystems ObjectScript. In addition, you can use PEX to develop, inbound and outbound adapters. The PEX framework allows you to create an entire production in Pytohn or Java or .NET or to create a production that has a mix of Python, Java, .NET, or ObjectScript components. Once integrated, the production components written in Pytohn, Java, and .NET are called at runtime and use the PEX framework to send messages to other components in the production. 

# 3. Flask and Postgres

The flask API has two objectives:
1. To generate call loops between the consumer and the Kafka producer
2. Manage a simple crud on a postgres database


# 4. Running the demo

1. Install:
    - [docker](https://docs.docker.com/get-docker/)
    - [docker-compose](https://docs.docker.com/compose/install/)
    - [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. Execute:
```sh
git clone https://github.com/intersystems-community/pex-demo.git
cd iris-datadog-example
docker compose up -d
```

3. Run:
```sh
cd datadog
python3 stress_flask.py -1  
```

This will create a series of infinite calls to the Flask API with the following ordering:
1. Generate a loop of 10 Kafka Producer <-> Consumer calls
2. One Post to the crud API
3. Eight Get calls to the crud API

# 5. Demo DataDog

There are two datadog agents:
- datadog-agent : To monitor docker instances and their logs
- datadog-agent-apm : To monitor the code and the PostGres database

## 5.1. datadog-agent

The purpose of this agent is to monitor the OS part of the containers, in particular the CPU, RAM, Disk consumption as well as to read the logs in the standard output of the containers.

In addition, this agent is responsible for retrieving custom metrics from the IRIS instance which are in OpenTelemetry format.

For the more, it also gather the JMX information from the Kafka JVM.

### 5.1.1. Configrations

#### 5.1.1.1. Agent
The agent it self :

```yaml
 datadog-agent:
    # Using the JMX version to enable autodiscovery to fetch JVM info of Kafka and zookeeper
    image: gcr.io/datadoghq/agent:latest-jmx
    environment:
      # DataDog API Key
      DD_API_KEY: ${DD_API_KEY}
      # DataDog API (in this case EU)
      DD_SITE: ${DD_SITE}
      DD_HOSTNAME: dd-agent
      # APM disabled because another agent is handeling itt
      DD_APM_ENABLED: false
      # Consume logs
      DD_LOGS_ENABLED: true
      # Consume logs of all container
      DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL: true
    volumes:
      # Basic binding to add specific configs on top
      - ./datadog/datadog-agent/:/etc/datadog-agent/
      - ./datadog/datadog-agent/conf.d/:/etc/datadog-agent/conf.d
      - ./datadog/datadog-agent/checks.d/:/etc/datadog-agent/checks.d
      # Volumes bindings to read dockers metrics
      - /var/run/docker.sock:/var/run/docker.sock
      - /proc/:/host/proc/:ro
      - /sys/fs/cgroup:/host/sys/fs/cgroup:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
```

#### 5.1.1.2. AutoDiscovery

For Kafka and JMX
```yaml
    labels:
      com.datadoghq.ad.logs: '[{"source": "kafka", "service": "kafka"}]'
      com.datadoghq.ad.check_names: '["kafka"]'
      com.datadoghq.ad.init_configs: '[{"is_jmx": true}]'
      com.datadoghq.ad.instances: |
        [{"host": "%%host%%","port":"9999"}] 
```

For IRIS and opentelemetry :
```yaml
    labels:
      com.datadoghq.ad.check_names: '["openmetrics"]'
      com.datadoghq.ad.init_configs: '[{}]'
      com.datadoghq.ad.instances: |
        [
          {
            "openmetrics_endpoint": "http://%%host%%:52773/api/monitor/metrics",
            "namespace": "prometheus",
            "metrics" : [{"iris.*":{"type":"gauge"}}]
          }
        ] 
```

Postgres logs :
```yaml
    labels:
      com.datadoghq.ad.logs: '[{"source": "postgresql", "service": "postgres"}]'
```

### 5.1.2. Datadog status 

To get an overview of the monitored services, we can use the status command:

```sh
docker exec -it iris-datadog-example-datadog-agent-1 agent status
```

<details>
  <summary>Output</summary>
  
  ```text
===============
Agent (v7.36.1)
===============

  Status date: 2022-06-02 11:51:10.401 UTC (1654170670401)
  Agent start: 2022-06-02 11:33:43.583 UTC (1654169623583)
  Pid: 373
  Go Version: go1.17.6
  Python Version: 3.8.11
  Build arch: amd64
  Agent flavor: agent
  Check Runners: 5
  Log Level: info

  Paths
  =====
    Config File: /etc/datadog-agent/datadog.yaml
    conf.d: /etc/datadog-agent/conf.d
    checks.d: /etc/datadog-agent/checks.d

  Clocks
  ======
    System time: 2022-06-02 11:51:10.401 UTC (1654170670401)

  Host Info
  =========
    bootTime: 2022-05-31 15:55:49 UTC (1654012549000)
    hostId: 096c481b-0000-0000-8361-8a56977d1b08
    kernelArch: x86_64
    kernelVersion: 5.10.104-linuxkit
    os: linux
    platform: ubuntu
    platformFamily: debian
    platformVersion: 21.10
    procs: 272
    uptime: 43h38m10s
    virtualizationRole: guest

  Hostnames
  =========
    hostname: dd-agent
    socket-fqdn: df11aef1b1bb
    socket-hostname: df11aef1b1bb
    hostname provider: configuration

  Metadata
  ========
    agent_version: 7.36.1
    config_apm_dd_url: 
    config_dd_url: 
    config_logs_dd_url: 
    config_logs_socks5_proxy_address: 
    config_no_proxy: []
    config_process_dd_url: 
    config_proxy_http: 
    config_proxy_https: 
    config_site: 
    feature_apm_enabled: false
    feature_cspm_enabled: false
    feature_cws_enabled: false
    feature_logs_enabled: true
    feature_networks_enabled: false
    feature_networks_http_enabled: false
    feature_networks_https_enabled: false
    feature_otlp_enabled: false
    feature_process_enabled: false
    feature_processes_container_enabled: true
    flavor: agent
    hostname_source: configuration
    install_method_installer_version: 
    install_method_tool: undefined
    install_method_tool_version: 
    logs_transport: TCP

=========
Collector
=========

  Running Checks
  ==============
    
    openmetrics (2.1.0)
    -------------------
      Instance ID: openmetrics:prometheus:23fd56880c530fb5 [OK]
      Configuration Source: container:docker://60edd3e536cac0fdb325c610598ec9cce899a7f9be10834fcacbd7e149e85082
      Total Runs: 69
      Metric Samples: Last Run: 208, Total: 14,200
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 1, Total: 69
      Average Execution Time : 38ms
      Last Execution Date : 2022-06-02 11:50:59 UTC (1654170659000)
      Last Successful Execution Date : 2022-06-02 11:50:59 UTC (1654170659000)
      
========
JMXFetch
========

  Information
  ==================
    runtime_version : 11.0.15
    version : 0.46.0
  Initialized checks
  ==================
    kafka
      instance_name : kafka-172.31.0.11-9999
      message : <no value>
      metric_count : 27
      service_check_count : 0
      status : OK
  Failed checks
  =============
    no checks
    
=========
Forwarder
=========

  Transactions
  ============
    Cluster: 0
    ClusterRole: 0
    ClusterRoleBinding: 0
    CronJob: 0
    DaemonSet: 0
    Deployment: 0
    Dropped: 0
    HighPriorityQueueFull: 0
    Ingress: 0
    Job: 0
    Node: 0
    PersistentVolume: 0
    PersistentVolumeClaim: 0
    Pod: 0
    ReplicaSet: 0
    Requeued: 0
    Retried: 0
    RetryQueueSize: 0
    Role: 0
    RoleBinding: 0
    Service: 0
    ServiceAccount: 0
    StatefulSet: 0

  Transaction Successes
  =====================
    Total number: 146
    Successes By Endpoint:
      check_run_v1: 69
      intake: 6
      metadata_v1: 2
      series_v1: 69

  On-disk storage
  ===============
    On-disk storage is disabled. Configure `forwarder_storage_max_size_in_bytes` to enable it.

  API Keys status
  ===============
    API key ending with c2eaf: API Key valid

==========
Endpoints
==========
  https://app.datadoghq.eu - API Key ending with:
      - c2eaf

==========
Logs Agent
==========

    Reliable: Sending uncompressed logs in SSL encrypted TCP to agent-intake.logs.datadoghq.eu on port 443

    You are currently sending Logs to Datadog through TCP (either because logs_config.force_use_tcp or logs_config.socks5_proxy_address is set or the HTTP connectivity test has failed). To benefit from increased reliability and better network performances, we strongly encourage switching over to compressed HTTPS which is now the default protocol.

    BytesSent: 1.9284616e+07
    EncodedBytesSent: 1.9284616e+07
    LogsProcessed: 28473
    LogsSent: 28473

  container_collect_all
  ---------------------
    - Type: file
      Identifier: 5050e59831572ce12b9e4a980004a9993a6729118f36043f74f9b9b7752c44b3
      Path: /var/lib/docker/containers/5050e59831572ce12b9e4a980004a9993a6729118f36043f74f9b9b7752c44b3/5050e59831572ce12b9e4a980004a9993a6729118f36043f74f9b9b7752c44b3-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/5050e59831572ce12b9e4a980004a9993a6729118f36043f74f9b9b7752c44b3/5050e59831572ce12b9e4a980004a9993a6729118f36043f74f9b9b7752c44b3-json.log
      BytesRead: 26675
      Average Latency (ms): 6989
      24h Average Latency (ms): 6989
      Peak Latency (ms): 8056
      24h Peak Latency (ms): 8056
    - Type: file
      Identifier: 60edd3e536cac0fdb325c610598ec9cce899a7f9be10834fcacbd7e149e85082
      Path: /var/lib/docker/containers/60edd3e536cac0fdb325c610598ec9cce899a7f9be10834fcacbd7e149e85082/60edd3e536cac0fdb325c610598ec9cce899a7f9be10834fcacbd7e149e85082-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/60edd3e536cac0fdb325c610598ec9cce899a7f9be10834fcacbd7e149e85082/60edd3e536cac0fdb325c610598ec9cce899a7f9be10834fcacbd7e149e85082-json.log
      BytesRead: 32058
      Average Latency (ms): 7002
      24h Average Latency (ms): 7002
      Peak Latency (ms): 8044
      24h Peak Latency (ms): 8044
    - Type: file
      Identifier: 761bd9e6fd53279026b15af2db0177a9a94a35db04c453348a0525cf9b7a84d4
      Path: /var/lib/docker/containers/761bd9e6fd53279026b15af2db0177a9a94a35db04c453348a0525cf9b7a84d4/761bd9e6fd53279026b15af2db0177a9a94a35db04c453348a0525cf9b7a84d4-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/761bd9e6fd53279026b15af2db0177a9a94a35db04c453348a0525cf9b7a84d4/761bd9e6fd53279026b15af2db0177a9a94a35db04c453348a0525cf9b7a84d4-json.log
      BytesRead: 856
      Average Latency (ms): 3026
      24h Average Latency (ms): 3026
      Peak Latency (ms): 6040
      24h Peak Latency (ms): 6040
    - Type: file
      Identifier: adf7949997bcecd7539f38bdd140bef42d1eadd619aa2e85f6093868a4942130
      Path: /var/lib/docker/containers/adf7949997bcecd7539f38bdd140bef42d1eadd619aa2e85f6093868a4942130/adf7949997bcecd7539f38bdd140bef42d1eadd619aa2e85f6093868a4942130-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/adf7949997bcecd7539f38bdd140bef42d1eadd619aa2e85f6093868a4942130/adf7949997bcecd7539f38bdd140bef42d1eadd619aa2e85f6093868a4942130-json.log
      BytesRead: 1145
      Average Latency (ms): 0
      24h Average Latency (ms): 0
      Peak Latency (ms): 0
      24h Peak Latency (ms): 0
    - Type: file
      Identifier: b515693e7ea68b819116822906c3f0be12b32116b2fd9c1a81ea258d6c67bdf5
      Path: /var/lib/docker/containers/b515693e7ea68b819116822906c3f0be12b32116b2fd9c1a81ea258d6c67bdf5/b515693e7ea68b819116822906c3f0be12b32116b2fd9c1a81ea258d6c67bdf5-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/b515693e7ea68b819116822906c3f0be12b32116b2fd9c1a81ea258d6c67bdf5/b515693e7ea68b819116822906c3f0be12b32116b2fd9c1a81ea258d6c67bdf5-json.log
      BytesRead: 40399
      Average Latency (ms): 4845
      24h Average Latency (ms): 4845
      Peak Latency (ms): 7897
      24h Peak Latency (ms): 7897
    - Type: file
      Identifier: b9587f11c67bca228010a59f326966caaa3c10ff2a17e44af118a8b62c593a4f
      Path: /var/lib/docker/containers/b9587f11c67bca228010a59f326966caaa3c10ff2a17e44af118a8b62c593a4f/b9587f11c67bca228010a59f326966caaa3c10ff2a17e44af118a8b62c593a4f-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/b9587f11c67bca228010a59f326966caaa3c10ff2a17e44af118a8b62c593a4f/b9587f11c67bca228010a59f326966caaa3c10ff2a17e44af118a8b62c593a4f-json.log
      BytesRead: 6.622755e+06
      Average Latency (ms): 120
      24h Average Latency (ms): 120
      Peak Latency (ms): 7839
      24h Peak Latency (ms): 7839
    - Type: file
      Identifier: df11aef1b1bb41a23bd1b4a905a0f5f3f8f59c3ba457c8f7cc9f49855fcc7f22
      Path: /var/lib/docker/containers/df11aef1b1bb41a23bd1b4a905a0f5f3f8f59c3ba457c8f7cc9f49855fcc7f22/df11aef1b1bb41a23bd1b4a905a0f5f3f8f59c3ba457c8f7cc9f49855fcc7f22-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/df11aef1b1bb41a23bd1b4a905a0f5f3f8f59c3ba457c8f7cc9f49855fcc7f22/df11aef1b1bb41a23bd1b4a905a0f5f3f8f59c3ba457c8f7cc9f49855fcc7f22-json.log
      BytesRead: 88009
      Average Latency (ms): 4563
      24h Average Latency (ms): 4563
      Peak Latency (ms): 7776
      24h Peak Latency (ms): 7776
    - Type: file
      Identifier: f340cc56e0a98c30421fc001b4eb992da20c5fee963b41f9c8011c594af4c0cc
      Path: /var/lib/docker/containers/f340cc56e0a98c30421fc001b4eb992da20c5fee963b41f9c8011c594af4c0cc/f340cc56e0a98c30421fc001b4eb992da20c5fee963b41f9c8011c594af4c0cc-json.log
      Status: OK
      BytesRead: 0
      Average Latency (ms): 0
      24h Average Latency (ms): 0
      Peak Latency (ms): 0
      24h Peak Latency (ms): 0

  docker
  ------
    - Type: file
      Identifier: 88fcc861217fb1a58c2308321b6ad882a2d37b2dfade1db7d5fec98393b32f6c
      Path: /var/lib/docker/containers/88fcc861217fb1a58c2308321b6ad882a2d37b2dfade1db7d5fec98393b32f6c/88fcc861217fb1a58c2308321b6ad882a2d37b2dfade1db7d5fec98393b32f6c-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/88fcc861217fb1a58c2308321b6ad882a2d37b2dfade1db7d5fec98393b32f6c/88fcc861217fb1a58c2308321b6ad882a2d37b2dfade1db7d5fec98393b32f6c-json.log
      BytesRead: 7202
      Average Latency (ms): 364
      24h Average Latency (ms): 364
      Peak Latency (ms): 7889
      24h Peak Latency (ms): 7889
    - Type: file
      Identifier: 8a639e1ccc54987418c3ed37d72bf5b0ce6df6fb5041071df8f894ab6e434801
      Path: /var/lib/docker/containers/8a639e1ccc54987418c3ed37d72bf5b0ce6df6fb5041071df8f894ab6e434801/8a639e1ccc54987418c3ed37d72bf5b0ce6df6fb5041071df8f894ab6e434801-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/8a639e1ccc54987418c3ed37d72bf5b0ce6df6fb5041071df8f894ab6e434801/8a639e1ccc54987418c3ed37d72bf5b0ce6df6fb5041071df8f894ab6e434801-json.log
      BytesRead: 389602
      Average Latency (ms): 13
      24h Average Latency (ms): 13
      Peak Latency (ms): 7764
      24h Peak Latency (ms): 7764

=============
Process Agent
=============

  Version: 7.36.1
  Status date: 2022-06-02 11:51:22.972 UTC (1654170682972)
  Process Agent Start: 2022-06-02 11:33:45.146 UTC (1654169625146)
  Pid: 377
  Go Version: go1.17.6
  Build arch: amd64
  Log Level: info
  Enabled Checks: [container rtcontainer process_discovery]
  Allocated Memory: 17,363,160 bytes
  Hostname: dd-agent

  =================
  Process Endpoints
  =================
    https://process.datadoghq.eu - API Key ending with:
        - c2eaf

  =========
  Collector
  =========
    Last collection time: 2022-06-02 11:51:17
    Docker socket: /var/run/docker.sock
    Number of processes: 0
    Number of containers: 10
    Process Queue length: 0
    RTProcess Queue length: 0
    Pod Queue length: 0
    Process Bytes enqueued: 0
    RTProcess Bytes enqueued: 0
    Pod Bytes enqueued: 0

=========
APM Agent
=========
  Status: Not running or unreachable on localhost:8126.
  Error: Get "http://localhost:8126/debug/vars": dial tcp 127.0.0.1:8126: connect: connection refused

=========
Aggregator
=========
  Checks Metric Sample: 14,338
  Dogstatsd Metric Sample: 4,638
  Event: 1
  Events Flushed: 1
  Number Of Flushes: 69
  Series Flushed: 18,106
  Service Check: 207
  Service Checks Flushed: 275
=========
DogStatsD
=========
  Event Packets: 0
  Event Parse Errors: 0
  Metric Packets: 4,637
  Metric Parse Errors: 0
  Service Check Packets: 69
  Service Check Parse Errors: 0
  Udp Bytes: 727,241
  Udp Packet Reading Errors: 0
  Udp Packets: 1,769
  Uds Bytes: 0
  Uds Origin Detection Errors: 0
  Uds Packet Reading Errors: 0
  Uds Packets: 0
  Unterminated Metric Errors: 0

=============
Autodiscovery
=============
  Enabled Features
  ================
    docker
  ```
  
</details>


## 5.2. datadog-agent-apm

This agent is there to monitor the performance of the code in interaction with the eco-system.

In this demo, three languages are used and one database (postgres):

- Python
  - Flask
  - Python Gateway
- .Net Core 2.1
- Java 1.8

### 5.2.1. Configuration

#### 5.2.1.1. Agent
The agent it self :

```yaml
  datadog-agent-apm:
    image: gcr.io/datadoghq/agent:latest
    ports:
      # Port used for APM
      - 8126:8126
    environment:
      DD_API_KEY: ${DD_API_KEY}
      DD_SITE: ${DD_SITE}
      DD_HOSTNAME: dd-apm-agent
      # Enable Application Performance Monitoring
      DD_APM_ENABLED: true
      DD_APM_NON_LOCAL_TRAFFIC: true
      DD_ENV: ${DD_ENV}
    volumes:
      - ./datadog/datadog-agent-apm/:/etc/datadog-agent/
      - ./datadog/datadog-agent-apm/conf.d/:/etc/datadog-agent/conf.d
      - ./datadog/datadog-agent-apm/checks.d/:/etc/datadog-agent/checks.d
```

#### 5.2.1.2. Postgres
To gather application metrics from postgres, we use this config file :

```yaml
init_config:

instances:
  - host: db
    port: 5432
    username: postgres
    password: postgres
```

This file is mount to the container at `/etc/datadog-agent/conf.d/postgres.d/` from `datadog/datadog-agent-apm/conf.d/postgres.d`

#### 5.2.1.3. .Net Core

For .Net core APM we use this config in the docker compose :

```yaml
    environment: 
      - DOTNET_GATEWAY
      - DD_ENV=${DD_ENV} 
      - DD_SERVICE=netgw
      - DD_VERSION=1.0.0 
      - DD_AGENT_HOST=datadog-agent-apm 
      - DD_TRACE_AGENT_PORT=8126 
      - DD_LOGS_INJECTION=true 
      - DD_TRACE_DEBUG=true
```
The configured nuget is here in `dotnet/KafkaConsumer.csproj`

```xml
    <PackageReference Include="Datadog.Monitoring.Distribution" Version="2.9.0-beta01" />
```

To enable APM on the .Net Core side, we have to modify the dockerfile with this :

```dockerfile
# Enable Datadog automatic instrumentation
# App is being copied to /app, so Datadog assets are at /app/datadog
ENV CORECLR_ENABLE_PROFILING=1
ENV CORECLR_PROFILER={846F5F1C-F9AE-4B07-969E-05C26BC060D8}
ENV CORECLR_PROFILER_PATH=/app/datadog/linux-x64/Datadog.Trace.ClrProfiler.Native.so
ENV DD_DOTNET_TRACER_HOME=/app/datadog

# Run the createLogPath script on Linux to ensure the automatic instrumentation logs are genereated without permission isues
RUN /app/datadog/createLogPath.sh
```
#### 5.2.1.4. Java

The configuration for Java is in two parts :

Download the dd-java-agent.jar with the dockerfile :

```dockerfile
ADD https://dtdg.co/latest-java-tracer dd-java-agent.jar
```

Configure the docker-compose to enable the datadog agent on the JVMARGS:

```yaml
      - JVMARGS=-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 -javaagent:/jgw/dd-java-agent.jar 
      - DD_ENV=${DD_ENV} 
      - DD_SERVICE=jgw
      - DD_VERSION=1.0.0 
      - DD_AGENT_HOST=datadog-agent-apm 
      - DD_TRACE_AGENT_PORT=8126 
      - DD_LOGS_INJECTION=true 
      - DD_TRACE_DEBUG=true
```

#### 5.2.1.5. Python Gateway

APM by default handle only standards libraries.

This is ok for .Net and Java because they used APM supported libraries (Confluent.Kafka for Consumer .Net and apache kafka-clients for java Producer).
- .Net integration : https://docs.datadoghq.com/tracing/setup_overview/compatibility_requirements/dotnet-core#integrations
- Java integration : https://docs.datadoghq.com/tracing/setup_overview/compatibility_requirements/java/#networking-framework-compatibility

For the Python code, none of the supported librairies by APM are used.

So we will use custom trace.

To do so :

Add ddtrace module to the image :

```dockerfile
RUN python -m pip install --upgrade ${GWLIBDIR}/*.whl ddtrace
```

Then import tracer to your code :

```python
from ddtrace import patch_all,tracer
patch_all()
```

Decorate the traced function :

```python
    @tracer.wrap()
    def OnInit(self):
        logging.info("[Python] ...KafkaProcess:OnInit() is called")
        return
```

### 5.2.2. Python flask

APM on python flask is easier than python gateway because python flask, sqlachemy and psycopg2 are supported librairies from dd-agent :
- https://docs.datadoghq.com/tracing/setup_overview/compatibility_requirements/python/#inetgrations

docker-compose :

```yaml
      - DD_ENV=${DD_ENV} 
      - DD_SERVICE=flask
      - DD_VERSION=1.0.0 
      - DD_AGENT_HOST=datadog-agent-apm 
      - DD_TRACE_AGENT_PORT=8126 
      - DD_LOGS_INJECTION=true 
      - DD_TRACE_DEBUG=true
```

dd-trace before gunicorn :

```dockerfile
CMD ["ddtrace-run", "gunicorn", "--conf", "gunicorn_conf.py", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

### 5.2.3. Datadog status 

To get an overview of the monitored services, we can use the status command:

```sh
docker exec -it iris-datadog-example-datadog-agent-apm-1 agent status
```

<details>
  <summary>Output</summary>
  
  ```text
===============
Agent (v7.36.0)
===============

  Status date: 2022-06-02 11:54:07.358 UTC (1654170847358)
  Agent start: 2022-06-02 11:33:44.019 UTC (1654169624019)
  Pid: 377
  Go Version: go1.17.6
  Python Version: 3.8.11
  Build arch: amd64
  Agent flavor: agent
  Check Runners: 4
  Log Level: info

  Paths
  =====
    Config File: /etc/datadog-agent/datadog.yaml
    conf.d: /etc/datadog-agent/conf.d
    checks.d: /etc/datadog-agent/checks.d

  Clocks
  ======
    System time: 2022-06-02 11:54:07.358 UTC (1654170847358)

  Host Info
  =========
    bootTime: 2022-05-31 15:55:49 UTC (1654012549000)
    hostId: 096c481b-0000-0000-8361-8a56977d1b08
    kernelArch: x86_64
    kernelVersion: 5.10.104-linuxkit
    os: linux
    platform: ubuntu
    platformFamily: debian
    platformVersion: 21.10
    procs: 11
    uptime: 43h38m5s
    virtualizationRole: guest

  Hostnames
  =========
    hostname: dd-apm-agent
    socket-fqdn: b515693e7ea6
    socket-hostname: b515693e7ea6
    host tags:
      env:demo
    hostname provider: configuration

  Metadata
  ========
    agent_version: 7.36.0
    config_apm_dd_url: 
    config_dd_url: 
    config_logs_dd_url: 
    config_logs_socks5_proxy_address: 
    config_no_proxy: []
    config_process_dd_url: 
    config_proxy_http: 
    config_proxy_https: 
    config_site: 
    feature_apm_enabled: true
    feature_cspm_enabled: false
    feature_cws_enabled: false
    feature_logs_enabled: false
    feature_networks_enabled: false
    feature_networks_http_enabled: false
    feature_networks_https_enabled: false
    feature_otlp_enabled: false
    feature_process_enabled: false
    feature_processes_container_enabled: true
    flavor: agent
    hostname_source: configuration
    install_method_installer_version: 
    install_method_tool: undefined
    install_method_tool_version: 

=========
Collector
=========

  Running Checks
  ==============
    
    postgres (12.3.2)
    -----------------
      Instance ID: postgres:5b8fbda465015d85 [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/postgres.d/conf.yaml
      Total Runs: 82
      Metric Samples: Last Run: 30, Total: 2,460
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 1, Total: 82
      Average Execution Time : 21ms
      Last Execution Date : 2022-06-02 11:54:06 UTC (1654170846000)
      Last Successful Execution Date : 2022-06-02 11:54:06 UTC (1654170846000)
      metadata:
        version.major: 12
        version.minor: 11
        version.patch: 0
        version.raw: 12.11 (Debian 12.11-1.pgdg110+1)
        version.scheme: semver
      
========
JMXFetch
========

  Information
  ==================
  Initialized checks
  ==================
    no checks
    
  Failed checks
  =============
    no checks
    
=========
Forwarder
=========

  Transactions
  ============
    Cluster: 0
    ClusterRole: 0
    ClusterRoleBinding: 0
    CronJob: 0
    DaemonSet: 0
    Deployment: 0
    Dropped: 0
    HighPriorityQueueFull: 0
    Ingress: 0
    Job: 0
    Node: 0
    PersistentVolume: 0
    PersistentVolumeClaim: 0
    Pod: 0
    ReplicaSet: 0
    Requeued: 0
    Retried: 0
    RetryQueueSize: 0
    Role: 0
    RoleBinding: 0
    Service: 0
    ServiceAccount: 0
    StatefulSet: 0

  Transaction Successes
  =====================
    Total number: 172
    Successes By Endpoint:
      check_run_v1: 81
      intake: 8
      metadata_v1: 2
      series_v1: 81

  On-disk storage
  ===============
    On-disk storage is disabled. Configure `forwarder_storage_max_size_in_bytes` to enable it.

  API Keys status
  ===============
    API key ending with c2eaf: API Key valid

==========
Endpoints
==========
  https://app.datadoghq.eu - API Key ending with:
      - c2eaf

==========
Logs Agent
==========


  Logs Agent is not running

=============
Process Agent
=============

  Version: 7.36.0
  Status date: 2022-06-02 11:54:15.896 UTC (1654170855896)
  Process Agent Start: 2022-06-02 11:33:46.644 UTC (1654169626644)
  Pid: 385
  Go Version: go1.17.6
  Build arch: amd64
  Log Level: info
  Enabled Checks: [process_discovery]
  Allocated Memory: 10,818,632 bytes
  Hostname: dd-apm-agent

  =================
  Process Endpoints
  =================
    https://process.datadoghq.eu - API Key ending with:
        - c2eaf

  =========
  Collector
  =========
    Last collection time: 2022-06-02 11:33:46
    Docker socket: 
    Number of processes: 0
    Number of containers: 0
    Process Queue length: 0
    RTProcess Queue length: 0
    Pod Queue length: 0
    Process Bytes enqueued: 0
    RTProcess Bytes enqueued: 0
    Pod Bytes enqueued: 0

=========
APM Agent
=========
  Status: Running
  Pid: 378
  Uptime: 1232 seconds
  Mem alloc: 9,985,472 bytes
  Hostname: dd-apm-agent
  Receiver: 0.0.0.0:8126
  Endpoints:
    https://trace.agent.datadoghq.eu

  Receiver (previous minute)
  ==========================
    No traces received in the previous minute.
    Default priority sampling rate: 2.7%
    Priority sampling rate for 'service:flask,env:': 21.2%
    Priority sampling rate for 'service:flask,env:demo': 21.2%
    Priority sampling rate for 'service:kafka,env:': 12.3%
    Priority sampling rate for 'service:kafka,env:demo': 12.3%
    Priority sampling rate for 'service:netgw-kafka,env:': 12.7%
    Priority sampling rate for 'service:netgw-kafka,env:demo': 12.7%
    Priority sampling rate for 'service:pygw,env:': 2.7%
    Priority sampling rate for 'service:pygw,env:demo': 2.7%

  Writer (previous minute)
  ========================
    Traces: 0 payloads, 0 traces, 0 events, 0 bytes
    Stats: 0 payloads, 0 stats buckets, 0 bytes

=========
Aggregator
=========
  Checks Metric Sample: 2,624
  Dogstatsd Metric Sample: 21,410
  Event: 1
  Events Flushed: 1
  Number Of Flushes: 81
  Series Flushed: 17,200
  Service Check: 164
  Service Checks Flushed: 243
=========
DogStatsD
=========
  Event Packets: 0
  Event Parse Errors: 0
  Metric Packets: 21,409
  Metric Parse Errors: 0
  Service Check Packets: 0
  Service Check Parse Errors: 0
  Udp Bytes: 2,599,987
  Udp Packet Reading Errors: 0
  Udp Packets: 11,015
  Uds Bytes: 0
  Uds Origin Detection Errors: 0
  Uds Packet Reading Errors: 0
  Uds Packets: 0
  Unterminated Metric Errors: 0
  ```
</details>
  
</details>


# 6. What's inside

## 6.1. UI

- InterSystems IRIS: `http://localhost:52773/csp/user/EnsPortal.ProductionConfig.zen`
- Flask API: 
  - Kafka loop : `http://localhost:5000/kafka`
  - Crud : `http://localhost:5000/items`



