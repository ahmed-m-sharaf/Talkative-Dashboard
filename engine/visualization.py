from core.intents import Intent


VISUALIZATION_MAP = {
    Intent.AVERAGE_AGE: "METRIC_CARD",

    Intent.APPLICATION_COUNT: "METRIC_CARD",

    Intent.TOP_SKILLS: "BAR_CHART",

    Intent.REJECTION_RATE: "BAR_CHART",

    Intent.SALARY_EXPECTATION: "METRIC_CARD",
}


def get_visualization(intent: Intent) -> str:
    return VISUALIZATION_MAP.get(
        intent,
        "TEXT_RESPONSE",
    )