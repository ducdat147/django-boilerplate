from django.http import HttpRequest, JsonResponse


def health(request: HttpRequest) -> JsonResponse:
    """Liveness probe for nginx and the container healthchecks.

    Deliberately dependency free: it must keep answering 200 while maintenance
    mode is on (see utils/maintenance.py) so the orchestrator does not consider
    the service dead. Use a separate readiness check if you need to know whether
    the database and broker are reachable.
    """
    return JsonResponse({"status": "ok"})
