import base64
from typing import Dict, Union

import grpc
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization

from settings import SETTINGS
import core.services.external_services.vault.protobufs.keys_pairs_pb2 as keys_pairs_pb2
from core.services.external_services.vault.protobufs.keys_pairs_pb2_grpc import KeysPairsServiceStub



class KeyCodeHelper:
    """
        Class that provides methods for obtaining 
        and managing key pairs securely.
    """


    async def get_keys_pairs(self) -> Dict:
        """
            Obtains key pairs from the gRPC service.

            Returns:
                Dict: Dictionary with key pairs.
        """
        channel = grpc.insecure_channel(SETTINGS.GRPC_SERVER_ADDRESS)
        stub = KeysPairsServiceStub(channel)
        
        request = keys_pairs_pb2.EncryptKeysRequest(system_code=SETTINGS.SYSTEM_CODE)
        response = stub.keysPairs(request)

        cipher_suite = Fernet(SETTINGS.VAULT_SECRET_KEY)
        decrypted_data = cipher_suite.decrypt(response.encrypted_data)

        return eval(decrypted_data.decode('utf-8'))


    async def load_pem_keys(
        self, 
        key: str, 
        private: bool = True
    ) -> Union[serialization.load_pem_private_key, serialization.load_pem_public_key]:
        """
            Loads a PEM key from the obtained key pairs.

            Args:
                key (str): The key type ("private_key" or "refresh_private_key").
                private (bool): True if it's a private key, False if it's a public key.

            Returns:
                cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey or
                cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey: The loaded PEM key.
        """
        _key = await self.get_keys_pairs()
        decode_key = base64.b64decode(_key[key])

        if private:
            return serialization.load_pem_private_key(decode_key, password=None)

        return serialization.load_pem_public_key(decode_key)


    async def private_key(self) -> serialization.load_pem_private_key:
        """
            Obtains the PEM private key.

            Returns:
                cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey: The PEM private key.
        """
        private_key = await self.load_pem_keys("private_key")
        return private_key


    async def refresh_private_key(self) -> serialization.load_pem_private_key:
        """
            Obtains the PEM refresh private key.

            Returns:
                cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey: The PEM refresh private key.
        """
        private_key = await self.load_pem_keys("refresh_private_key")
        return private_key


    async def public_key(self) -> serialization.load_pem_public_key:
        """
            Obtains the PEM public key.

            Returns:
                cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey: The PEM public key.
        """
        public_key = await self.load_pem_keys("public_key", False)
        return public_key


    async def refresh_public_key(self) -> serialization.load_pem_public_key:
        """
            Obtains the PEM refresh public key.

            Returns:
                cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey: The PEM refresh public key.
        """
        refresh_public_key = await self.load_pem_keys("refresh_public_key", False)
        return refresh_public_key



KEY_CODE = KeyCodeHelper()
