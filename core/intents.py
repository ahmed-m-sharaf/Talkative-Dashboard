from enum import Enum


class Intent(str, Enum):
    AVERAGE_AGE = "average_age"
    APPLICATION_COUNT = "application_count"
    TOP_SKILLS = "top_skills"
    REJECTION_RATE = "rejection_rate"
    SALARY_EXPECTATION = "salary_expectation"
    UNKNOWN = "unknown"