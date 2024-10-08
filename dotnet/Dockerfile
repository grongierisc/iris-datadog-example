ARG IRIS_IMAGE
FROM ${IRIS_IMAGE} AS iris

FROM mcr.microsoft.com/dotnet/core/sdk:2.1 AS build

ENV DOTNET_CLI_TELEMETRY_OPTOUT 1
ENV ISC_PACKAGE_INSTALLDIR /usr/irissys
ENV GWLIBDIR /source/lib
ENV ISC_LIBDIR ${ISC_PACKAGE_INSTALLDIR}/dev/dotnet/bin/Core21

WORKDIR /source
COPY --from=iris $ISC_LIBDIR/*.* $GWLIBDIR/

# copy csproj and restore as distinct layers
COPY *.csproj ./

# copy and publish app and libraries
COPY . .
RUN dotnet publish -c release -o /app

# final stage/image
FROM mcr.microsoft.com/dotnet/core/runtime:2.1

WORKDIR /app
COPY --from=build /app ./

# Configs to start the Gateway Server
RUN cp KafkaConsumer.runtimeconfig.json IRISGatewayCore21.runtimeconfig.json && \
    cp KafkaConsumer.deps.json IRISGatewayCore21.deps.json

# Enable Datadog automatic instrumentation
# App is being copied to /app, so Datadog assets are at /app/datadog
ENV CORECLR_ENABLE_PROFILING=1
ENV CORECLR_PROFILER={846F5F1C-F9AE-4B07-969E-05C26BC060D8}
ENV CORECLR_PROFILER_PATH=/app/datadog/linux-x64/Datadog.Trace.ClrProfiler.Native.so
ENV DD_DOTNET_TRACER_HOME=/app/datadog

# Run the createLogPath script on Linux to ensure the automatic instrumentation logs are genereated without permission isues
RUN /app/datadog/createLogPath.sh

CMD dotnet IRISGatewayCore21.dll ${DOTNET_GATEWAY} "" "" 0.0.0.0 "" 2>&1