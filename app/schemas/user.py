from pydantic import BaseModel, Field, model_validator

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

class UserChangePasswordSchema(BaseModel):
    current_password: str = Field(min_length=8, max_length=72, examples=["a/@1234567"])
    new_password: str = Field(min_length=8, max_length=72, examples=["a/@1234567"])
    confirm_new_password: str = Field(min_length=8, max_length=72, examples=["a/@1234567"])

    @model_validator(mode="after")
    def check_new_passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("New password and confirmation do not match")
        return self