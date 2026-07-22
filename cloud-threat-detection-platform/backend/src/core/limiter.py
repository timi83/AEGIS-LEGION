from slowapi import Limiter
from slowapi.util import get_remote_address


def _client_key(request):
    """
    Rate-limit key = the real client IP. Behind a proxy (Render/Vercel) the
    socket peer is the proxy, so prefer the left-most X-Forwarded-For entry
    (the original client) and fall back to the socket address otherwise.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=_client_key)
