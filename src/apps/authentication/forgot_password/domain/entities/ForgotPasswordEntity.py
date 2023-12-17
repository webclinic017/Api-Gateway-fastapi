from pydantic import BaseModel, EmailStr, validator



class ForgotPasswordRequestEntity(BaseModel):
    email: EmailStr

    @validator("email")
    def email_validator(cls, email: str):
        if "@" not in email:
            raise ValueError(f"{email}, no es un correo electrónico válido.")
        return email