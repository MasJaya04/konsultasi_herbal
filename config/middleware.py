import json
import logging
import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class RequestContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())


class RateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        client_ip = request.META.get("REMOTE_ADDR", "unknown")
        cache_key = f"rate_limit:{client_ip}"
        current_count = cache.get(cache_key, 0)
        if current_count >= settings.RATE_LIMIT_PER_MINUTE:
            payload = {
                "message": "Batas permintaan tercapai. Silakan coba lagi dalam 1 menit.",
                "request_id": getattr(request, "request_id", ""),
            }
            return HttpResponse(json.dumps(payload), status=429, content_type="application/json")
        cache.set(cache_key, current_count + 1, timeout=60)

    def process_response(self, request, response):
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        return response


class RequestLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("request_id", self.extra.get("request_id", ""))
        extra.setdefault("user_id", self.extra.get("user_id", ""))
        extra.setdefault("context", self.extra.get("context", ""))
        return msg, kwargs
