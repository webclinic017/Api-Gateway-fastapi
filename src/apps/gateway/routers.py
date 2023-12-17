from fastapi import APIRouter

from apps.gateway.proxy_http.interfaces.controllers.PoxyHTTPController import reverse_proxy_http
from apps.gateway.proxy_websocket.interfaces.controllers.ProxyWebsocketController import reverse_proxy_websocket



gateway = APIRouter(prefix="/gateway", tags=["Gateway"])
gateway.include_router(reverse_proxy_http)
gateway.include_router(reverse_proxy_websocket)