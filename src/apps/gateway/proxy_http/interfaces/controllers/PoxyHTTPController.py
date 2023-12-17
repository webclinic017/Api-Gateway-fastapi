from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Request, 
    Response, 
    status
)

from httpx import ConnectError

from core.databases.Models import Users
from core.utils.GetEndpoint import get_endpoint
from core.utils.MakeRequest import make_request
from core.utils.GetMicroservices import get_microservices
from core.helpers.PermissionHelper import PERMISSION_HELPER



ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE"}

reverse_proxy_http = APIRouter()

@reverse_proxy_http.api_route("/{path:path}", methods=ALLOWED_METHODS, include_in_schema=False)
async def reverseProxy(
    path: str, 
    request: Request, 
    authenticated: Users = Depends(PERMISSION_HELPER.get_current_user)
):
    """
        Reverse proxy endpoint to forward requests based on the path.

        Args:
        - path (str): The path to the endpoint.
        - request (Request): FastAPI request object.
        - authenticated (Users, optional): Authenticated user. Default is the result of PERMISSION_HELPER.get_current_user.

        Returns:
        - JSON response or PDF response based on the microservice response.
    """
    path = f"/{path}"

    await get_endpoint(path)
    
    microservices = await get_microservices(path)
    url = f"{microservices}{path}?{request.query_params}" if request.query_params else f"{microservices}{path}"
    body = await request.body()

    try:
        response = await make_request(request.method, url, dict(request.headers), body)
        
        # Handle non-200 responses
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Unknown error"))

        # Check if the response is a PDF and return appropriately
        if response.headers.get("content-type") == "application/pdf":
            response.headers["Content-Disposition"] = "inline; filename=documento_oficial.pdf"
            return Response(content=response.content, media_type="application/pdf")

        return response.json()

    except ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="The service is not available, please contact the support area."
        )
