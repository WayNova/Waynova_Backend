from pydantic import BaseModel, EmailStr, validator

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    mobile: str
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
