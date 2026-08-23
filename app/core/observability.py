from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider


def configure_observability(service_name: str = "ai-job-agent") -> None:
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    logging.getLogger(__name__).info("OpenTelemetry initialized for %s", service_name)


def tracer():
    return trace.get_tracer("ai-job-agent")
