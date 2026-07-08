from core.intents import Intent
from core.analytics import AnalyticsService


REGISTRY = {
    Intent.AVERAGE_AGE: AnalyticsService.get_average_age_by_role,

    Intent.APPLICATION_COUNT: AnalyticsService.get_application_count_by_status,

    Intent.TOP_SKILLS: AnalyticsService.get_top_skills_for_job,

    Intent.REJECTION_RATE: AnalyticsService.get_rejection_rate_by_source,

    Intent.SALARY_EXPECTATION: AnalyticsService.get_salary_expectations_by_experience,
}