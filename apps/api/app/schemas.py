from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class AuthInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    demo_mode: bool


class OnboardingInput(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)
    program: str = Field(min_length=1, max_length=120)
    subjects: list[str] = Field(min_length=1, max_length=12)
    exam_date: date | None = None
    daily_minutes: int = Field(default=120, ge=15, le=720)
    learning_style: Literal["examples", "visual", "practice", "reading"] = "examples"


class ChatInput(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    mode: Literal["learn", "hint", "socratic", "exam"] = "socratic"
    subject: str | None = None


class QuizSubmission(BaseModel):
    question_id: str
    answer_index: int = Field(ge=0, le=20)
    confidence: int = Field(ge=1, le=5)


class FocusSessionInput(BaseModel):
    topic: str = Field(min_length=1, max_length=160)
    duration_minutes: int = Field(ge=1, le=180)


class RoomInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    subject: str = Field(min_length=2, max_length=120)
    capacity: int = Field(default=6, ge=2, le=30)
    is_private: bool = False


class FlashcardReview(BaseModel):
    rating: int = Field(ge=0, le=5)
