from pydantic import BaseModel


class PlayerCreate(BaseModel):
    name: str
    age: int 
    rating: int   
    country: str


class PlayerUpdate(BaseModel):
    name: str
    age: int
    rating: int
    country: str