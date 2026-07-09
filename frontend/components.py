import streamlit as st

from frontend.charts import (
    render_bar_chart,
    render_table,
)
from core.intents import Intent


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


def get_result_message(response) -> str:
    status = response.execution_result.status
    if status == "INVALID_PARAMETER":
        return f"Validation Error: {response.execution_result.raw_data.get('error')}"
    if status == "MISSING_PARAMETERS":
        missing = response.execution_result.raw_data.get('missing_parameters', [])
        return f"Missing required parameters: {', '.join(missing)}"
    if status == "UNKNOWN_INTENT":
        return response.execution_result.raw_data.get('message', "This query is out of scope or could not be mapped.")

    # Under SUCCESS status
    intent = response.intent_mapping.target_endpoint
    data = response.execution_result.raw_data
    params = response.intent_mapping.extracted_parameters

    if intent == Intent.AVERAGE_AGE:
        age = data.get("average_age", 0)
        sample = data.get("sample_size", 0)
        loc = f" in **{params.city}**" if params.city else ""
        return f"The average age of **{params.role}** candidates{loc} is **{age:.2f} years** (sample size: {sample})."

    elif intent == Intent.APPLICATION_COUNT:
        count = data.get("count", 0)
        people = data.get("people_count", 0)
        status_str = f"**{params.status.value}** " if params.status else ""
        role_str = f" for **{params.role}**" if params.role else ""
        loc = f" in **{params.city}**" if params.city else ""
        return f"Found **{count}** {status_str}applications ({people} unique candidates){role_str}{loc}."

    elif intent == Intent.TOP_SKILLS:
        skills_list = data.get("skills", [])
        if not skills_list:
            return f"No skills found in the database for **{params.role}**."
        skills_str = ", ".join([f"**{s['skill']}** ({s['count']})" for s in skills_list])
        return f"The top skills for **{params.role}** candidates are: {skills_str}."

    elif intent == Intent.REJECTION_RATE:
        rate = data.get("rejection_rate", 0)
        total = data.get("total", 0)
        rej = data.get("rejected", 0)
        src = f" from **{params.source}**" if params.source else ""
        return f"The rejection rate for candidates{src} is **{rate:.2f}%** (with {rej} rejected out of {total} total applications)."

    elif intent == Intent.SALARY_EXPECTATION:
        avg_sal = data.get("average_salary", 0)
        sample = data.get("sample_size", 0)
        role_str = f" for **{params.role}**" if params.role else ""
        exp_str = ""
        if params.min_experience is not None and params.max_experience is not None:
            exp_str = f" with **{params.min_experience}-{params.max_experience} years** of experience"
        elif params.min_experience is not None:
            exp_str = f" with **>= {params.min_experience} years** of experience"
        elif params.max_experience is not None:
            exp_str = f" with **<= {params.max_experience} years** of experience"
        return f"The average expected salary{role_str}{exp_str} is **{avg_sal:,.2f}** (sample size: {sample})."

    return "Query executed successfully."


def render_response(response):
    status = response.execution_result.status
    visualization = response.visualization_instruction
    data = response.execution_result.raw_data

    # 1. Render primary result/error/clarification message
    if status == "INVALID_PARAMETER":
        render_error(data.get("error", "Invalid parameter provided."))
    elif status == "MISSING_PARAMETERS":
        render_clarification(data.get("missing_parameters", []))
    elif status == "UNKNOWN_INTENT":
        st.warning(data.get("message", "This query is out of scope or could not be mapped to any recruitment metrics."))
    elif status == "SUCCESS":
        # Render result text message first
        msg = get_result_message(response)
        st.info(msg)

        # 2. Render visualization instructions
        if visualization == "METRIC_CARD":
            if "average_age" in data:
                render_metric_card(
                    "Average Age",
                    f'{data["average_age"]:.2f} Years',
                    f'Sample Size: {data["sample_size"]}',
                )
            elif "average_salary" in data:
                render_metric_card(
                    "Average Expected Salary",
                    f'{data["average_salary"]:,.2f}',
                    f'Sample Size: {data["sample_size"]}',
                )
            elif "count" in data:
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

        elif visualization == "BAR_CHART":
            render_bar_chart(data)

        elif visualization == "TABLE":
            render_table(data)

        else:
            render_text_response(data)

    # 3. Always render Routing Details and LLM JSON for all queries at the bottom
    with st.expander("🔍 Show Routing Details & LLM Response JSON", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Intent Routing Details")
            st.markdown(f"**Target Intent:** `{response.intent_mapping.target_endpoint.value}`")
            st.markdown(f"**Routing Confidence:** `{response.intent_mapping.confidence_score:.4f}`")
            st.progress(max(0.0, min(1.0, response.intent_mapping.confidence_score)))
            st.markdown("**Extracted Parameters:**")
            st.json(response.intent_mapping.extracted_parameters.model_dump(exclude_none=True))
        with col2:
            st.subheader("LLM Response JSON")
            st.json(response.intent_mapping.model_dump(mode="json"))
            st.subheader("Full API Response JSON")
            st.json(response.model_dump(mode="json"))