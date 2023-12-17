from pydantic import BaseModel, validator



class LoginRequestEntity(BaseModel):
    system_code: str
    email: str
    password: str

    @validator("system_code")
    def system_code_validator(cls, system_code: str):
        if len(system_code) < 1 or len(system_code) > 10:
            raise ValueError("La longitud del system_code debe tener entre 1 y 10 caracteres.")
        return system_code

    @validator("email")
    def email_validator(cls, email: str):
        if not email:
            raise ValueError('El correo electrónico no puede estar vacío')
        if '@' not in email:
            raise ValueError('El correo electrónico no es valido.')
        return email

    @validator("password")
    def password_validator(cls, password: str):
        if len(password) < 8:
            raise ValueError("La contraseña debe tener un mínimo de 8 caracteres.")
        return password



class LoginResponseEntity(BaseModel):
    type: str
    token: str
    refresh_token: str