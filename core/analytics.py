from datetime import date
from sqlalchemy import func
from database import get_session, Application, ApplicationStatus, Candidate, Job, Skill


class AnalyticsService:

    @staticmethod
    def get_average_age_by_role(
        role: str,
        city: str | None = None,
        department: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        if not role:
            raise ValueError("role is required")

        session = get_session()
        try:
            query = (
                session.query(
                    func.avg(Candidate.age),
                    func.count(Candidate.id),
                )
                .join(Application)
                .join(Job)
                .filter(Job.title == role)
            )

            if city:
                query = query.filter(Candidate.city == city)
            if department:
                query = query.filter(Job.department == department)
            if start_date:
                query = query.filter(Application.created_at >= start_date)
            if end_date:
                query = query.filter(Application.created_at <= end_date)

            average_age, sample_size = query.first()

            return {
                "average_age": round(average_age or 0, 2),
                "sample_size": sample_size or 0,
            }
        finally:
            session.close()

    @staticmethod
    def get_application_count_by_status(
        status: ApplicationStatus | None = None,
        role: str | None = None,
        city: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        session = get_session()
        try:
            query = (
                session.query(
                    func.count(Application.id),
                    func.count(func.distinct(Candidate.id)),
                )
                .join(Candidate)
                .join(Job)
            )

            if status is not None:
                query = query.filter(Application.status == status)
            if role:
                query = query.filter(Job.title == role)
            if city:
                query = query.filter(Candidate.city == city)
            if start_date:
                query = query.filter(Application.created_at >= start_date)
            if end_date:
                query = query.filter(Application.created_at <= end_date)

            apps_count, candidates_count = query.first()

            return {
                "count": apps_count or 0,
                "people_count": candidates_count or 0,
            }
        finally:
            session.close()

    @staticmethod
    def get_top_skills_for_job(
        role: str,
        top_k: int = 5,
    ) -> dict:
        if not role:
            raise ValueError("role is required")

        session = get_session()
        try:
            skills = (
                session.query(
                    Skill.name,
                    func.count(Skill.id).label("count"),
                )
                .join(Skill.candidates)
                .join(Candidate.applications)
                .join(Application.job)
                .filter(Job.title == role)
                .group_by(Skill.id)
                .order_by(func.count(Skill.id).desc())
                .limit(top_k)
                .all()
            )

            return {
                "skills": [
                    {
                        "skill": name,
                        "count": count,
                    }
                    for name, count in skills
                ]
            }
        finally:
            session.close()

    @staticmethod
    def get_rejection_rate_by_source(
        source: str,
    ) -> dict:
        if not source:
            raise ValueError("source is required")

        session = get_session()
        try:
            total = (
                session.query(func.count(Application.id))
                .filter(Application.source == source)
                .scalar()
            )

            rejected = (
                session.query(func.count(Application.id))
                .filter(Application.source == source)
                .filter(Application.status == ApplicationStatus.REJECTED)
                .scalar()
            )

            rate = 0
            if total:
                rate = round((rejected / total) * 100, 2)

            return {
                "rejection_rate": rate,
                "total": total,
                "rejected": rejected,
            }
        finally:
            session.close()

    @staticmethod
    def get_salary_expectations_by_experience(
        min_experience: float | None = None,
        max_experience: float | None = None,
        role: str | None = None,
    ) -> dict:
        session = get_session()
        try:
            query = (
                session.query(
                    func.avg(Application.salary_expectation),
                    func.count(Application.id),
                )
                .join(Candidate)
                .join(Job)
            )

            if min_experience is not None:
                query = query.filter(Candidate.experience_years >= min_experience)
            if max_experience is not None:
                query = query.filter(Candidate.experience_years <= max_experience)
            if role:
                query = query.filter(Job.title == role)

            average_salary, sample_size = query.first()

            return {
                "average_salary": round(average_salary or 0, 2),
                "sample_size": sample_size or 0,
            }
        finally:
            session.close()
