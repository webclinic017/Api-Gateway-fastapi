from pydantic import (
    BaseModel, 
    EmailStr,
    validator
)



class RegisterRequestEntity(BaseModel):
    email: EmailStr
    password: str
    password_repeat: str

    @validator("email")
    def email_validator(cls, email: str):
        if "@" not in email:
            raise ValueError(f"{email}, no es un correo electrónico válido.")
        return email

    @validator("password")
    def password_validator(cls, password: str):
        if len(password) < 8 or len(password) > 16:
            raise ValueError("La contraseña debe tener un mínimo de 8 caracteres y un máximo de 16 caracteres.")
        return password

    @validator("password_repeat")
    def password_repeat_validator(cls, password_repeat, values, **kwargs):
        if not password_repeat == values['password']:
            raise ValueError('Las contraseñas deben ser las mismas.')
        return password_repeat
    


class RegisterResponseEntity(BaseModel):
    id: int
    email: str