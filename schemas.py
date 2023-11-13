from pydantic import BaseModel, Field


class AuthDetails(BaseModel):
    username: str = Field(description="the username", min_length=1)
    password: str = Field(description="the password", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "password123"
            }
        }

