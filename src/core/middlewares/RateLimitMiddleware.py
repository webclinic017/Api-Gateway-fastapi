from typing import Union
from datetime import datetime, timedelta

from fastapi import status, Request, Response

from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from settings import SETTINGS



class RateLimitMiddleware(BaseHTTPMiddleware):
    """
        Middleware to limit the number of requests per second 
        and temporarily block if the limit is exceeded per IP.
    """

    def __init__(self, app):
        """
            Initializes an instance of the middleware.

            Args:
                app: Instance of the FastAPI application.
        """
        super().__init__(app)
        self.requests = {}  # We use a dictionary to track requests per IP and their last request.


    async def dispatch(self, request: Request, call_next) -> Union[JSONResponse, Response]:
        """
            Handles incoming requests and applies limitations per IP.

            Args:
                request: Request object.
                call_next: Function to call the next middleware layer.

            Returns:
                HTTP response.
        """
        client_ip = request.client.host

        if not self.allow_request(client_ip):
            remaining_time = self.get_remaining_block_time(client_ip)

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": status.HTTP_429_TOO_MANY_REQUESTS,
                    "message": f"Too many requests from {client_ip}. Please try again after {remaining_time} seconds."
                }
            )

        response = await call_next(request)
        return response


    def allow_request(self, client_ip: str) -> bool:
        """
            Checks if the current request from a given IP is allowed based on the configured request rate.

            Args:
                client_ip: Client's IP address.

            Returns:
                bool: True if the request is allowed, False if it's limited.
        """
        now = datetime.now()

        if client_ip not in self.requests:
            self.requests[client_ip] = {"requests": [now], "blocked_until": None}

        # Block if still within the blocking time
        blocked_until = self.requests[client_ip]["blocked_until"]
        if blocked_until and blocked_until > now:
            return False

        # Clean up previous requests outside the interval
        self.requests[client_ip]["requests"] = [
            request for request in self.requests[client_ip]["requests"] if now - request < timedelta(seconds=SETTINGS.REQUEST_INTERVAL)
        ]

        if len(self.requests[client_ip]["requests"]) >= SETTINGS.REQUESTS_PER_SECOND:
            # Block and set the blocking time
            self.requests[client_ip]["blocked_until"] = now + timedelta(seconds=SETTINGS.BLOCK_DURATION)
            return False

        self.requests[client_ip]["requests"].append(now)

        return True


    def get_remaining_block_time(self, client_ip: str) -> int:
        """
            Gets the remaining block time for a given IP.

            Args:
                client_ip: Client's IP address.

            Returns:
                int: Remaining time in seconds.
        """
        now = datetime.now()
        blocked_until = self.requests[client_ip]["blocked_until"]

        if blocked_until and blocked_until > now:
            return int((blocked_until - now).total_seconds())
        return 0
