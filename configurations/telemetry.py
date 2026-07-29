import logging
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_NAME,
    SERVICE_VERSION,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

from configurations.hooks import (
    django_request_hook,
    django_response_hook,
    log_hook,
    request_hook,
    response_hook,
)


def init_instrumentation(tracer_provider: TracerProvider, meter_provider: MeterProvider, is_service: bool = False):
    LoggingInstrumentor().instrument(
        set_logging_format=True,
        log_level=logging.INFO,
        tracer_provider=tracer_provider,
        log_hook=log_hook,
    )
    RequestsInstrumentor().instrument(
        request_hook=request_hook,
        response_hook=response_hook,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
    )
    ThreadingInstrumentor().instrument(tracer_provider=tracer_provider)
    CeleryInstrumentor().instrument(tracer_provider=tracer_provider, meter_provider=meter_provider)
    if is_service:
        DjangoInstrumentor().instrument(
            request_hook=django_request_hook,
            response_hook=django_response_hook,
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
            is_sql_commentor_enabled=True,
        )


def init_telemetry(is_service: bool = False, **kwargs):
    """
    Variables:
    - otlp_endpoint: str, endpoint for OTLP exporter
    - is_service: bool, whether this is a service application
    - service_name: str, name of the service (default: "prisvio")
    """
    resource = Resource.create(
        {
            DEPLOYMENT_ENVIRONMENT: os.getenv("DEPLOYMENT_ENVIRONMENT", "production"),
            SERVICE_NAME: kwargs.get("service_name", os.getenv("OTEL_SERVICE_NAME", "prisvio")),
            SERVICE_VERSION: "1.0.0",
        }
    )

    otlp_endpoint = kwargs.get("otlp_endpoint", os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", default=None))
    if not (otlp_endpoint and isinstance(otlp_endpoint, str)):
        return

    tracer_provider = TracerProvider(
        resource=resource,
        sampler=ALWAYS_ON,
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=otlp_endpoint))],
    )
    metrics.set_meter_provider(meter_provider)

    init_instrumentation(tracer_provider=tracer_provider, meter_provider=meter_provider, is_service=is_service)
