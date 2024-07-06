import re
from pathlib import Path
from urllib.parse import urljoin
from uuid import UUID

from openinference.semconv.resource import ResourceAttributes
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix import TraceDataset
from phoenix.config import TRACE_DATASET_DIR, get_env_host, get_env_port

PHOENIX_DEFAULT_PORT = 6006

_TRACE_FILE_ID_REGEX = re.compile(r"trace_dataset-(?P<id>[a-fA-F0-9\-]{36}).parquet")


def is_port_in_use(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def is_phoenix_already_launched(port=None):
    """This actually only checks if the port 6006 is taken."""
    return is_port_in_use(port or PHOENIX_DEFAULT_PORT)


def get_id_of_most_recent_trace_file(trace_dir=TRACE_DATASET_DIR):
    trace_dir = Path(trace_dir)

    matching_files = [
        f
        for f in trace_dir.iterdir()
        if f.is_file() and _TRACE_FILE_ID_REGEX.search(f.name)
    ]

    if not matching_files:
        return None

    most_recent_file = max(matching_files, key=lambda f: f.stat().st_mtime)

    match = _TRACE_FILE_ID_REGEX.search(most_recent_file.name)
    if match:
        return match.group("id")
    else:
        return None


def maybe_load_trace_dataset(
    uuid: str | UUID | None = None, trace_dir=TRACE_DATASET_DIR
):
    if not uuid:
        uuid = get_id_of_most_recent_trace_file(trace_dir)
        if not uuid:
            return
    if isinstance(uuid, str):
        uuid = UUID(uuid)
    try:
        return TraceDataset.load(uuid, trace_dir)
    except FileNotFoundError:
        return


def save_trace_dataset(phoenix_client, trace_dir=TRACE_DATASET_DIR):
    tds = phoenix_client.get_trace_dataset()
    tds.save(directory=trace_dir)


def setup_trace_provider(project_name=None, port=None):
    if project_name:
        resource = Resource(attributes={ResourceAttributes.PROJECT_NAME: project_name})
    else:
        resource = Resource(attributes={})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    collector_endpoint = urljoin(
        f"http://{get_env_host()}:{port or get_env_port()}", "v1/traces"
    )
    span_exporter = OTLPSpanExporter(endpoint=collector_endpoint)
    simple_span_processor = SimpleSpanProcessor(span_exporter=span_exporter)
    trace.get_tracer_provider().add_span_processor(simple_span_processor)
