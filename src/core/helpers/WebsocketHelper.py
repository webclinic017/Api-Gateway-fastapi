import asyncio
from urllib.parse import urlparse, urlunparse

from fastapi import WebSocket



class WebSocketHelper:
    """
        Helper class for WebSocket operations.

        Attributes:
            None
    """

    @staticmethod
    async def convert_url_to_ws(url: str) -> str:
        """
            Converts a URL to a WebSocket URL.

            Args:
                url (str): The URL to be converted.

            Returns:
                str: The WebSocket URL.
        """
        parsed_url = urlparse(url)

        if parsed_url.scheme == "http":
            new_scheme = "ws"
        elif parsed_url.scheme == "https":
            new_scheme = "wss"
        else:
            return url

        return urlunparse(
            (
                new_scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            )
        )


    async def consume(self, ws: WebSocket, websocket: WebSocket) -> None:
        """
            Consumes messages from one WebSocket and forwards them to another WebSocket.

            Args:
                ws: WebSocket from which messages will be consumed.
                websocket: WebSocket to which messages will be forwarded.

            Returns:
                None
        """
        while True:
            try:
                message = await websocket.receive_bytes()
                await ws.send(message)

            except asyncio.CancelledError:
                break

            except Exception as e:
                break


    async def produce(self, ws: WebSocket, websocket: WebSocket) -> None:
        """
            Produces messages from one WebSocket and sends them to another WebSocket.

            Args:
                ws: WebSocket from which messages will be produced.
                websocket: WebSocket to which messages will be sent.

            Returns:
                None
        """
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=10.0)
                await websocket.send_bytes(message)

            except asyncio.CancelledError:
                break

            except Exception as e:
                break



WS_HELPER = WebSocketHelper()
