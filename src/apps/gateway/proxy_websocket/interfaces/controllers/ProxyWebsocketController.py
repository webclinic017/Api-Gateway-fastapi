import asyncio

from fastapi import APIRouter, WebSocket, status, websockets

from core.utils.GetEndpoint import get_endpoint
from core.helpers.WebsocketHelper import WS_HELPER
from core.utils.GetMicroservices import get_microservices



reverse_proxy_websocket = APIRouter()

@reverse_proxy_websocket.websocket("/ws/{path:path}")
async def websocketProxy(websocket: WebSocket, path: str):
    """
        WebSocket proxy to forward data based on the path.

        Args:
        - websocket (WebSocket): FastAPI WebSocket object.
        - path (str): The path to the endpoint.

        Returns:
        - WebSocket connection or successful closure.
    """
    path = f"/{path}"

    await get_endpoint(path)  # Reusing the previous function to handle errors
    
    microservices = await get_microservices(path)
    url = f"{microservices}{path}"
    wsUrl = await WS_HELPER.convert_url_to_ws(url)
    
    await websocket.accept()
    
    try:
        async with websockets.connect(wsUrl) as ws:
            consumer_task = asyncio.ensure_future(WS_HELPER.consume(ws, websocket))
            producer_task = asyncio.ensure_future(WS_HELPER.produce(ws, websocket))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

    except Exception as error:
        await websocket.close(code=status.WS_1006_ABNORMAL_CLOSURE)
