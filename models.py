from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)

class HomeRequest(BaseModel):
    total_budget: float = Field(gt=0, le=100000000)
    room_types: list[str] = Field(min_length=1)
    num_lights: int = Field(default=0, ge=0, le=100)
    num_fans: int = Field(default=0, ge=0, le=100)
    num_furniture: int = Field(default=0, ge=0, le=100)
    num_dining_tables: int = Field(default=0, ge=0, le=20)
    style: str = "Any"
    additional_requirements: str = ""

class PartyRequest(BaseModel):
    total_budget: float = Field(gt=0, le=100000000)
    party_type: str = Field(min_length=2, max_length=80)
    num_guests: int = Field(gt=0, le=10000)
    venue_type: str = "Not specified"
    needs_catering: bool = True
    needs_decoration: bool = True
    needs_entertainment: bool = False
    additional_requirements: str = ""
