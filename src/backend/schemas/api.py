from pydantic import BaseModel


class SignInInputSchema(BaseModel):
    username: str
    password: str
