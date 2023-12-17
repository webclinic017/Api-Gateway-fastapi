from pydantic import BaseModel, validator



class ChangePasswordRequestEntity(BaseModel):
    new_password: str
    repeat_new_password: str

    @validator("new_password")
    def new_password_validator(cls, new_password:str):
        if len(new_password) < 8 or len(new_password) > 16:
            raise ValueError("La nueva contraseña debe tener un mínimo de 8 caracteres y un máximo de 16 caracteres.")
        return new_password

    @validator("repeat_new_password")
    def repeat_new_password_validator(cls, repeat_new_password:str):
        if len(repeat_new_password) < 8 or len(repeat_new_password) > 16:
            raise ValueError("La nueva contraseña repetida debe tener un mínimo de 8 caracteres y un máximo de 16 caracteres.")
        return repeat_new_password