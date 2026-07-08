from datetime import date
from enum import Enum

from sqlalchemy import (
    Column,
    Date,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.database import Base


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


class ApplicationStatus(str, Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    PENDING = "Pending"


class ApplicationSource(str, Enum):
    LINKEDIN = "LinkedIn"
    WEBSITE = "Website"
    REFERRAL = "Referral"
    INDEED = "Indeed"


candidate_skills = Table(
    "candidate_skills",
    Base.metadata,
    Column(
        "candidate_id",
        ForeignKey("candidates.id"),
        primary_key=True,
    ),
    Column(
        "skill_id",
        ForeignKey("skills.id"),
        primary_key=True,
    ),
)


class Candidate(Base):

    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)

    full_name: Mapped[str] = mapped_column(String(100))

    age: Mapped[int]

    gender: Mapped[Gender] = mapped_column(SqlEnum(Gender))

    city: Mapped[str]

    experience_years: Mapped[float]

    applications: Mapped[list["Application"]] = relationship(
        back_populates="candidate"
    )

    skills: Mapped[list["Skill"]] = relationship(
        secondary=candidate_skills,
        back_populates="candidates",
    )


class Job(Base):

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str]

    department: Mapped[str]

    location: Mapped[str]

    applications: Mapped[list["Application"]] = relationship(
        back_populates="job"
    )


class Skill(Base):

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(unique=True)

    candidates: Mapped[list["Candidate"]] = relationship(
        secondary=candidate_skills,
        back_populates="skills",
    )


class Application(Base):

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id")
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id")
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SqlEnum(ApplicationStatus)
    )

    source: Mapped[ApplicationSource] = mapped_column(
        SqlEnum(ApplicationSource)
    )

    salary_expectation: Mapped[float]

    created_at: Mapped[date] = mapped_column(Date)

    candidate: Mapped["Candidate"] = relationship(
        back_populates="applications"
    )

    job: Mapped["Job"] = relationship(
        back_populates="applications"
    )