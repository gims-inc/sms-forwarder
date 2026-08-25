from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api.telemetry.config import TelemetryConfig


def telemetry_lifespan(app: FastAPI) -> None:
    config = TelemetryConfig()
    if not config.enabled:
        return

    if not getattr(app.state, "_sms_forwarder_telemetry_instrumented", False):
        app.state._sms_forwarder_telemetry_instrumented = True
        FastAPIInstrumentor.instrument_app(app)
        AsyncioInstrumentor().instrument()

    current_tracer_provider = trace.get_tracer_provider()
    if isinstance(current_tracer_provider, ProxyTracerProvider):
        resource = Resource.create({SERVICE_NAME: "sms-forwarder-service"})
        trace_provider = TracerProvider(resource=resource)
        trace_provider.add_span_processor(BatchSpanProcessor(config.get_trace_exporter()))
        trace.set_tracer_provider(trace_provider)

    current_meter_provider = metrics.get_meter_provider()
    if isinstance(current_meter_provider, ProxyMeterProvider):
        resource = Resource.create({SERVICE_NAME: "sms-forwarder-service"})
        metric_reader = PeriodicExportingMetricReader(config.get_metric_exporter())
        metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(metric_provider)
