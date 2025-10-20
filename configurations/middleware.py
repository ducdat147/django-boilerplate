import json
import logging

from opentelemetry import trace

from configurations.hooks import add_event
from configurations.logging import sanitize_data

logger = logging.getLogger(__name__)


class TracingMiddleware:
    """
    Middleware to log POST data for debugging purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.tracer = trace.get_tracer(__name__)

    def __call__(self, request):
        span = trace.get_current_span()
        try:
            if request.method in ["POST", "PUT", "PATCH"] and bool(request.body):
                if getattr(request, "content_type", "").startswith("application/json"):
                    body = json.loads(request.body.decode("utf-8"))
                    body = sanitize_data(body)
                else:
                    body = sanitize_data(request.POST)
                add_event(
                    span,
                    attributes={
                        "log.severity": "INFO",
                        "request.body": json.dumps(body),
                    },
                )
            if request.method == "GET" and hasattr(request, "GET") and request.GET:
                params = sanitize_data(request.GET)
                add_event(
                    span,
                    attributes={
                        "log.severity": "INFO",
                        "request.queryparams": json.dumps(params),
                    },
                )
            response = self.get_response(request)
            response_data = sanitize_data(getattr(response, "data", None))
            if response_data:
                add_event(
                    span,
                    attributes={
                        "log.severity": "INFO",
                        "response.body": json.dumps(response_data),
                    },
                )
            trace_id_dec = span.get_span_context().trace_id
            response["X-Trace-ID"] = hex(trace_id_dec).replace("0x", "")
            return response
        except Exception as e:
            logger.exception(e)
        response = self.get_response(request)
        trace_id_dec = span.get_span_context().trace_id
        response["X-Trace-ID"] = hex(trace_id_dec).replace("0x", "")
        return response
