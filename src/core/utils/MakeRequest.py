from typing import Dict, Any

from httpx import AsyncClient



async def make_request(
        method: str, 
        url: str, 
        headers: Dict[str, Any], 
        body: bytes
    ):
    """
        Makes an asynchronous request to a specific URL.

        Args:
        - method (str): HTTP method.
        - url (str): The URL of the endpoint.
        - headers (Dict[str, Any]): Request headers.
        - body (bytes): Request body.

        Returns:
        - Response object.
    """
    async with AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            data=body,
            timeout=600.0
        )
    return response
