from types import SimpleNamespace

from fastapi import FastAPI
from opentelemetry.metrics import ProxyMeterProvider
from opentelemetry.trace import ProxyTracerProvider

from api.telemetry import lifespan as telemetry_module


class _FakeSpanProcessor:
    def __init__(self, *_args, **_kwargs):
        pass


class _FakeTraceProvider:
    def __init__(self, *args, **kwargs):
        self._processors = []

    def add_span_processor(self, *_args, **_kwargs):
        self._processors.append(_FakeSpanProcessor())


class _FakeMetricProvider:
    def __init__(self, *args, **kwargs):
        pass


def test_should_only_configure_telemetry_once(monkeypatch):
    app = FastAPI()

    trace_calls = []
    meter_calls = []

    monkeypatch.setattr(
        telemetry_module,
        "TelemetryConfig",
        lambda: SimpleNamespace(enabled=True, get_trace_exporter=lambda: object(), get_metric_exporter=lambda: object()),
    )
    monkeypatch.setattr(telemetry_module, "Resource", SimpleNamespace(create=lambda *_args, **_kwargs: object()))
    monkeypatch.setattr(telemetry_module, "TracerProvider", _FakeTraceProvider)
    monkeypatch.setattr(telemetry_module, "MeterProvider", _FakeMetricProvider)
    monkeypatch.setattr(telemetry_module, "BatchSpanProcessor", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        telemetry_module,
        "PeriodicExportingMetricReader",
        lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(
        telemetry_module,
        "trace",
        SimpleNamespace(
            get_tracer_provider=lambda: ProxyTracerProvider(),
            set_tracer_provider=lambda provider: trace_calls.append(provider),
        ),
    )
    monkeypatch.setattr(
        telemetry_module,
        "metrics",
        SimpleNamespace(
            get_meter_provider=lambda: ProxyMeterProvider(),
            set_meter_provider=lambda provider: meter_calls.append(provider),
        ),
    )
    monkeypatch.setattr(
        telemetry_module,
        "FastAPIInstrumentor",
        SimpleNamespace(instrument_app=lambda *_args, **_kwargs: None),
    )
    monkeypatch.setattr(
        telemetry_module,
        "AsyncioInstrumentor",
        lambda: SimpleNamespace(instrument=lambda: None),
    )

    telemetry_module.telemetry_lifespan(app)
    telemetry_module.telemetry_lifespan(app)

    assert len(trace_calls) == 1
    assert len(meter_calls) == 1
    assert app.state._sms_forwarder_telemetry_instrumented is True
