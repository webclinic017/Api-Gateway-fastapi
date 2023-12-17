from typing import Optional, Union, Dict
from datetime import datetime, timedelta

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from settings import SETTINGS
from .KeyCodeHelper import KEY_CODE



class JwtManagerHelper:
    """
        Class that provides methods for creating, 
        refreshing, and validating JWT tokens.
    """


    def __init__(self, data: Dict = {}, token: str = None) -> None:
        """
            Initializes an instance of JwtManagerHelper.

            Args:
                data (Dict, optional): Data to include in the token (default is an empty dictionary).
                token (str, optional): JWT token to process (default is None).
        """
        self.data = data
        self.token = token


    async def create_token(self, expires_delta: Optional[timedelta] = None) -> str:
        """
            Creates a JWT token with the provided data.

            Args:
                expires_delta (timedelta, optional): Token validity duration (default is None).

            Returns:
                str: Generated JWT token.
        """
        to_encode = self.data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        private_key: RSAPrivateKey = await KEY_CODE.private_key()

        return jwt.encode(to_encode, private_key, algorithm=SETTINGS.ALGORITHM)


    async def refresh_token(self, expires_delta: Optional[timedelta] = None) -> str:
        """
            Refreshes a JWT token with the provided data.

            Args:
                expires_delta (timedelta, optional): Token validity duration (default is None).

            Returns:
                str: Refreshed JWT token.
        """
        to_encode = self.data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        private_key: RSAPrivateKey = await KEY_CODE.refresh_private_key()

        return jwt.encode(to_encode, private_key, algorithm=SETTINGS.ALGORITHM)


    async def validate_token(self) -> Union[Dict, str]:
        """
            Validates a JWT token and returns the data contained in it.

            Returns:
                Union[Dict, str]: Data contained in the token or an error message.
        """
        try:
            public_key: RSAPublicKey = await KEY_CODE.public_key()
            return jwt.decode(self.token, key=public_key, algorithms=[SETTINGS.ALGORITHM])

        except jwt.ExpiredSignatureError:
            return {"token": "The token has expired."}

        except jwt.InvalidTokenError:
            return {"token": "The token is not valid."}


    @staticmethod
    async def extract_token(token: str) -> str:
        """
            Extracts and decodes a JWT token.

            Args:
                token (str): JWT token to decode.

            Returns:
                str: Decoded JWT token.
        """
        public_key: RSAPublicKey = await KEY_CODE.public_key()
        return jwt.decode(token, public_key, SETTINGS.ALGORITHM)
