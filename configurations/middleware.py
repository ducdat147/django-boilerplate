# -*- coding: utf-8 -*-
import json
import logging

from opentelemetry import trace

from .logging import sanitize_data

logger = logging.getLogger(__name__)


class TracingMiddleware:
    """
    Middleware to log POST data for debugging purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.tracer = trace.get_tracer(__name__)

    def __call__(self, request):
        try:
            span = trace.get_current_span()
            if request.method in ["POST", "PUT", "PATCH"]:
                body = json.loads(request.body.decode("utf-8"))
                body = sanitize_data(body)
                logger.info(json.dumps(body))
            elif request.method == "GET" and hasattr(request, "GET") and request.GET:
                logger.info(json.dumps(request.GET))
            response = self.get_response(request)
            response_data = getattr(response, "data", None)
            if response_data:
                logger.info(json.dumps(sanitize_data(response_data)))
            trace_id_dec = span.get_span_context().trace_id
            response["X-Trace-ID"] = hex(trace_id_dec).replace("0x", "")
            return response
        except Exception as e:
            logger.error(str(e))
        return self.get_response(request)
