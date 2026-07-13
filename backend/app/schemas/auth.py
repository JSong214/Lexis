import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

CefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
LearningGoal = Literal[
    "General English",
    "CET-4",
    "CET-6",
    "IELTS",
    "TOEFL",
    "Postgraduate Entrance English",
    "Academic English",
    "Workplace English",
]


class AuthCredentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    cefr_level: CefrLevel
    learning_goal: LearningGoal
    created_at: datetime


class UserPreferencesUpdate(BaseModel):
    cefr_level: CefrLevel
    learning_goal: LearningGoal
