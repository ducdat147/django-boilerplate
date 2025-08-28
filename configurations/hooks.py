# -*- coding: utf-8 -*-
import json
from logging import LogRecord

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from opentelemetry.sdk.trace import Span
from opentelemetry.trace.status import StatusCode
from requests import Response

MIN_LENGTH = 2
MAX_LENGHT = 6500


def add_event(span: Span, attributes: dict = {}, message: str = "log"):
    if not attributes:
        return
    span.add_event(name=message, attributes=attributes)


def request_hook(span: Span, request: WSGIRequest):
    if span and span.is_recording():
        attributes = {}
        try:
            params = (
                json.dumps(
                    getattr(request, "GET", None),
                    indent=2,
                ).encode("utf-8")
                if getattr(request, "GET", None)
                else None
            )
            body = getattr(request, "body", None)
            if bool(params) and MIN_LENGTH < len(params) < MAX_LENGHT:
                attributes["requests.queryparams"] = params
            if bool(body) and MIN_LENGTH < len(body) < MAX_LENGHT:
                attributes["requests.body"] = body
            if bool(attributes):
                add_event(span, attributes=attributes)
        except Exception as e:
            print(str(e))


def response_hook(span: Span, request: WSGIRequest, response: Response):
    if span and span.is_recording():
        try:
            content = getattr(response, "content", None)
            if (
                content
                and isinstance(content, bytes)
                and MIN_LENGTH < len(content) < MAX_LENGHT
            ):
                add_event(span, attributes={"response.body": content})

            status = getattr(response, "status_code", None)
            if status is not None:
                span.set_status(StatusCode.OK if status < 400 else StatusCode.ERROR)
        except Exception as e:
            print(str(e))


def django_request_hook(span: Span, request: WSGIRequest):
    return


def django_response_hook(span: Span, request: WSGIRequest, response: Response):
    if span and span.is_recording():
        tags_span = {}
        user = getattr(request, "user", None)
        if user and request.user.is_authenticated:
            tags_span["user.id"] = user.id
            phone_number = getattr(user, "phone_number", None)
            email = getattr(user, "email", None)
            if not span.attributes.get("phone_number") and phone_number:
                tags_span["user.phone_number"] = phone_number
            if not span.attributes.get("email") and email:
                tags_span["user.email"] = email
            span.set_attributes(tags_span)
        status = getattr(response, "status_code", None)
        if status is not None:
            span.set_status(StatusCode.OK if status < 400 else StatusCode.ERROR)


def get_formatted_message(record: LogRecord) -> str:
    """Helper function để format message"""
    if isinstance(record.msg, dict):
        return json.dumps(record.msg, indent=2, ensure_ascii=False)
    elif isinstance(record.msg, bytes):
        return record.msg.decode("utf-8", errors="replace")
    else:
        try:
            return record.getMessage()
        except (TypeError, ValueError):
            return str(record.msg % record.args)


def log_hook(span: Span, record: LogRecord):
    try:
        if span and span.is_recording():
            if record.levelname in ["ERROR", "CRITICAL"]:
                span.set_status(StatusCode.ERROR)

            content = get_formatted_message(record)

            attributes = {
                "log.severity": record.levelname,
                "log.message": content,
                "code.lineno": record.lineno,
                "code.funcname": record.funcName,
                "code.filename": record.filename,
                "module": record.module,
                "log.logger": record.name,
                "timestamp": record.created,
            }
            if str(settings.BASE_DIR) in record.pathname:
                attributes["filepath"] = record.pathname.replace(
                    str(settings.BASE_DIR), ""
                )
            # if record.exc_info:
            #     attributes["exception.type"] = record.exc_info[0].__name__
            #     attributes["exception.message"] = str(record.exc_info[1])
            add_event(span, attributes=attributes)
    except Exception as e:
        print(f"Error in log_hook: {str(e)}")
