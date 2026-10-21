import json
import logging

from opentelemetry import trace

from configurations.hooks import add_event
from configurations.logging import sanitize_data
from utils import maintenance

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


class MaintenanceModeMiddleware:
    """
    Short-circuits requests with a 503 while maintenance mode is on.

    Covers the full site, a subset of paths (`MAINTENANCE_SCOPES`) or writes only
    (`MAINTENANCE_READ_ONLY`). The admin stays reachable no matter what, so the
    flags can always be turned off again from `/admin/constance/config/`. Flag
    resolution, path exemptions, scopes and the IP allowlist all live in
    `utils.maintenance`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        reason = maintenance.get_block_reason(request)
        if reason is None:
            return self.get_response(request)

        # Deferred: core.sites pulls in models, and this module is imported
        # while Django is still wiring up the middleware stack.
        from core.sites import admin_site

        response = admin_site.service_unavailable(request, message=maintenance.get_message(reason))
        retry_after = maintenance.get_retry_after()
        if retry_after:
            response["Retry-After"] = str(retry_after)
        return response
