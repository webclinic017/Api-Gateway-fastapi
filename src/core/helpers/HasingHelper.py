from passlib.context import CryptContext



class HashingHelper:
    """
        Class that provides methods for hashing and 
        verifying passwords using the bcrypt scheme.
    """


    def __init__(self) -> None:
        """
            Initializes an instance of HashingHelper.
        """
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    async def hash_password(self, password: str) -> str:
        """
            Hashes the given password using the bcrypt scheme.

            Args:
                password (str): The plain-text password to be hashed.

            Returns:
                str: The hashed password.
        """
        return self.password_context.hash(password)


    async def verify_password(self, hashed_password: str, plain_password: str) -> bool:
        """
            Verifies if the plain password matches the hashed password.

            Args:
                hashed_password (str): The hashed password.
                plain_password (str): The plain-text password to be verified.

            Returns:
                bool: True if the passwords match, False otherwise.
        """
        return self.password_context.verify(plain_password, hashed_password)



HASHING = HashingHelper()
