from datetime import date
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator

from core.intents import Intent
from database.models import ApplicationStatus, ApplicationSource



class RouteParameters(BaseModel):
    role: Optional[str] = None

    city: Optional[str] = None

    department: Optional[str] = None

    status: Optional[ApplicationStatus] = None

    source: Optional[str] = None

    top_k: Optional[int] = None

    min_experience: Optional[float] = None

    max_experience: Optional[float] = None

    start_date: Optional[date] = None

    end_date: Optional[date] = None

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        from database.database import get_session
        from database.models import Job
        from sqlalchemy import func
        session = get_session()
        try:
            db_job = session.query(Job).filter(func.lower(Job.title) == func.lower(v.strip())).first()
            if db_job:
                return db_job.title
        finally:
            session.close()
        return v

    @field_validator("city", mode="before")
    @classmethod
    def normalize_city(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        from database.database import get_session
        from database.models import Candidate
        from sqlalchemy import func
        session = get_session()
        try:
            db_cand = session.query(Candidate).filter(func.lower(Candidate.city) == func.lower(v.strip())).first()
            if db_cand:
                return db_cand.city
        finally:
            session.close()
        return v

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str):
            v_clean = v.strip().lower()
            for status_enum in ApplicationStatus:
                if status_enum.value.lower() == v_clean:
                    return status_enum
        return v

    @field_validator("source", mode="before")
    @classmethod
    def normalize_source(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v_clean = v.strip().lower()
        for source_enum in ApplicationSource:
            if source_enum.value.lower() == v_clean:
                return source_enum.value
        return v



class RouterRequest(BaseModel):
    intent: Intent

    confidence_score: float = Field(
        ge=0,
        le=1,
    )

    needs_clarification: bool = False

    missing_parameters: list[str] = Field(default_factory=list)

    parameters: RouteParameters