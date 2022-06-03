# 1. IRIS DataDog Example
Demo showcasing InterSystems IRIS, Flask, Kafka and Postgres monitoring with DataDog.

# 2. Achitecture
![image](https://user-images.githubusercontent.com/47849411/171857687-2b212a98-1062-49ec-84a7-d25cdf5b4408.png)

- [1. IRIS DataDog Example](#1-iris-datadog-example)
- [2. Achitecture](#2-achitecture)
  - [2.1. IRIS + Kafka](#21-iris--kafka)
  - [2.2. Flask and Postgres](#22-flask-and-postgres)
- [3. Running the demo](#3-running-the-demo)
- [4. Datadog Monitoring](#4-datadog-monitoring)
  - [4.1. Datadog Agent](#41-datadog-agent)
    - [4.1.1. Configuration](#411-configuration)
    - [4.1.2. Result :](#412-result-)
      - [4.1.2.1. Infrastructure Map :](#4121-infrastructure-map-)
      - [4.1.2.2. Container Overview dashboard](#4122-container-overview-dashboard)
      - [4.1.2.3. Docker Dashboard](#4123-docker-dashboard)
  - [4.2. Kafka](#42-kafka)
    - [4.2.1. Configuration](#421-configuration)
    - [4.2.2. Result](#422-result)
  - [4.3. IRIS](#43-iris)
    - [4.3.1. Configuration](#431-configuration)
    - [4.3.2. Result](#432-result)
  - [4.4. Postgres](#44-postgres)
    - [4.4.1. Configuration](#441-configuration)
    - [4.4.2. Result](#442-result)
  - [4.5. .Net Core](#45-net-core)
    - [4.5.1. Configuration](#451-configuration)
    - [4.5.2. Result](#452-result)
  - [4.6. Java](#46-java)
    - [4.6.1. Configuration](#461-configuration)
    - [4.6.2. Result](#462-result)
  - [4.7. Python Gateway](#47-python-gateway)
    - [4.7.1. Configuration](#471-configuration)
    - [4.7.2. Result](#472-result)
  - [4.8. APM](#48-apm)
    - [4.8.1. Service Map](#481-service-map)
    - [4.8.2. Custom Dashboard](#482-custom-dashboard)
  - [4.9. Python flask](#49-python-flask)
    - [4.9.1. Configuration](#491-configuration)
    - [4.9.2. Result](#492-result)
  - [4.10. Datadog status](#410-datadog-status)
- [5. What's inside](#5-whats-inside)
  - [5.1. UI](#51-ui)

## 2.1. IRIS + Kafka

IRIS is a database and a middleware, for this demo we mainly use it as a middleware. It makes use of PEX to manage an Kafka Produceur, an Kafka Consumer and a Python code to stimulate the Kafka Producer.

The Production EXtension (PEX) framework provides you with a choice of implementation languages when you are developing interoperability productions. Interoperability productions enable you to integrate systems with different message formats and communication protocols. If you are not familiar with interoperability productions, see [Introduction to Productions](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=EGIN_intro#EGIN_productions).

As of January 2022, PEX supports Python, Java, and .NET (C#) languages. PEX provides flexible connections between business services, processes, and operations that are implemented in PEX-supported languages or in InterSystems ObjectScript. In addition, you can use PEX to develop, inbound and outbound adapters. The PEX framework allows you to create an entire production in Pytohn or Java or .NET or to create a production that has a mix of Python, Java, .NET, or ObjectScript components. Once integrated, the production components written in Pytohn, Java, and .NET are called at runtime and use the PEX framework to send messages to other components in the production. 

## 2.2. Flask and Postgres

The flask API has two objectives:
1. To generate call loops between the consumer and the Kafka producer
2. Manage a simple crud on a postgres database


# 3. Running the demo

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

# 4. Datadog Monitoring

## 4.1. Datadog Agent

The purpose of this agent is to monitor the OS part of the containers, in particular the CPU, RAM, Disk consumption as well as to read the logs in the standard output of the containers.

In addition, this agent is responsible for retrieving custom metrics from the IRIS instance which are in OpenTelemetry format.

For the more, it also gather the JMX information from the Kafka JVM.

This agent is there to monitor the performance of the code in interaction with the eco-system.

In this demo, three languages are used and one database (postgres):

- Python
  - Flask
  - Python Gateway
- .Net Core 2.1
- Java 1.8

### 4.1.1. Configuration
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
      DD_HOSTNAME: datadog-agent-docker
      # Enable Application Performance Monitoring
      DD_APM_ENABLED: true
      DD_APM_NON_LOCAL_TRAFFIC: true
      # Consume logs
      DD_LOGS_ENABLED: true
      # Consume logs of all container
      DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL: true
      DD_PROCESS_AGENT_ENABLED: true 
    volumes:
      # Basic binding to add specific configs for postgres
      - ./datadog/datadog-agent/conf.d/postgres.d:/etc/datadog-agent/conf.d/postgres.d
      # binding to host to handle dd-agent stop
      - ./datadog/datadog-agent/run:/opt/datadog-agent/run
      # Volumes bindings to read dockers metrics
      - /var/run/docker.sock:/var/run/docker.sock 
      - /proc/:/host/proc/:ro 
      - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro 
      - /var/lib/docker/containers:/var/lib/docker/containers:ro 
      - /etc/passwd:/etc/passwd:ro
```

### 4.1.2. Result :

#### 4.1.2.1. Infrastructure Map :

<img width="1404" alt="image" src="https://user-images.githubusercontent.com/47849411/171635910-aabc0bcb-c49f-44a8-97c0-07d1d2d63b4a.png">

#### 4.1.2.2. Container Overview dashboard

<img width="1404" alt="image" src="https://user-images.githubusercontent.com/47849411/171858778-e50f14f2-9d3f-40c7-8994-10d8efedfcc2.png">

#### 4.1.2.3. Docker Dashboard

<img width="1404" alt="image" src="https://user-images.githubusercontent.com/47849411/171858983-d145af9e-235e-452f-8ff0-9ea54e789408.png">

## 4.2. Kafka 

### 4.2.1. Configuration

The kafka configuration is made with autodiscovery and labels annotations on docker-compose :

```yaml
    labels:
      com.datadoghq.ad.logs: '[{"source": "kafka", "service": "kafka"}]'
      com.datadoghq.ad.check_names: '["kafka"]'
      com.datadoghq.ad.init_configs: '[{"is_jmx": true}]'
      com.datadoghq.ad.instances: |
        [{"host": "%%host%%","port":"9999"}] 
```

### 4.2.2. Result 

<img width="581" alt="image" src="https://user-images.githubusercontent.com/47849411/171859262-6286f4f5-0694-4e54-9f92-2e535bff4f2b.png">

## 4.3. IRIS

### 4.3.1. Configuration

IRIS is compatible with OpenTelemetry, we use autodiscovery to gather thoses customes metrics

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

### 4.3.2. Result 

<img width="708" alt="image" src="https://user-images.githubusercontent.com/47849411/171859565-f6e1da6e-f666-46c4-a64e-9772698899da.png">

<img width="1410" alt="image" src="https://user-images.githubusercontent.com/47849411/171859716-ca8be424-29c6-4a05-8b98-0c226083f999.png">

## 4.4. Postgres

### 4.4.1. Configuration 

Logs are gather thow audodiscovery.

Postgres logs :
```yaml
    labels:
      com.datadoghq.ad.logs: '[{"source": "postgresql", "service": "postgres"}]'
```

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


### 4.4.2. Result 

<img width="1410" alt="image" src="https://user-images.githubusercontent.com/47849411/171859869-85806d6d-cf97-4bea-9cff-5ab825fce34d.png">

## 4.5. .Net Core

### 4.5.1. Configuration

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

### 4.5.2. Result

<img width="873" alt="image" src="https://user-images.githubusercontent.com/47849411/171862710-ce1aebdb-c8d6-480c-9d96-523a379f8797.png">

## 4.6. Java

### 4.6.1. Configuration

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

### 4.6.2. Result

<img width="962" alt="image" src="https://user-images.githubusercontent.com/47849411/171862881-b0f40f28-9995-447c-9ef9-dd2b69335ac8.png">

## 4.7. Python Gateway

### 4.7.1. Configuration

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
### 4.7.2. Result

<img width="979" alt="image" src="https://user-images.githubusercontent.com/47849411/171863090-9e8bca2d-3bd2-414b-a663-a318c149c5ef.png">

## 4.8. APM

### 4.8.1. Service Map

<img width="1314" alt="image" src="https://user-images.githubusercontent.com/47849411/171863282-8c5def95-8a18-45c0-9f1e-589268075743.png">

### 4.8.2. Custom Dashboard

<img width="1255" alt="image" src="https://user-images.githubusercontent.com/47849411/171863536-38f21b42-3ffe-488d-b83e-028ac381d17b.png">



## 4.9. Python flask

### 4.9.1. Configuration

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

### 4.9.2. Result

<img width="1255" alt="image" src="https://user-images.githubusercontent.com/47849411/171864080-7a2a7c9d-25c0-495c-a9b7-543d3bdc3307.png">

## 4.10. Datadog status 

To get an overview of the monitored services, we can use the status command:

```sh
docker exec -it iris-datadog-example-datadog-agent-docker-1 agent status
```

<details>
  <summary>Output</summary>
  
  ```text
===============
Agent (v7.36.1)
===============

  Status date: 2022-06-03 13:09:59.441 UTC (1654261799441)
  Agent start: 2022-06-03 12:41:48.906 UTC (1654260108906)
  Pid: 381
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
    NTP offset: 94.037ms
    System time: 2022-06-03 13:09:59.441 UTC (1654261799441)

  Host Info
  =========
    bootTime: 2022-06-01 05:43:51 UTC (1654062231000)
    hostId: 096c481b-0000-0000-8361-8a56977d1b08
    kernelArch: x86_64
    kernelVersion: 5.10.104-linuxkit
    os: linux
    platform: ubuntu
    platformFamily: debian
    platformVersion: 21.10
    procs: 250
    uptime: 54h58m15s
    virtualizationRole: guest

  Hostnames
  =========
    hostname: datadog-agent-docker
    socket-fqdn: 4ca25cead439
    socket-hostname: 4ca25cead439
    host tags:
      env:demo
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
    feature_apm_enabled: true
    feature_cspm_enabled: false
    feature_cws_enabled: false
    feature_logs_enabled: true
    feature_networks_enabled: false
    feature_networks_http_enabled: false
    feature_networks_https_enabled: false
    feature_otlp_enabled: false
    feature_process_enabled: true
    feature_processes_container_enabled: false
    flavor: agent
    hostname_source: configuration
    install_method_installer_version: docker
    install_method_tool: docker
    install_method_tool_version: docker
    logs_transport: TCP

=========
Collector
=========

  Running Checks
  ==============
    
    container
    ---------
      Instance ID: container [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/container.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 266, Total: 29,708
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 20ms
      Last Execution Date : 2022-06-03 13:09:53 UTC (1654261793000)
      Last Successful Execution Date : 2022-06-03 13:09:53 UTC (1654261793000)
      
    
    cpu
    ---
      Instance ID: cpu [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/cpu.d/conf.yaml.default
      Total Runs: 111
      Metric Samples: Last Run: 9, Total: 992
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 0s
      Last Execution Date : 2022-06-03 13:09:45 UTC (1654261785000)
      Last Successful Execution Date : 2022-06-03 13:09:45 UTC (1654261785000)
      
    
    disk (4.7.0)
    ------------
      Instance ID: disk:e5dffb8bef24336f [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/disk.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 320, Total: 35,840
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 77ms
      Last Execution Date : 2022-06-03 13:09:52 UTC (1654261792000)
      Last Successful Execution Date : 2022-06-03 13:09:52 UTC (1654261792000)
      
    
    docker
    ------
      Instance ID: docker [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/docker.d/conf.yaml.default
      Total Runs: 111
      Metric Samples: Last Run: 61, Total: 6,771
      Events: Last Run: 1, Total: 12
      Service Checks: Last Run: 1, Total: 111
      Average Execution Time : 149ms
      Last Execution Date : 2022-06-03 13:09:44 UTC (1654261784000)
      Last Successful Execution Date : 2022-06-03 13:09:44 UTC (1654261784000)
      
    
    file_handle
    -----------
      Instance ID: file_handle [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/file_handle.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 5, Total: 560
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 0s
      Last Execution Date : 2022-06-03 13:09:51 UTC (1654261791000)
      Last Successful Execution Date : 2022-06-03 13:09:51 UTC (1654261791000)
      
    
    io
    --
      Instance ID: io [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/io.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 28, Total: 3,118
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 0s
      Last Execution Date : 2022-06-03 13:09:58 UTC (1654261798000)
      Last Successful Execution Date : 2022-06-03 13:09:58 UTC (1654261798000)
      
    
    load
    ----
      Instance ID: load [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/load.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 6, Total: 672
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 0s
      Last Execution Date : 2022-06-03 13:09:50 UTC (1654261790000)
      Last Successful Execution Date : 2022-06-03 13:09:50 UTC (1654261790000)
      
    
    memory
    ------
      Instance ID: memory [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/memory.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 20, Total: 2,240
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 0s
      Last Execution Date : 2022-06-03 13:09:57 UTC (1654261797000)
      Last Successful Execution Date : 2022-06-03 13:09:57 UTC (1654261797000)
      
    
    network (2.7.0)
    ---------------
      Instance ID: network:d884b5186b651429 [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/network.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 198, Total: 22,176
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 12ms
      Last Execution Date : 2022-06-03 13:09:49 UTC (1654261789000)
      Last Successful Execution Date : 2022-06-03 13:09:49 UTC (1654261789000)
      
    
    ntp
    ---
      Instance ID: ntp:d884b5186b651429 [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/ntp.d/conf.yaml.default
      Total Runs: 2
      Metric Samples: Last Run: 1, Total: 2
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 1, Total: 2
      Average Execution Time : 32.419s
      Last Execution Date : 2022-06-03 12:57:34 UTC (1654261054000)
      Last Successful Execution Date : 2022-06-03 12:57:34 UTC (1654261054000)
      
    
    openmetrics (2.1.0)
    -------------------
      Instance ID: openmetrics:prometheus:da1df6e06f18515a [OK]
      Configuration Source: container:docker://65e7f799bc858fc07d740f6a24f2285c7cf400943c52ae79d03feaa8d26541ab
      Total Runs: 111
      Metric Samples: Last Run: 211, Total: 23,413
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 1, Total: 111
      Average Execution Time : 57ms
      Last Execution Date : 2022-06-03 13:09:48 UTC (1654261788000)
      Last Successful Execution Date : 2022-06-03 13:09:48 UTC (1654261788000)
      
    
    postgres (12.3.2)
    -----------------
      Instance ID: postgres:5b8fbda465015d85 [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/postgres.d/conf.yaml
      Total Runs: 112
      Metric Samples: Last Run: 30, Total: 3,360
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 1, Total: 112
      Average Execution Time : 25ms
      Last Execution Date : 2022-06-03 13:09:46 UTC (1654261786000)
      Last Successful Execution Date : 2022-06-03 13:09:46 UTC (1654261786000)
      metadata:
        version.major: 12
        version.minor: 11
        version.patch: 0
        version.raw: 12.11 (Debian 12.11-1.pgdg110+1)
        version.scheme: semver
      
    
    uptime
    ------
      Instance ID: uptime [OK]
      Configuration Source: file:/etc/datadog-agent/conf.d/uptime.d/conf.yaml.default
      Total Runs: 112
      Metric Samples: Last Run: 1, Total: 112
      Events: Last Run: 0, Total: 0
      Service Checks: Last Run: 0, Total: 0
      Average Execution Time : 0s
      Last Execution Date : 2022-06-03 13:09:56 UTC (1654261796000)
      Last Successful Execution Date : 2022-06-03 13:09:56 UTC (1654261796000)
      
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
      instance_name : kafka-172.29.0.10-9999
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
    Total number: 240
    Successes By Endpoint:
      check_run_v1: 112
      intake: 13
      metadata_v1: 3
      series_v1: 112

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

    BytesSent: 8.3937665e+07
    EncodedBytesSent: 8.3937665e+07
    LogsProcessed: 120010
    LogsSent: 120010

  container_collect_all
  ---------------------
    - Type: file
      Identifier: 1019069586dee544f213b694de7fe298d3475beb5a2a6a3d763f32fd02f94ad6
      Path: /var/lib/docker/containers/1019069586dee544f213b694de7fe298d3475beb5a2a6a3d763f32fd02f94ad6/1019069586dee544f213b694de7fe298d3475beb5a2a6a3d763f32fd02f94ad6-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/1019069586dee544f213b694de7fe298d3475beb5a2a6a3d763f32fd02f94ad6/1019069586dee544f213b694de7fe298d3475beb5a2a6a3d763f32fd02f94ad6-json.log
      BytesRead: 1.0368136e+07
      Average Latency (ms): 29
      24h Average Latency (ms): 29
      Peak Latency (ms): 8098
      24h Peak Latency (ms): 8098
    - Type: file
      Identifier: 4ca25cead4391da5e1ee82d0693fe1c51906576a4d9097c9d51da9ce5cc4b73e
      Path: /var/lib/docker/containers/4ca25cead4391da5e1ee82d0693fe1c51906576a4d9097c9d51da9ce5cc4b73e/4ca25cead4391da5e1ee82d0693fe1c51906576a4d9097c9d51da9ce5cc4b73e-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/4ca25cead4391da5e1ee82d0693fe1c51906576a4d9097c9d51da9ce5cc4b73e/4ca25cead4391da5e1ee82d0693fe1c51906576a4d9097c9d51da9ce5cc4b73e-json.log
      BytesRead: 171050
      Average Latency (ms): 2138
      24h Average Latency (ms): 2138
      Peak Latency (ms): 8081
      24h Peak Latency (ms): 8081
    - Type: file
      Identifier: 5d17f23fe9344b8aa5d55e342f8a6fe9e43a4a713bb575c8d83f9de6b4e2ea0f
      Path: /var/lib/docker/containers/5d17f23fe9344b8aa5d55e342f8a6fe9e43a4a713bb575c8d83f9de6b4e2ea0f/5d17f23fe9344b8aa5d55e342f8a6fe9e43a4a713bb575c8d83f9de6b4e2ea0f-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/5d17f23fe9344b8aa5d55e342f8a6fe9e43a4a713bb575c8d83f9de6b4e2ea0f/5d17f23fe9344b8aa5d55e342f8a6fe9e43a4a713bb575c8d83f9de6b4e2ea0f-json.log
      BytesRead: 26667
      Average Latency (ms): 6998
      24h Average Latency (ms): 6998
      Peak Latency (ms): 8065
      24h Peak Latency (ms): 8065
    - Type: file
      Identifier: 64aaa501f95d1765ed566441e6fb0bfd795733b196e2f34cbc7dd48ceb331d7f
      Path: /var/lib/docker/containers/64aaa501f95d1765ed566441e6fb0bfd795733b196e2f34cbc7dd48ceb331d7f/64aaa501f95d1765ed566441e6fb0bfd795733b196e2f34cbc7dd48ceb331d7f-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/64aaa501f95d1765ed566441e6fb0bfd795733b196e2f34cbc7dd48ceb331d7f/64aaa501f95d1765ed566441e6fb0bfd795733b196e2f34cbc7dd48ceb331d7f-json.log
      BytesRead: 856
      Average Latency (ms): 0
      24h Average Latency (ms): 0
      Peak Latency (ms): 0
      24h Peak Latency (ms): 0
    - Type: file
      Identifier: 65e7f799bc858fc07d740f6a24f2285c7cf400943c52ae79d03feaa8d26541ab
      Path: /var/lib/docker/containers/65e7f799bc858fc07d740f6a24f2285c7cf400943c52ae79d03feaa8d26541ab/65e7f799bc858fc07d740f6a24f2285c7cf400943c52ae79d03feaa8d26541ab-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/65e7f799bc858fc07d740f6a24f2285c7cf400943c52ae79d03feaa8d26541ab/65e7f799bc858fc07d740f6a24f2285c7cf400943c52ae79d03feaa8d26541ab-json.log
      BytesRead: 32880
      Average Latency (ms): 107
      24h Average Latency (ms): 107
      Peak Latency (ms): 8056
      24h Peak Latency (ms): 8056
    - Type: file
      Identifier: af78a090992c11b2eab4e7efe163abb7030c1407a3f63d1b34c39a11cee83a2b
      Path: /var/lib/docker/containers/af78a090992c11b2eab4e7efe163abb7030c1407a3f63d1b34c39a11cee83a2b/af78a090992c11b2eab4e7efe163abb7030c1407a3f63d1b34c39a11cee83a2b-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/af78a090992c11b2eab4e7efe163abb7030c1407a3f63d1b34c39a11cee83a2b/af78a090992c11b2eab4e7efe163abb7030c1407a3f63d1b34c39a11cee83a2b-json.log
      BytesRead: 2.9546076e+07
      Average Latency (ms): 6
      24h Average Latency (ms): 6
      Peak Latency (ms): 8009
      24h Peak Latency (ms): 8009
    - Type: file
      Identifier: d6f050386db0451f014913a4526939b46983a1927d782db6c46627eec1500254
      Path: /var/lib/docker/containers/d6f050386db0451f014913a4526939b46983a1927d782db6c46627eec1500254/d6f050386db0451f014913a4526939b46983a1927d782db6c46627eec1500254-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/d6f050386db0451f014913a4526939b46983a1927d782db6c46627eec1500254/d6f050386db0451f014913a4526939b46983a1927d782db6c46627eec1500254-json.log
      BytesRead: 1149
      Average Latency (ms): 7946
      24h Average Latency (ms): 7946
      Peak Latency (ms): 7946
      24h Peak Latency (ms): 7946

  docker
  ------
    - Type: file
      Identifier: f82bafd510c090a3908de66bde401e1555d69a6f2414ead8ceb73e973dda1024
      Path: /var/lib/docker/containers/f82bafd510c090a3908de66bde401e1555d69a6f2414ead8ceb73e973dda1024/f82bafd510c090a3908de66bde401e1555d69a6f2414ead8ceb73e973dda1024-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/f82bafd510c090a3908de66bde401e1555d69a6f2414ead8ceb73e973dda1024/f82bafd510c090a3908de66bde401e1555d69a6f2414ead8ceb73e973dda1024-json.log
      BytesRead: 392185
      Average Latency (ms): 930
      24h Average Latency (ms): 930
      Peak Latency (ms): 7910
      24h Peak Latency (ms): 7910
    - Type: file
      Identifier: 355e65ea8010ccf2097c98b7627895bf796072022210bbb6c14663018b732990
      Path: /var/lib/docker/containers/355e65ea8010ccf2097c98b7627895bf796072022210bbb6c14663018b732990/355e65ea8010ccf2097c98b7627895bf796072022210bbb6c14663018b732990-json.log
      Status: OK
      Inputs:
        /var/lib/docker/containers/355e65ea8010ccf2097c98b7627895bf796072022210bbb6c14663018b732990/355e65ea8010ccf2097c98b7627895bf796072022210bbb6c14663018b732990-json.log
      BytesRead: 7431
      Average Latency (ms): 380
      24h Average Latency (ms): 380
      Peak Latency (ms): 7888
      24h Peak Latency (ms): 7888

=============
Process Agent
=============

  Version: 7.36.1
  Status date: 2022-06-03 13:10:04.83 UTC (1654261804830)
  Process Agent Start: 2022-06-03 12:41:50.158 UTC (1654260110158)
  Pid: 375
  Go Version: go1.17.6
  Build arch: amd64
  Log Level: info
  Enabled Checks: [process rtprocess]
  Allocated Memory: 18,900,728 bytes
  Hostname: datadog-agent-docker

  =================
  Process Endpoints
  =================
    https://process.datadoghq.eu - API Key ending with:
        - c2eaf

  =========
  Collector
  =========
    Last collection time: 2022-06-03 13:10:03
    Docker socket: /var/run/docker.sock
    Number of processes: 136
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
  Status: Running
  Pid: 374
  Uptime: 1697 seconds
  Mem alloc: 14,159,808 bytes
  Hostname: datadog-agent-docker
  Receiver: 0.0.0.0:8126
  Endpoints:
    https://trace.agent.datadoghq.eu

  Receiver (previous minute)
  ==========================
    From java 1.8.0_312 (OpenJDK 64-Bit Server VM), client 0.102.0~b67f6e3380
      Traces received: 766 (310,301 bytes)
      Spans received: 766
      
    From .NET 2.1.30 (.NET Core), client 2.9.0.0
      Traces received: 775 (375,450 bytes)
      Spans received: 775
      
    From python 3.9.13 (CPython), client 1.1.4
      Traces received: 1728 (4,629,012 bytes)
      Spans received: 19633
      
    From python 3.8.13 (CPython), client 1.1.4
      Traces received: 3415 (1,163,013 bytes)
      Spans received: 3415
      
    Default priority sampling rate: 4.9%
    Priority sampling rate for 'service:flask,env:': 9.9%
    Priority sampling rate for 'service:flask,env:demo': 9.9%
    Priority sampling rate for 'service:kafka,env:': 21.6%
    Priority sampling rate for 'service:kafka,env:demo': 21.6%
    Priority sampling rate for 'service:netgw-kafka,env:': 21.9%
    Priority sampling rate for 'service:netgw-kafka,env:demo': 21.9%
    Priority sampling rate for 'service:pygw,env:': 4.9%
    Priority sampling rate for 'service:pygw,env:demo': 4.9%

  Writer (previous minute)
  ========================
    Traces: 0 payloads, 0 traces, 0 events, 0 bytes
    Stats: 0 payloads, 0 stats buckets, 0 bytes

=========
Aggregator
=========
  Checks Metric Sample: 150,547
  Dogstatsd Metric Sample: 62,262
  Event: 13
  Events Flushed: 13
  Number Of Flushes: 112
  Series Flushed: 170,325
  Service Check: 1,791
  Service Checks Flushed: 1,896
=========
DogStatsD
=========
  Event Packets: 0
  Event Parse Errors: 0
  Metric Packets: 62,261
  Metric Parse Errors: 0
  Service Check Packets: 112
  Service Check Parse Errors: 0
  Udp Bytes: 9,955,281
  Udp Packet Reading Errors: 0
  Udp Packets: 27,763
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


# 5. What's inside

## 5.1. UI

- InterSystems IRIS: `http://localhost:52773/csp/user/EnsPortal.ProductionConfig.zen`
- Flask API: 
  - Kafka loop : `http://localhost:5000/kafka`
  - Crud : `http://localhost:5000/items`



