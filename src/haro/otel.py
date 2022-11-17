"""setup opentelemetry exporters and instrumentors

https://github.com/open-telemetry/opentelemetry-python/blob/e1a4c38/docs/examples/django/client.py
"""
import os


def setup(service_name, service_namespace, /, enable_console=False):
    # setup resource
    from opentelemetry.sdk import resources
    from setuptools_scm import get_version
    import sys
    resource = resources.Resource(attributes={
        # # https://opentelemetry.io/docs/reference/specification/resource/semantic_conventions/#service
        resources.SERVICE_NAME: service_name,
        resources.SERVICE_NAMESPACE: service_namespace,
        resources.SERVICE_VERSION: get_version(search_parent_directories=True),
        # https://opentelemetry.io/docs/reference/specification/resource/semantic_conventions/deployment_environment/
        resources.DEPLOYMENT_ENVIRONMENT: "haro-server",
        # https://opentelemetry.io/docs/reference/specification/resource/semantic_conventions/process/
        resources.PROCESS_RUNTIME_NAME: sys.implementation.name,
        resources.PROCESS_RUNTIME_VERSION: '.'.join(map(str, sys.implementation.version)),
        resources.PROCESS_RUNTIME_DESCRIPTION: sys.version,
        resources.PROCESS_COMMAND_ARGS: sys.argv,
    })

    setup_tracer(resource, enable_console=enable_console)
    setup_metric(resource, enable_console=enable_console)
    setup_logger(resource, enable_console=enable_console)
    setup_instrumentor()


def setup_tracer(resource, /, enable_console=False):
    """trace exporter

    https://github.com/open-telemetry/opentelemetry.io/blob/dfadc50/content/en/docs/instrumentation/python/exporters.md
    """
    from opentelemetry.trace import set_tracer_provider
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

    tracer_provider = TracerProvider(resource=resource)
    set_tracer_provider(tracer_provider)
    if enable_console:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
        tracer_provider.add_span_processor(
            SimpleSpanProcessor(ConsoleSpanExporter())
        )
    if (os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or
            os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")):
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter())
        )


def setup_metric(resource, /, enable_console=False):
    """metric exporter

    https://github.com/open-telemetry/opentelemetry.io/blob/dfadc50/content/en/docs/instrumentation/python/exporters.md
    https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples/metrics
    """
    from opentelemetry import metrics
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

    metric_readers = [
        PeriodicExportingMetricReader(OTLPMetricExporter()),
    ]
    if enable_console:
        metric_readers.append(
            PeriodicExportingMetricReader(ConsoleMetricExporter())
        )
    if (os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or
            os.environ.get("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")):
        metrics.set_meter_provider(
            MeterProvider(resource=resource, metric_readers=metric_readers)
        )


def setup_logger(resource, /, enable_console=False):
    """log exporter

    from https://github.com/open-telemetry/opentelemetry-python/blob/69c9e39/docs/examples/logs/example.py
    """
    from opentelemetry.sdk._logs import LoggerProvider, set_logger_provider
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    if enable_console:
        from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor, ConsoleLogExporter
        logger_provider.add_log_record_processor(
            SimpleLogRecordProcessor(ConsoleLogExporter())
        )
    if (os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") or
            os.environ.get("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")):
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter())
        )
    # and add 'opentelemetry.sdk._logs.LoggingHandler' handler


def setup_instrumentor():
    # requests instrumentation
    import opentelemetry.instrumentation.requests
    opentelemetry.instrumentation.requests.RequestsInstrumentor().instrument()
