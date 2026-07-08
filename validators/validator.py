from sqlalchemy.orm import Session
from database import get_session, Candidate, Job, ApplicationStatus


class JobValidator:
    @staticmethod
    def validate(session: Session, role: str | None) -> tuple[bool, str | None]:
        if role is None:
            return True, None

        exists = (
            session.query(Job)
            .filter(Job.title == role)
            .first()
        )

        if exists is None:
            return False, f"Unknown job role: '{role}'."

        return True, None


class CityValidator:
    @staticmethod
    def validate(session: Session, city: str | None) -> tuple[bool, str | None]:
        if city is None:
            return True, None

        exists = (
            session.query(Candidate)
            .filter(Candidate.city == city)
            .first()
        )

        if exists is None:
            return False, f"Unknown city: '{city}'."

        return True, None


class StatusValidator:
    @staticmethod
    def validate(status: ApplicationStatus | None) -> tuple[bool, str | None]:
        if status is None:
            return True, None

        try:
            ApplicationStatus(status)
            return True, None
        except ValueError:
            return False, f"Invalid application status: '{status}'."


class RequestValidator:
    @staticmethod
    def validate(router_request) -> tuple[bool, str | None]:
        session = get_session()
        try:
            params = router_request.parameters
            validators = [
                JobValidator.validate(session, params.role),
                CityValidator.validate(session, params.city),
                StatusValidator.validate(params.status),
            ]

            for is_valid, error in validators:
                if not is_valid:
                    return False, error

            return True, None
        finally:
            session.close()