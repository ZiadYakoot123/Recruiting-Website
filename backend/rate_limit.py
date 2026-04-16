import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.store = defaultdict(deque)
        self.limit = get_settings().rate_limit_per_minute

    async def dispatch(self, request: Request, call_next):
        key = f"{request.client.host}:{request.url.path}"
        now = time.time()
        dq = self.store[key]
        while dq and now - dq[0] > 60:
            dq.popleft()
        if len(dq) >= self.limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        dq.append(now)
        return await call_next(request)
