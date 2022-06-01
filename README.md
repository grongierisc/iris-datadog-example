# IRIS DataDog Example
Demo showcasing InterSystems IRIS, Flask, Kafka and Postgres monitoring with DataDog.

![DataDog_macro excalidraw](https://user-images.githubusercontent.com/47849411/171481830-56d358de-79b5-41b3-8e38-b8de6df5a41d.png)

# IRIS

IRIS is a database and a middleware, for this demo we mainly use it as a middleware. It makes use of PEX to manage an Kafka Produceur, an Kafka Consumer and a Python code to stimulate the Kafka Producer.

The Production EXtension (PEX) framework provides you with a choice of implementation languages when you are developing interoperability productions. Interoperability productions enable you to integrate systems with different message formats and communication protocols. If you are not familiar with interoperability productions, see [Introduction to Productions](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=EGIN_intro#EGIN_productions).

As of January 2022, PEX supports Python, Java, and .NET (C#) languages. PEX provides flexible connections between business services, processes, and operations that are implemented in PEX-supported languages or in InterSystems ObjectScript. In addition, you can use PEX to develop, inbound and outbound adapters. The PEX framework allows you to create an entire production in Pytohn or Java or .NET or to create a production that has a mix of Python, Java, .NET, or ObjectScript components. Once integrated, the production components written in Pytohn, Java, and .NET are called at runtime and use the PEX framework to send messages to other components in the production. 

# Flask and Postgres

The flask API has two objectives:
1. To generate call loops between the consumer and the Kafka producer
2. Manage a simple crud on a postgres database


# Running the demo

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
2. Two Post to the crud API
3. Seven Get calls to the crud API

# Demo DataDog

There are two datadog agents:
- datadog-agent : To monitor docker instances and their logs
- datadog-agent-apm : To monitor the code and the PostGres database

## datadog-agent

The purpose of this agent is to monitor the OS part of the containers, in particular the CPU, RAM, Disk consumption as well as to read the logs in the standard output of the containers.

In addition, this agent is responsible for retrieving custom metrics from the IRIS instance which are in OpenTelemetry format.

For the more, it also gather the JMX information from the Kafka JVM.

### Configrations

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

AutoDiscovery :

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



# What's inside

## UI

- InterSystems IRIS: `http://localhost:52773/csp/user/EnsPortal.ProductionConfig.zen`
- Flask API: 
  - Kafka loop : `http://localhost:5000/kafka`
  - Crud : `http://localhost:5000/items`



