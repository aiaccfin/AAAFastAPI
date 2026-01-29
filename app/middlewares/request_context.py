import uuid
import contextvars
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

request_context = contextvars.ContextVar("request_context", default={})


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            context = {
                "request_id": str(uuid.uuid4()),
                "user": getattr(request.state, "user", "anonymous"),
                "client_ip": request.client.host if request.client else "unknown"
            }
            request_context.set(context)

            response = await call_next(request)

            return response

        except Exception as e:
            # If anything fails in middleware, still return proper response
            return Response(
                content=f"Middleware Error: {str(e)}",
                status_code=500
            )
