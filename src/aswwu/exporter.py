# exporter.py

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Define the service name resource
resource = Resource(attributes={
    SERVICE_NAME: f"python_server_{os.environ.get('ENVIRONMENT')}"  # Replace with your actual service name
})

# Create a TracerProvider with the defined resource
provider = TracerProvider(resource=resource)

# Configure the OTLP/HTTP Span Exporter with necessary headers and endpoint
otlp_exporter = OTLPSpanExporter(
    endpoint="https://api.axiom.co/v1/traces",
    headers={
        "Authorization": f"Bearer {os.environ.get('AXIOM_TOKEN')}",
        "X-Axiom-Dataset": "python_server"    # Replace with your dataset name
    }
)

# Create a BatchSpanProcessor with the OTLP exporter
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)

# Set the TracerProvider as the global tracer provider
trace.set_tracer_provider(provider)

# Define a tracer for external use
tracer = trace.get_tracer("python_server")