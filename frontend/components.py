import streamlit as st

from frontend.charts import (
    render_bar_chart,
    render_table,
)


def render_metric_card(title: str, value, help_text: str | None = None):

    st.metric(
        label=title,
        value=value,
        help=help_text,
    )


def render_error(message: str):

    st.error(message)


def render_clarification(missing_parameters: list[str]):

    st.warning("More information is required.")

    st.write("Please provide:")

    for parameter in missing_parameters:
        st.write(f"- {parameter}")


def render_text_response(data: dict):

    st.json(data)


def render_response(response):

    status = response.execution_result.status

    if status == "INVALID_PARAMETER":

        render_error(
            response.execution_result.raw_data["error"]
        )

        return

    if status == "MISSING_PARAMETERS":

        render_clarification(
            response.execution_result.raw_data[
                "missing_parameters"
            ]
        )

        return

    visualization = response.visualization_instruction

    data = response.execution_result.raw_data

    if visualization == "METRIC_CARD":

        if "average_age" in data:

            render_metric_card(
                "Average Age",
                f'{data["average_age"]:.2f} Years',
                f'Sample Size: {data["sample_size"]}',
            )

            return

        if "average_salary" in data:

            render_metric_card(
                "Average Salary",
                f'{data["average_salary"]:.2f}',
                f'Sample Size: {data["sample_size"]}',
            )

            return

        if "count" in data:

            prompt_lower = response.metadata.user_prompt.lower()
            if any(word in prompt_lower for word in ["people", "person", "candidate", "applicant"]):
                label = "Candidates"
                value = data.get("people_count", data["count"])
            else:
                label = "Applications"
                value = data["count"]

            render_metric_card(
                label,
                value,
            )

            return


    if visualization == "BAR_CHART":

        render_bar_chart(data)

        return

    if visualization == "TABLE":

        render_table(data)

        return


    render_text_response(data)