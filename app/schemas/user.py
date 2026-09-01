from pydantic import BaseModel, Field

class UserRegisterSchema(BaseModel):
    username: str = Field(min_length=3, max_length=250)
    password: str = Field(min_length=8, max_length=72, examples=["a/@1234567"])
    
class UserloginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=250)
    password: str = Field(min_length=8, max_length=72, examples=["a/@1234567"])

class UserRefreshTokenSchema(BaseModel):
    token: str = Field(description="Refresh token of user")

class LoginResponseSchema(BaseModel):
    detail: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True